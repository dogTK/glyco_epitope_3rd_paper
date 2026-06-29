# Drug-induced rewiring of glyco-epitope potential in hepatocellular carcinoma: a transcriptome-based framework for glyco-targetability prediction

Authors: Tatsuya Koreeda^1,\*^, Hiroshi Honda^2^, Yuki Suyama^3^, Yoshihiro Yamanishi^4^

Affiliations:\
^1^ Independent Researcher, 651-2244, Kobe-shi, Hyogo, Japan\
^2^ Honda Biotech. Laboratory, Shimookamoto-cho, 329-1104, Utsunomiya-shi, Tochigi, Japan\
^3^ Zeon BioSolutions, Inc., 1-5-5 Minatojima-minamimachi, Chuo-ku, Kobe-shi, Hyogo 650-0047, Japan\
^4^ Graduate School of Informatics, Nagoya University, Chikusa, Nagoya 464-8601, Japan

\*Corresponding author: Tatsuya Koreeda, Email: ta.koreeda@gmail.com

Running head: Drug-induced glyco-epitope rewiring in HCC

## Abstract

（後で記載）

Keywords: glyco-epitope / glycosylation / hepatocellular carcinoma / drug response / lectin / glyco-targetability / LINCS L1000

---

## Introduction

細胞表面の糖鎖構造は、タンパク質・脂質に付加される翻訳後修飾の中でも特に多様性が高く、細胞間認識、シグナル伝達、免疫応答において中心的な役割を果たす[@varki_1993_glycobiology] [@varki_2017_glycobiology] [@reily_2019_natrevnephrol]。糖鎖が形成する特定の構造単位は糖鎖エピトープ（glyco-epitope）と呼ばれ、レクチン、抗体、糖鎖結合タンパク質（glycan-reader）に認識される分子インターフェースとして機能する。これらの糖鎖エピトープは、バイオマーカー検出、レクチン結合アッセイ、抗糖鎖抗体、さらには抗体医薬の標的として活用されており[@munkley_2016_oncotarget] [@narimatsu_2019_cell]、糖鎖工学・がん生物学の双方から注目を集める分子群である。

糖鎖エピトープの形成は、糖転移酵素、糖鎖分解酵素、ヌクレオチド糖代謝酵素などをコードする糖鎖関連遺伝子群（glycogene）の協調的な発現によって制御される[@he_2024_sigtransducttargetther] [@schjoldager_2020_natrevmolcellbiol]。すなわち、特定の glyco-epitope が細胞表面に提示されるかどうかは、関与する複数の glycogene が同時に適切なレベルで発現しているかどうかに依存する。このため、glyco-epitope の存在ポテンシャル（潜在的提示可能性）は、個々の酵素遺伝子の発現を読み解くというよりも、glycogene 群が形成する転写プログラムの観点から評価する必要がある。

肝細胞がん（HCC）は原発性肝臓がんの中で最も多く、世界的に重要な悪性腫瘍の一つである。HCC では糖鎖修飾異常が広く報告されており、典型的には core fucose（コアフコース）の増加、シアル化の亢進、O-GalNAc 型糖鎖の修飾変化などが観察される[@miyoshi_2008_jbiochem] [@zhang_2022_frontimmunol] [@wang_2023_oncogene]。AFP-L3（Lens culinaris agglutinin 結合型 AFP）はコアフコース化を基盤とした HCC 臨床バイオマーカーの代表例であり[@sato_2022_cancers]、STn（sialyl-Tn）や Lewis 抗原などの糖鎖エピトープも腫瘍組織での発現が報告されている[@pinho_2015_natrevcancer] [@burdick_2020_jtranslmed]。これらの事実は、HCC 細胞表面の糖鎖エピトープが診断・モニタリング・標的療法の文脈で意義を持つことを示すが、同時に、どの薬剤がどの glyco-epitope の提示ポテンシャルを変化させうるかは、体系的には理解されていない。

薬剤応答という観点から glycogene を解析した研究では、様々な化合物が HCC 細胞の glycogene 発現を大規模に変動させることが示されてきた[@angata_2020_frontoncol] [@koreeda_2024_glycoconjj] [@martinez-morales_2021_peerj]。しかしこれらの研究は主に個別遺伝子あるいは特定の機能経路に焦点を当てており、「薬剤誘導性 glycogene プログラムが、どの glyco-epitope の提示可能性をどの程度変化させるか」という glyco-epitope ポテンシャルとしての問いへの変換は行われていない。すなわち、薬剤処理によって誘導される転写変化が、細胞表面の glyco-epitope 空間にどのように対応するか、また、その結果としてレクチン・抗体・glycan-reader による検出や標的化可能性（glyco-targetability）がどのように変化するかは、未解明の問題として残っている。

この問いに答えるための基盤として、LINCS L1000 プロジェクトが提供する大規模薬剤応答トランスクリプトームデータ[@subramanian_2017_cell] [@keenan_2018_cels]と、CycleGAN による genome-wide 発現推定[@jeon_2022_bmcbioinformatics]は、glycogene 群を網羅的に解析する上で有力なリソースである。私たちはすでに、LINCS L1000 を用いた HCC 細胞における薬剤誘導性 glycogene 共発現モジュール解析（2nd paper: 投稿中）において、glycogene 応答が機能的モジュールとして組織化されることを示しており、本研究はその知見を glyco-epitope ポテンシャルという新たな軸へと拡張する。

本研究では、HCC 細胞株（HepG2）の薬剤誘導性転写プロファイルを基に、glyco-epitope の生合成に必要な glycogene 群・対応するレクチン/抗体を体系的に対応付けた glyco-targetability dictionary を構築し、各薬剤の glyco-epitope potential スコアを算出することで薬剤・MoA 横断の全体マップを構築した。さらに、特定エピトープスコアを変動させる薬剤群の MoA/ATC 富化を評価し、AFP-L3/コアフコース・STn・Lewis・galectin 軸など HCC 固有の糖鎖エピトープ文脈との接続を示す。本研究は、「薬剤が HCC 細胞の glyco-epitope 標的性・検出可能性を再配線しうる」という視点から、糖鎖バイオマーカー・レクチン検出・抗体医薬開発に資する情報基盤を提供するものである。

---

## Material and Method

（後で記載）

---

## Results

（後で記載）

---

## Discussion

（後で記載）

---

## References

（後で記載）
