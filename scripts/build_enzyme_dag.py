"""GlycoEnzOnto の反応ルール（Reactant → Product）から酵素の前後関係DAGを組む。

辞書は「決定基を作る最終反応の酵素」しか持っていない（GD2 → B4GALNT1 のみ）。
上流を機械的に辿れるようにするため、
  酵素A → 酵素B のエッジを「Aの生成物の中にBの基質パターンが現れる」で定義する。
糖鎖表記は非還元末端が左・還元末端が右なので、Bの基質パターンがAの生成物の
部分文字列として現れれば、BはAの生成物に働ける。
"""
import re, pandas as pd
from collections import defaultdict, deque

GEO = "/Users/koreedatatsuya/research/lincs_glyco_2nd_paper/inputs/GlycoEnzOnto/"
rules = pd.read_csv(GEO + "finishedGlycogenes.tsv", sep="\t")
rules = rules[rules.Rules.notna() & (rules.Rules != "no reaction")]


def norm(s):
    """空白除去・不確定リンケージ `?` を X に統一。"""
    s = re.sub(r"\s+", "", str(s))
    return s.replace("-?)", "-X)")


def to_regex(pattern):
    """基質パターンを正規表現に変換。

    - `...` / `<...>` は任意の並び
    - リンケージ位置は X（不定）なら何にでも、数字なら自身か X に一致
    """
    p = norm(pattern)
    p = p.replace("<...>", "\x01").replace("...", "\x01")
    out = []
    for ch in re.escape(p):
        out.append(ch)
    r = "".join(out).replace(re.escape("\x01"), ".*")
    # リンケージ数字/X を緩める: -3) → -[3X]) 、-X) → -[0-9X])
    r = re.sub(r"\\-X\\\)", r"\\-[0-9X]\\)", r)
    r = re.sub(r"\\-(\d)\\\)", r"\\-[\1X]\\)", r)
    return r


def alts(field):
    return [a for a in norm(field).split("|") if a and a.lower() != "nan"]


react, prod = {}, {}
for _, r in rules.iterrows():
    g = r.geneName
    react.setdefault(g, []).extend(alts(r.Reactant))
    prod.setdefault(g, []).extend(alts(r.Product))

genes = sorted(set(react) & set(prod))
print(f"ルールを持つ酵素: {len(genes)}")

# --- DAG: A -> B （Aの生成物に Bの基質が現れる） ---
rx = {g: [re.compile(to_regex(p)) for p in react[g]] for g in genes}
up = defaultdict(set)     # B の上流 = {A}
for a in genes:
    pa = prod[a]
    for b in genes:
        if a == b:
            continue
        if any(r.search(p) for r in rx[b] for p in pa):
            up[b].add(a)

print(f"エッジ数: {sum(len(v) for v in up.values()):,}")

# --- 検証：GD2 の既知の合成経路をたどれるか ---
print("\n=== 検証: B4GALNT1(GD2の末端酵素) の上流を辿る ===")
CHAIN = ["UGCG", "B4GALT6", "ST3GAL5", "ST8SIA1"]
seen, order = {"B4GALNT1": 0}, deque([("B4GALNT1", 0)])
while order:
    g, d = order.popleft()
    if d >= 4:
        continue
    for a in up.get(g, ()):
        if a not in seen:
            seen[a] = d + 1
            order.append((a, d + 1))
for c in CHAIN:
    print(f"  {c:10s} {'到達 (深さ ' + str(seen[c]) + ')' if c in seen else '未到達'}")
print(f"  深さ4以内の上流酵素 計 {len(seen)-1}")
print("  深さ1:", sorted(g for g, d in seen.items() if d == 1))

pd.DataFrame([(b, a) for b, v in up.items() for a in v],
             columns=["GENE", "UPSTREAM_GENE"]).to_csv(
    "/Users/koreedatatsuya/research/glyco_epitope_3rd_paper/data/processed/"
    "glycoenzonto_enzyme_dag.csv", index=False)
print("\n保存: data/processed/glycoenzonto_enzyme_dag.csv")
