# glyco-epitope 辞書（Snowflake `RAW.GLYCOEPITOPE`）

3rd paper Fig2「glyco-targetability dictionary（epitope × 生合成遺伝子 × 認識分子）」の基盤データ。
出所: GlycoEpitope DB (https://www.glycoepitope.jp)。

## 背景（2026-07-15 時点の状況）

- エピトープ一覧（**173件**、EP番号・糖鎖配列・構造フラグ）は `RAW.GLYCOEPITOPE.EPITOPES` に配置。
  - もとは `RAW.LINCS.GLYCOEPITOPE_EPITOPES` にあったが、glyco-epitope辞書の一部なので 2026-07-22 に `RAW.GLYCOEPITOPE` へ clone して移設（旧LINCS側の同名テーブルは互換のため当面残置）。
- 旧 epitope→遺伝子軸マッピング（`VW_GLYCOEPITOPE_AXIS_GENES` 等）は、消失した `BIOINFORMATICS` DB を参照して**壊れている**。
- そこで **Enzyme 軸を再取得**し、新スキーマ `RAW.GLYCOEPITOPE` に整備した。

## 作成物（`RAW.GLYCOEPITOPE`）

| オブジェクト | 種別 | 内容 |
|-------------|------|------|
| `EPITOPES` | TABLE | エピトープ一覧173件（EP番号・EPITOPE_NAME・糖鎖配列・HAS_FUCOSE等の構造フラグ）。`RAW.LINCS.GLYCOEPITOPE_EPITOPES` からclone移設 |
| `EPITOPE_ENZYME` | TABLE | epitope→酵素。56エピトープ/56行（biosynthetic 55, degradation 1）、遺伝子名41種。列: EPITOPE_ID, ENZYME_ROLE, GENE_SYMBOL(生名), EC, CAZY, REACTION, DESCRIPTION |
| `ENZYME_HGNC_CROSSWALK` | TABLE | 酵素生名→HGNC。41行。列: GENE_SYMBOL_RAW, HGNC_SYMBOL, MAPPING_METHOD, CONFIDENCE |
| `VW_EPITOPE_GLYCOGENE` | VIEW | 上3つをjoin。epitope→HGNC glycogene。列: EPITOPE_ID, **EPITOPE_NAME**, ENZYME_ROLE, GENE_SYMBOL_RAW, HGNC_SYMBOL, MAPPING_METHOD, CONFIDENCE, EC, CAZY |

スクレイパー: `scripts/glycoepitope_scrape_enzyme.py`（enzymeタブ、レート制限付き）
HGNC対応表: `scripts/glycoepitope_hgnc_crosswalk.py`（下記マップ）

## HGNC正規化の結果

- glycoepitope.jpの酵素名はHGNC正式シンボルでない（例 `ST6Gal I`, `C4ST-1 (CHST11)`）。名前＋**EC番号**を根拠に対応付け。
- 41名 → **32がHGNC割当**（curated_alias 29 / paren_extract 2 / paren_alias 1）、review 7、nonhuman 2。
- **マップした30 HGNCは全てLINCS glycogene(`GLYCO_GENES_WIDE`)に存在** → epitope→glycogene→LINCS発現が連結可能。
- **47エピトープ**が1つ以上のHGNC-mapped酵素を持つ。

### 要確認（review, HGNC未割当・推測で埋めていない）

以下7件はEC/名前だけでは一意に決められず、専門家判断が必要（`MAPPING_METHOD='review'`）:

| 生名 | EC | 候補・メモ |
|------|-----|-----------|
| `AT-1` | 2.3.1.- | O-アセチル化 acetyltransferase。CASD1 / SLC33A1 等で曖昧 |
| `Beta3Gal-T3` | 2.4.1.79 | ECはgloboside(B3GALNT1)を指し名前(GalT3)と不一致 |
| `Gal-6-sulfotransferase` | (なし) | CHST1 / CHST3 で曖昧 |
| `GalT` | (なし) | 総称、一意化不可 |
| `LA2 synthase` | 2.4.1.206 | 不明瞭 |
| `Sialyltransferase 3` | 2.4.99.10 | ST6GALNAC系？ 不明瞭 |
| `polypeptide alpha-GalNAc-T` | (GT27) | GALNTファミリー総称（多遺伝子） |

### 除外（非ヒト, nonhuman）

- `PMT-1`（酵母, EP0003 O-Mannosyl/Yeast）
- `Heparitinase(Flavobacterium heparinum)`（細菌）

## 未対応（今後）

- **Antibody / Lectin / Diseases 軸**: 同じ要領で `/epitopes/{ID}/antibody`, `/lectin`, `/diseases` から取得予定（Fig2の 認識分子軸＝レクチン/抗体等）。
- review 7件の確定。
- 117エピトープはglycoepitope.jp上でenzyme記載なし（サイト側の欠損）。
