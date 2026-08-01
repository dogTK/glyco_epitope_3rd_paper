# 山西先生との接続点：target repositioning × 糖鎖酵素/エピトープ

> ⚠ **前提の訂正（2026-08-02）**：本ドキュメントは「共同研究の落とし所メモ」として書かれているが、
> **山西先生はユーザーの指導教員であり、山西研は所属研究室である**（外部の共同研究相手ではない）。
> 下の「分担イメージ」は外部との交渉を想定した枠なので、**分担ではなく
> 「研究室の資産のうち何を借りるか」のリスト**として読み替えること。
> ロードマップは `docs/roadmap_to_thesis.md`。

山西芳裕先生（名古屋大）の手法資産と、本プロジェクト（薬剤誘導 glyco-epitope 辞書）の合流点を整理する。

> **Fig4採用（2026-07-28）**：下記「接続（3点）」の1が、3rd paper本体のFig4（epitope×疾患 target-repositioningマップ）として正式採用された。詳細は`docs/paper_value.md`。共同研究の話とは別に、まず自前で（既存の疾患シグネチャ基盤828疾患を使って）dryのプロトタイプを作る。

## 起点となる論文

**Namba, Iwata, Yamanishi. "From drug repositioning to target repositioning:
prediction of therapeutic targets using genetically perturbed transcriptomic signatures."
Bioinformatics (ISMB) 2022, 38(S1):i68.**
https://academic.oup.com/bioinformatics/article/38/Supplement_1/i68/6617490

### 論文の要点
- **発想**：薬をリポジショニングするのでなく、**標的(target)をリポジショニング**する。創薬しやすい標的が枯れてきたので、遺伝子摂動署名で「その標的が別疾患でも治療標的になり得るか」を予測。
- **入力**：遺伝子ノックダウン署名(4,345)＋過剰発現署名(3,114)＋疾患署名(79疾患)。
- **手法**：①inverse signature法（摂動署名×疾患署名の相関＝シグネチャー逆位）②trans-disease法（疾患類似度で正則化したロジスティック回帰＋マルチタスク学習で **阻害すべき標的 vs 活性化すべき標的** を判別）。
- **性能**：trans-disease法で AUC 0.63〜0.65（SNPベースライン0.52〜0.59より上だが modest）。オーファン標的の新規予測（例：ATLのTAF1B）。
- **教訓**：**トランスクリプトームからの標的予測の精度天井はこの程度**。精度勝負でなく「新標的を出す＝記述・仮説生成」で価値を作るスタンス。

## 本プロジェクトとの接続（3点）

1. **対象を「薬」でなく「糖鎖酵素/エピトープ」にする**
   FUT8/MGAT5/ST6GALNAC1 等が「HCCで阻害/活性化すべき標的か」を評価。
   epitope potential（薬→エピトープ）を、標的側（酵素KD/OE→表現型）から補完。

2. **入力を薬署名でなく遺伝子摂動署名(KD/OE)にする**
   薬署名は弱く取りこぼす（本プロジェクトのdry検証・この論文のinverse sign法も同様に弱い）。
   LINCSのshRNA/ORF摂動署名は「その遺伝子を直接いじった因果」でクリーン。糖鎖酵素の標的価値はこちらで読む方が筋が良い。

3. **阻害 vs 活性化の判別枠を流用**
   前段の議論「エピトープを下げると価値（免疫チェックポイント: STn/sialyl/core-fucose-PD-L1）／上げると価値（感作標的: STn/GD2/Globo-H）」の判別に、
   trans-disease法の inhibitory/activatory 標的判別がそのまま対応。

## 山西研の他の手法資産（接続候補）

- **GxRNN / TRIOMPHE**：望む発現プロファイルから分子をde novo生成 → 「望む**糖鎖エピトープ状態**を起こす分子生成」へ拡張（エピトープ条件付き創薬）。
- **AlphaFold構造×ドッキング×MLで薬効/毒性予測**（坂尻・山西 2024）→ 糖鎖酵素(FUT8等)を標的にした構造ベース予測。「core fucoseを直接抗体標的にできない→酵素を狙う」問題を回避。
- **DTI予測（化学空間×ゲノム空間）**：標的を糖鎖エピトープまで拡張。

## 分担イメージ

- **本プロジェクト（自分）**：薬剤誘導 glyco-epitope 辞書（epitope→生合成酵素→認識分子、検出/標的の役割分け）。
- **山西研**：target repositioning（糖鎖酵素の阻害/活性化判別）／エピトープ条件付き分子生成／糖鎖酵素ドッキング。

## スタンスの一致
「dryで精度勝負しない、記述・仮説生成で価値を作る」は、山西先生のtarget repositioning論文とも、本プロジェクトの `docs/reframe_reversal_to_targetability.md`（予測でなく記述、勝ち筋はwet）とも一致する。

関連: `docs/reframe_reversal_to_targetability.md`、`/paper-value`、`/project-links`。
