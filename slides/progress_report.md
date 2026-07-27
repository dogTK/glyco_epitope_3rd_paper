---
marp: true
theme: uncover
paginate: true
size: 16:9
footer: 'Glyco-epitope Rewiring in HCC'
style: |
  @import "./tailwind.build.css";

  :root {
    --bg: #FAF8F4;
    --ink: #1C1C1A;
    --sub: #6B6A63;
    --accent: #2E5E56;
    --accent-soft: rgba(46, 94, 86, 0.08);
    --rule: #DEDAD0;
  }

  section {
    background: var(--bg);
    color: var(--ink);
    font-family: "Hiragino Sans", "Hiragino Kaku Gothic ProN", -apple-system, sans-serif;
    font-size: 25px;
    line-height: 1.65;
    text-align: left;
    justify-content: flex-start;
    padding: 56px 72px;
  }

  section::after {
    color: var(--sub);
    font-size: 13px;
  }

  footer {
    color: var(--sub);
    font-size: 13px;
    letter-spacing: 0.04em;
  }

  h1, h2 {
    font-family: "Hiragino Mincho ProN", "Yu Mincho", serif;
    color: var(--ink);
    font-weight: 600;
    text-align: left;
    margin: 0 0 0.3em 0;
  }

  h2 {
    font-size: 32px;
  }

  .kicker {
    font-family: "Hiragino Sans", sans-serif;
    font-size: 14px;
    font-weight: 600;
    letter-spacing: 0.18em;
    color: var(--accent);
    margin-bottom: 10px;
  }

  section.lead {
    justify-content: center;
    padding: 0 100px;
  }
  section.lead h1 {
    font-size: 46px;
    line-height: 1.4;
    border-bottom: 1px solid var(--rule);
    padding-bottom: 28px;
    margin-bottom: 28px;
  }
  section.lead .byline {
    font-family: "Hiragino Sans", sans-serif;
    font-size: 16px;
    color: var(--sub);
    letter-spacing: 0.06em;
  }

  section.section {
    justify-content: center;
    padding: 0 100px;
  }
  section.section .num {
    font-family: "Hiragino Mincho ProN", serif;
    font-size: 20px;
    color: var(--accent);
    letter-spacing: 0.1em;
    margin-bottom: 6px;
  }
  section.section h1 {
    font-size: 54px;
    border: none;
    margin: 0;
  }

  p { margin: 0.5em 0; }
  p strong {
    font-weight: 600;
  }
  ul {
    margin: 0.2em 0 0.9em 0;
    padding-left: 1.1em;
  }
  li {
    margin: 0.15em 0;
    font-size: 22px;
  }
  li::marker {
    color: var(--accent);
  }

  .caption {
    font-size: 15px;
    color: var(--sub);
    margin-top: 10px;
  }

  .placeholder {
    border: 1px dashed var(--rule);
    border-radius: 6px;
    color: var(--sub);
    font-size: 15px;
    text-align: center;
    padding: 36px 20px;
    margin: 12px 0;
  }

  .flow {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 0;
    margin: 10px 0 12px 0;
  }
  .flow .step {
    border-left: 3px solid var(--accent);
    background: var(--accent-soft);
    padding: 6px 16px;
    border-radius: 0 6px 6px 0;
    width: 92%;
    line-height: 1.35;
  }
  .flow .step .t {
    font-size: 19px;
    font-weight: 600;
  }
  .flow .step .s {
    font-size: 13px;
    color: var(--sub);
  }
  .flow .arrow {
    color: var(--accent);
    font-size: 13px;
    padding-left: 22px;
    opacity: 0.7;
    line-height: 1.2;
  }

  .notes {
    margin-top: 10px;
    font-size: 15px;
    color: var(--sub);
  }
  .notes b {
    color: var(--ink);
    font-weight: 600;
  }
---

<!-- _class: lead -->

# Drug-induced Rewiring of Glyco-epitope Potential in Hepatocellular Carcinoma

<span class="byline">Tatsuya Koreeda ・ 2026-06-29</span>

---

<!-- _class: section -->

<div class="num">01</div>

# Background

---

<div class="kicker">BACKGROUND</div>

## なぜ Glyco-epitope × HCC か

**糖鎖エピトープ（glyco-epitope）は細胞表面の分子インターフェース**
- レクチン・抗体・glycan-reader に認識される標的
- バイオマーカー・抗体医薬として臨床応用あり

**HCC では糖鎖修飾異常が広く観察される**
- Core fucose 増加（AFP-L3 が代表的バイオマーカー）
- STn、Lewis 抗原など複数の glyco-epitope が腫瘍で発現

**未解決の問い：どの薬剤がどの glyco-epitope を変化させるか？**
- 体系的な理解がない → 本研究で解決する

---

<div class="kicker">BACKGROUND</div>

## 糖鎖修飾のタイプと glyco-epitope

![w:700](assets/he2024_glycosylation_types.jpg)

<div class="caption">図: He et al., Signal Transduct Target Ther 2024 (CC BY 4.0)</div>

---

<div class="kicker">RESEARCH CONCEPT</div>

## 研究の枠組み

<div class="grid grid-cols-5 gap-6">
<div class="col-span-3">

<div class="flow">
  <div class="step"><div class="t">Drug-induced transcriptome</div><div class="s">LINCS L1000 + CycleGAN</div></div>
  <div class="arrow">↓</div>
  <div class="step"><div class="t">Glycogene program</div><div class="s">各薬剤の glycogene 発現プロファイル</div></div>
  <div class="arrow">↓</div>
  <div class="step"><div class="t">Glyco-epitope potential</div><div class="s">glyco-targetability score 算出</div></div>
  <div class="arrow">↓</div>
  <div class="step"><div class="t">Lectin / antibody / biomarker / glycan-reader</div><div class="s">との接続</div></div>
  <div class="arrow">↓</div>
  <div class="step"><div class="t">Glyco-targetability マップ</div><div class="s">HCC 文脈</div></div>
</div>

<div class="notes">
<b>データ：</b>HepG2 細胞株 × LINCS L1000 薬剤応答
<b>先行：</b>2nd paper の glycogene 機能モジュールを活用
</div>

</div>
<div class="col-span-2">

![w:400](assets/jeon2022_cyclegan.jpg)

<div class="caption">L1000 ⇄ RNA-seq 変換（CycleGAN）<br>図: Jeon et al., BMC Bioinformatics 2022 (CC BY 4.0)</div>

</div>
</div>
