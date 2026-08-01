"""特異性チェック：上位エピトープは「汎ストレスの代理指標」ではないか。

3つの角度で潰す:
  1 全トランスクリプトーム(23,614遺伝子)の撹乱の大きさとの相関
  2 撹乱の大きさを回帰で除いた後も閾値を越える薬が残るか
  3 パネル385遺伝子から作ったランダム対照と比べて、本当に応答が大きいのか
"""
import numpy as np, pandas as pd

ROOT = "/Users/koreedatatsuya/research/glyco_epitope_3rd_paper/"
CELL = "HEPG2"

# ---- 1. 全遺伝子から「その薬がどれだけ細胞を揺すったか」を出す ----
meta = pd.read_parquet(ROOT + "data/processed/abs_full_16cell_24h_meta.parquet")
X = np.load(ROOT + "data/processed/abs_full_16cell_24h.npy", mmap_mode="r")
sel = np.where(meta.cell.values == CELL)[0]
sub = np.asarray(X[sel], dtype=np.float32)
m = meta.iloc[sel]
print(f"{CELL}: 全遺伝子行列 {sub.shape}")

dm = pd.DataFrame(sub, index=m.pertname.values).groupby(level=0).mean()
stress = (dm - dm.median()).abs().mean(axis=1).rename("stress")
print(f"撹乱の大きさ: 中央値 {stress.median():.3f} / 最大 {stress.max():.3f} ({stress.idxmax()})")
del sub, X

# ---- エピトープΔ（案D・ゲート後）を再計算 ----
term = pd.read_csv(ROOT + "data/processed/epitope_step_gene.csv")
dag = pd.read_csv(ROOT + "data/processed/glycoenzonto_enzyme_dag.csv")
UP = dag.groupby("GENE").UPSTREAM_GENE.apply(set).to_dict()
trt = pd.read_parquet(ROOT + "data/processed/abs_glyco_16cell_24h.parquet")
META = ["cell", "pertname", "timepoint", "dose", "idx"]
ctl = pd.read_csv(ROOT + "data/processed/ctl_glyco_baseline.csv", low_memory=False)
ctl["cell"] = ctl.SAMPLE_ID.str.split("_").str[1]
PANEL = sorted(set(c for c in trt.columns if c not in META) & set(ctl.columns))

t = trt[trt.cell == CELL].groupby("pertname")[PANEL].mean()
c = ctl[ctl.cell == CELL][PANEL].median()
thr = float(c.median())

sets = term.groupby("EPITOPE_NAME").HGNC_SYMBOL.apply(lambda s: frozenset(s) & set(PANEL))
sets = sets[sets.apply(len) > 0]
rep = {}
for epi, gs in sets.items():
    rep.setdefault(gs, epi)
EPIS = sorted(rep.values())

d = {}
for e in EPIS:
    seeds = set(term[term.EPITOPE_NAME == e].HGNC_SYMBOL)
    up = sorted((set().union(*[UP.get(x, set()) for x in seeds]) - seeds) & set(PANEL))
    if up and float(c[up].max()) < thr:
        continue                                   # ゲート落ち
    g = sorted(sets[e])
    d[e] = t[g].max(axis=1) - c[g].max()
D = pd.DataFrame(d)
stress = stress.reindex(D.index)
print(f"ゲート通過 {D.shape[1]} エピトープ / {len(D)} 薬\n")

# ---- 2. ストレスとの相関 / 除去後の残存 ----
rows = []
for e in D.columns:
    y, s = D[e].values, stress.values
    r = np.corrcoef(y, s)[0, 1]
    b = np.polyfit(s, y, 1)
    resid = y - np.polyval(b, s)
    rows.append(dict(epitope=e, n_2x=int((np.abs(y) >= 1).sum()),
                     r_stress=r, n_2x_resid=int((np.abs(resid) >= 1).sum())))
R = pd.DataFrame(rows).sort_values("n_2x", ascending=False)
R["retained"] = (100 * R.n_2x_resid / R.n_2x.replace(0, np.nan)).round(0)

# ---- 3. ランダム対照（パネルの単一遺伝子 385個すべて） ----
allg = ((t[PANEL] - c[PANEL]).abs() >= 1).sum()
print("=== 参考: パネル385遺伝子それぞれで「2倍以上動かす薬」の本数分布 ===")
print(f"  中央値 {allg.median():.0f} / 75%点 {allg.quantile(.75):.0f} / "
      f"90%点 {allg.quantile(.9):.0f} / 最大 {allg.max():.0f}")

term_gene = {e: sorted(sets[e]) for e in D.columns}
R["pct_rank"] = [round(float((allg < allg[term_gene[e]].max()).mean() * 100)) for e in R.epitope]

print("\n=== 特異性チェック（上位12）===")
print(f"{'epitope':30s}{'2倍以上':>8}{'ストレス相関':>12}{'除去後':>8}{'残存%':>7}{'パネル内順位':>12}")
for _, x in R.head(12).iterrows():
    print(f"{x.epitope:30s}{x.n_2x:8d}{x.r_stress:12.3f}{x.n_2x_resid:8d}"
          f"{'' if np.isnan(x.retained) else int(x.retained):>7}{x.pct_rank:>11}%")

R.to_csv(ROOT + "results/tables/epitope_specificity_check_hepg2.csv", index=False)
print(f"\n中央値: ストレス相関 |r| = {R.r_stress.abs().median():.3f} / "
      f"除去後の残存 = {R.retained.median():.0f}%")
print("保存: results/tables/epitope_specificity_check_hepg2.csv")
