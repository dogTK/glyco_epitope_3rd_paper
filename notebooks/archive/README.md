# archive（筋悪と判断して退避）

2026-07-25、signature-reversal → targetability への方針転換（`docs/reframe_reversal_to_targetability.md`）に伴い、
reversal/dry予測ベースの以下notebookを退避。参照可・復帰可（git mvで履歴保持）。

- 01_epitope_potential — 薬×epitope potential(step内max×step間min, コントラスト)
- 02_hcc_core_fucose — HepG2で承認薬がcore fucose等を増減（※core fucose候補リストはwet種として復帰余地あり）
- 03_hcc_normalization_reversal — HCC↔正常(PHH)のreversal（統計は糖鎖固有でないと判明）
- 03_epitope_projection_fig3a — Fig3aをepitope空間で（疾患マッチング, 分離せず）
- 04_reversal_ranking_benchmark — 承認薬recovery AUROC（全空間ランダム級, ep-tx有意差なし）

2026-08-02、汎系統（cross-lineage）路線の終了に伴い以下を追加退避。
出力は `results/_retired/01_cross_lineage/`（目録は同ディレクトリのREADME）。

- 01_cross_lineage_epitope_transferability — Fig4旧背骨。実データで不成立（`docs/negative_result_cross_cell_transfer.md`）
- 02_epitope_signature_umap — z-score空間のUMAP。構造が出ない原因はベースライン減算と判明し、絶対量版（analytics/03-05）に置換済み
