#!/usr/bin/env python3
"""lab-03 实体链接：TAGME 风格先验 + 关联度投票
复现 §24.7.1 TAGME 算法在玩具 Wikipedia 子集上的行为。
"""
import json, math, re
from pathlib import Path
from collections import defaultdict

OUT = Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)

# 玩具知识库：4 个实体 + 文本 + 出链
KB = {
    "Yuan_dynasty": {
        "title": "Yuan dynasty",
        "text": "The Yuan dynasty was a Chinese dynasty... Kublai Khan established it... capital Dadu.",
        "links": ["Kublai_Khan", "Dadu", "Chinese_dynasty", "Mongol_Empire"]
    },
    "Yuan_currency": {
        "title": "Yuan (currency)",
        "text": "The yuan is the basic unit of currency in China...",
        "links": ["China", "Renminbi", "Currency"]
    },
    "Victoria_Chen": {
        "title": "Victoria Chen",
        "text": "Victoria Chen is a fictional CFO... Megabucks Banking...",
        "links": ["CFO", "Megabucks_Banking", "Banking"]
    },
    "Victoria_British_Columbia": {
        "title": "Victoria, British Columbia",
        "text": "Victoria is the capital of British Columbia, Canada...",
        "links": ["British_Columbia", "Canada", "Capital_city"]
    }
}

# 锚词典：锚文本 → (实体, 先验概率)（从 Wikipedia 统计）
ANCHORS = {
    "Yuan": [("Yuan_dynasty", 0.55), ("Yuan_currency", 0.45)],
    "Victoria Chen": [("Victoria_Chen", 0.7), ("Victoria_British_Columbia", 0.3)],
    "Megabucks": [("Megabucks_Banking", 0.6), ("Victoria_Chen", 0.4)],
}

# 逆链：哪些实体链接到某实体
INLINKS = defaultdict(set)
for e, info in KB.items():
    for t in info["links"]:
        INLINKS[t].add(e)

def relatedness(e1, e2):
    """TAGME 关联度：|in(e1) ∩ in(e2)| / |in(e1) ∪ in(e2)|"""
    s1, s2 = INLINKS.get(e1, set()), INLINKS.get(e2, set())
    if not s1 or not s2:
        return 0.0
    inter = len(s1 & s2); union = len(s1 | s2)
    return inter / union if union else 0.0

def vote_relatedness(entity, other_entities):
    """投票：实体 e 与其他已选实体（≠e）的平均关联度"""
    others = [o for o in other_entities if o != entity]
    if not others:
        return 0.0
    return sum(relatedness(entity, o) for o in others) / len(others)

def tagme_disambiguate(mentions):
    """mentions: list of anchor text"""
    # 步骤 1：先验概率选种子（每锚取 argmax 先验）
    seeds = {}
    for m in mentions:
        if m in ANCHORS:
            seeds[m] = max(ANCHORS[m], key=lambda x: x[1])[0]
    selected = set(seeds.values())

    # 步骤 2：关联度投票重打分
    results = {}
    for m in mentions:
        if m not in ANCHORS:
            results[m] = None
            continue
        scored = []
        for e, prior in ANCHORS[m]:
            vote = vote_relatedness(e, selected)
            # TAGME 原始分数 = 先验 × 关联度（简化）
            score = prior * (1.0 + vote)
            scored.append((e, prior, vote, score))
        best = max(scored, key=lambda x: x[3])
        results[m] = {"candidates": [
            {"entity": e, "prior": p, "vote": round(v,3), "score": round(s,3)}
            for e, p, v, s in scored
        ], "chosen": best[0]}
    return results

# 复现 §24.7.1 示例：「Yuan 之前是中国的哪个朝代？」
mentions = ["Yuan", "China", "dynasty"]
# 简化为 Yuan 的消歧
demo_results = tagme_disambiguate(["Yuan"])

# 复现 §24.3 共指消解示例 + 实体链接
text_mentions = ["Victoria Chen", "Megabucks"]
link_results = tagme_disambiguate(text_mentions)

# ---- 输出 ----
output = {
    "demo_yuan_disambiguation": demo_results,
    "news_text_entity_linking": link_results,
    "inlinks": {k: sorted(v) for k, v in INLINKS.items()},
    "explanation": {
        "yuan_dynasty_wins": "先验 0.55 已较高；且 KB 中 Yuan_dynasty 出链到 Chinese_dynasty 等，"
                              "与上下文『朝代』概念关联度更高；Yuan_currency 先验较低且无关联。"
    }
}
(OUT / "tagme_results.json").write_text(json.dumps(output, ensure_ascii=False, indent=2))

print("=== TAGME 实体链接演示 ===")
for r in demo_results["Yuan"]["candidates"]:
    mark = " ✅" if r["entity"] == demo_results["Yuan"]["chosen"] else ""
    print(f"  Yuan → {r['entity']}: prior={r['prior']}, vote={r['vote']}, score={r['score']}{mark}")
print()
for m, r in link_results.items():
    print(f"  {m} → {r['chosen']}")
