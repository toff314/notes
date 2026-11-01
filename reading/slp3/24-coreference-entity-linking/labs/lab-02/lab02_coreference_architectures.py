#!/usr/bin/env python3
"""lab-02 共指模型三种架构 + 简化 e2e-coref
玩具语料复现 §24.4 的共指链。
"""
import json, math, random
from pathlib import Path

OUT = Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)

# 玩具语料：4 个共指链（her pay 是链3 单例但谓语性 NP，§24.1.3 不计为提及 → 已被 lab-01 过滤）
MENTIONS = [
    {"id": 0, "text": "Victoria Chen",  "chain": 1, "type": "name",   "gender": "F", "num": "SG", "pos": "SUBJ"},
    {"id": 1, "text": "Megabucks Banking", "chain": 2, "type": "name", "gender": "N", "num": "SG", "pos": "SUBJ"},
    {"id": 2, "text": "her",            "chain": 1, "type": "pron",   "gender": "F", "num": "SG", "pos": "POSS"},
    {"id": 3, "text": "the 38-year-old","chain": 1, "type": "defnp",  "gender": "F", "num": "SG", "pos": "SUBJ"},
    {"id": 4, "text": "the company",    "chain": 2, "type": "defnp",  "gender": "N", "num": "SG", "pos": "SUBJ"},
    {"id": 5, "text": "she",            "chain": 1, "type": "pron",   "gender": "F", "num": "SG", "pos": "SUBJ"},
    {"id": 6, "text": "Lotsabucks",     "chain": 4, "type": "name",   "gender": "N", "num": "SG", "pos": "OBJ"},
    {"id": 7, "text": "Megabucks",      "chain": 2, "type": "name",   "gender": "N", "num": "SG", "pos": "OBJ"},
]
GOLD = {0:1, 1:2, 2:1, 3:1, 4:2, 5:1, 6:4, 7:2}

# ---- 提及对架构（规则版：性别/数一致 + 近因）----
def mention_pair_resolve():
    links = {}
    for i in range(len(MENTIONS)):
        mi = MENTIONS[i]
        best_j, best_score = None, 0.55
        for j in range(i):
            mj = MENTIONS[j]
            if mi["gender"] != mj["gender"] or mi["num"] != mj["num"]:
                continue
            # 字符串包含（Megabucks ⊆ Megabucks Banking）
            contain = 1.0 if (mi["text"].lower() in mj["text"].lower() or mj["text"].lower() in mi["text"].lower()) else 0.0
            score = 0.5 + 0.25 * contain + 0.1 * (mi["type"] == mj["type"]) + 0.05 * (i - j <= 2)
            if score > best_score:
                best_score = score; best_j = j
        if best_j is not None:
            links[i] = best_j
    return links

# ---- 提及排序架构（含 ϵ）----
def mention_rank_resolve():
    links = {}
    for i in range(len(MENTIONS)):
        mi = MENTIONS[i]
        scores = []
        for j in range(i):
            mj = MENTIONS[j]
            if mi["gender"] != mj["gender"] or mi["num"] != mj["num"]:
                scores.append((j, 0.1))
            else:
                contain = 1.0 if (mi["text"].lower() in mj["text"].lower() or mj["text"].lower() in mi["text"].lower()) else 0.0
                s = 0.4 + 0.25 * contain + 0.15 * (mi["type"] == mj["type"]) + 0.1 / (i - j)
                scores.append((j, s))
        scores.append((-1, 0.45))  # ϵ：无先行语
        best_j, best_s = max(scores, key=lambda x: x[1])
        if best_j >= 0 and best_s > 0.45:
            links[i] = best_j
    return links

# ---- 基于实体（簇）架构：链接到簇 ----
def entity_based_resolve():
    clusters = []  # list of list of mention ids
    links = {}
    for i in range(len(MENTIONS)):
        mi = MENTIONS[i]
        best_c, best_s = None, 0.4
        for ci, cluster in enumerate(clusters):
            mj = MENTIONS[cluster[-1]]
            if mi["gender"] != mj["gender"] or mi["num"] != mj["num"]:
                continue
            contain = any(mi["text"].lower() in MENTIONS[c]["text"].lower() or
                          MENTIONS[c]["text"].lower() in mi["text"].lower() for c in cluster)
            same_head = any(mi["text"].lower().split()[-1] == MENTIONS[c]["text"].lower().split()[-1] for c in cluster)
            # 定指 NP → 已有簇（the company 回指 Megabucks Banking）
            definite = 1.0 if mi["type"] == "defnp" else 0.0
            # 代词 → 性别一致的最近非单例簇（显著性）
            pron = 1.0 if mi["type"] == "pron" else 0.0
            s = 0.35 + 0.3 * contain + 0.2 * same_head + 0.2 * definite + 0.25 * pron + 0.1 * (mi["type"] == mj["type"] and mi["type"] != "name") + 0.05 * len(cluster)
            if s > best_s:
                best_s = s; best_c = ci
        if best_c is None or best_s < 0.55:  # 单例：无强证据时新开链
            clusters.append([i])
        else:
            clusters[best_c].append(i)
            links[i] = clusters[best_c][0]
    return links, clusters

def links_to_chains(links):
    parent = list(range(len(MENTIONS)))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for i, j in links.items():
        parent[find(i)] = find(j)
    chains = {}
    for i in range(len(MENTIONS)):
        chains.setdefault(find(i), []).append(i)
    return list(chains.values())

def f1_clusters(pred_chains):
    """pairwise F1：标准共指评价（在共同提及对上的 P/R）"""
    def pairs(chains):
        ps = set()
        for c in chains:
            for a in range(len(c)):
                for b in range(a+1, len(c)):
                    ps.add((c[a], c[b]))
        return ps
    gold_sets = {}
    for i, c in GOLD.items():
        gold_sets.setdefault(c, []).append(i)
    gold_chains = list(gold_sets.values())
    P = pairs(pred_chains); R = pairs(gold_chains)
    tp = len(P & R)
    p = tp / len(P) if P else 0
    r = tp / len(R) if R else 0
    return 2*p*r/(p+r) if p+r else 0, p, r

results = {}
lp = mention_pair_resolve()
lr = mention_rank_resolve()
le, clusters = entity_based_resolve()

for name, links in [("mention_pair", lp), ("mention_rank", lr), ("entity_based", le)]:
    chains = links_to_chains(links)
    f1, p, r = f1_clusters(chains)
    results[name] = {"links": links, "chains": chains, "P": round(p,3), "R": round(r,3), "F1": round(f1,3)}

# ---- 简化 e2e-coref 训练（合成梯度演示）----
random.seed(42)
# 随机打分 → 用黄金链做一步"学习"演示损失下降
def random_score(i, j):
    return random.uniform(-1, 1)

losses = []
lr_e2e = 0.1
weights = {"w": random.uniform(0.5, 1.0)}
for epoch in range(20):
    total_loss = 0
    for i in range(len(MENTIONS)):
        gold_js = [j for j in range(i) if GOLD[j] == GOLD[i]]
        if not gold_js:
            continue
        # 简化：合法先行语概率 = softmax over gold ∪ {ϵ}
        scores = {j: weights["w"] * random_score(i, j) for j in gold_js}
        scores[-1] = 0.0  # ϵ
        Z = sum(math.exp(s) for s in scores.values())
        loss = -math.log(sum(math.exp(s) for j, s in scores.items() if j != -1) / Z)
        total_loss += loss
        # 梯度步（演示）
        weights["w"] -= lr_e2e * (loss - 0.5) * 0.01
    losses.append(round(total_loss / len(MENTIONS), 4))

results["e2e_coref_loss_curve"] = losses
results["e2e_final_loss"] = losses[-1]

(OUT / "compare_architectures.json").write_text(json.dumps(results, ensure_ascii=False, indent=2))
(OUT / "e2e_coref_loss.csv").write_text("epoch,loss\n" + "\n".join(f"{e},{l}" for e, l in enumerate(losses)))

print("=== 三种架构对比 ===")
for name in ("mention_pair", "mention_rank", "entity_based"):
    r = results[name]
    print(f"{name}: P={r['P']} R={r['R']} F1={r['F1']} chains={r['chains']}")
print(f"\ne2e-coref loss curve (first 5): {losses[:5]}")
print(f"final loss: {losses[-1]}")
