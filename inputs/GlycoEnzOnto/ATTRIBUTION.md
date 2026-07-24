# GlycoEnzOnto（再配布・帰属表示）

本ディレクトリのデータは GlycoEnzOnto に由来する。**CC-BY-4.0** ライセンス（`GlycoEnzOnto_LICENSE.md`）に基づき、帰属表示のうえ再利用している。

- `glycoenzonto_pathways.json` — 経路 → 遺伝子メンバーシップ（gene↔pathway 参照用）
- `glycogenes_from_gmt.txt` — GlycoEnzOnto 収載 glycogene 一覧

**出典・引用**：
Theodore Groth, Alexander D Diehl, Rudiyanto Gunawan, Sriram Neelamegham.
"GlycoEnzOnto: A GlycoEnzyme Pathway and Molecular Function Ontology."
*Bioinformatics.* 2022 Oct 25;38(24):5413–5420. doi:10.1093/bioinformatics/btac704
GitHub: https://github.com/neel-lab/GlycoEnzOnto （CC-BY-4.0）

**用途**（本プロジェクト）：epitope potential スコアリングで、エピトープの生合成酵素を
「反応ステップ」に分割するための経路根拠として使用。詳細は `docs/epitope_potential_design.md`。

（原本一式は `../../../lincs_glyco_2nd_paper/inputs/GlycoEnzOnto/` に配置。owl・反応ルール parser 等はそちらを参照。）
