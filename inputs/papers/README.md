# 先行研究PDF

3rd paper執筆・設計の参照元となる論文PDFの置き場。

## 運用ルール

- **PDF本体はgit管理しない**（`.gitignore` で `inputs/papers/*.pdf` を除外）。出版社PDFは再配布不可のものが多く、リポジトリも重くなるため。
- **書誌情報はこのREADMEに追記する**。PDFが手元に無い環境でも「何を参照したか」が追えるようにする。

## ファイル名

```
著者姓_年_誌名_キーワード.pdf
```

例: `Namba_2022_Bioinformatics_target-repositioning.pdf`

## 方針検討時の扱い

**研究の方針・図構成・解析設計を考えるときは、ここのPDFを必ず材料に含める。**
山西研の論文群は本プロジェクトの直接の先行研究であり、「既出でないか」「どう差別化するか」を毎回確認する。

## 収録リスト

| ファイル名 | 著者 / 年 / 誌名 | 内容・本プロジェクトでの位置づけ |
|---|---|---|
| `Molecular Informatics - 2019 - Akiyoshi - Omics-based Identification of Glycan Structures as Biomarkers for a Variety of (1).pdf` | Akiyoshi, Iwata, Berenger, **Yamanishi**. *Mol Inf* 2020, 39:1900112 | ⚠**最重要**。CREEDS疾患シグネチャ（79疾患）×glycogene（332遺伝子）を13のKEGG糖鎖経路の**filling rate**（経路内で変動したglycogeneの割合、up/down区別なし）に集約し、**PCA/GTMで疾患-疾患の糖鎖類似度マップ**を作成。「悪性黒色腫≈多発性骨髄腫（N-glycan biosynthesis）」「C型肝炎≈鎌状赤血球症」等を報告。**疾患横断の糖鎖類似マップは既出**。→ 本プロジェクトの差別化は①薬剤軸②エピトープ解像度＋方向性③認識分子/標的性 |
| `Predicting inhibitory and activatory drug targets by chemically and genetically perturbed transcriptome signatures.pdf` | Sawada, Iwata, Tabei, Yamato, **Yamanishi**. *Sci Rep* 2018, 8:156 | 薬剤処理シグネチャ × KD署名（阻害）/ OE署名（活性化）の相関で**阻害標的 vs 活性化標的を判別**。DC法（教師なし相関）とJL法（joint learning）。1,124薬/829標的/365疾患。**活性化側は負のフィードバックで相関が弱い**（教師なしDC法は活性化で機能せずJL法が必要）という知見が、エピトープ「上げる/下げる」判別に直結 |
| `From drug repositioning to target repositioning- prediction of therapeutic targets using genetically perturbed transcriptomic signatures.pdf` | Namba, Iwata, **Yamanishi**. *Bioinformatics* 2022, 38(S1):i68 | target repositioning。Fig4の元ネタ。詳細は `docs/yamanishi_collaboration.md` |

## 山西研の LINCS 論文（2026-07-29 調査、PDF未取得）

「山西研でLINCSを使っている論文」を網羅調査した結果。**Akiyoshi（糖鎖論文の筆頭著者）は Iwata 2017 / Iwata 2019 の共著者でもある**——同研究室内で「糖鎖×CREEDS」と「薬剤×LINCS」が別々に走っており、それを繋ぐ人材が既にいる。「糖鎖×LINCS」は彼らの射程内と考えるべき。

### A. 化合物誘導トランスクリプトーム（trt_cp）

| 論文 | 内容 | うちとの関係 |
|---|---|---|
| **Iwata, Sawada, Iwata, Kotera, Yamanishi. *Sci Rep* 2017, 7:40164** — "Elucidating the modes of action for bioactive compounds in a **cell-specific** manner" | 16,268化合物 × 68細胞株。①163 KEGG経路の濃縮解析（**上位5%・下位5%の遺伝子で超幾何検定＋FDR**）→②転写類似度で標的予測→③適応予測 | ⚠**最重要**。「**同一細胞株マッチング**」と「**別細胞株マッチング**」を比較し、同一細胞株が大幅に優ると報告。**薬剤応答が細胞を跨いで転移しないことを2017年に文書化済み**で、細胞内マッチングで設計を回避している。集合ベースの経路集約も要参照 |
| **Iwata, Hirose, Kohara, Liao, Sawada, Akiyoshi, Tani, Yamanishi. *J Med Chem* 2018, 61(21):9583** — "**Pathway-based** drug repositioning for cancers: computational prediction and **experimental validation**" | 1,112薬 × 66細胞株。増殖経路を不活化し細胞死経路を活性化する薬を探索。**in vitro 3アッセイ（生存率・細胞毒性・アポトーシス）でwet検証** | 「経路構造スコア＋wet検証」といううちのFig構成の、ほぼ完成形の先例 |
| **Iwata, Yuan, Zhao, Tabei, Berenger, Sawada, Akiyoshi, Hamano, Yamanishi. *Bioinformatics* 2019, 35:i191** — tensor-train分解 | 261薬×16細胞株×978遺伝子。LINCSは薬×細胞の大半が未測定という前提で欠損補完 | "drugs function in a cell-dependent manner" を前提に置く |
| **Iwata & Yamanishi 2018**, Methods Mol Biol — LINCS利用の総説 | 手法解説 | 参照用 |
| **Yamanaka, Iwata, Kaitoh, Yamanishi. *Mol Inf* 2025, 44(5-6):e2444** | 疾患関連組織の細胞特異性を考慮した薬剤探索・設計 | 最新。細胞特異性 |

### B. 化合物＋遺伝子摂動

上の収録リストの Sawada 2018 / Namba 2022 を参照。**Namba 2022 が使った摂動セットは RAW.LINCS にそのまま存在する**（trt_sh.cgs = 4,345、trt_oe = 3,114 で論文の数字と完全一致）。

### C. 生成系

**Kaitoh & Yamanishi. *JCIM* 2021** — TRIOMPHE。望むトランスクリプトームプロファイルから分子を生成。

### D. LINCSを使っていない

**Akiyoshi et al. *Mol Inf* 2020**（糖鎖の論文）— CREEDS疾患シグネチャのみ。薬剤も遺伝子摂動も無い。

## LINCS の再現性に関する外部評価（重要）

**Lim & Pavlidis. *Sci Rep* 2021, 11:17624** — "Evaluation of connectivity map shows limited reproducibility in drug repositioning"

- CMap1由来シグネチャでCMap2を検索したときの**成功率17%**
- DE再現性はCMap間でもCMap内でも低い
- **「DE強度が再現性を予測し、それは化合物濃度と細胞株の応答性に左右される」**

→ `docs/negative_result_cross_cell_transfer.md` で観測した交差細胞の非転移性・強度依存は、**LINCSの documented behavior** であり、パイプラインの不具合ではない。分野の対処法は ①細胞内マッチング（Iwata 2017）②DE強度フィルタ（Lim & Pavlidis）③値ベースでなく**集合ベース**の経路集約（Iwata 2017/2018）の3つ。うちは③が未対応。

## 既に設計docで参照済みの主要論文（PDF未収録含む）

- **Namba, Iwata, Yamanishi. *Bioinformatics* 2022, 38(S1):i68** — target repositioning。Fig4の元ネタ。→ `docs/yamanishi_collaboration.md`
- **Wang et al. *npj Syst Biol Appl* 2022 (PMC9640590)** — regulome-based drug activity across the diseasome。Fig3a再現の対象。→ `docs/HANDOFF.md`
- **Huang et al. *Dev Cell* 2021** — GlycoMaple。epitope potentialの集約ロジック（step内max × step間min）の出典。→ `docs/epitope_potential_design.md`
- **Groth et al. *Bioinformatics* 2022** — GlycoEnzOnto。経路/反応データの出典（CC-BY-4.0、帰属必須）。→ `inputs/GlycoEnzOnto/`
