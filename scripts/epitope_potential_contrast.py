"""epitope potential v2 + コントラスト（HEPG2）。

前回の素の potential は全化合物で一律プラス寄り（共通の底上げ）で分離が弱かった。
明示的DMSO対照が無いため、**全化合物平均を基準線**にして「平均的な薬よりどれだけ強く動かすか」で対比する。

手順:
  1. cmean（化合物 × glycogene, zスコア平均）を作る
  2. 遺伝子ごとに across-compound 平均を引く（centered）= コントラスト
  3. centered に step内max × step間min を適用 → potential_contrast
  4. さらに化合物間で zスコア化してランク付け

出力: results/tables/epitope_potential_hepg2_contrast.csv
使い方: conda run -n glyco_pred python scripts/epitope_potential_contrast.py
"""
import os
import numpy as np
import pandas as pd
import snowflake.connector as sc

SF = dict(account='DUETMBM-LL33279', user='KOREEDA', role='ACCOUNTADMIN',
          warehouse='BIOINFORMATICS_XS', authenticator='SNOWFLAKE_JWT',
          private_key_file=os.path.expanduser('~/.ssh/snowflake_rsa_key.pem'))
CELL = 'HEPG2'
OUT = 'results/tables/epitope_potential_hepg2_contrast.csv'


def potential_matrix(expr_by_compound, ep_steps, genes):
    """化合物×遺伝子 → 化合物×エピトープ（step内max, step間min）"""
    result = {}
    for (epid, epname), grp in ep_steps.groupby(['EPITOPE_ID', 'EPITOPE_NAME']):
        step_max = [expr_by_compound[r['HGNC_SYMBOL']].max(axis=1) for _, r in grp.iterrows()]
        result[f'{epid}|{epname}'] = pd.concat(step_max, axis=1).min(axis=1)
    return pd.DataFrame(result)


def main():
    con = sc.connect(database='RAW', schema='GLYCOEPITOPE', **SF)
    cur = con.cursor()
    steps = cur.execute(
        "SELECT EPITOPE_ID, EPITOPE_NAME, STEP_ID, HGNC_SYMBOL FROM RAW.GLYCOEPITOPE.EPITOPE_STEP_GENE"
    ).fetch_pandas_all()
    cols = set(r[0] for r in cur.execute(
        "SELECT COLUMN_NAME FROM RAW.INFORMATION_SCHEMA.COLUMNS "
        "WHERE TABLE_SCHEMA='LINCS' AND TABLE_NAME='GLYCO_GENES_WIDE'").fetchall())
    genes = sorted(set(steps['HGNC_SYMBOL']) & cols)

    sel = ', '.join(['"pertname"'] + [f'"{g}"' for g in genes])
    expr = cur.execute(
        f'SELECT {sel} FROM RAW.LINCS.GLYCO_GENES_WIDE WHERE "cell"=%s', (CELL,)).fetch_pandas_all()
    expr.columns = ['pertname'] + genes
    for g in genes:
        expr[g] = pd.to_numeric(expr[g], errors='coerce')
    cmean = expr.groupby('pertname')[genes].mean()
    print(f'化合物 {cmean.shape[0]} × 遺伝子 {cmean.shape[1]}（HEPG2）')

    ep_steps = (steps[steps.HGNC_SYMBOL.isin(genes)]
                .groupby(['EPITOPE_ID', 'EPITOPE_NAME', 'STEP_ID'])['HGNC_SYMBOL']
                .apply(list).reset_index())

    # (1) 素 potential  (2) コントラスト: 遺伝子を across-compound 平均で中心化
    raw = potential_matrix(cmean, ep_steps, genes)
    centered = cmean - cmean.mean(axis=0)
    contrast = potential_matrix(centered, ep_steps, genes)
    # 化合物間 zスコア（エピトープ列ごと）
    zpot = (contrast - contrast.mean(axis=0)) / contrast.std(axis=0)

    os.makedirs('results/tables', exist_ok=True)
    contrast.to_csv(OUT)
    zpot.to_csv(OUT.replace('.csv', '_z.csv'))

    # 分離度の比較（列ごとの標準偏差の中央値と、値域）
    print(f'\n【分離度】 素potential: 平均±{raw.stack().std():.3f}, 値域[{raw.min().min():.3f},{raw.max().max():.3f}]')
    print(f'          コントラスト: 平均±{contrast.stack().std():.3f}, 値域[{contrast.min().min():.3f},{contrast.max().max():.3f}]')

    # 代表エピトープ: コントラストの上位・下位
    for key in [k for k in contrast.columns if 'Sialyl Lewis x' in k or 'HNK-1' in k or 'Lewis y' in k]:
        s = contrast[key].dropna().sort_values(ascending=False)
        print(f'\n[{key}]  ↑増やす薬 top3 / ↓減らす薬 bottom3 (zスコア併記)')
        for name, v in s.head(3).items():
            print(f'   +{v:.3f} (z={zpot[key][name]:+.2f})  {name}')
        for name, v in s.tail(3).items():
            print(f'   {v:.3f} (z={zpot[key][name]:+.2f})  {name}')
    con.close()


if __name__ == '__main__':
    main()
