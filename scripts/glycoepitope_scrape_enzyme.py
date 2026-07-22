"""GlycoEpitope (glycoepitope.jp) の各エピトープ Enzyme タブをスクレイプし、
epitope → 生合成/分解 酵素（遺伝子名・EC・CAZy・反応式）を抽出する。

出力: RAW.GLYCOEPITOPE.EPITOPE_ENZYME（Snowflake）

- 対象エピトープIDは Snowflake の RAW.GLYCOEPITOPE.EPITOPES から取得（173件）。
- glycoepitope.jp は一括APIが無いため、各 /epitopes/{ID}/enzyme のHTMLを解析。
- レート制限（sleep=0.6s）を入れて丁寧に取得。

注意: GENE_SYMBOL は glycoepitope.jp の記載名で、HGNC正式シンボルとは限らない
（例 "ST6GAL I", "C4ST-1 (CHST11)"）。LINCS glycogene と突合するには別途HGNC正規化が必要。

使い方: conda run -n glyco_pred python scripts/glycoepitope_scrape_enzyme.py
"""
import os
import re
import sys
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
import snowflake.connector as sc
from snowflake.connector.pandas_tools import write_pandas

UA = {"User-Agent": "Mozilla/5.0 (research; glyco-epitope-3rd)"}
ENZYME_URL = "https://www.glycoepitope.jp/epitopes/{}/enzyme"

SF = dict(account='DUETMBM-LL33279', user='KOREEDA', role='ACCOUNTADMIN',
          warehouse='BIOINFORMATICS_XS', authenticator='SNOWFLAKE_JWT',
          private_key_file=os.path.expanduser('~/.ssh/snowflake_rsa_key.pem'))


def parse_enzyme(epid, html):
    soup = BeautifulSoup(html, "html.parser")
    rows, role = [], None
    for el in soup.find_all(["h3", "table"]):
        if el.name == "h3":
            t = el.get_text(" ", strip=True).lower()
            role = ("biosynthetic" if "biosynthetic enzyme" in t
                    else "degradation" if "degradation enzyme" in t else None)
        elif el.name == "table" and role is not None:
            d = {}
            for tr in el.find_all("tr"):
                th, td = tr.find("th"), tr.find("td")
                if th and td:
                    d[th.get_text(" ", strip=True)] = td.get_text(" ", strip=True)
            name = d.get("Name", "").strip()
            if not name:
                continue
            cazy = ",".join(re.findall(r"CAZy:\s*([A-Z]{2}\d+)", d.get("DB", ""))) or None
            rows.append(dict(
                EPITOPE_ID=epid, ENZYME_ROLE=role, GENE_SYMBOL=name,
                EC=(d.get("EC", "").replace("EC", "").strip() or None),
                CAZY=cazy, REACTION=(d.get("Reaction") or None),
                DESCRIPTION=(d.get("Description") or None),
            ))
    return rows


def main():
    con = sc.connect(database='RAW', schema='GLYCOEPITOPE', **SF)
    ids = [r[0] for r in con.cursor().execute(
        "SELECT EPITOPE_ID FROM RAW.GLYCOEPITOPE.EPITOPES ORDER BY EPITOPE_ID").fetchall()]
    print(f"scraping enzyme tab for {len(ids)} epitopes...", file=sys.stderr)

    rows = []
    for i, epid in enumerate(ids, 1):
        try:
            r = requests.get(ENZYME_URL.format(epid), headers=UA, timeout=30)
            if r.status_code == 200:
                rows.extend(parse_enzyme(epid, r.text))
            else:
                print(f"  [{epid}] HTTP {r.status_code}", file=sys.stderr)
        except Exception as e:
            print(f"  [{epid}] ERR {e}", file=sys.stderr)
        if i % 20 == 0:
            print(f"  ...{i}/{len(ids)}", file=sys.stderr)
        time.sleep(0.6)

    df = pd.DataFrame(rows)
    df["SOURCE"] = "glycoepitope.jp/epitopes/{id}/enzyme"
    df["LOADED_AT"] = pd.Timestamp.utcnow().tz_localize(None)
    ok, _, nrows, _ = write_pandas(con, df, "EPITOPE_ENZYME",
                                   auto_create_table=True, overwrite=True,
                                   quote_identifiers=False)
    print(f"loaded RAW.GLYCOEPITOPE.EPITOPE_ENZYME ok={ok} rows={nrows} "
          f"epitopes={df['EPITOPE_ID'].nunique()} genes={df['GENE_SYMBOL'].nunique()}")
    con.close()


if __name__ == "__main__":
    main()
