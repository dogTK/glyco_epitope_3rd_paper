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

## 収録リスト

| ファイル名 | 著者 / 年 / 誌名 | 内容・本プロジェクトでの位置づけ |
|---|---|---|
| | | |

## 既に設計docで参照済みの主要論文（PDF未収録含む）

- **Namba, Iwata, Yamanishi. *Bioinformatics* 2022, 38(S1):i68** — target repositioning。Fig4の元ネタ。→ `docs/yamanishi_collaboration.md`
- **Wang et al. *npj Syst Biol Appl* 2022 (PMC9640590)** — regulome-based drug activity across the diseasome。Fig3a再現の対象。→ `docs/HANDOFF.md`
- **Huang et al. *Dev Cell* 2021** — GlycoMaple。epitope potentialの集約ロジック（step内max × step間min）の出典。→ `docs/epitope_potential_design.md`
- **Groth et al. *Bioinformatics* 2022** — GlycoEnzOnto。経路/反応データの出典（CC-BY-4.0、帰属必須）。→ `inputs/GlycoEnzOnto/`
