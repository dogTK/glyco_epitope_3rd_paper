# 計画: CREEDS疾患シグネチャを Snowflake に用意する

目的: Fig.3a再現の疾患シグネチャ `y_trans`（Snowflakeに未整備）を `RAW.CREEDS` として取り込む。

関連: `docs/repro_regulome_fig3.md`, `notebooks/validation/01_repro_fig3a.ipynb`

---

## 0. データ実体（確認済み 2026-07-14）

- 取得元: `https://maayanlab.cloud/CREEDS/download/disease_signatures-v1.0.json`（16.8 MB, JSON配列, last-modified 2021-02-22）
- 件数: **828 シグネチャ**。うち `do_id` あり **695**（論文の「695 profiles」と一致）
- organism: human 555 / mouse 215 / rat 58
- 1シグネチャのフィールド:

| フィールド | 例 | 備考 |
|-----------|-----|------|
| `id` | `dz:328` | シグネチャ主キー |
| `do_id` | `DOID:11723` | Disease Ontology。疾患名寄せの鍵 |
| `umls_cui` | `C0013264` | UMLS。名寄せ補助 |
| `disease_name` | `Duchenne muscular dystrophy` | |
| `geo_id` / `platform` | `GSE466` / `GPL81` | 出所 |
| `cell_type` / `organism` | ... / `human` | |
| `ctrl_ids` / `pert_ids` | `[GSM...]` | サンプルGSM配列 |
| `up_genes` / `down_genes` | `[[gene, value], ...]` | Characteristic Direction スコア。**value符号=方向、絶対値=重み** |
| `curator` / `version` | | |

> 注意: mouse/rat は遺伝子シンボルがマウス表記（例 `Actc1`）。ヒトL1000と突合するなら **organism='human' を主対象**にし、mouse/ratは使うならオルソログ変換が別途必要。まずは human 555 で進める。

---

## 1. 設計判断（要確認）

1. **スキーマ**: `RAW.CREEDS` を新設（`RAW.LINCS` 等と並列）。CREEDSは独立ソースなので分離。
2. **対象**: まず全828行をraw取り込み → 解析ビューで `organism='human' AND do_id IS NOT NULL`（≈ヒト＋DOID付き）に絞る。生データは捨てない。
3. **テーブル構成（3層）**:
   - `RAW_DISEASE_SIGNATURES_JSON (V VARIANT)` … 生JSON着地（1行=1シグネチャ）
   - `DISEASE_SIGNATURES_META` … 1行=1シグネチャのメタ（id, do_id, disease_name, organism, geo_id, n_up, n_down 等）
   - `DISEASE_SIGNATURE_GENES` … ロング形式（signature_id, gene, value, direction）。解析はこれを使う
4. 疾患レベル集約（同一疾患の複数シグネチャ平均）は**解析側（ノートブック）で実施**し、DBはシグネチャ粒度で保持。

---

## 2. 手順

### Step 1. ダウンロード（済/再取得可）
```bash
curl -s "https://maayanlab.cloud/CREEDS/download/disease_signatures-v1.0.json" \
  -o <scratchpad>/creeds_disease.json   # 16.8 MB
```
※ `data/raw/` には置かない（プロジェクト規約）。scratchpad → Snowflake stage へ。

### Step 2. スキーマ・ステージ・ファイル形式
```sql
CREATE SCHEMA IF NOT EXISTS RAW.CREEDS;
CREATE FILE FORMAT IF NOT EXISTS RAW.CREEDS.FF_JSON_ARRAY
  TYPE = JSON STRIP_OUTER_ARRAY = TRUE;
CREATE STAGE IF NOT EXISTS RAW.CREEDS.CREEDS_STAGE
  FILE_FORMAT = RAW.CREEDS.FF_JSON_ARRAY;
```

### Step 3. アップロード（PUT）と着地
```bash
snow stage copy <scratchpad>/creeds_disease.json @RAW.CREEDS.CREEDS_STAGE -c admin
```
```sql
CREATE OR REPLACE TABLE RAW.CREEDS.RAW_DISEASE_SIGNATURES_JSON (V VARIANT);
COPY INTO RAW.CREEDS.RAW_DISEASE_SIGNATURES_JSON
  FROM @RAW.CREEDS.CREEDS_STAGE/creeds_disease.json.gz  -- PUTで自動gzip
  FILE_FORMAT = (FORMAT_NAME = RAW.CREEDS.FF_JSON_ARRAY);
-- 期待: 828 行
```

### Step 4. メタテーブル
```sql
CREATE OR REPLACE TABLE RAW.CREEDS.DISEASE_SIGNATURES_META AS
SELECT
  V:id::string           AS signature_id,
  V:do_id::string        AS do_id,
  V:umls_cui::string     AS umls_cui,
  V:disease_name::string AS disease_name,
  V:geo_id::string       AS geo_id,
  V:platform::string     AS platform,
  V:cell_type::string    AS cell_type,
  V:organism::string     AS organism,
  V:curator::string      AS curator,
  V:version::string      AS version,
  ARRAY_SIZE(V:ctrl_ids) AS n_ctrl,
  ARRAY_SIZE(V:pert_ids) AS n_pert,
  ARRAY_SIZE(V:up_genes) AS n_up,
  ARRAY_SIZE(V:down_genes) AS n_down
FROM RAW.CREEDS.RAW_DISEASE_SIGNATURES_JSON;
```

### Step 5. 遺伝子ロングテーブル
```sql
CREATE OR REPLACE TABLE RAW.CREEDS.DISEASE_SIGNATURE_GENES AS
SELECT V:id::string AS signature_id,
       g.value[0]::string AS gene,
       g.value[1]::float  AS value,
       'up'  AS direction
FROM RAW.CREEDS.RAW_DISEASE_SIGNATURES_JSON,
     LATERAL FLATTEN(input => V:up_genes) g
UNION ALL
SELECT V:id::string, g.value[0]::string, g.value[1]::float, 'down'
FROM RAW.CREEDS.RAW_DISEASE_SIGNATURES_JSON,
     LATERAL FLATTEN(input => V:down_genes) g;
```

### Step 6. 検証
```sql
SELECT COUNT(*) FROM RAW.CREEDS.RAW_DISEASE_SIGNATURES_JSON;            -- 828
SELECT organism, COUNT(*) FROM RAW.CREEDS.DISEASE_SIGNATURES_META
  GROUP BY 1;                                                          -- human 555 / mouse 215 / rat 58
SELECT COUNT(*) FROM RAW.CREEDS.DISEASE_SIGNATURES_META WHERE do_id IS NOT NULL; -- 695
SELECT direction, COUNT(*) FROM RAW.CREEDS.DISEASE_SIGNATURE_GENES GROUP BY 1;
-- 1シグネチャの中身がJSONと一致するかスポット確認
```

### Step 7.（任意）解析用ビュー
```sql
CREATE OR REPLACE VIEW RAW.CREEDS.VW_HUMAN_DISEASE_GENES AS
SELECT g.*
FROM RAW.CREEDS.DISEASE_SIGNATURE_GENES g
JOIN RAW.CREEDS.DISEASE_SIGNATURES_META m USING (signature_id)
WHERE m.organism = 'human' AND m.do_id IS NOT NULL;
```

---

## 3. 完了条件（Definition of Done）— 実行済み 2026-07-14

- [x] `RAW.CREEDS` に raw/meta/genes の3テーブル＋`VW_HUMAN_DISEASE_GENES`ビューが存在
- [x] 行数チェック: raw=828, human=555 / mouse=215 / rat=58, do_id付き=695, distinct do_id=235（ヒト178）
- [x] `DISEASE_SIGNATURE_GENES` が (signature_id, gene, value, direction) で引ける（全490,686行 / ヒット293,034行）
- [x] スポット1件一致: `dz:328`（Duchenne muscular dystrophy）up=202/down=396 がJSON原本と一致
- [x] `notebooks/validation/01_repro_fig3a.ipynb` Step2 を Snowflake `RAW.CREEDS` 参照に差し替え

### 作成物

| オブジェクト | 種別 | 行数 |
|-------------|------|------|
| `RAW.CREEDS.RAW_DISEASE_SIGNATURES_JSON` | TABLE (VARIANT) | 828 |
| `RAW.CREEDS.DISEASE_SIGNATURES_META` | TABLE | 828 |
| `RAW.CREEDS.DISEASE_SIGNATURE_GENES` | TABLE | 490,686 |
| `RAW.CREEDS.VW_HUMAN_DISEASE_GENES` | VIEW | 293,034 |
| `RAW.CREEDS.CREEDS_STAGE` / `FF_JSON_ARRAY` | STAGE / FILE FORMAT | — |

---

## 4. 留意点

- **名寄せ**: 疾患軸で `COMPOUND_TO_INDICATION`（MeSH/EFO）と CREEDS（DOID/UMLS）を突合する必要。DOID↔MeSH↔EFO のクロスウォークが後続の要作業（別タスク）。
- **organism**: 初期はhumanのみ。mouse/rat活用時はオルソログ変換（例: HGNCオルソログ表）を別途用意。
- **遺伝子シンボル**: CREEDSは旧シンボルを含みうる。L1000ランドマークと突合時に欠損が出たらHGNCエイリアス正規化を検討。
- 生JSONは保持するので、後で `pert_ids`/`ctrl_ids` を使う拡張（GEO再解析）にも対応可能。
