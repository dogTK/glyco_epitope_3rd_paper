---
tags:
  - 概念
  - 設計
日付: 2026-08-08
---

# Glycan Translator（推論器）

## 一言でいうと

**推論器は「glycogene発現 → 糖鎖エピトープ量」の変換だけをやる。
化学摂動（薬剤）は推論器の外に置く。**

推論器から見れば入力は `signature_id` 付きの glycogene ベクトルにすぎず、
それが薬剤なのか CRISPR KO なのか疾患 RNA-seq なのかを**知らなくてよい**。

$$
f:\ \text{glycogene signature} \longrightarrow \text{glycan epitope vector}
$$

を、**Glyco DB + 文献KG**を使ってできるだけ生物学的に正しく実現することだけが仕事。

---

## 全体像

```text
              【推論器の外】

   LINCS / chemical perturbation data
                  │
                  ▼
         Glycogene signature
         (signature_id, gene, value)
                  │
══════════════════╪══════════════════
             【推論器】
                  │
        ┌─────────┴─────────┐
        │  Glycan Translator │
        │   glycogene values │
        │        +           │
        │  Glyco-related DBs │
        │        +           │
        │  Literature KG     │
        └─────────┬─────────┘
                  ▼
        Glycan epitope vector
        sLeX +1.42 / α2,6-Sia +0.82 /
        core fucose −0.41 / ...
══════════════════╪══════════════════
              【推論器の外】
                  ▼
         EPITOPE_SCORE TABLE
         ┌────────┼────────┐
         ▼        ▼        ▼
        PCA     距離計算   Ranking
```

化合物情報（perturbation / cell / dose / time）は `SIGNATURE_METADATA` に持っておき、
**推論の結果に後から JOIN する**。この分離により、推論器は「薬剤」という概念を持たずに済む。

---

## 成果物は行列そのもの

入力の glycogene 発現行列を $X$、出力を $Z$ とすると、

$$
X_{\text{signature}\times\text{glycogene}}
\ \overset{\text{Translator}}{\longrightarrow}\
Z_{\text{signature}\times\text{glycan epitope}}
$$

```text
                 sLeX   α2,6-Sia   GD2   LacNAc   CoreFuc  ...
Drug A / A549    +1.42    +0.82    -0.2    +1.12    -0.41
Drug B / A549    -1.12    +0.13    +1.3    -0.62    +0.22
Drug C / A549    +0.34    -1.72    +0.8    +0.44    -1.21
```

> 推論器そのものより、**このデータセットを作ること**が研究成果、という言い方もできる。
> ＝ **Perturbational Glycan Epitope Atlas**。
> 「どの薬剤がどの糖鎖エピトープを形成・抑制しそうか」を横断検索できる atlas。

---

## なぜ epitope 空間に移すと面白いか

glycogene 発現空間では遠い薬剤でも、glycan epitope 空間では近づきうる。

```text
Drug A → pathway A → sLeX ↑
Drug B → pathway B → sLeX ↑     ← 遺伝子では別物、糖鎖では同じ
```

つまり **「glycome に与える影響が似ている薬剤」** が近くなる空間になる。
`glycogene expression space` vs `glycan epitope space` で薬剤クラスタリングが
どう変わるかを比べること自体が図になる。

エピトープごとの drug ranking も JOIN 一発：

```sql
SELECT m.perturbation, m.cell, e.score, e.confidence
FROM GLYCAN_EPITOPE_SCORE e
JOIN SIGNATURE_METADATA m USING (signature_id)
WHERE e.epitope = 'SIALYL_LEWIS_X'
ORDER BY e.score DESC;   -- 逆順なら sLeX を下げる候補
```

---

## 推論器に入れる知識は2種類だけ

### ① Glyco-related structured DB

GlycoEnzOnto / GlyGen / GlyTouCan / GlycoEpitope など。
`gene – enzyme – reaction – substrate – product – glycan – motif – epitope – localization – dependency`
を取る。**canonical biochemical knowledge**。

### ② Literature Knowledge Graph

DB では拾えない、実験的・条件依存的な知識。

```text
MGAT5      ─ promotes →              β1,6 branching
Structure X ─ precursor_of →         sLeX
Gene A     ─ inhibits →              reaction Y
Reaction A ─ competes_with →         Reaction B
ST6GAL1 ↑  ─ experimentally_assoc. → α2,6-sialylation ↑
```

---

## 実装の2形態（どちらを採るかも比較対象になる）

```text
[LLM推論型]                      [ルールコンパイル型]
DB + KG                          DB + KG
   ↓                                ↓
LLM Reasoner ← glycogene sig       LLM
   ↓                                ↓
reasoning trace                  executable rules
   ↓                                ↓  ← glycogene sig
epitope score                    deterministic reasoner
                                    ↓
                                 epitope score
```

後者のほうが再現性は高い。**どちらを採用するか自体を研究として比較できる。**

---

## 出力テーブルは3枚に分ける

| テーブル | 中身 | 主なカラム |
|---|---|---|
| `EPITOPE_SCORE` | 最終結果 | signature_id, epitope_id, score, direction, confidence, model_version |
| `EPITOPE_CONTRIBUTION` | なぜその score なのか | signature_id, epitope_id, gene, reaction_id, contribution_score |
| `EPITOPE_EVIDENCE` | 根拠 | signature_id, epitope_id, knowledge_source, evidence_id, evidence_type, confidence |

```text
EPITOPE_CONTRIBUTION 例
SIG001 | sLeX | FUT7    | R123 | +0.82
SIG001 | sLeX | ST3GAL4 | R456 | +0.61
SIG001 | sLeX | B4GALT1 | R789 | +0.31
```

これで「sLeX score = +1.42」だけでなく **「なぜ +1.42 なのか」まで追える**。

---

## 下流でできること

`EPITOPE_SCORE` が出来た時点から先は、普通のオミクス解析になる：
PCA / UMAP / hierarchical clustering / chemical clustering / epitope clustering /
cosine similarity / target glycan への距離 / drug ranking / cell-line consistency /
dose-response / time-course / drug class enrichment / MoA enrichment。

---

## 関連

- [[エピトープ生成ロジック]] — 現行の max/min＋上流ゲート方式。Translator の中身の**現時点の実装**にあたる
- [[シグネチャー逆位法]]（捨てた枠組み）
- `docs/epitope_potential_design.md`
