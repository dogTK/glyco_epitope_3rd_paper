"""wet標的の選定根拠をデータから確認する。

問い: HepG2 で「薬剤で最も動く」糖鎖遺伝子はどれで、FUT8(core fucose)はどこに位置するか。
指標: 各細胞内で (薬剤ごとの平均発現 − その細胞の全薬剤中央値) の分布の広がり。
      = 「その細胞でその遺伝子が薬剤によってどれだけ振れるか」
"""
import pandas as pd, numpy as np

ROOT = "/Users/koreedatatsuya/research/glyco_epitope_3rd_paper/"
S = ("/private/tmp/claude-501/-Users-koreedatatsuya-research-glyco-epitope-3rd-paper/"
     "f5f4bed0-501b-45cb-b4b9-c64704f525a7/scratchpad/")

df = pd.read_parquet(ROOT + "data/processed/abs_glyco_16cell_24h.parquet")
META = ['cell', 'pertname', 'timepoint', 'dose', 'idx']
genes = [c for c in df.columns if c not in META]

epi = pd.read_csv(S + "epi_genes_list.csv")
epi_map = epi.groupby('GENE')['EPITOPE_NAME'].apply(list).to_dict()
sizes = pd.read_csv(S + "epi.csv").set_index('EPITOPE_NAME')

rows = []
for cell, g in df.groupby('cell'):
    if len(g) < 200:
        continue
    dm = g.groupby('pertname')[genes].mean()          # 薬剤ごとの平均
    dev = dm - dm.median()                             # 細胞内の典型からのズレ
    rows.append(pd.DataFrame({
        'cell': cell, 'gene': genes, 'n_drug': len(dm),
        'sd': dev.std().values,
        'p95': dev.abs().quantile(0.95).values,
        'base': dm.median().values,
    }))
R = pd.concat(rows)

print("=== 細胞ごとの薬剤誘導スプレッド（全385 glycogeneの中央値 sd）===")
print(R.groupby('cell')['sd'].median().sort_values(ascending=False).to_string())

H = R[R.cell == 'HEPG2'].set_index('gene').sort_values('sd', ascending=False)
H['rank'] = np.arange(1, len(H) + 1)
print(f"\n=== HEPG2 ({H.n_drug.iloc[0]}薬) で薬剤によって最も動く glycogene 上位15 ===")
print(H.head(15)[['sd', 'p95', 'base', 'rank']].round(3).to_string())

print("\n=== 注目エピトープの構成遺伝子が HEPG2 でどこに位置するか ===")
watch = {
    'Core Fucose (FUT8)':        ['FUT8'],
    'Bisecting GlcNAc (MGAT3)':  ['MGAT3'],
    'b1,6 branching (MGAT5)':    ['MGAT5'],
    'Lewis y (7遺伝子/L1000 5)':  ['FUT1', 'FUT2', 'FUT3', 'FUT4', 'FUT5', 'FUT6', 'FUT9'],
    'Sialyl Lewis a=CA19-9':     ['FUT3', 'ST3GAL3', 'ST3GAL4'],
    'Sialyl Lewis x':            ['FUT3', 'FUT4', 'FUT5', 'FUT6', 'FUT7', 'ST3GAL3', 'ST3GAL4'],
    'T antigen (C1GALT1)':       ['C1GALT1'],
}
for name, gs in watch.items():
    have = [g for g in gs if g in H.index]
    if not have:
        print(f"{name:28s} : L1000内に無し")
        continue
    sub = H.loc[have, ['sd', 'base', 'rank']]
    print(f"{name:28s} : " + ", ".join(
        f"{g}(sd={sub.loc[g,'sd']:.2f}, base={sub.loc[g,'base']:.1f}, {int(sub.loc[g,'rank'])}位)"
        for g in have))

print("\n=== FUT8 を全細胞で比較（どの細胞で最も薬剤に動くか）===")
f8 = R[R.gene == 'FUT8'].sort_values('sd', ascending=False)
print(f8[['cell', 'sd', 'p95', 'base', 'n_drug']].round(3).to_string(index=False))
