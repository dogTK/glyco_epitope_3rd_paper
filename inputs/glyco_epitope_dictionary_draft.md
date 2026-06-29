# Glyco-Epitope Dictionary（Fig 2 素案）

6エージェント並列調査による整理（2026-06-29）

---

## サマリーテーブル

| エピトープ | 主要合成glycogene | HCC証拠 | 検出手段 | 薬剤変動 |
|-----------|----------------|---------|---------|---------|
| **Core fucose** | FUT8, GMDS, SLC35C1 | AFP-L3（FDA承認）、FUT8高発現 | LCA, AAL | Sorafenib（間接）、2-Fluorofucose |
| **Sialyl-Lewis** | ST3GAL3/4/6, FUT3, FUT7 | sLeX↑→転移・セレクチン結合、予後不良 | CSLEX1, MAA | HDACi（FUT3/6変動）、2F-Fuc |
| **Tn / STn** | GALNT family, COSMC, C1GALT1, ST6GALNAC1 | TACA、COSMC低下→Tn蓄積 | VVA（Tn）、B72.3/CC49（STn） | 5-aza（DNMTi）、HDACi |
| **Poly-LacNAc** | B3GNT2, B3GNT8, B3GNT3, B4GALT1 | B3GNT8→CD147転移促進、Galectin-3予後マーカー | Galectin-1/3/9, LEL | ATRA（HCC直接証拠あり） |
| **High mannose** | MGAT1, MAN1A1/B1, MAN2A1/2, EDEM1-3 | Haptoglobin糖ペプチド AUC 93%（AFP超え） | ConA, GNA, HHL | Swainsonine, Tunicamycin |
| **Gangliosides** | ST3GAL5, ST8SIA1, B4GALNT1 | GD3正常比4倍↑、B4GALNT1→GD2→免疫抑制 | Dinutuximab（抗GD2）, R24 | PDMP（HepG2直接確認） |

---

## 各エピトープ詳細

### Core fucose (Fucα1-6GlcNAc)

**生合成glycogene**
- FUT8 — α1,6-フコシルトランスフェラーゼ、core fucose付加の唯一の酵素
- GMDS, TSTA3 — de novo GDP-fucose合成経路
- FUK, FPGT — サルベージ経路
- SLC35C1 — GDP-fucoseゴルジ輸送担体

**HCC証拠**
- AFP-L3（LCA-reactive core fucosylated AFP）：FDA承認HCC診断バイオマーカー
- FUT8はHCC組織で正常肝より高発現（複数コホート）
- 血清core fucosylated glycoproteins（AGP, haptoglobin, transferrin）がHCCで増加
- FUT8過剰発現→HCC増殖・浸潤促進（EGFRシグナル修飾）

**検出**
- LCA（Lens culinaris agglutinin）：AFP-L3標準検出レクチン
- AAL（Aleuria aurantia lectin）：broad fucose検出、flow/IF利用可

**薬剤変動**
- 2-Fluorofucose（2FF）：GDP-fucose競合阻害剤
- Sorafenib：FUT8/core fucosylation変動報告あり（間接的）
- mTOR阻害薬：糖ヌクレオチド代謝経由でfucosylation低下

---

### Sialyl-Lewis (sLeX / sLeA)

**生合成glycogene**
- ST3GAL3, ST3GAL4, ST3GAL6 — α2-3 SA付加（sLeX合成に必須）
- FUT3（sLeA主担当）、FUT7（sLeX主担当）、FUT4, FUT5, FUT6
- B4GALT1, B3GNT — type 2 LacNAc scaffold提供

**HCC証拠**
- sLeX発現はHCCで正常肝比較して有意に上昇；門脈浸潤・転移と正相関
- E/P-セレクチン結合→血管内皮接着→血行性転移促進
- 高sLeX発現HCCは予後不良（複数コホート）

**検出**
- CSLEX1（BD）、KM93：抗sLeX抗体（IHC/flow/ELISA）
- CA19-9（116-NS-19-9）：抗sLeA（血清ELISA）
- MAA（Maackia amurensis）：α2-3 SA検出レクチン

**薬剤変動**
- 2F-Fuc、P-F-Fuc：FUT活性競合阻害→sLeX低下→セレクチン結合抑制
- Peracetylated 3Fax-Neu5Ac：ST3GAL阻害→sLeX低下
- HDAC阻害剤：FUT3/FUT6発現変化を誘導

---

### Tn / STn (GalNAcα-O-Ser/Thr / NeuAcα2-6GalNAcα-O-Ser/Thr)

**生合成glycogene**
- GALNT family（GALNT1〜20）：O-GalNAc付加の開始酵素
- COSMC（C1GALT1C1）：T合成酵素のシャペロン。変異/メチル化→Tn/STn蓄積
- C1GALT1（T-synthase）：Tn→Core 1延長。低下=Tn蓄積
- ST6GALNAC1：GalNAcをシアル化→STn生成。HCCで発現亢進

**HCC証拠**
- 正常肝で低発現、HCCで上昇（TACA文脈で腫瘍特異的）
- STnはHCC細胞株（HepG2, Hep3B）で検出、tumor invasiveness・免疫回避と関連
- COSMC低発現/メチル化→Tn蓄積→HCC悪性化と相関

**検出**
- Tn抗体：9A7, 5F4, MLS128；CAR-T/ADC開発で利用
- STn抗体：B72.3, CC49, 3F1；腫瘍診断・免疫療法で実績
- レクチン：VVA（Tn）、MAA/SNA（STn補完）

**薬剤変動**
- 5-azacytidine（DNMTi）：COSMCメチル化解除→C1GALT1回復→Tn減少
- HDACi（vorinostat等）：ムチン関連遺伝子の転写制御→O-糖鎖プロファイル変化

---

### Poly-LacNAc ((GlcNAcβ1-3Galβ1-4)n)

**生合成glycogene**
- B3GNT2：HCC細胞株H7721で直接確認済み。EGF→EGFR→B3GNT2↑→poly-LacNAc↑
- B3GNT8：HCCで高発現。CD147のN-glycan修飾→転移促進（c-Jun依存的）
- B3GNT3：PD-L1のpoly-LacNAc化（N192, N200位）を触媒→免疫回避の鍵
- B4GALT1：LacNAc単位を完成。B3GNT2と交互作用でpoly-LacNAc鎖伸長
- GCNT2：Linear→I-抗原型へ分岐化、galectin-9結合に影響

**HCC証拠**
- B3GNT8がHCC組織で高発現→CD147修飾→転移促進
- Galectin-3がHCCで過剰発現→進行度・予後不良と相関
- EGFR、CD147上のpoly-LacNAcがキャリア蛋白シグナル・浸潤と接続

**検出**
- Galectin-1, -3（HCC高発現reader）、Galectin-9（免疫チェックポイント）
- LEL（Lycopersicon esculentum lectin）、STL（Solanum tuberosum lectin）

**薬剤変動**
- ATRA：HCC H7721でB3GNT2↓→poly-LacNAc減少（HCC直接エビデンス）
- 2-deoxyglucose：PD-L1グリコシル化阻害→T細胞毒性感受性増加
- EGFR阻害剤：EGF/EGFR→B3GNT2軸の遮断（間接的）

---

### High mannose (Man5-9GlcNAc2)

**生合成glycogene**
- ALG genes（ALG1〜14）：ドリコール経路でMan5GlcNAc2前駆体を合成
- MGAT1（GnT-I）：複合型への分岐点。低発現/阻害→高マンノース蓄積
- MAN1A1, MAN1A2, MAN1B1：ER/Golgi α-マンノシダーゼI群
- MAN2A1, MAN2A2：Golgi α-マンノシダーゼII群。阻害（swainsonine）でMan5-6蓄積
- EDEM1/2/3：UPR亢進時に発現上昇、品質管理（ERAD）

**HCC証拠**
- Haptoglobin上の高マンノース糖ペプチドがAUC 80〜93%でAFP超え（早期HCC診断）
- 肝硬変→早期→後期HCCにかけて高マンノース型が段階的増加
- HBV感染・HCCでUPR常態的亢進→processing酵素活性低下→高マンノース蓄積

**検出**
- ConA（α-マンノース全般）：lectin affinity chromatography / flow
- GNA（Galanthus nivalis agglutinin）：Man-α1→3末端特異的
- HHL（Hippeastrum hybrid lectin）：高マンノース型に強親和性

**薬剤変動**
- Swainsonine（α-mannosidase II阻害剤）：Man5-6蓄積誘導
- Tunicamycin（N-glycosylation阻害剤）：N-グリコシル化全体阻害→ER stress
- mTOR/HSP90阻害薬：MAN2A1/MGAT1発現低下→高マンノース傾向

---

### Gangliosides (GM3, GD2, GD3, GM2...)

**生合成glycogene**
- ST3GAL5（GM3 synthase）：ganglioside合成経路の入口
- ST8SIA1（GD3 synthase）：GM3→GD3変換。HCCで活性上昇
- B4GALNT1（GM2/GD2 synthase）：GM3→GM2、GD3→GD2。HCCで高発現→EMT促進・免疫抑制

**HCC証拠**
- GD3：正常肝比約4倍上昇（早期マーカー候補）
- B4GALNT1高発現→GD2/GM2増加→HCC進行（HES4-SPP1-TAM/Th2 axis）
- ST8SIA1 + B4GALNT1の2遺伝子シグネチャーでGD2陽性表現型を予測可能

**検出**
- Dinutuximab（ch14.18）：FDA承認抗GD2抗体、HCCへの臨床試験進行中
- R24：抗GD3 mAb
- TLC-immunostaining：腫瘍組織gangliosideプロファイル同定

**薬剤変動**
- PDMP（glucosylceramide synthase阻害剤）：HepG2でGM3↓、増殖・スフィア形成抑制（直接確認）
- D-EtDO-P4：GM3低下、Akt1リン酸化増強（HepG2）

---

## 論文接続メモ

- **B3GNT3 → PD-L1グリコシル化**：Poly-LacNAcが免疫チェックポイントに直結。薬剤でB3GNT3を変動させることがPD-L1表面提示に影響する可能性。
- **High mannose haptoglobin**：AFP-L3の対抗バイオマーカーとして位置づけ可能。
- **ATRA → B3GNT2↓**：HCC直接証拠のある薬剤-glycogene-エピトープ軸として論文に組み込める。
- **Wet validation優先候補**：Core fucose（AAL/LCA）、Gangliosides（抗GD2）がFDA承認試薬あり。
