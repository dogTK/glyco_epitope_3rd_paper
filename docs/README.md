# docs 索引

**最終整理 2026-08-02。** どれが現行の方針で、どれが歴史的記録かを分ける。
古い文書も消していない——否定的結果の記録は**同じ設計を再発明しないために要る**ため。
代わりに、現行でないものには冒頭に訂正ブロックを置いてある。

---

## まずここ（現行の方針）

| 文書 | 中身 |
|---|---|
| **`roadmap_to_thesis.md`** | **最初に読む。** 研究の構造（3層の鎖）、Phase 0〜3、死んだ案と生きた案の判別基準、確定事項と未決事項 |
| `paper_value.md` | 論文の売り・新規性・創薬への出口・正直な線引き（2026-08-02 全面改稿） |
| `wet_target_selection.md` | wet の標的（細胞株 × エピトープ）の選定。HepG2 は支持、core fucose は不支持 |

## 決定の根拠（生きている記録・消さないこと）

| 文書 | 中身 |
|---|---|
| `negative_result_cross_cell_transfer.md` | 汎系統マップが不成立と確定した経緯（perm p=1.000）。**同じ設計を再発明しないための記録** |
| `set_based_aggregation_feasibility.md` | エピトープ集合の超幾何が原理的に不成立（47中31が1遺伝子）。経路レベルなら65経路で可能 |
| `reframe_reversal_to_targetability.md` | signature-reversal を捨てて表面表現型へ転換した理由（2026-07-25） |

## 参照データ（現行・正確）

| 文書 | 中身 |
|---|---|
| `lincs_data_inventory.md` | Snowflake の LINCS 資産棚卸し。**エピトープ57遺伝子の測定区分**（landmark 3 / BING 37 / plain inferred 6 / L1000外 11）は重要 |
| `glycoepitope_dictionary.md` | 辞書（`RAW.GLYCOEPITOPE`）の設計・テーブル構成・HGNC正規化 |

## 訂正ブロック付き（部分的に有効）

| 文書 | 何が生きていて、何が死んでいるか |
|---|---|
| `epitope_potential_design.md` | パイプラインの構想と出典の整理は有効。**スコア定義（Δにmax/minを掛ける）は誤りで未修正**。版の段階表も古い |
| `epitope_supplement_rationale.md` | 補完の方針（元DBの系統的な穴を埋める）は有効。**「単一遺伝子＝スコアリングに最適」という評価と core fucose 筆頭の優先順位は反証済み** |
| `yamanishi_collaboration.md` | 山西研の手法資産の整理は有効。**冒頭の訂正ブロックは行き過ぎ**——体制は実際に共同研究（dry は著者、wet は山西研側）なので、分担イメージの節はおおむね妥当。ただし山西先生は指導教員でもある |

## 歴史的記録（現在の方針には使わない）

| 文書 | 注意 |
|---|---|
| `HANDOFF.md` | 2026-07-15 時点。§4（Snowflake資産）と §8（環境・ハマりどころ）だけ現役。「次にやること」は全て決着済みか破棄済み。存在しない doc を2件参照している |

---

## 参照されているが存在しない文書

`repro_regulome_fig3.md` / `plan_creeds_to_snowflake.md` — `HANDOFF.md` §5 が参照しているが、
リポジトリに無い（作成されなかったか削除された）。**新たに書く必要はない**——
再現手順が要るときは `notebooks/reproduction/01_repro_fig3a.ipynb` のコードを直接読む。

## 運用の教訓

**skill に doc の内容をコピーしない。** `/paper-value` skill は `docs/paper_value.md` のコピーを
持っていたが、skill 側は `.gitignore` されているため更新から取り残され、
**2026-07-25 の内容のまま4つの方針転換に置いていかれた**。
「見失ったときに立ち返る先」が最も古い、という最悪の状態だった。
2026-08-02 に skill は参照のみに変更済み。
