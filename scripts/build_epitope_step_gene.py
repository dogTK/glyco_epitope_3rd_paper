"""epitope → 反応ステップ → 遺伝子 の対応表を構築し Snowflake に load。

ロジック（docs/epitope_potential_design.md）:
- エピトープの生合成酵素(HGNC)を GlycoEnzOnto の「特異的経路」でグループ化。
- 総称経路（>25遺伝子: glycan biosynthetic pathway 等）はステップにしない=除外。
- エピトープ内で「同じ特異的経路を共有する遺伝子」を連結成分でまとめ、1ステップ＝冗長isoenzyme群とする。
  → epitope potential では ステップ内=max（OR）、ステップ間=min（律速AND）で集約する。
- どの特異的経路にも属さない遺伝子は、その遺伝子単独で1ステップ扱い。

出力: RAW.GLYCOEPITOPE.EPITOPE_STEP_GENE
使い方: conda run -n glyco_pred python scripts/build_epitope_step_gene.py

GlycoEnzOnto は CC-BY-4.0（Groth et al., Bioinformatics 2022）。inputs/GlycoEnzOnto/ATTRIBUTION.md 参照。
"""
import os
import json
import pandas as pd
import snowflake.connector as sc
from snowflake.connector.pandas_tools import write_pandas

SF = dict(account='DUETMBM-LL33279', user='KOREEDA', role='ACCOUNTADMIN',
          warehouse='BIOINFORMATICS_XS', authenticator='SNOWFLAKE_JWT',
          private_key_file=os.path.expanduser('~/.ssh/snowflake_rsa_key.pem'))

PATHWAYS_JSON = 'inputs/GlycoEnzOnto/glycoenzonto_pathways.json'
UMBRELLA_MAX = 25   # これ超の経路は総称としてステップから除外


def load_specific_pathways():
    raw = json.load(open(PATHWAYS_JSON))
    paths = {k.strip('"'): set(v) for k, v in raw.items()}
    specific = {k: v for k, v in paths.items() if len(v) <= UMBRELLA_MAX}
    gene2paths = {}
    for p, genes in specific.items():
        for g in genes:
            gene2paths.setdefault(g, set()).add(p)
    return specific, gene2paths


def cluster_steps(genes, gene2paths):
    """エピトープの遺伝子集合を、特異的経路の共有で連結成分クラスタリング。"""
    genes = list(genes)
    parent = {g: g for g in genes}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        parent[find(a)] = find(b)

    for i, gi in enumerate(genes):
        for gj in genes[i + 1:]:
            if gene2paths.get(gi, set()) & gene2paths.get(gj, set()):
                union(gi, gj)

    comps = {}
    for g in genes:
        comps.setdefault(find(g), []).append(g)
    return list(comps.values())


def step_label(members, specific, gene2paths):
    """成分の代表ステップ名 = 成分内で共有される最小の特異的経路。無ければ遺伝子名。"""
    shared = None
    for g in members:
        gp = gene2paths.get(g, set())
        shared = gp if shared is None else (shared & gp)
    shared = shared or set()
    if shared:
        return min(shared, key=lambda p: len(specific[p]))
    return members[0] if len(members) == 1 else '/'.join(sorted(members))


def main():
    specific, gene2paths = load_specific_pathways()
    con = sc.connect(database='RAW', schema='GLYCOEPITOPE', **SF)
    df = con.cursor().execute("""
        SELECT EPITOPE_ID, EPITOPE_NAME, HGNC_SYMBOL
        FROM RAW.GLYCOEPITOPE.VW_EPITOPE_GLYCOGENE
        WHERE HGNC_SYMBOL IS NOT NULL AND ENZYME_ROLE='biosynthetic'
    """).fetch_pandas_all()

    rows = []
    for (epid, epname), grp in df.groupby(['EPITOPE_ID', 'EPITOPE_NAME']):
        genes = sorted(set(grp['HGNC_SYMBOL']))
        comps = cluster_steps(genes, gene2paths)
        for si, members in enumerate(sorted(comps, key=lambda m: sorted(m)), 1):
            label = step_label(members, specific, gene2paths)
            for g in sorted(members):
                rows.append(dict(EPITOPE_ID=epid, EPITOPE_NAME=epname,
                                 STEP_ID=si, STEP_PATHWAY=label, HGNC_SYMBOL=g))

    out = pd.DataFrame(rows)
    out['SOURCE'] = 'GlycoEnzOnto(CC-BY) + VW_EPITOPE_GLYCOGENE'
    ok, _, n, _ = write_pandas(con, out, 'EPITOPE_STEP_GENE',
                               auto_create_table=True, overwrite=True, quote_identifiers=False)
    print(f'loaded RAW.GLYCOEPITOPE.EPITOPE_STEP_GENE ok={ok} rows={n}')
    print(f'epitopes={out.EPITOPE_ID.nunique()}  '
          f'avg_steps/ep={out.groupby("EPITOPE_ID").STEP_ID.nunique().mean():.2f}  '
          f'genes={out.HGNC_SYMBOL.nunique()}')
    # 代表例
    for epid in ['EP0012', 'EP0001', 'EP0011']:
        sub = out[out.EPITOPE_ID == epid]
        if len(sub):
            print(f'\n{epid} {sub.EPITOPE_NAME.iloc[0]}:')
            for si, s in sub.groupby('STEP_ID'):
                print(f'  step{si} [{s.STEP_PATHWAY.iloc[0]}]: {", ".join(s.HGNC_SYMBOL)}')
    con.close()


if __name__ == '__main__':
    main()
