# キュレーション補完エピトープの論拠（manuscript用）

glyco-epitope 辞書（`RAW.GLYCOEPITOPE`）は GlycoEpitope DB (glycoepitope.jp) 由来だが、
**がん/HCC糖鎖生物学で中核的ないくつかの構造がDBに収載されていない**。
本ドキュメントは、それらを手動キュレーションで辞書に加える**科学的根拠と選定基準**を整理する（論文Methods/Discussion素材）。

---

## 1. なぜ補完が必要か（データソースの構造的な穴）

GlycoEpitope DB は主に **「名前の付いた終末糖鎖決定基」**（Lewis抗原・ガングリオシド・グロボシド・血液型など、
特異的な抗体/レクチンで認識される終端構造）を収載する。一方で、

> **単一の分岐/修飾糖転移酵素が糖鎖コアに作用して生じる「構造クラス」エピトープ**

——core fucosylation、bisecting GlcNAc、β1,6分岐など——は、終末決定基として命名されないため
**DBに独立エントリを持たない**。しかしこれらは

1. がん・HCC糖鎖の中核（バイオマーカー・転移・悪性度に直結）、
2. **確立したレクチン/抗体で検出可能**、
3. **単一遺伝子にクリーンに対応**（＝薬剤誘導potentialのスコアリングにむしろ最適）、

という理由から、辞書に含めるべきである。この「穴」は網羅範囲の問題ではなく、
**元DBのエピトープ定義（終末決定基中心）に由来する系統的なもの**であり、
補完はアドホックな追加ではなく方法論的に正当化される。

## 2. 選定基準（inclusion criteria）

エピトープを手動追加するのは、以下を**すべて**満たす場合に限る:

- **(C1) 検出可能性**: 確立したレクチンまたは抗体で検出できる糖鎖決定基である。
- **(C2) 遺伝子ハンドル**: 定義となる生合成/修飾酵素が明確で、可能なら単一遺伝子。かつ
  **LINCS glycogene パネル（`GLYCO_GENES_WIDE`）に存在**する（＝薬剤応答に連結できる）。
- **(C3) 文脈適合**: HCC glyco-targetability の論旨（Fig5の core fucose / TACA / selectin / galectin軸）に直接資する。

推測で遺伝子を割り当てない方針（辞書本体の review 運用）と一貫させ、
遺伝子ハンドルが一意でないものは **`CONFIDENCE` を下げ、要議論フラグを明示**して収載する。

## 3. 補完エピトープ一覧と個別根拠

全候補遺伝子は `GLYCO_GENES_WIDE` に存在することを確認済み（C2充足）。

| エピトープ | 遺伝子 | 構造 | 検出試薬 | HCC/がんでの意義 | 確信度 |
|-----------|--------|------|---------|-----------------|--------|
| Core fucose | **FUT8** | N型コアの α1,6-Fuc | AAL, LCA | **AFP-L3**（承認HCCバイオマーカー）の実体 | high（単一遺伝子） |
| Bisecting GlcNAc | **MGAT3** | コアManへの β1,4-GlcNAc（bisect） | E4-PHA | 悪性度/転移の制御。MGAT5と拮抗 | high（単一遺伝子） |
| β1,6分岐 (tri/tetra-antennary) | **MGAT5** | β1,6-GlcNAc分岐→poly-LacNAc足場 | L-PHA | がん転移マーカー。galectin軸の起点 | high（単一遺伝子） |
| poly-LacNAc / i抗原 | **B3GNT2** (+B4GALT1) | 直鎖 [-3Galβ1-4GlcNAc-]n | galectin-3, LEL | galectin-3リガンド本体（Fig5 galectin軸） | medium（複数遺伝子/下流依存） |
| Tn抗原 | **C1GALT1C1(COSMC)** / GALNT | GalNAcα-O-Ser/Thr（未伸長） | VVA, anti-Tn | 汎がんTACA。STn/T抗原の上流 | low（遺伝子ハンドル要議論） |

### 3.1 Core fucose — FUT8（最優先）
FUT8 は N型糖鎖コア最内 GlcNAc への α1,6-フコース転移を担う**唯一の酵素**。
その産物である core-fucosylated AFP が **AFP-L3**（Lens culinaris agglutinin 反応性AFP）であり、
HCC と良性肝疾患を鑑別する**臨床承認バイオマーカー**。本研究の wet validation（HepG2 + AAL/LCA）の中心。
単一遺伝子=1スコアで potential 化でき、HCC論旨の要。
- 引用が必要: FUT8酵素機能、AFP-L3のHCC鑑別能。

### 3.2 Bisecting GlcNAc — MGAT3 (GnT-III)
MGAT3 はコアβ-Man に bisecting β1,4-GlcNAc を付加。これは以降のプロセシング（MGAT5分岐を含む）を
**遮断**し、E-cadherin・増殖因子受容体の機能を修飾する。肝がんでは分化/悪性度マーカーとして
古くから研究され、**MGAT5と生合成的に拮抗**するため対の指標として有用。検出は E4-PHA。
- 引用が必要: GnT-IIIによるbisect形成とMGAT5拮抗、HCCでの意義。

### 3.3 β1,6分岐 — MGAT5 (GnT-V)
MGAT5 は β1,6-GlcNAc 分岐を形成し、これが poly-LacNAc で伸長されて **galectin-3 の優先リガンド**となる。
腫瘍浸潤・転移との関連が確立。**drug→glycogene→epitope 連鎖を Fig5 の galectin/poly-LacNAc 軸へ橋渡し**する
結節点。検出は L-PHA。
- 引用が必要: GnT-V/β1,6分岐と転移、galectin-3リガンド化。

### 3.4 poly-LacNAc / i抗原 — B3GNT2 (+B4GALT1)
直鎖 poly-LacNAc は B3GNT2（GlcNAc付加）と B4GALT1（Gal付加）の交互伸長で作られ、
galectin ファミリーの主要リガンド骨格。Fig5 galectin軸の**実体**だが、
(a) 2遺伝子が関与し、(b) MGAT5分岐の下流でもあるため、
単一酵素エピトープほどクリーンでない → `CONFIDENCE=medium`、代表遺伝子は B3GNT2 とし注記。
- 引用が必要: poly-LacNAc生合成、galectin-3結合。

### 3.5 Tn抗原 — 遺伝子ハンドル要議論
Tn（GalNAcα-O-Ser/Thr）は汎がんTACA。生合成上は GALNT ファミリー（〜20遺伝子）による
O-GalNAc 開始で生じるが、**病的な蓄積は多くの場合 COSMC (C1GALT1C1) シャペロン機能低下による
コア1伸長の停止**として説明される。したがって
- 「Tnの存在」= GALNT開始、
- 「Tnの蓄積」= C1GALT1/COSMC 低下、

と**モデリング上の選択**が入る。辞書には代表ハンドルとして C1GALT1C1 を low 確信で置き、
論文では**この曖昧性を明記**する（唯一の生合成的事実ではなく解析上の割り切り）。
- 引用が必要: TnとCOSMC/C1GALT1、汎がんTACAとしての位置づけ。

## 4. 論文に明記すべき区別（誠実性）

辞書エントリは2種に分かれることをMethodsで明示する:

1. **catalog epitopes**（GlycoEpitope DB由来）: 終末決定基。多くは複数酵素の生合成経路を持つ。
2. **curated structure-class epitopes**（本補完）: 単一の分岐/修飾酵素で定義。
   `SOURCE='manual_curation'` でフラグし、`CONFIDENCE` を付す。

特に **poly-LacNAc・Tn の遺伝子割当は一意な生合成事実ではなくモデリング選択**である点を
limitation として述べる。core fucose/bisecting/β1,6分岐は単一遺伝子で曖昧性が小さい。

## 5b. 実装状況（2026-07-24）

Tier1（FUT8/MGAT3/MGAT5）を `RAW.GLYCOEPITOPE` に手動キュレーションでロード済み：
- `EPITOPES` に MAN0001=Core Fucose(FUT8/AFP-L3), MAN0002=Bisecting GlcNAc(MGAT3), MAN0003=β1,6分岐(MGAT5)
- `EPITOPE_ENZYME` に `SOURCE='manual_curation'`（EC/CAZy付与）、crosswalk ALIASにHGNC自己マップ追加
- crosswalk/VIEW/EPITOPE_STEP_GENE 再構築済み → 辞書は 52エピトープ/57遺伝子
- 解析: `notebooks/analytics/02_hcc_core_fucose.ipynb`（HepG2で承認薬の上げ下げ）
- Tier2（poly-LacNAc/Tn）は未実装（要議論フラグのまま保留）。

## 5. 実装方針（次アクション）

- `RAW.GLYCOEPITOPE.EPITOPE_ENZYME` に手動行を追加（`SOURCE='manual_curation'`, `ENZYME_ROLE='biosynthetic'`,
  EC/CAZy は既知値、`EPITOPE_ID` は `MANUAL_xxx` 等で衝突回避）。
- クロスウォーク・ビューは既存ロジックで自動的に乗る（HGNCは追加行に直接付与 or ALIAS拡張）。
- Tier1（FUT8/MGAT3/MGAT5）を先行、Tier2（B3GNT2/C1GALT1C1）は要議論フラグ付きで追加。

## 6. 引用が必要な主張（TODO: 正式文献を挿入）

- [ ] FUT8のcore fucosylation機能 / AFP-L3のHCCバイオマーカー承認・鑑別能
- [ ] MGAT3(GnT-III)のbisect形成・MGAT5拮抗・HCCでの役割
- [ ] MGAT5(GnT-V)のβ1,6分岐・転移・galectin-3リガンド化
- [ ] poly-LacNAc生合成(B3GNT2/B4GALT1)とgalectin-3結合
- [ ] Tn抗原とCOSMC(C1GALT1C1)・汎がんTACA
- [ ] 各レクチンの特異性（AAL/LCA=core fuc, E4-PHA=bisect, L-PHA=β1,6分岐, VVA=Tn, LEL=poly-LacNAc）
