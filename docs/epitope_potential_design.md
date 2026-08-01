# epitope potential スコアリング設計

薬剤誘導トランスクリプトームから **glyco-epitope potential**（各エピトープが薬剤でどれだけ増減しうるか）を
推定する計算の設計書。3rd paper の中核（Fig3）にあたる。

> ## ⚠ 未修正の設計誤り（2026-07-29 発見・2026-08-02 時点で未対応）
>
> **下の「スコア定義」は誤っている。** `Δexpr_g(d)`（z-score = 変化量）に max/min を掛けているが、
> 律速ロジック（step間 min）は発現**レベル**に対して定義されている。
> Δ に min を掛けると「最も**下がった**ステップ」を拾うが、それは律速ステップではない
> （大きく下がっても元が潤沢なら律速でないし、ほとんど動かなくても元から低ければそこが律速）。
> 射影は非線形なので「先に引く」と「後で引く」は一致しない。
>
> ```
> 現行（誤）: Δ発現 → max/min射影 → Δエピトープ
> 正しい形  : 処理後レベル → 射影 → エピトープ量(処理後)
>             対照レベル   → 射影 → エピトープ量(対照)
>             差を取る    → Δエピトープ
> ```
>
> これは交差細胞の否定的結果で観測された「+0.05 の人工物」の発生源でもある
> （Δのminは最も負の値なので、応答が強い薬ほど大きく振れ、スカラーの薬剤強度が漏れる）。
> 詳細 `docs/negative_result_cross_cell_transfer.md` 末尾。
>
> **修正に必要な絶対量データは取得済み**（`data/processed/abs_full_*.npy`、
> 118,900試料 × 23,614遺伝子、2026-08-01）。修正は roadmap の Phase 0-1。
>
> ## ⚠ 根本原因：辞書が「経路」でなく「決定的な1反応」しか持っていない（2026-08-02 判明）
>
> 52エピトープ中 **44が1ステップ**、うち大半が1遺伝子。これは糖鎖生物学の実態ではなく、
> **辞書の作りに由来する**。GlycoEpitope DB は「抗体・レクチンが認識する決定基」のカタログなので、
> **その決定基を作る最終反応の酵素だけ**を載せている。実データで確認：
>
> | エピトープ | 辞書が持つ酵素 | 実際の生合成に必要な段階 |
> |---|---|---|
> | **GD2** | **B4GALNT1 のみ**（EC 2.4.1.92） | UGCG → B4GALT5/6 → ST3GAL5 → ST8SIA1 → B4GALNT1 の**5段階** |
> | **T抗原** | **C1GALT1 のみ** | GALNT族で Tn を作ってから C1GALT1（+ COSMC シャペロン） |
> | Lewis y | FUT1,2,3,4,5,6,9 の7個 | **7個は全て同一反応のアイソ酵素**（EC 2.4.1.152 が重複）。経路ではない |
> | Sialyl Lewis x | FUT群 + ST3GAL3/4 | フコシル化とシアリル化で**EC が2種**→ここだけ2ステップになった |
>
> つまり **「多遺伝子エピトープ」の正体はほぼアイソ酵素の冗長性であって、多段階の経路ではない。**
> ステップ数が1か2かは「登録された酵素が2種類以上のEC番号にまたがるか」で決まっていた。
>
> **結果として、間min（律速）は動かす対象そのものを与えられていない。**
> 手法の中核ロジックが空回りしているのは、ロジックの問題ではなく**辞書の被覆の問題**である。
>
> ### 直せる。部品は揃っている
>
> GlycoEnzOnto に上流経路がある。GD2 の欠けている上流は、そのまま2つの経路に対応する：
>
> ```
> ganglioside core structure biosynthetic pathway      : UGCG, B4GALT6, B4GALNT1, B3GALT4   （L1000に4/4）
> terminal sialylation of gangliosides biosynthetic pw : ST3GAL2, ST3GAL5, ST6GALNAC4/5, ST8SIA1/3/5
> ```
>
> **上流遺伝子は L1000 に存在する。辞書が繋いでいないだけ。**
>
> ### これは希釈ではなく、本来の意味の回復である
>
> 「上流を足すとエピトープ間の区別がつかなくなる（全ガングリオシドが UGCG を共有する等）」
> という懸念はあるが、**min ロジックはまさにそのために設計されている**：
>
> - **末端酵素**が「どのエピトープか」を決める（特異性）
> - **上流**が「基質があるか」を決める（容量・律速）
> - `min(上流の容量, 末端酵素)` が正しい模型
>
> 現状は上流が空なので min が恒等写像に潰れている。**上流を繋ぐことで初めて手法が生きる。**
> Phase 0 の設計判断として優先度が高い。
>
> ## ⚠ 「版の段階」表も古い
>
> v3（分岐競合の減点）を「中期」としているが、**v2 の集合ベース化は原理的に不可能**と判明している
> （47エピトープ中31が1遺伝子で、内max も 間min も恒等写像になる。
> `docs/set_based_aggregation_feasibility.md`）。単一遺伝子エピトープでは
> **スコア＝その遺伝子の値そのもの**であることを論文で明示する必要がある。

## 全体パイプライン

```
エピトープ辞書（3rd, 自作）
  RAW.GLYCOEPITOPE.VW_EPITOPE_GLYCOGENE : epitope → 生合成酵素(HGNC)
        │
        ▼  遺伝子を「反応ステップ」に分割
GlycoEnzOnto 経路（2nd, CC-BY-4.0）
  lincs_glyco_2nd_paper/inputs/GlycoEnzOnto/  : pathway → gene メンバーシップ
        │
        ▼  発現変化を集約（GlycoMaple ロジック）
LINCS L1000 発現変化 × 内max × 間min
        │
        ▼
epitope potential（薬剤 × エピトープ スコア行列）
```

出典が全て明確：**ロジック=GlycoMaple (Huang et al. 2021)**、**経路/反応データ=GlycoEnzOnto (Groth et al. 2022, CC-BY-4.0)**、
**発現=LINCS L1000**、**エピトープ辞書=自作**。

## なぜこの設計か（背景）

- 先行検証で「生 transcriptome の cosine では薬剤-疾患の分離が出ない」「glycogene に絞っても出ない」ことを確認済み
  → **単純な遺伝子の和では効かない。射影／スコアリングが要る**、というのが出発点。
- エピトープはその**合成経路の全ステップが揃って初めて**できる。かつ同一ステップの isoenzyme は**冗長**。
  フラットな和はこの2つを区別できないので、**経路構造を反映した集約**が必要。

## 方針確定（2026-07-26）：GlycoMapleの経路ロジックに則る

epitope potential は **GlycoMapleの経路フラックス・ロジックに則る**。自作の負の論理（truncation専用ルール等）は入れない。
- 合成酵素↑ → その糖鎖が増える（core fucose 等）
- **伸長酵素↓（C1GALT1/COSMC 等）→ 経路が止まり手前の短縮構造(Tn/STn)が溜まる**

の両方が、同じ経路モデルの中で自然に表現される。特別ルールを盛らず一貫した枠組みで扱う。
※現行 `EPITOPE_STEP_GENE`（合成ステップの max/min）はその簡略版。truncationまで含めるなら GlycoMaple の経路モデル（伸長停止→前駆体蓄積）に寄せる。

## コアロジック（GlycoMaple 準拠）

GlycoMaple の公式集約ルールと一致：
- 複数 isoenzyme → デフォルトは最高発現遺伝子を採用（**max**）
- 酵素複合体／律速 → 最低発現サブユニット（**min**）
- 集約規則・閾値は設定可能

これを本プロジェクトの「エピトープ = 反応ステップの列」に適用する。

### スコア定義

薬剤 d・エピトープ e について、e の生合成酵素を反応ステップ `s = 1..S` に分割し：

```
step活性  A_s(d) = max_{g ∈ step s}  Δexpr_g(d)     … ステップ内 isoenzyme は OR（冗長）
potential P_e(d) = min_s A_s(d)                     … ステップ間は律速の AND
```

- `Δexpr_g(d)`：LINCS における薬剤 d による glycogene g の発現変化（z-score / level5）
- `min`：必要工程のどれか一つでも下がればエピトープは増えない、という生物学と一致
- 単一遺伝子の暴れに弱ければ **soft-min（-logΣexp(-A_s)）** に置換

### ステップ分割の根拠

GlycoEnzOnto の経路メンバーシップで自動分割する。例：
- **Sialyl Lewis x**：FUT3/4/5/6/7 → 「terminal fucosylation」経路（同一ステップ=max）、
  ST3GAL3/4 → 「terminal sialylation」経路（別ステップ=min）
- **HNK-1**：B3GAT1/B3GAT2/CHST10 → 「human natural killer 1 epitope biosynthetic pathway」

EC 番号だけでは末尾が `-` に潰れる酵素があり粗い。GlycoEnzOnto の経路クラスを第一の分割根拠とし、
EC は補助にする。

## 版の段階

| 版 | ロジック | 必要データ | 状態 |
|---|---|---|---|
| v1 | 符号付き和/平均 | 既存 | 参考（分離せず） |
| **v2** | **step: 内max × 間min（GlycoMaple-lite）** | GlycoEnzOnto 経路 + LINCS | **本命・次に実装** |
| v3 | + 分岐競合の減点（例 MGAT3⊣MGAT5, type1⊣type2 Lewis） | GlycoEnzOnto reaction rules | 中期 |

## 使用する外部リソース

### GlycoEnzOnto（2nd paper に配置済み・CC-BY-4.0）
`lincs_glyco_2nd_paper/inputs/GlycoEnzOnto/`
- `GlycoEnzOnto.gmt`（122経路）／`../glycoenzonto_pathways.json`（gene↔pathway 反転済み）
- `ruleProcess/`：反応ルール parser（v3 の分岐競合判定用）
- `finishedGlycogenes.xlsx`：412 glycogene 注釈（HGNC crosswalk 検証・review 11件裏取り）
- `results/supplementary/S01_data_qc/glycoenzonto_lincs_coverage.csv`：LINCS 収載フィルタ
- **帰属表示（CC-BY）必須**。引用：Groth et al., Bioinformatics 2022; 38(24):5413.

### GlycoMaple（ロジックのみ引用）
- 経路マップ本体は web 専用（GlyCosmos）で公開 API/CLI/DL は無し。**集約ロジックのみ採用**し引用する。
- 引用：Huang et al., Dev Cell 2021; 56(8):1195-1209.

## 照合済みの事実（統合の前提）

- 3rd paper の 47 エピトープ由来 **54 HGNC 遺伝子は GlycoEnzOnto 412 遺伝子に 100% 含まれる**（カバー外ゼロ）。
- 上記の代表エピトープで「遺伝子 → 反応ステップ」への分割が成立することを確認済み。
- LINCS 収載も概ね良好（例外：FUT5 未収載だが同ステップの他 FUT で代替可）。

## 検証済みの否定的結果（2026-07-25, 過剰主張しないための記録）

dryの統計優位でエピトープ/糖鎖の売りを立てようとしたが、いずれも棄却された。**dryの精度・有意性では戦えない**ことが確定。

- **疾患ごとの承認薬recovery（AUROC）**: transcriptome 0.503 / glycogene 0.452 / epitope 0.520 で全てランダム級、ep-tx差+0.03（Wilcoxon p=0.26）。「epitope逆位がtranscriptomeより高精度」は棄却（notebooks/reproduction/04）。
- **HCC↔正常(PHH)のreversalが承認薬を構造化する検定**: 全トランスクリプトーム(958)/glycogene(385)/epitope(52) いずれも perm_p=0.002 で**同じ**。→ この有意性は糖鎖固有でない。かつ承認薬は集団として正常化に偏らない（むしろ微増幅、承認vs非承認 p=0.014）。※perm検定(実δ vs ランダムδ)は空間の優劣を区別できない緩い検定だった。
- **射影の価値は統計でなく解釈可能性のみ**（どのエピトープが動いたか名前で言える／レクチン・抗体で測れる）。

→ **勝ち筋はwet validation**（例: 予測通りHepG2でcore fucoseがAAL/LCAで動く）。dryは候補生成と解釈に徹する。

## 既知の限界（論文 limitation に記載）

1. **発現 ≠ エピトープ量**：酵素の局在変化（GALA）・翻訳後制御で乖離しうる（Pearce 2018 も指摘）。
2. **辞書のステップ順は近似**：GlycoEnzOnto 経路クラスで分割するが、厳密な逐次順・分岐点は v3 の reaction rules 導入まで粗い。
3. **1エピトープ＝代表酵素の割り切り**は解消済み（スクレイパー修正で合成経路の全酵素を取得済み）。

## 次アクション

1. `glycoenzonto_pathways.json` を 3rd paper 側にコピー（帰属明記）。
2. `VW_EPITOPE_GLYCOGENE` の各エピトープ酵素を経路クラスにマップした **「epitope → step → gene」対応表**を作成。
3. LINCS 発現変化を結合し、`内max × 間min` で **薬剤 × 47エピトープ potential 行列**を算出（まず数エピトープで挙動確認）。
4. v3：reaction rules から分岐競合ペアを抽出し減点項を追加。
