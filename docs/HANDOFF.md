# 引き継ぎドキュメント（2026-07-15 時点）

3rd paper（薬剤誘導性 glyco-epitope potential）に向けた、先行研究Fig3a再現とglyco-epitope辞書整備のハンドオフ。

---

## 1. これまでの流れ（一言で）

先行研究 **Wang et al., "Regulome-based characterization of drug activity across the human diseasome"**（npj Syst Biol Appl 2022, PMC9640590）の **Fig3a（transcriptomeベースの薬剤-疾患相関 boxplot）を再現** → **glycogene版に応用** → 本命の **glyco-epitope辞書（epitope→生合成遺伝子）をSnowflakeに整備**、まで進んだ。

---

## 2. 先行研究の要点（再現対象）

- 手法: LINCS L1000 薬剤シグネチャ と 疾患シグネチャ を、①transcriptome ②regulome(転写因子) で照合しコサイン相関。
- **Fig3a=transcriptome版**: 相関は0付近で弱く、がん負/免疫正の分離は**出ない**。強い分離は **Fig3b=regulome版**（ChIP-Atlas＋Fisherで転写因子軸に射影）で初めて出る。
- 本再現はFig3aのみ。Fig3b(regulome)は未実装。

---

## 3. 確定した設計判断（ユーザー合意済み）

| 論点 | 決定 |
|------|------|
| 承認薬マッピング | ChEMBL `COMPOUND_TO_INDICATION`（MAX_PHASE=4）。論文のKEGGではなく実用重視 |
| 薬剤シグネチャ集約 | 化合物(PERTNAME)ごとに全trt_cp平均（論文は未明記、疾患側の平均と対称に） |
| 疾患シグネチャ集約 | 同一do_idのCREEDS複数シグネチャを平均（論文どおり） |
| 共通遺伝子 | L1000ランドマーク ∩ CREEDS（landmark版で784、論文≈848） |
| organism | human のみ |
| 用語 | **「reader」使用禁止 → 「認識分子」**（レクチン/抗体等） |

---

## 4. Snowflake 資産（接続: `snow -c admin`、DB=RAW）

### RAW.CREEDS（疾患シグネチャ, 新規作成）
- `RAW_DISEASE_SIGNATURES_JSON` (VARIANT, 828) / `DISEASE_SIGNATURES_META` (828) / `DISEASE_SIGNATURE_GENES` (490,686)
- `VW_HUMAN_DISEASE_GENES`（ヒト+DOID, 293,034行）
- `VW_FIG3A_APPROVED_DRUG_MAP`（疾患↔承認薬↔L1000突合済み: **41疾患/89薬剤/130ペア**）

### RAW.GLYCOEPITOPE（glyco-epitope辞書, 新規作成）
- `EPITOPE_ENZYME`（epitope→酵素: 56エピトープ/41遺伝子名。列 EPITOPE_ID, ENZYME_ROLE, GENE_SYMBOL, EC, CAZY, REACTION, DESCRIPTION）
- `ENZYME_HGNC_CROSSWALK`（酵素名→HGNC: 41行。32割当/review7/nonhuman2）
- `VW_EPITOPE_GLYCOGENE`（join。epitope→HGNC glycogene）

### RAW.LINCS（既存, 主に参照）
- `L1000_LEVEL5_LANDMARK`（薬剤 x_trans源, trt_cp 205,034行, 遺伝子列≈959。メタ列は大文字, 遺伝子列も大文字）
- `GLYCO_GENES_WIDE`（薬剤×glycogene推定発現, 385遺伝子。**メタ列は小文字クォート識別子**"pertname"等, 遺伝子列は大文字, 値はVARCHAR→要numeric化）
- `COMPOUND_TO_INDICATION`（承認薬。MAX_PHASE_FOR_IND=4）
- `GLYCOEPITOPE_EPITOPES`（epitope一覧173, 既存）
- ⚠ `VW_GLYCOEPITOPE_AXIS_GENES` / `VW_GLYCOEPITOPE_CATEGORY_SUMMARY` は**壊れている**（消失した`BIOINFORMATICS` DBを参照）。RAW.GLYCOEPITOPEが実質の代替。

---

## 5. リポジトリ成果物

- `docs/repro_regulome_fig3.md` — Fig3a再現手順書（設計判断・結果・glycogene版まで）
- `docs/plan_creeds_to_snowflake.md` — CREEDS取込計画（実行済み記録）
- `docs/glycoepitope_dictionary.md` — glyco-epitope辞書の設計・HGNC正規化・review項目
- `docs/HANDOFF.md` — 本ファイル
- `notebooks/reproduction/01_repro_fig3a.ipynb` — Fig3a再現（landmark版, Snowflake接続込み実コード）
- `notebooks/reproduction/02_glycogene_fig3a.ipynb` — glycogene版
- `scripts/glycoepitope_scrape_enzyme.py` — glycoepitope.jp enzymeタブ スクレイパー
- `scripts/glycoepitope_hgnc_crosswalk.py` — 酵素名→HGNC対応表ビルダー
- 図/表は `results/figures/`, `results/tables/`（**gitignore対象**＝ローカルのみ）: `fig3a_repro.png`, `fig3a_glycogene.png`, 各`_correlations.csv`

---

## 6. 主要な結果・学び

1. **Fig3a再現成功**: landmark版も論文Fig3a同様、相関0付近・分離なし。「transcriptomeは弱い→regulomeが必要」という論文の主張を独立再現。
2. **glycogene版も分離せず**: 遺伝子をglycogeneに絞っても弱いまま。landmark版とペア相関ほぼ0（56%符号反転）で、順位変化はノイズ由来。→ **単純な遺伝子部分集合化では効かない。epitope potentialへの「射影/scoring」が必要**という示唆。
3. **epitope→glycogene連結が通った**: HGNC正規化した30遺伝子は**全てLINCS glycogeneに存在**、47エピトープが連結可能。

---

## 7. オープン項目（次にやること）

- [ ] **HGNC review 7件の確定**（AT-1, Beta3Gal-T3, Gal-6-sulfotransferase, GalT, LA2 synthase, Sialyltransferase 3, polypeptide alpha-GalNAc-T）。confidence=medium 3件(CHST10/CHST4/CHSY3)も要チェック。
- [ ] **Antibody / Lectin / Diseases 軸の取得**（`/epitopes/{ID}/antibody` `/lectin` `/diseases`、enzymeと同じ要領）→ Fig2 認識分子軸
- [ ] **epitope→glycogene→LINCS の接続試作**: 薬剤ごとに epitope の生合成遺伝子群の発現変化を集計 = epitope potential の最初のスコア
- [ ] （任意）Fig3b regulome版の実装（ChIP-Atlas＋Fisher）

---

## 8. 環境・注意点（ハマりどころ）

- **Python環境**: conda env `glyco_pred`（`conda run -n glyco_pred python ...`）。snowflake-connector-python, pandas, bs4, requests, scipy 入り。※CLAUDE.md記載の`glyco-epitope-3rd`/`micromamba`は**存在しない**。
- **Snowflake接続(Python)**: `connection_name='admin'`は秘密鍵を自動ロードしないので、明示指定が必要:
  ```python
  sc.connect(account='DUETMBM-LL33279', user='KOREEDA', role='ACCOUNTADMIN',
             warehouse='BIOINFORMATICS_XS', authenticator='SNOWFLAKE_JWT',
             private_key_file=os.path.expanduser('~/.ssh/snowflake_rsa_key.pem'))
  ```
  CLIは `snow sql -c admin -q "..."`。
- **自動commit/pushフック**: Stop時に `.claude/hooks/git-commit-push.sh` が `session_summary.txt`1行目をコミットメッセージにmainへpush。add対象は `-u` ＋ `manuscript/ notes/ scripts/ inputs/ docs/ notebooks/ .claude/`（docs/notebooks は今回追加）。**results/ はgitignore**。
- **GLYCO_GENES_WIDE のメタ列は小文字クォート識別子** → SQLで `"pertname"` のようにダブルクォート必須。
- glycoepitope.jp は一括DL無し。detailはSPAだが `/epitopes/{ID}/enzyme` 等はブラウザUAでHTML取得可。117/173エピトープはenzyme記載なし（サイト側欠損）。
