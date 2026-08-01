"""エピトープ単位で「薬剤が検出閾値を越えて動かすか」を数える。

前回(check_wet_target_spread.py)の誤り: 385 glycogene の中での順位で議論した。
それは遺伝子の話であってエピトープの話ではなく、比較相手(UGT・トランスポーター等)は
そもそもエピトープを持たない遺伝子なので、順位に創薬的な意味がない。

正しい問い: **各エピトープを、何本の薬が検出可能な大きさで動かすか。**
閾値は統計でなくアッセイ側から決める（レクチンフローで見える倍率）。

射影の順序は正しい形にしてある:
  処理後レベル → 射影(内max) → エピトープ量(処理後)
  対照レベル   → 射影(内max) → エピトープ量(対照)
  差を取る
※ step構造(間min)はSnowflakeのEPITOPE_STEP_GENEが要るのでここでは内maxのみ。
  52エピトープ中の大半は最大2ステップなので、一次近似としては妥当。
"""
import pandas as pd, numpy as np

ROOT = "/Users/koreedatatsuya/research/glyco_epitope_3rd_paper/"
S = ("/private/tmp/claude-501/-Users-koreedatatsuya-research-glyco-epitope-3rd-paper/"
     "f5f4bed0-501b-45cb-b4b9-c64704f525a7/scratchpad/")

df = pd.read_parquet(ROOT + "data/processed/abs_glyco_16cell_24h.parquet")
META = ['cell', 'pertname', 'timepoint', 'dose', 'idx']
genes = set(df.columns) - set(META)

epi = pd.read_csv(S + "epi_genes_list.csv")
epi = epi[epi.GENE.isin(genes)]
sets = epi.groupby('EPITOPE_NAME')['GENE'].apply(list).to_dict()

CELL = 'HEPG2'
g = df[df.cell == CELL]
print(f"{CELL}: {g.pertname.nunique()}薬 / {len(g)}試料\n")

# 薬剤ごとの平均（絶対量レベル）
lv = g.groupby('pertname')[sorted(genes)].mean()

rows = []
for name, gs in sets.items():
    epi_level = lv[gs].max(axis=1)          # 内max を「レベル」に対して適用
    base = epi_level.median()               # 対照相当（細胞内の典型レベル）
    d = epi_level - base                    # Δエピトープ（log2）
    rows.append({
        'epitope': name, 'n_gene': len(gs), 'base': base,
        'n_2x': int((d.abs() >= 1.0).sum()),
        'n_2x_up': int((d >= 1.0).sum()),
        'n_2x_dn': int((d <= -1.0).sum()),
        'n_3x': int((d.abs() >= np.log2(3)).sum()),
        'max_up': d.max(), 'max_dn': d.min(),
    })
R = pd.DataFrame(rows).sort_values('n_2x', ascending=False)
R['pct_2x'] = (100 * R.n_2x / len(lv)).round(1)

print(f"=== エピトープを2倍以上動かす薬の本数（{CELL}, 全{len(lv)}薬, 内max射影）===")
print(R.head(18)[['epitope', 'n_gene', 'base', 'n_2x', 'pct_2x',
                  'n_2x_up', 'n_2x_dn', 'max_up', 'max_dn']].round(2).to_string(index=False))

print(f"\n=== 2倍以上動かす薬が1本も無いエピトープ ===")
dead = R[R.n_2x == 0]
print(f"{len(dead)}/{len(R)} エピトープ")
print(", ".join(dead.epitope.head(20)))

print("\n=== 注目エピトープ ===")
for k in ['Core Fucose (N-glycan alpha1,6)', 'beta1,6-GlcNAc Branching',
          'Bisecting GlcNAc', 'T Antigen', 'Lewis y', 'Sialyl Lewis a',
          'Sialyl Lewis x', 'Lewis x']:
    r = R[R.epitope == k]
    if len(r):
        r = r.iloc[0]
        print(f"  {k:34s} 遺伝子{r.n_gene}  base {r.base:5.2f}  "
              f"2倍以上 {r.n_2x:3d}本({r.pct_2x:4.1f}%)  "
              f"最大 +{r.max_up:.2f}/{r.max_dn:.2f} log2")
    else:
        print(f"  {k:34s} 辞書に無し（L1000内の遺伝子が0）")
