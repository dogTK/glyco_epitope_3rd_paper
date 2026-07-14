import os, re
import pandas as pd
import snowflake.connector as sc
from snowflake.connector.pandas_tools import write_pandas

SF = dict(account='DUETMBM-LL33279', user='KOREEDA', role='ACCOUNTADMIN',
          warehouse='BIOINFORMATICS_XS', authenticator='SNOWFLAKE_JWT',
          private_key_file=os.path.expanduser('~/.ssh/snowflake_rsa_key.pem'))

# 高〜中確信のHGNC割当（名前＋EC番号を根拠に確認）。曖昧なものは入れない=review。
ALIAS = {
    'FUT3': 'FUT3', 'FUT7': 'FUT7', 'FUT9': 'FUT9',
    'GAL3ST1': 'GAL3ST1', 'Gal3ST3': 'GAL3ST3', 'NDST-1': 'NDST1',
    'ST6Gal I': 'ST6GAL1', 'ST3Gal I': 'ST3GAL1', 'ST3Gal IV': 'ST3GAL4',
    'ST3Gal V': 'ST3GAL5', 'ST6GalNAc I': 'ST6GALNAC1', 'ST6GalNAc VI': 'ST6GALNAC6',
    'ST8Sia I': 'ST8SIA1', 'ST8Sia IV': 'ST8SIA4', 'ST8Sia V': 'ST8SIA5',
    'O-GlcNAcT': 'OGT', 'Beta3GlcT': 'B3GLCT', 'Forssman synthase': 'GBGT1',
    'core 1 beta1-3Gal-T': 'C1GALT1', 'Alpha4Gal-T1': 'A4GALT', 'a4Gal-T': 'A4GALT',
    'Beta3Gal-T4': 'B3GALT4', 'Beta3Gal-T5': 'B3GALT5',
    'Beta4Gal-T4': 'B4GALT4', 'Beta4Gal-T6': 'B4GALT6',
    'GalNAc-T': 'B4GALNT1',            # EC 2.4.1.92 = GM2/GD2 synthase
    'CST': 'GAL3ST1',                  # cerebroside sulfotransferase EC 2.8.2.11
    'HNK-1 ST': 'CHST10',             # medium
    'HEC-GlcNAc6ST': 'CHST4',         # medium
}
# 括弧内にHGNCを含むもの（正規表現で抽出）: C4ST-1 (CHST11), C6ST-2(CHST7), ChSy-3(CSGlcAT)
PAREN_OVERRIDE = {'ChSy-3(CSGlcAT)': 'CHSY3'}  # CSGlcAT の括弧内はHGNCでないため明示
NONHUMAN = {'PMT-1', 'Heparitinase(Flavobacterium heparinum)'}
CONF = {}  # confidence override
for k in ['HNK-1 ST', 'HEC-GlcNAc6ST', 'ChSy-3(CSGlcAT)']:
    CONF[k] = 'medium'

con = sc.connect(database='RAW', schema='GLYCOEPITOPE', **SF)
cur = con.cursor()
names = [r[0] for r in cur.execute(
    "SELECT DISTINCT GENE_SYMBOL FROM RAW.GLYCOEPITOPE.EPITOPE_ENZYME ORDER BY GENE_SYMBOL").fetchall()]

rows = []
for n in names:
    hgnc, method, conf = None, 'review', 'low'
    if n in NONHUMAN:
        method, conf = 'nonhuman', 'na'
    elif n in PAREN_OVERRIDE:
        hgnc, method, conf = PAREN_OVERRIDE[n], 'paren_alias', CONF.get(n, 'medium')
    else:
        m = re.search(r'\(([A-Z0-9]{3,})\)', n)  # HGNCらしい括弧内トークン
        if m and re.match(r'^(CHST|CHSY|B\dGAL|ST\d|FUT|GALNT)', m.group(1)):
            hgnc, method, conf = m.group(1), 'paren_extract', 'high'
        elif n in ALIAS:
            hgnc, method, conf = ALIAS[n], 'curated_alias', CONF.get(n, 'high')
    rows.append(dict(GENE_SYMBOL_RAW=n, HGNC_SYMBOL=hgnc, MAPPING_METHOD=method, CONFIDENCE=conf))

xw = pd.DataFrame(rows)
ok, _, nrows, _ = write_pandas(con, xw, "ENZYME_HGNC_CROSSWALK",
                               auto_create_table=True, overwrite=True, quote_identifiers=False)
print("crosswalk loaded:", ok, nrows)
print(xw['MAPPING_METHOD'].value_counts().to_string())
print("\nreview対象（要確認）:")
print(xw[xw.MAPPING_METHOD=='review']['GENE_SYMBOL_RAW'].to_string(index=False))

# epitope→hgnc ビュー
cur.execute("""
CREATE OR REPLACE VIEW RAW.GLYCOEPITOPE.VW_EPITOPE_GLYCOGENE AS
SELECT e.EPITOPE_ID, e.ENZYME_ROLE, e.GENE_SYMBOL AS GENE_SYMBOL_RAW,
       x.HGNC_SYMBOL, x.MAPPING_METHOD, x.CONFIDENCE, e.EC, e.CAZY
FROM RAW.GLYCOEPITOPE.EPITOPE_ENZYME e
LEFT JOIN RAW.GLYCOEPITOPE.ENZYME_HGNC_CROSSWALK x
  ON e.GENE_SYMBOL = x.GENE_SYMBOL_RAW
""")

# LINCS glycogene カバレッジ
cur.execute("""
WITH hg AS (SELECT DISTINCT HGNC_SYMBOL g FROM RAW.GLYCOEPITOPE.ENZYME_HGNC_CROSSWALK WHERE HGNC_SYMBOL IS NOT NULL),
glyco AS (SELECT COLUMN_NAME g FROM RAW.INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='LINCS' AND TABLE_NAME='GLYCO_GENES_WIDE')
SELECT (SELECT COUNT(*) FROM hg) mapped_hgnc,
       (SELECT COUNT(*) FROM hg JOIN glyco USING(g)) in_lincs_glyco
""")
print("\nHGNC mapped / in LINCS glyco:", cur.fetchone())
# epitope coverage
cur.execute("""
SELECT COUNT(DISTINCT EPITOPE_ID) FROM RAW.GLYCOEPITOPE.VW_EPITOPE_GLYCOGENE WHERE HGNC_SYMBOL IS NOT NULL
""")
print("epitopes with >=1 HGNC-mapped enzyme:", cur.fetchone()[0])
con.close()
