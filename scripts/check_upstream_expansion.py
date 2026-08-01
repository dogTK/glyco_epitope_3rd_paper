"""上流を足すと信号が潰れる原因を切り分け、正規化で救えるか試す。

仮説: min を「生の発現量」に掛けるのが誤り。
  UGCG が常に低ければ、末端酵素が何倍動いても min は UGCG に固定され Δ=0 になる。
  しかし発現量の絶対値は酵素間で比較できない（kcat も基質親和性も違う）。
  「律速」の意味は「その酵素にしては異常に低い」であるべき。

対策: 各遺伝子を **16細胞株を通じた自分自身の典型値** で割ってから min を取る。
      → 「相対的に枯れている工程」が律速として選ばれる。
"""
import pandas as pd, numpy as np

ROOT = "/Users/koreedatatsuya/research/glyco_epitope_3rd_paper/"
dag = pd.read_csv(ROOT + "data/processed/glycoenzonto_enzyme_dag.csv")
UP = dag.groupby('GENE').UPSTREAM_GENE.apply(set).to_dict()
term = pd.read_csv(ROOT + "data/processed/epitope_step_gene.csv")

trt = pd.read_parquet(ROOT + "data/processed/abs_glyco_16cell_24h.parquet")
META = ['cell', 'pertname', 'timepoint', 'dose', 'idx']
ctl = pd.read_csv(ROOT + "data/processed/ctl_glyco_baseline.csv", low_memory=False)
ctl['cell'] = ctl.SAMPLE_ID.str.split('_').str[1]
PANEL = sorted(set(c for c in trt.columns if c not in META) & set(ctl.columns))

# 各遺伝子の「典型値」= 全対照サンプルを通じた中央値
GENE_REF = ctl[PANEL].median()


def expand(depth):
    out = {}
    for epi, g in term.groupby('EPITOPE_NAME'):
        seeds = sorted(set(g.HGNC_SYMBOL) & set(PANEL))
        if not seeds:
            continue
        steps, seen, frontier = {0: seeds}, set(seeds), set(g.HGNC_SYMBOL)
        for k in range(1, depth + 1):
            nxt = set()
            for x in frontier:
                nxt |= UP.get(x, set())
            frontier = nxt - seen
            layer = sorted(frontier & set(PANEL))
            if layer:
                steps[k] = layer
            seen |= frontier
        out[epi] = steps
    return out


def project(levels, spec, centered):
    L = levels - GENE_REF if centered else levels
    out = {}
    for epi, steps in spec.items():
        per = [L[gs].max(axis=1) for gs in steps.values() if gs]
        out[epi] = pd.concat(per, axis=1).min(axis=1)
    return pd.DataFrame(out)


CELL = 'HEPG2'
t = trt[trt.cell == CELL].groupby('pertname')[PANEL].mean()
c = ctl[ctl.cell == CELL][PANEL].median()

print(f"{CELL}: {len(t)}薬\n")
print(f"{'方式':28s}{'depth':>6}{'2倍以上(総)':>12}{'GD2':>6}{'T抗原':>7}{'β1,6':>7}{'|r|中央':>9}")
for centered in [False, True]:
    for depth in [0, 1, 2]:
        spec = expand(depth)
        d = project(t, spec, centered) - project(c.to_frame().T, spec, centered).iloc[0]
        cm = d.corr().abs().values
        off = cm[~np.eye(len(cm), dtype=bool)]
        name = "遺伝子ごとに正規化" if centered else "生の発現量（現行）"
        print(f"{name:28s}{depth:6d}{int((d.abs()>=1).sum().sum()):12d}"
              f"{int((d['GD2'].abs()>=1).sum()):6d}"
              f"{int((d['T Antigen'].abs()>=1).sum()):7d}"
              f"{int((d['beta1,6-GlcNAc Branching'].abs()>=1).sum()):7d}"
              f"{np.nanmedian(off):9.3f}")

# どの遺伝子が律速に選ばれているかを見る
print("\n=== GD2(depth=1): 各方式でどのステップが min に選ばれるか ===")
spec = expand(1)['GD2']
for centered in [False, True]:
    L = t - GENE_REF if centered else t
    per = pd.DataFrame({k: L[gs].max(axis=1) for k, gs in spec.items()})
    win = per.idxmin(axis=1).value_counts()
    lab = "正規化後" if centered else "生の発現量"
    print(f"  {lab:12s} 律速に選ばれたstep: {win.to_dict()}")
    print(f"               step別の中央値: {per.median().round(2).to_dict()}")
