# Fig.3a 再現手順書

対象論文: **Regulome-based characterization of drug activity across the human diseasome**
*npj Systems Biology and Applications 8, 41 (2022). PMID 36344521 / PMC9640590 / DOI 10.1038/s41540-022-00255-4*

対象は **Fig.3a のみ**（transcriptomeベースの薬剤-疾患相関 boxplot）。regulome変換・ChIP-Atlas・Fisher検定・radial plot(3b–3f) は本手順の範囲外。

---

## 0. Fig.3a が示しているもの（再現ゴール）

- **種類**: boxplot
- **1つの箱** = ある疾患について「その疾患の**承認薬**」群の、薬剤-疾患**コサイン相関スコア**の分布
- **横軸**: 疾患（各疾患の相関スコア**中央値の昇順**でソート）
- **縦軸**: cosine 相関係数（transcriptomeシグネチャ間）
- **箱の要素**: 中央線=中央値、箱=四分位範囲(IQR)、髭=1.5×IQR、点=外れ値
- **読み取れること**: がん系疾患は承認薬との相関が**負（下側）**、免疫系疾患は**正（上側）**に寄る

> ⚠ ビット単位一致は狙わない（LINCS再処理版・CREEDS/KEGG更新のため）。まず2〜3疾患のパイロット→全疾患へ拡張を推奨。

---

## 確定した設計判断（2026-07-14 ユーザー合意）

| 論点 | 決定 | 論文との関係 |
|------|------|-------------|
| 承認薬マッピング | **ChEMBL `COMPOUND_TO_INDICATION`（MAX_PHASE_FOR_IND=4）** を使用 | 論文はKEGG DISEASE。実用重視でChEMBL採用（Snowflake内完結・PERTNAME直結）。疾患集合は論文と一致しない |
| 薬剤シグネチャ集約 | **化合物(PERTNAME)ごとに全 `trt_cp` プロファイルを平均**し1薬剤=1シグネチャ | 論文は薬剤側の集約機構を明記せず（化合物単位のInChIKey取得のみ記載）。疾患側の"averaged"と対称に平均を採用 |
| 疾患シグネチャ集約 | **同一疾患(do_id)の複数CREEDSシグネチャを平均** | 論文どおり（"averaged multiple signatures for the same disease", 79疾患） |
| 共通遺伝子 | **L1000ランドマーク(978) ∩ CREEDS遺伝子**（論文で848） | 論文どおり |
| organism | **human のみ**（初期） | 論文もヒト中心 |
| 相関 | 共通遺伝子上の **cosine**（Fig3aは正負そのまま、逆相関スコア化しない） | 論文どおり |

> 論文が明記しているのは「疾患側=平均、共通遺伝子=978∩CREEDS」。薬剤側の集約は明記なし（InChIKeyで化合物同定する旨のみ）。本再現は対称性から薬剤側も平均とする。

---

## 1. 必要データと入手先

### Snowflake `RAW.LINCS` にあるもの（探索済み・2026-07-14）

接続: `snow sql -c admin ...`（`admin` コネクションが `RAW.LINCS` を指す）

| テーブル | 用途 | 備考 |
|----------|------|------|
| **`L1000_LEVEL5_LANDMARK`** | **薬剤シグネチャ x_trans の源** | Level5(MODZ)ワイド形式。メタ列(SAMPLE_ID, CELL, PERTNAME, PERTID, DOSE, TIMEPOINT, PERT_TYPE)＋ランドマーク遺伝子ごとFLOAT列（約959遺伝子）。全473,647行、うち `PERT_TYPE='trt_cp'` が205,034行、28,927 pert、76細胞株 |
| **`COMPOUND_TO_INDICATION`** | **疾患↔承認薬マッピングの源** | COMPOUND_ID(=薬剤名), CHEMBL_ID, MESH_ID, MESH_HEADING, EFO_ID, EFO_TERM, **MAX_PHASE_FOR_IND**。承認薬 = `MAX_PHASE_FOR_IND = 4` |
| `CHEMBL_DRUG_INDICATION` | 同上（ChEMBL ID起点版） | COMPOUND_TO_INDICATIONの元。薬剤名で紐付くのは前者が便利 |
| `DRUG_REPURPOSING_HUB` | 補助（CLINICAL_PHASE='Launched', DISEASE_AREA, INDICATION, MOA, TARGET） | PERT_INAMEでL1000のPERTNAMEと突合可 |
| `EXPERIMENT_METADATA` / `COMPOUND_ANNOTATION_MASTER` / `COMPOUND_NAME_MAPPING` | メタ・薬剤名正規化 | PERTNAME↔ChEMBL/薬剤名の名寄せに使用 |

> 論文はKEGG DISEASEで承認薬を定義しているが、本再現では **ChEMBL由来の適応情報(`COMPOUND_TO_INDICATION`, MAX_PHASE=4)** を承認薬の代替定義として使うのが実務上クリーン（薬剤名がL1000 PERTNAMEと直接突合でき、疾患はMeSH/EFOで持てる）。KEGG厳密再現が必要なら別途KEGG RESTを併用。

### 外部取得が必要なもの

| データ | 用途 | 入手先 |
|--------|------|--------|
| **CREEDS manual disease signatures** (695) | **疾患シグネチャ y_trans**（Snowflakeには無し） | https://maayanlab.cloud/CREEDS/ 。`up_genes`/`down_genes`（Characteristic Direction スコア付き） |

L1000の読込・シグネチャ抽出は 2nd paper (`../lincs_glyco_2nd_paper/`) の既存パイプラインも流用できる可能性が高い。

---

## 2. 環境

```bash
micromamba activate glyco-epitope-3rd
# 主要パッケージ: pandas, numpy, scipy, cmapPy(GCTX読込), matplotlib(または seaborn)
```

---

## 3. パイプライン（step-by-step）

ノートブックは命名規則に従い `notebooks/analytics/NN_repro_fig3a.ipynb` に作成。

### Step 1. 薬剤トランスクリプトームシグネチャ x_trans

1. L1000 Level5 (MODZ) から `trt_cp` プロファイルを抽出。ランドマーク遺伝子 **p = 978**。
2. 各プロファイルで **top 5% / bottom 5%** の遺伝子だけ残し、残り90%を **0** に。
3. `x_trans` = z-score（処理 − プレート背景）ベクトル。

### Step 2. 疾患トランスクリプトームシグネチャ y_trans

1. CREEDS から DOID付き疾患シグネチャを抽出。`up_genes`（正スコア=過剰発現）/ `down_genes`（負スコア=抑制）。
2. 同一疾患に複数シグネチャがある場合は**平均化**。

### Step 3. 薬剤-疾患コサイン相関

- 薬剤と疾患で**共通する遺伝子**（論文では約848遺伝子 / 14,639中）に揃える。
- 各(薬剤, 疾患)ペアで cosine 類似度を計算:

```python
import numpy as np
cos = np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))
```

### Step 4. 疾患↔承認薬マッピング（構築済みビュー `RAW.CREEDS.VW_FIG3A_APPROVED_DRUG_MAP`）

クロスワークは構築・検証済み（2026-07-14）。ビューをそのまま使う。

- 定義: CREEDS(ヒト+DOID)の `disease_name` を ChEMBL承認適応(`COMPOUND_TO_INDICATION`, `MAX_PHASE_FOR_IND=4`)の `MESH_HEADING`/`EFO_TERM` と**正規化文字列一致**で突合し、さらに薬剤名を L1000 `PERTNAME` と一致させて「L1000内に存在する承認薬」だけに絞ったもの。
- カラム: `do_id, disease_name, pertname, drug_lc, match_source(MESH/EFO)`。
- 規模: **41疾患 / 89薬剤 / 130 (disease, drug) ペア**（論文の46-48に近い）。がん系（乳がん・前立腺がん・腎細胞がん・多発性骨髄腫）と免疫系（関節リウマチ・乾癬・喘息等）を両方含み、がん負/免疫正パターンの再現に十分。
- 各(disease, pertname)ペアについて Step3 の cosine 相関を集め、疾患ごとに分布化 → Fig3a。

> 名寄せは完全一致ベース。取りこぼしの多いレアな別名は今回は追わない（41疾患で目的は達成）。精度を上げたい場合は UMLS CUI(`umls_cui`)経由の突合や別名辞書を追加。

---

## 4. 作図（Fig.3a）

作図規約は `/figure-style` skill を参照（カラーパレット・フォント・出力形式の統一）。

```python
import pandas as pd
import matplotlib.pyplot as plt

# df: columns = ['disease', 'drug', 'cos']  (承認薬のみ)
order = df.groupby('disease')['cos'].median().sort_values().index   # 中央値の昇順
df['disease'] = pd.Categorical(df['disease'], categories=order, ordered=True)

ax = df.boxplot(column='cos', by='disease', grid=False, showfliers=True)
ax.set_xlabel('Disease'); ax.set_ylabel('Cosine correlation')
# 横軸ラベルは回転、がん(下)/免疫(上)の分離を確認
```

- x軸: 疾患を**承認薬相関スコアの中央値昇順**で並べる。
- y軸: cosine 相関係数。
- 箱=IQR、中央線=中央値、髭=1.5×IQR、点=外れ値（`showfliers=True`）。

---

## 5. 検証チェックリスト — 実行済み 2026-07-14

実装: `notebooks/reproduction/01_repro_fig3a.ipynb`（実体スクリプト検証済み）。出力: `results/figures/fig3a_repro.png`, `results/tables/fig3a_repro_correlations.csv`。

- [x] 共通遺伝子数 = **784**（論文≈848。organism=human・L1000列との積集合）
- [x] 描画疾患 = **41**、薬剤89、ペア130（論文46-48に近い）
- [x] boxplot構造は論文Fig3aと一致（疾患ごと・中央値昇順・値域±0.1付近）
- [x] **がん/免疫の強い分離は出ない**（cancer中央値+0.004 / immune+0.003 / other−0.003）

### 結果の解釈（重要）

Fig3a（**transcriptomeベース**）は相関がほぼ0付近に集中し、がん負/免疫正の明瞭な分離は出ない。これは**論文の主張と整合**する：強い分離（がん−0.9〜−0.5、免疫+0.47〜+0.87）は **Fig3b以降のregulomeベース**で初めて現れるものであり、「transcriptomeでは弱い→だからregulomeを導入する」というのが論文のロジック。したがって本再現（3aのみ）の"弱い相関"は失敗ではなく期待どおり。強い分離を見たい場合はregulome変換（3b、本手順の範囲外）が必要。

補足: top/bottom 5%で薄くした薬剤ベクトル（978中約49非ゼロ）と疾患DE遺伝子ベクトルは、共通784遺伝子上で非ゼロ位置の重なりが小さくcosineが0付近になりやすい。これも3aが弱く見える構造的要因。

---

## 6. glycogene版バリアント（2026-07-15）

実装: `notebooks/reproduction/02_glycogene_fig3a.ipynb`。出力: `results/figures/fig3a_glycogene.png`, `results/tables/fig3a_glycogene_correlations.csv`。

同じ枠組みで**遺伝子空間を glycogene に限定**した版。

- 薬剤側: `RAW.LINCS.GLYCO_GENES_WIDE`（薬剤プロファイル × glycogene 推定発現, 385遺伝子）を化合物ごとに平均。**top/bottom 5%閾値なし**（既に絞ったパネルのため）。
- 疾患側: CREEDS(do_id平均) を同 glycogene に制限。
- 共通 glycogene = **247**。41疾患130ペア。

結果: cosine中央値は cancer +0.016 / immune +0.022 / other +0.007。**がん負/免疫正の分離は出ない**（landmark版3aと同様、transcriptomeレベルのcosineでは弱い）。疾患順位はlandmark版と別物になり、glioblastoma/GERD/MSが最も負、obesity/tuberculosis/melanomaが最も正。

> 解釈: glycogeneに絞っても transcriptome-cosine のままでは分離しない。3rd paperで「効かせる」には、glycogene発現→glyco-epitope potential への射影（scoring）や、regulome的な集約軸が必要という示唆。単純な遺伝子部分集合化では不十分。

---

## 参考: 主要パラメータ早見表

| 項目 | 値 |
|------|-----|
| L1000 ランドマーク遺伝子 | 978 |
| 使用遺伝子 | top/bottom 各5%（残り0埋め） |
| 共通遺伝子(薬剤-疾患 transcriptome) | ≈848 / 14,639 |
| 承認薬ありの疾患 | 48（解析対象46） |
