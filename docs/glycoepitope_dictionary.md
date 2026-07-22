# glyco-epitope 辞書（Snowflake `RAW.GLYCOEPITOPE`）

3rd paper Fig2「glyco-targetability dictionary（epitope × 生合成遺伝子 × 認識分子）」の基盤データ。
出所: GlycoEpitope DB (https://www.glycoepitope.jp)。

## 背景（2026-07-15 時点の状況）

- エピトープ一覧（**173件**、EP番号・糖鎖配列・構造フラグ）は `RAW.GLYCOEPITOPE.EPITOPES` に配置。
  - もとは `RAW.LINCS.GLYCOEPITOPE_EPITOPES` にあったが、glyco-epitope辞書の一部なので 2026-07-22 に `RAW.GLYCOEPITOPE.EPITOPES` へ clone 移設し、**旧LINCS側の同名テーブルはDROP済み**。
- 旧 epitope→遺伝子軸マッピング（`VW_GLYCOEPITOPE_AXIS_GENES` 等）は、消失した `BIOINFORMATICS` DB を参照して**壊れている**。
- そこで **Enzyme 軸を再取得**し、新スキーマ `RAW.GLYCOEPITOPE` に整備した。

## 作成物（`RAW.GLYCOEPITOPE`）

| オブジェクト | 種別 | 内容 |
|-------------|------|------|
| `EPITOPES` | TABLE | エピトープ一覧173件（EP番号・EPITOPE_NAME・糖鎖配列・HAS_FUCOSE等の構造フラグ）。`RAW.LINCS.GLYCOEPITOPE_EPITOPES` からclone移設 |
| `EPITOPE_ENZYME` | TABLE | epitope→酵素。56エピトープ/**113行**、酵素名**69種**。1エピトープに合成経路の全酵素（例 Sialyl Lewis x = 7酵素）が入る。列: EPITOPE_ID, ENZYME_ROLE, GENE_SYMBOL(生名), EC, CAZY, REACTION, DESCRIPTION |
| `ENZYME_HGNC_CROSSWALK` | TABLE | 酵素生名→HGNC。69行。列: GENE_SYMBOL_RAW, HGNC_SYMBOL, MAPPING_METHOD, CONFIDENCE |
| `VW_EPITOPE_GLYCOGENE` | VIEW | 上3つをjoin。epitope→HGNC glycogene。列: EPITOPE_ID, **EPITOPE_NAME**, ENZYME_ROLE, GENE_SYMBOL_RAW, HGNC_SYMBOL, MAPPING_METHOD, CONFIDENCE, EC, CAZY |

スクレイパー: `scripts/glycoepitope_scrape_enzyme.py`（enzymeタブ、レート制限付き）
HGNC対応表: `scripts/glycoepitope_hgnc_crosswalk.py`（下記マップ）

## HGNC正規化の結果

- glycoepitope.jpの酵素名はHGNC正式シンボルでない（例 `ST6Gal I`, `C4ST-1 (CHST11)`）。名前＋**EC番号**を根拠に対応付け。
- 69名 → **56がHGNC割当**（curated_alias 52 / paren_extract 3 / paren_alias 1）、review 11、nonhuman 2。
- **マップした HGNC 54遺伝子中53がLINCS glycogene(`GLYCO_GENES_WIDE`)に存在** → epitope→glycogene→LINCS発現が連結可能。
- **49エピトープ**が1つ以上のHGNC-mapped酵素を持つ。

### 要確認（review, HGNC未割当・推測で埋めていない）

以下11件はEC/名前だけでは一意に決められず、専門家判断が必要（`MAPPING_METHOD='review'`）:

| 生名 | EC | 候補・メモ |
|------|-----|-----------|
| `AT-1` | 2.3.1.- | O-アセチル化 acetyltransferase。CASD1 / SLC33A1 等で曖昧 |
| `Beta3Gal-T3` | 2.4.1.79 | ECはgloboside(B3GALNT1)を指し名前(GalT3)と不一致 |
| `Beta3GlcNAcT` | 2.4.1.222 | Fringe(LFNG/MFNG/RFNG)の3候補で一意化不可 |
| `Beta4GalT` | 2.4.1.38/90 | 総称（B4GALT1系だが番号なし） |
| `ChSy-2(CSS3)` | 2.4.1.226 | 名称(ChSy-2)と括弧(CSS3)が不整合、CHPF/CHSY3で曖昧 |
| `Gal-6-sulfotransferase` | (なし) | CHST1 / CHST3 で曖昧 |
| `GalT` | (なし) | 総称、一意化不可 |
| `LA2 synthase` | 2.4.1.206 | B3GNT5?（Lc3合成）だが名称不明瞭 |
| `ST3Gal` | 2.4.99.- | 総称（ローマ数字なし） |
| `Sialyltransferase 3` | 2.4.99.10 | ST6GALNAC系？ 不明瞭 |
| `polypeptide alpha-GalNAc-T` | (GT27) | GALNTファミリー総称（多遺伝子） |

### 除外（非ヒト, nonhuman）

- `PMT-1`（酵母, EP0003 O-Mannosyl/Yeast）
- `Heparitinase(Flavobacterium heparinum)`（細菌）

## カバレッジと限界（epitope potential 設計時の注意）

ファネル: 173エピトープ → 56(glycoepitope.jpに酵素記載) → 49(HGNC割当あり) → 54 distinct HGNC遺伝子。

- `VW_EPITOPE_GLYCOGENE` は **113行 / 56 distinct epitope**、つまり **1エピトープに複数酵素（合成経路の全酵素）** が入る。
  例: Sialyl Lewis x = FUT3/4/5/6/7 + ST3GAL3/4 の7酵素、HNK-1 = B3GAT1/B3GAT2/CHST10 の3酵素。
  （2026-07-22 にスクレイパーのバグ修正で改善。旧版は1テーブル=1辞書に潰し最後の酵素しか残さず 56行/1エピトープ1酵素だった。）
- `ENZYME_ROLE` で biosynthetic / degradation を区別可能。potential計算では合成のみ使うか分解を差し引くか要検討。

## 未対応（今後）

- **Antibody / Lectin / Diseases 軸**: 同じ要領で `/epitopes/{ID}/antibody`, `/lectin`, `/diseases` から取得予定（Fig2の 認識分子軸＝レクチン/抗体等）。
- review 11件の確定（→ 連結エピトープ増）。
- 117エピトープはglycoepitope.jp上でenzyme記載なし（サイト側の欠損）。KEGG/GlyGen/CAZy等で酵素補完したい。
