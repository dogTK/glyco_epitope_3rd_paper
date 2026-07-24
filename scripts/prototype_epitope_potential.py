"""epitope potential v2 プロトタイプ（HEPG2）。

ロジック（docs/epitope_potential_design.md）:
  step活性 A_s = max_{g in step} zscore_g   （ステップ内 isoenzyme = OR）
  potential P_e = min_s A_s                 （ステップ間 = 律速 AND）

- 発現: RAW.LINCS.GLYCO_GENES_WIDE（cell=HEPG2）。glycogene列のz-scoreを化合物(pertname)平均。
- ステップ: RAW.GLYCOEPITOPE.EPITOPE_STEP_GENE（GlycoEnzOnto由来, CC-BY）。
出力: results/tables/epitope_potential_hepg2_v2.csv（薬剤×エピトープ）
使い方: conda run -n glyco_pred python scripts/prototype_epitope_potential.py
"""
import os
import numpy as np
import pandas as pd
import snowflake.connector as sc

SF = dict(account='DUETMBM-LL33279', user='KOREEDA', role='ACCOUNTADMIN',
          warehouse='BIOINFORMATICS_XS', authenticator='SNOWFLAKE_JWT',
          private_key_file=os.path.expanduser('~/.ssh/snowflake_rsa_key.pem'))
CELL = 'HEPG2'
OUT = 'results/tables/epitope_potential_hepg2_v2.csv'


def main():
    con = sc.connect(database='RAW', schema='GLYCOEPITOPE', **SF)
    cur = con.cursor()

    # ステップ表
    steps = cur.execute("""
        SELECT EPITOPE_ID, EPITOPE_NAME, STEP_ID, HGNC_SYMBOL
        FROM RAW.GLYCOEPITOPE.EPITOPE_STEP_GENE
    """).fetch_pandas_all()

    # GLYCO_GENES_WIDE に列がある遺伝子だけ使う
    cols = set(r[0] for r in cur.execute("""
        SELECT COLUMN_NAME FROM RAW.INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA='LINCS' AND TABLE_NAME='GLYCO_GENES_WIDE'
    """).fetchall())
    genes = sorted(set(steps['HGNC_SYMBOL']) & cols)
    missing = sorted(set(steps['HGNC_SYMBOL']) - cols)
    print(f'使用遺伝子 {len(genes)} / 欠損 {missing}')

    # 発現取得（pertname + gene列）: メタ列は小文字クォート
    sel = ', '.join(['"pertname"'] + [f'"{g}"' for g in genes])
    expr = cur.execute(
        f'SELECT {sel} FROM RAW.LINCS.GLYCO_GENES_WIDE WHERE "cell"=%s', (CELL,)
    ).fetch_pandas_all()
    expr.columns = ['pertname'] + genes
    for g in genes:
        expr[g] = pd.to_numeric(expr[g], errors='coerce')
    # 化合物平均（署名/用量/時間をまとめる）
    cmean = expr.groupby('pertname')[genes].mean()
    print(f'化合物 {cmean.shape[0]} × 遺伝子 {cmean.shape[1]}（HEPG2）')

    # potential: step内max → step間min
    ep_steps = (steps[steps.HGNC_SYMBOL.isin(genes)]
                .groupby(['EPITOPE_ID', 'EPITOPE_NAME', 'STEP_ID'])['HGNC_SYMBOL']
                .apply(list).reset_index())
    result = {}
    for (epid, epname), grp in ep_steps.groupby(['EPITOPE_ID', 'EPITOPE_NAME']):
        step_max = []
        for _, r in grp.iterrows():
            step_max.append(cmean[r['HGNC_SYMBOL']].max(axis=1))   # step内 max
        pot = pd.concat(step_max, axis=1).min(axis=1)              # step間 min
        result[f'{epid}|{epname}'] = pot
    mat = pd.DataFrame(result)   # 化合物 × エピトープ
    os.makedirs('results/tables', exist_ok=True)
    mat.to_csv(OUT)
    print(f'\n書き出し: {OUT}  shape={mat.shape}')

    # 代表エピトープの上位化合物
    for key in [k for k in mat.columns if 'Sialyl Lewis x' in k or 'HNK-1' in k or 'Lewis y' in k]:
        top = mat[key].dropna().sort_values(ascending=False).head(5)
        print(f'\n[{key}] potential上位:')
        for name, v in top.items():
            print(f'   {v:+.3f}  {name}')
    con.close()


if __name__ == '__main__':
    main()
