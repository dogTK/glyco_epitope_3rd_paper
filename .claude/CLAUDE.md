# glyco_epitope_3rd_paper

糖鎖エピトープに関する第3論文プロジェクト。

## 研究背景

- **1st paper**: 糖鎖遺伝子のON-ratio解析（HHTデータ）
- **2nd paper**: LINCS L1000を用いたglycogene関連薬剤スクリーニング・類似性解析（`lincs_glyco_2nd_paper/`）
- **3rd paper**: 本プロジェクト（詳細は進捗に応じて追記）

## ディレクトリ構造

```
glyco_epitope_3rd_paper/
├── data/
│   ├── raw/          # 生データ（変更禁止）
│   └── processed/    # 前処理済みデータ
├── notebooks/
│   ├── analytics/    # 解析ノートブック
│   ├── engineering/  # データ処理・変換
│   ├── visualization/# 作図専用
│   └── lib/          # 共通関数
├── scripts/          # バッチ処理スクリプト
├── results/
│   ├── figures/      # 出力図
│   └── tables/       # 出力テーブル
├── inputs/           # 外部入力ファイル
└── manuscript/       # 原稿ファイル
```

## データソース

- **Snowflake** からデータを参照する（**snowcli** 経由）
- ローカルの `data/raw/` には置かず、Snowflakeクエリ経由で取得

## 環境

- **conda env**: `glyco-epitope-3rd`
- 作成: `micromamba env create -f environment.yml`
- 起動: `micromamba activate glyco-epitope-3rd`

## 研究の方向性・中心概念

既存の「glycogene応答からHCC治療薬を探す」方向は、治療効果に直結しにくくdryだけでは限界がある。

**新方向性**: LINCS薬剤応答から **薬剤誘導性glyco-epitope potential** を推定し、糖鎖バイオマーカー・レクチン検出・抗糖鎖抗体/抗体医薬文脈に接続する。

```
drug-induced transcriptome
  → glycogene program
  → predicted glyco-epitope potential
  → lectin / antibody / biomarker / glycan-binding protein axis
  → glyco-targetability
```

疾患治療効果を直接主張するのではなく、
「HCC細胞の糖鎖エピトープ標的性・検出可能性・細胞表面インターフェースを薬剤で再配線しうる」という落とし方にする。

## 想定Figure構成

- **Fig 1**: 研究コンセプト — LINCS drug response → glycogene program → glyco-epitope potential → glyco-targetability
- **Fig 2**: glyco-targetability dictionary — エピトープ × biosynthesis genes × lectin/antibody/biomarker/認識分子 対応表
- **Fig 3**: 薬剤ごとの epitope potential heatmap — drug/MoA × glyco-epitope score
- **Fig 4**: MoA/ATC enrichment — 特定エピトープスコア上位薬剤に濃縮するMoA/ATC
- **Fig 5**: HCC文脈への接続 — core fucose/AFP-L3-like、STn/TACA、Lewis/selectin、galectin/poly-LacNAcなどの drug-epitope-modality network

## 外部データの位置づけ

主解析はLINCS。外部データは補助的に使用。

**外部データ候補**: TCGA-LIHC、HCC scRNA-seq、CPTAC、既存HCC glycomics/lectin array文献

**外部データ使用目的**:
- HCCでのcarrier protein・認識分子(レクチン/抗体等)発現確認
- 正常肝との差異
- HCC TMEにglycan-binding protein陽性細胞の存在確認
- HCC糖鎖バイオマーカー文脈への接続

## Wet validation（最小構成）

薬効試験ではなく **lectin staining validation** が最小かつ最も効果的。

| 項目 | 内容 |
|------|------|
| 細胞 | HepG2 |
| 条件 | DMSO vs candidate drug 2-3個 |
| 時間 | 48h or 72h |
| 検出 | lectin staining 1-2種類（flow cytometry or IF） |

**優先候補**: core fucose / fucosylation axis → AAL or LCA lectin

## 関連プロジェクト

- `../lincs_glyco_2nd_paper/` — 2nd paper（l1000-glyco env）
- `../1st_paper/` — 1st paper

## 作図スタイル

作図時は `/figure-style` skillを参照。

## ノートブック命名規則

`XX_概要.ipynb`（連番プレフィックス）— 2nd paperの慣例に従う。

## Obsidianノート編集ルール

- デイリーノートに**勝手に見出し（##）を追加しない**。既存のセクション内に書くこと。
- ユーザーが明示的に「見出しを追加して」と言った場合のみ追加可。

## Obsidian作業ログ

Stop hookによりセッション終了時にObsidianのデイリーノートへ自動ログが記録される。

**Claude への指示**: **毎回の応答の最後**に必ずBash toolで以下を実行すること（ユーザーへの返答のみで作業をしていない場合は省略可）：

```bash
echo "やったことの日本語サマリー（1行）" > /Users/koreedatatsuya/research/glyco_epitope_3rd_paper/.claude/session_summary.txt
```

hookはこのファイルを読んでノートに記録する。ファイルがない場合は記録しない（フォールバックなし）。
