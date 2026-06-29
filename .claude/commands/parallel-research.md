# /parallel-research

指定したトピックリストに対して並列エージェントを起動し、文献付きのリサーチ結果をMarkdownにまとめる。

## 使い方

```
/parallel-research <調査テーマ> / <トピック1>, <トピック2>, ...
```

例：
```
/parallel-research glyco-epitope / Core fucose, Sialyl-Lewis, Tn/STn
/parallel-research HCC薬剤 / Sorafenib, Regorafenib, 5-FU
```

## Claude への指示

$ARGUMENTS を解析して `<テーマ> / <トピック1>, <トピック2>, ...` の形式を読み取る。

各トピックに対して以下の内容を調査する並列エージェントを **同時に** 起動する（`run_in_background: true`）：

1. 主要な関連遺伝子・タンパク質
2. HCC（または指定疾患）文脈でのエビデンス
3. 検出・測定手段
4. 薬剤による変動エビデンス
5. **PubMed / PMC / DOI リンクを必ず含める**（リンクなしの情報は「要文献確認」と明記）

全エージェントの完了を待ち、結果を以下の形式でMarkdownにまとめて `inputs/<テーマ>_research_<YYYY-MM-DD>.md` に保存する：

- サマリーテーブル（全トピック × 主要項目）
- 各トピックの詳細セクション（文献リンク付き）
- リンクなし項目には ⚠️ 要文献確認 を明記
- 論文接続メモ（このプロジェクトへの示唆）

保存後、サマリーテーブルをユーザーに表示する。
