#!/usr/bin/env python3
"""lab-04: 连贯判别（原始顺序 vs 打乱顺序）

对应 §25.3.3 句子顺序判别任务（Barzilay and Lapata, 2005）。
用实体网格转移概率作为连贯性度量，区分原始顺序与随机打乱顺序。
"""
import json
import os
import random
import re
from collections import Counter, defaultdict

out_dir = os.path.join(os.path.dirname(__file__), 'out')
os.makedirs(out_dir, exist_ok=True)

random.seed(42)

# ── 输入文档（书中 §25.3.2 图 25.9 的文本，6 句）──
docs = {
    "d1": [
        "The Justice Department is conducting an antitrust trial against Microsoft Corp.",
        "The government accuses Microsoft of bullying competitors.",
        "Microsoft denies the charges.",
        "The trial began in October 1998.",
        "The case is expected to last for months.",
        "The outcome could shape the future of the software industry.",
    ],
    "d2": [
        "John bought a piano for his living room.",
        "He had been saving money for years.",
        "The piano was delivered last week.",
        "John invited his friends over to see it.",
        "They all admired the beautiful instrument.",
        "John played his favorite songs for them.",
    ],
    "d3": [
        "The new library opened downtown last Monday.",
        "City officials attended the ribbon-cutting ceremony.",
        "The building cost over twelve million dollars.",
        "It houses more than two hundred thousand books.",
        "Residents can also access computers and meeting rooms.",
        "The library will be open seven days a week.",
    ],
}

# ── 简单实体抽取（人名、组织、关键名词）──
ENTITY_PATTERNS = [
    r'\b(Microsoft|John|Justice Department|City)\b',
    r'\b(piano|living room|money|friends|instrument|songs)\b',
    r'\b(library|building|books|computers|meeting rooms|residents)\b',
    r'\b(trial|case|outcome|software industry|charges)\b',
    r'\b(antitrust|government|competitors)\b',
]

def extract_entities(sentence):
    """从句子中抽取实体提及（简化版，用正则匹配）。"""
    entities = []
    for pat in ENTITY_PATTERNS:
        for m in re.finditer(pat, sentence, re.IGNORECASE):
            entities.append(m.group(0).lower())
    return entities

def get_role(entity, sentence):
    """判断实体在句中的语法角色：简化为主语(S)/宾语(O)/其他(X)。"""
    words = sentence.split()
    entity_words = entity.split()
    # 简化：如果实体出现在句首附近 → 主语；句中 → 宾语；其他 → X
    pos = -1
    for i, w in enumerate(words):
        if w.lower().startswith(entity_words[0]):
            pos = i
            break
    if pos <= 2:
        return 'S'
    elif pos < len(words) - 1:
        return 'O'
    else:
        return 'X'

def build_grid(sentences):
    """构建实体网格：行=句子，列=实体，值=S/O/X/-。"""
    all_entities = []
    for s in sentences:
        all_entities.extend(extract_entities(s))
    unique_entities = sorted(set(all_entities))

    grid = []
    for s in sentences:
        row = {}
        ents_in_sent = extract_entities(s)
        for ent in unique_entities:
            if ent in ents_in_sent:
                row[ent] = get_role(ent, s)
            else:
                row[ent] = '-'
        grid.append(row)
    return grid, unique_entities

def extract_transitions(grid, entities):
    """从网格中抽取长度为 2 的转移。"""
    transitions = []
    for ent in entities:
        seq = [grid[i].get(ent, '-') for i in range(len(grid))]
        for i in range(len(seq) - 1):
            transitions.append((seq[i], seq[i+1]))
    return transitions

def compute_transition_probs(all_transitions):
    """计算转移概率（从训练文档中统计）。"""
    counts = Counter(all_transitions)
    total = sum(counts.values())
    return {t: c / total for t, c in counts.items()}, counts

def coherence_score(sentences, trans_probs, trans_counts):
    """用实体网格转移概率计算文档连贯性得分。"""
    grid, entities = build_grid(sentences)
    transitions = extract_transitions(grid, entities)
    if not transitions:
        return 0.0
    # 得分 = 平均转移概率的负对数（概率越高越连贯）
    score = 0.0
    for t in transitions:
        prob = trans_probs.get(t, 1e-6)
        score += -prob  # 负概率作为"不连贯"惩罚
    return score / len(transitions)

# ── 主实验 ──
results = []

# 1. 用 d1 作为"训练"文档统计转移概率
train_grid, train_ents = build_grid(docs["d1"])
train_transitions = extract_transitions(train_grid, train_ents)
trans_probs, trans_counts = compute_transition_probs(train_transitions)

print("=" * 60)
print("lab-04: 连贯判别（原始顺序 vs 打乱顺序）")
print("=" * 60)
print(f"\n训练文档 d1 的实体网格转移统计：")
print(f"  共 {len(train_transitions)} 个转移")
top_trans = sorted(trans_counts.items(), key=lambda x: -x[1])[:5]
for t, c in top_trans:
    print(f"  {t[0]}→{t[1]}: {c} 次 (P={trans_probs[t]:.4f})")

# 2. 对每个文档，比较原始顺序与 5 个随机打乱顺序
print(f"\n{'文档':<6} {'原始得分':<12} {'打乱均分':<12} {'判别正确'}")
print("-" * 40)

correct = 0
total_pairs = 0

for doc_id, sentences in docs.items():
    orig_score = coherence_score(sentences, trans_probs, trans_counts)
    shuffled_scores = []
    for trial in range(5):
        shuffled = sentences.copy()
        random.shuffle(shuffled)
        shuffled_scores.append(coherence_score(shuffled, trans_probs, trans_counts))
    avg_shuffled = sum(shuffled_scores) / len(shuffled_scores)
    # 判别：原始顺序得分应更低（因为得分是负概率，越低越连贯）
    is_correct = orig_score < avg_shuffled
    if is_correct:
        correct += 1
    total_pairs += 1
    print(f"{doc_id:<6} {orig_score:<12.4f} {avg_shuffled:<12.4f} {'✓' if is_correct else '✗'}")
    results.append({
        "doc_id": doc_id,
        "original_score": orig_score,
        "shuffled_avg": avg_shuffled,
        "shuffled_scores": shuffled_scores,
        "correct": is_correct,
    })

accuracy = correct / total_pairs
print(f"\n判别准确率: {correct}/{total_pairs} = {accuracy:.1%}")
print(f"结论: 原始顺序 {'更连贯' if accuracy > 0.5 else '未显示更连贯'} (得分越低越连贯)")

# 保存结果
output = {
    "task": "句子顺序判别 (Barzilay and Lapata, 2005)",
    "training_doc": "d1",
    "num_transitions": len(train_transitions),
    "top_transitions": [{"from": t[0], "to": t[1], "count": c, "prob": trans_probs[t]} for t, c in top_trans],
    "results": results,
    "accuracy": accuracy,
    "interpretation": "得分 = 平均转移概率的负值，越低越连贯",
}
output_file = os.path.join(out_dir, 'coherence_discrimination.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print(f"\n结果已保存到 {output_file}")
