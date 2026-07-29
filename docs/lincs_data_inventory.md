# LINCS データ棚卸しと山西研手法の再現準備（2026-07-29）

「山西研（Iwata 2017 / Namba 2022）の手法を再現するために LINCS のデータを用意する」ための、
Snowflake 上の資産の棚卸しと、今回追加した注釈テーブルの記録。

---

## 1. 結論：行列データは全部そろっていた。欠けていたのは「注釈」

`RAW.LINCS` には GSE92742（LINCS Phase 1）の Level 5 が**全量**入っていた。
足りなかったのは遺伝子の測定区分（landmark / BING / inferred）とシグネチャの品質指標で、
これは gctx 本体ではなく GEO の別ファイルにある小さな txt。今回それを取得して載せた。

---

## 2. もともとあったもの

### 発現行列

| テーブル | 中身 | 備考 |
|---|---|---|
| `L1000_EXPRESSION_LONG` | **12,328遺伝子 × 473,647シグネチャ**（58.4億行, long） | GSE92742 Level 5 全量。Iwata 2017 の遺伝子空間そのもの |
| `L1000_LEVEL5_LANDMARK` | 同473,647シグネチャの wide版, 遺伝子列 **959** | landmark 978 のうち **19欠**（列名衝突と思われる）。高速アクセス用 |
| `GLYCO_GENES_WIDE` / `_GSE92742` | 薬剤 × glycogene 385 | 値はVARCHAR、メタ列は小文字クォート識別子 |
| `DCIC_EXPRESSION_LONG` | 23,614遺伝子 × 718,055（推論RNA-seq, 169.6億行） | LINCS DCIC 2021 |
| `CTL_PREDICTED_RNASEQ_LONG` / `CTL_GLYCO_GENES_WIDE` | 対照 188,708サンプル | 射影順序の修正（処理後レベル→射影→差）に使う絶対量 |

### 摂動タイプの内訳（`L1000_LEVEL5_LANDMARK`）

```
trt_cp       205,034 sig   20,413 pert × 71 cell   ← Iwata 2017
trt_sh       154,993 sig   18,493 pert × 20 cell
trt_sh.cgs    36,720 sig    4,345 pert × 17 cell   ← Namba 2022（論文の4,345と完全一致）
trt_sh.css    24,368 sig    3,807 pert × 16 cell
trt_oe        22,205 sig    3,461 pert × 10 cell   ← Namba 2022
ctl_vehicle   14,423 / trt_lig 8,256 / ctl_vector 6,826 / ctl_untrt 588
```

`trt_sh.cgs` / `trt_oe` の `PERTNAME` は遺伝子シンボル（UGT1A1, CASD1…）なので、
糖鎖酵素の KD/OE 署名はそのまま引ける。

### ステージ（生ファイル）

`@RAW.LINCS.LINCS_S3_STAGE` に元の gctx がある。
ただし**行列は既に上のテーブルに展開済み**なので、再取得の必要はない。

```
GSE92742_Broad_LINCS_Level5_COMPZ.MODZ_n473647x12328.gctx.gz    21.3 GB
GSE70138_Broad_LINCS_Level3_INF_mlr12k_n113012x22268.gct.gz     11.9 GB   ← Phase 2、未ロード
cp_predicted_RNAseq_profiles.gctx                              171.5 GB
ctl_predicted_RNAseq_profiles.gctx                              17.9 GB
LINCS_DCIC_2021_ChemicalPert_PredictedRNAseq_ChDir_Sigs.gctx    68.3 GB
```

---

## 3. 今回追加したもの

GEO `GSE92nnn/GSE92742/suppl/` から取得（合計 24 MB）。
`@RAW.LINCS.METADATA_STAGE` にステージし、`RAW.LINCS.TSV_GZ` ファイルフォーマットでロード。

| テーブル / ビュー | 行数 | 中身 |
|---|---|---|
| `GENE_INFO` | 12,328 | `PR_GENE_ID`(Entrez), `PR_GENE_SYMBOL`, **`PR_IS_LM`**, **`PR_IS_BING`** |
| `SIG_INFO` | 473,647 | `SIG_ID`, pert/cell/dose/time, `DISTIL_ID` |
| `SIG_METRICS` | 473,647 | **`DISTIL_CC_Q75`, `TAS`, `PCT_SELF_RANK_Q25`, `IS_EXEMPLAR`, `DISTIL_NSAMPLE`** |
| `KEGG_PATHWAY_GENE` | 39,573 | KEGG REST（`/list/pathway/hsa`, `/link/hsa/pathway`）372経路 |
| `VW_GENE_SPACE` | 12,328 | 上記に `GENE_CLASS` = landmark / best_inferred / inferred を付与 |
| `VW_SIG_QC` | 473,647 | `SIG_INFO` ⨝ `SIG_METRICS`、`-666`→NULL、`IS_GOLD` フラグ付き |
| `VW_KEGG_PATHWAY_L1000` | 32,411 | KEGG × L1000 遺伝子空間（Entrez ID で結合） |

### 結合の健全性（検証済み）

- `SIG_INFO.SIG_ID` ⨝ `L1000_LEVEL5_LANDMARK.SAMPLE_ID` = **473,647 / 473,647（欠損ゼロ）**
- `GENE_INFO.PR_GENE_SYMBOL` ⨝ `L1000_EXPRESSION_LONG.GENE_SYMBOL` = **12,328 / 12,328（欠損ゼロ）**
- `GENE_INFO`: landmark **978**、BING **10,174** ＝ Broad の公称値と一致

### ロード時のハマりどころ

- `sig_info.PERT_DOSE` / `PERT_TIME` は `-666.0|-666.000000` のような**パイプ結合文字列**が入る
  （複数用量を統合したシグネチャ）。**VARCHAR でロードし、ビュー側で `try_to_double`** すること。
- `sig_metrics` の欠損値は `-666.0`。`VW_SIG_QC` で NULL 化済み。

---

## 4. 追加でわかった重要な事実

### 4.1 gold signature（`DISTIL_CC_Q75 >= 0.2 AND PCT_SELF_RANK_Q25 <= 5`）

| pert_type | 全 sig | gold | gold率 | TAS中央値 |
|---|---|---|---|---|
| trt_cp | 205,034 | 72,172 | 35.2% | 0.147 |
| trt_sh.cgs | 36,720 | **0** | 0.0% | **0.322** |
| trt_oe | 22,205 | 6,787 | 30.6% | 0.163 |
| trt_lig | 8,256 | 2,208 | 26.7% | 0.134 |

**`trt_sh.cgs` の gold が 0 本なのは品質が悪いからではない。**
CGS は複数shRNAを統合済みで `distil_cc_q75` / `pct_self_rank_q25` が定義されず `-666` になるため。
実際 **TAS 中央値は全摂動型で最良（0.322）**。CGS を絞るときは gold でなく **TAS** を使う。

### 4.2 エピトープ辞書57遺伝子の測定区分

| 区分 | n | 遺伝子 |
|---|---|---|
| **best_inferred (BING)** | **37** | A4GALT, B3GALT4, B3GAT1, B4GALNT1, B4GALT1/2/3/4/6, C1GALT1, CHST10/11/2/3/7, CHSY1, EXT2, FUT2/3/6/8/9, GAL3ST1, MGAT3, NDST1, OGT, POFUT1/2, POMGNT1, POMT1/2, ST3GAL1/4, ST6GAL1, ST8SIA1/4/5 |
| not_in_L1000 | 11 | B3GAT2, B3GLCT, CHSY3, FUT4, FUT5, GAL3ST2, GAL3ST3, GBGT1, ST3GAL3, **ST6GALNAC1**, ST6GALNAC6 |
| inferred（plain） | 6 | B3GALT5, CHST4, FUT7, **MGAT5**, ST6GALNAC5, ST8SIA2 |
| landmark | 3 | EXT1, FUT1, ST3GAL5 |

**これは `docs/negative_result_cross_cell_transfer.md` の前提を精緻化する。**
あの検証は非landmarkを一律「推論」として扱っていたが、実際は**37遺伝子がBING**＝
Broad が「信頼して推論できる」と認定した 10,174 遺伝子の側にいる。
交差細胞の否定的結果そのもの（推論モデルが細胞株ごとに学習されている、という原理的な話）は
BING かどうかで覆らないが、**null 対照のプールは BING に揃えて引き直すべき**だった
（従来は `GLYCO_GENES_WIDE` から無差別に引いていた）。

一方で、物語の中心にある **MGAT5 は plain inferred、ST6GALNAC1（STn）は L1000 に無い**。
この2つを主役に据えた主張は L1000 単独では支えられない。

### 4.3 KEGG 糖鎖経路の L1000 カバレッジ

| pathway | L1000遺伝子 | うち landmark | うち BING |
|---|---|---|---|
| hsa00510 N-Glycan biosynthesis | 41 | 1 | 38 |
| hsa00513 Various types of N-glycan | 29 | 1 | 28 |
| hsa00514 Other types of O-glycan | 29 | 2 | 26 |
| hsa00563 GPI-anchor biosynthesis | 24 | 1 | 23 |
| hsa00601 GSL lacto/neolacto | 23 | 1 | 17 |
| hsa00512 Mucin type O-glycan | 21 | 1 | 18 |
| hsa00534 GAG heparan sulfate | 20 | 2 | 15 |
| hsa00532 GAG chondroitin/dermatan | 16 | 0 | 16 |
| hsa00515 Mannose type O-glycan | 14 | 2 | 12 |
| hsa00603 GSL globo/isoglobo | 14 | 1 | 11 |
| hsa00604 GSL ganglio | 13 | 1 | 11 |
| hsa00511 Other glycan degradation | 13 | 1 | 11 |
| hsa00533 GAG keratan sulfate | 11 | 0 | 10 |

集合ベースの超幾何検定に必要な規模（10〜41遺伝子）は各経路で確保できている。

---

## 5. まだ無いもの

- **GSE70138（Phase 2）の Level 5** — ステージには Level 3 の gct.gz のみ。Phase 2 の
  `sig_info` / Level 5 を足せば化合物数と細胞株数が増える。現状は Phase 1 のみで再現可能。
- **派生テーブル：各シグネチャの上位5% / 下位5% 遺伝子セット**
  （12,328 の 5% ＝ 616遺伝子ずつ。Iwata 2017 の超幾何検定の入力）。未作成。
- **KEGG 163経路への絞り込み基準** — 今回取得したのは hsa 全 372経路（L1000遺伝子を含むのは371、
  10遺伝子以上は355）。Iwata 2017 の「163経路」は KEGG のリリース年か経路カテゴリの
  絞り込みによると思われ、**基準は論文本文で要確認**（PDF未取得）。

---

## 6. 再現ルート別の残作業

### Iwata 2017（trt_cp × 細胞特異的 MoA、集合ベース）
1. 上位5%/下位5%遺伝子セットのテーブル化（`VW_GENE_SPACE` で landmark / BING に絞る版も）
2. `VW_KEGG_PATHWAY_L1000` に対する超幾何検定＋FDR
3. **同一細胞株マッチング**で薬剤類似度（交差細胞はやらない＝2017年の教訓）

### Namba 2022（trt_sh.cgs / trt_oe × 疾患署名、target repositioning）
1. データはほぼ揃い済み（CGS 4,345 は論文と一致、疾患側は `RAW.CREEDS` 828疾患）
2. CGS の絞り込みは gold でなく **TAS** で（§4.1）
3. inverse signature 法 → trans-disease 法

---

関連: `docs/negative_result_cross_cell_transfer.md`（§4.2 で前提を更新）、
`docs/yamanishi_collaboration.md`、`inputs/papers/README.md`、`docs/HANDOFF.md`
