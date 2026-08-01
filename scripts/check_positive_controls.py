"""陽性対照になりうる薬（糖鎖への作用が既知）が LINCS に入っているか調べる。

wet が使えない場合、検証は「作用が文献で分かっている薬を、スコアが正しく拾えるか」に置き換わる。
そのベンチマークが組めるかどうかを、まず在庫で確認する。
"""
import pandas as pd

ROOT = "/Users/koreedatatsuya/research/glyco_epitope_3rd_paper/"
df = pd.read_parquet(ROOT + "data/processed/abs_glyco_16cell_24h.parquet")

# 糖鎖生合成に直接作用することが知られている化合物
KNOWN = {
    "tunicamycin":     "N型糖鎖付加の阻害（DPAGT1）→ 全N型が減る",
    "swainsonine":     "α-mannosidase II 阻害 → hybrid型が溜まり複合型が減る",
    "kifunensine":     "ER α-mannosidase I 阻害 → high mannose が溜まる",
    "castanospermine": "glucosidase 阻害 → high mannose 側へ",
    "deoxynojirimycin": "glucosidase 阻害",
    "brefeldin-a":     "ゴルジ崩壊 → 糖鎖成熟が止まる",
    "monensin":        "ゴルジ内 pH 撹乱 → 糖鎖成熟障害",
    "benzyl-2-acetamido-2-deoxy-galactopyranoside": "O型糖鎖伸長の阻害",
    "2-deoxy-glucose": "解糖阻害・糖ヌクレオチド供給低下",
    "6-diazo-5-oxonorleucine": "GFAT阻害 → UDP-GlcNAc低下",
    "azaserine":       "グルタミン代謝 → ヘキソサミン経路",
    "thiamet-g":       "OGA阻害 → O-GlcNAc上昇",
    "alloxan":         "OGT阻害",
    "streptozotocin":  "OGA/OGT 関連",
}

perts = pd.Index(df.pertname.unique())
low = pd.Series(perts, index=perts.str.lower())

print(f"LINCS 24h 全体: {len(perts):,} 化合物 / {df.cell.nunique()} 細胞\n")
print(f"{'化合物':46s} {'LINCS':>6s} {'HEPG2':>6s}  作用")
print("-" * 118)
hep = set(df[df.cell == 'HEPG2'].pertname.unique())
n_all = n_hep = 0
for name, moa in KNOWN.items():
    hit = [p for p in perts if name in p.lower()]
    if hit:
        n_all += 1
        inhep = [h for h in hit if h in hep]
        if inhep:
            n_hep += 1
        print(f"{hit[0][:45]:46s} {'○':>6s} {'○' if inhep else '−':>6s}  {moa}")
    else:
        print(f"{name[:45]:46s} {'−':>6s} {'−':>6s}  {moa}")

print(f"\n→ 既知作用の化合物 {len(KNOWN)} 件中 LINCS に {n_all} 件、HEPG2(24h) に {n_hep} 件")

# HEPG2 で使える細胞株の薬剤数も確認
print("\n=== 細胞株ごとの 24h 薬剤数（陽性対照が最も揃う細胞を選ぶため）===")
c = df.groupby('cell').pertname.nunique().sort_values(ascending=False)
print(c.head(8).to_string())
