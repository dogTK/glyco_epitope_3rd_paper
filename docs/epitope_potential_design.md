# epitope potential スコアリング設計

薬剤誘導トランスクリプトームから **glyco-epitope potential**（各エピトープが薬剤でどれだけ増減しうるか）を
推定する計算の設計書。3rd paper の中核（Fig3 heatmap）にあたる。

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

## 既知の限界（論文 limitation に記載）

1. **発現 ≠ エピトープ量**：酵素の局在変化（GALA）・翻訳後制御で乖離しうる（Pearce 2018 も指摘）。
2. **辞書のステップ順は近似**：GlycoEnzOnto 経路クラスで分割するが、厳密な逐次順・分岐点は v3 の reaction rules 導入まで粗い。
3. **1エピトープ＝代表酵素の割り切り**は解消済み（スクレイパー修正で合成経路の全酵素を取得済み）。

## 次アクション

1. `glycoenzonto_pathways.json` を 3rd paper 側にコピー（帰属明記）。
2. `VW_EPITOPE_GLYCOGENE` の各エピトープ酵素を経路クラスにマップした **「epitope → step → gene」対応表**を作成。
3. LINCS 発現変化を結合し、`内max × 間min` で **薬剤 × 47エピトープ potential 行列**を算出（まず数エピトープで挙動確認）。
4. v3：reaction rules から分岐競合ペアを抽出し減点項を追加。
