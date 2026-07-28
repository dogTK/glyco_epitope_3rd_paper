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

## 既に設計docで参照済みの主要論文（PDF未収録含む）

- **Namba, Iwata, Yamanishi. *Bioinformatics* 2022, 38(S1):i68** — target repositioning。Fig4の元ネタ。→ `docs/yamanishi_collaboration.md`
- **Wang et al. *npj Syst Biol Appl* 2022 (PMC9640590)** — regulome-based drug activity across the diseasome。Fig3a再現の対象。→ `docs/HANDOFF.md`
- **Huang et al. *Dev Cell* 2021** — GlycoMaple。epitope potentialの集約ロジック（step内max × step間min）の出典。→ `docs/epitope_potential_design.md`
- **Groth et al. *Bioinformatics* 2022** — GlycoEnzOnto。経路/反応データの出典（CC-BY-4.0、帰属必須）。→ `inputs/GlycoEnzOnto/`
