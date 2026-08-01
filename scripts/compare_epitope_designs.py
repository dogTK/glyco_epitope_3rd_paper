"""案A〜Dを、先に決めた基準で比較する。

案:
  A 末端のみ（現行 depth=0）           … min が空回りする
  B 上流あり × 生の発現量               … 律速が発現量の大小に乗っ取られる（棄却予定）
  C 上流あり × 遺伝子ごとに中心化        … 「その酵素にしては低い」を律速とする
  D 末端の値 × 上流ゲート                … 上流は min に入れず「基質があるか」の門としてのみ使う

基準（信号量だけで選ぶと循環するので4つ見る）:
  1 再現性  同じ薬を試料で半分に割った2本のエピトープベクトルの一致度（高いほど良い）
            対照として別の薬同士の一致度も出す＝差が信号
  2 信号量  2倍以上動く 薬×エピトープ の数
  3 特異性  エピトープ間の相関の中央値（高すぎると皆同じ動き＝区別がつかない）
  4 ストレス漏れ  全385 glycogene の平均|Δ|（＝その薬がどれだけ細胞を揺すったか）との相関
"""
import pandas as pd, numpy as np, itertools

ROOT = "/Users/koreedatatsuya/research/glyco_epitope_3rd_paper/"
dag = pd.read_csv(ROOT + "data/processed/glycoenzonto_enzyme_dag.csv")
UP = dag.groupby('GENE').UPSTREAM_GENE.apply(set).to_dict()
term = pd.read_csv(ROOT + "data/processed/epitope_step_gene.csv")

trt = pd.read_parquet(ROOT + "data/processed/abs_glyco_16cell_24h.parquet")
META = ['cell', 'pertname', 'timepoint', 'dose', 'idx']
ctl = pd.read_csv(ROOT + "data/processed/ctl_glyco_baseline.csv", low_memory=False)
ctl['cell'] = ctl.SAMPLE_ID.str.split('_').str[1]
PANEL = sorted(set(c for c in trt.columns if c not in META) & set(ctl.columns))
REF = ctl[PANEL].median()

CELL = 'HEPG2'
S = trt[trt.cell == CELL]
C = ctl[ctl.cell == CELL][PANEL].median()


def spec(depth):
    out = {}
    for epi, g in term.groupby('EPITOPE_NAME'):
        seeds = sorted(set(g.HGNC_SYMBOL) & set(PANEL))
        if not seeds:
            continue
        steps, seen, fr = {0: seeds}, set(seeds), set(g.HGNC_SYMBOL)
        for k in range(1, depth + 1):
            nxt = set()
            for x in fr:
                nxt |= UP.get(x, set())
            fr = nxt - seen
            lay = sorted(fr & set(PANEL))
            if lay:
                steps[k] = lay
            seen |= fr
        out[epi] = steps
    return out


SPEC0, SPEC1 = spec(0), spec(1)
# 上流ゲート: その細胞で上流ステップの最大発現が全遺伝子中央値を超えていれば通す
GATE = {e: (float(C[s[1]].max()) >= float(C.median())) if 1 in s else True
        for e, s in SPEC1.items()}


def score(levels, method):
    L = levels - REF if method in ('C',) else levels
    sp = SPEC1 if method in ('B', 'C') else SPEC0
    out = {}
    for epi, steps in sp.items():
        per = [L[gs].max(axis=1) for gs in steps.values() if gs]
        v = pd.concat(per, axis=1).min(axis=1)
        if method == 'D' and not GATE.get(epi, True):
            v = v * 0.0            # 基質が無い＝そのエピトープは動かせない
        out[epi] = v
    return pd.DataFrame(out)


BASE = {m: score(C.to_frame().T, m).iloc[0] for m in 'ABCD'}
FULL = {m: score(S.groupby('pertname')[PANEL].mean(), m) - BASE[m] for m in 'ABCD'}

# --- 1. 分割再現性 ---
rng = np.random.default_rng(0)
grp = {p: g for p, g in S.groupby('pertname') if len(g) >= 2}
halves = {}
for m in 'ABCD':
    a, b = {}, {}
    for p, g in grp.items():
        idx = rng.permutation(len(g)); h = len(g) // 2
        a[p] = score(g.iloc[idx[:h]][PANEL].mean().to_frame().T, m).iloc[0] - BASE[m]
        b[p] = score(g.iloc[idx[h:]][PANEL].mean().to_frame().T, m).iloc[0] - BASE[m]
    halves[m] = (pd.DataFrame(a).T, pd.DataFrame(b).T)


def cos(x, y):
    d = np.linalg.norm(x) * np.linalg.norm(y)
    return float(np.dot(x, y) / d) if d > 0 else np.nan


print(f"対象: {CELL} / 全{FULL['A'].shape[0]}薬 / 分割可能 {len(grp)}薬 / {FULL['A'].shape[1]}エピトープ\n")
print(f"{'案':3s}{'説明':26s}{'再現性':>8s}{'別薬(帰無)':>11s}{'差':>7s}"
      f"{'信号量':>8s}{'特異性|r|':>10s}{'ストレス漏れ':>12s}")

LAB = {'A': '末端のみ（現行）', 'B': '上流あり×生の発現量',
       'C': '上流あり×遺伝子中心化', 'D': '末端×上流ゲート'}
stress = S.groupby('pertname')[PANEL].mean().sub(C).abs().mean(axis=1)

for m in 'ABCD':
    A, B = halves[m]
    same = np.nanmedian([cos(A.loc[p].values, B.loc[p].values) for p in A.index])
    pairs = list(itertools.islice(itertools.combinations(A.index, 2), 4000))
    diff = np.nanmedian([cos(A.loc[p].values, B.loc[q].values) for p, q in pairs])
    d = FULL[m]
    cm = d.corr().abs().values
    off = np.nanmedian(cm[~np.eye(len(cm), dtype=bool)])
    leak = np.nanmedian([abs(np.corrcoef(d[e], stress[d.index])[0, 1]) for e in d.columns])
    print(f"{m:3s}{LAB[m]:26s}{same:8.3f}{diff:11.3f}{same-diff:7.3f}"
          f"{int((d.abs() >= 1).sum().sum()):8d}{off:10.3f}{leak:12.3f}")

print("\n=== 案Dのゲートで落ちたエピトープ ===")
off_ = [e for e, v in GATE.items() if not v]
print(f"{len(off_)}/{len(GATE)} 件: {', '.join(off_[:12]) if off_ else 'なし（全て基質あり）'}")
