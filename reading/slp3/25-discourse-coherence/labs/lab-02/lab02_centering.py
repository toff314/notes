#!/usr/bin/env python3
"""lab-02: 中心理论 Cb/Cf/Cp 追踪与连贯性评估"""
import json
import os
from collections import OrderedDict

out_dir = os.path.join(os.path.dirname(__file__), 'out')
os.makedirs(out_dir, exist_ok=True)

# 语法角色权重（书中 §25.3.1：主语 > 宾语 > 其他）
ROLE_WEIGHTS = {"subject": 3, "object": 2, "other": 1}

# 更准确的实体抽取：基于关键词和代词
ENTITY_KEYWORDS = {
    "John": "subject",
    "He": "subject",
    "he": "subject",
    "piano": "object",
    "a piano": "object",
    "store": "object",
    "music store": "object",
}

def extract_entities(sentence):
    """
    从句子中提取实体和语法角色。
    使用规则模拟语法角色标注（实际应用应使用 spaCy）。
    """
    entities = []
    words = sentence.split()
    
    # 检测主语（人名或代词）
    for w in words:
        if w in ["John", "He", "he", "She", "she", "They", "they"]:
            # 统一使用原名（处理代词共指）
            canonical = {"He": "John", "he": "John"}.get(w, w)
            entities.append({"text": canonical, "role": "subject"})
            break
    
    # 检测宾语（名词或名词短语）
    for i, w in enumerate(words):
        if w in ["piano", "store"] and i > 0:
            entities.append({"text": w, "role": "object"})
        elif w == "piano." and i > 0:
            entities.append({"text": "piano", "role": "object"})
    
    # 去重并保持顺序
    seen = set()
    unique = []
    for e in entities:
        if e["text"] not in seen:
            seen.add(e["text"])
            unique.append(e)
    
    return unique

def compute_cf(entities):
    """
    计算前向中心 Cf(Un)：按语法角色排序的实体列表
    排序规则：主语 > 宾语 > 其他（同角色按出现顺序）
    """
    sorted_entities = sorted(
        entities,
        key=lambda e: (-ROLE_WEIGHTS.get(e["role"], 0),)
    )
    return [e["text"] for e in sorted_entities]

def compute_cb(current_sentence, prev_cf, prev_cb):
    """
    计算后向中心 Cb(Un)：当前句子中与前一话语的 Cb 或 Cf 最高排名成员共指的实体
    简化实现：找当前句子中与 prev_cf[0]（前一话语的 Cp）匹配的实体
    """
    current_entities = extract_entities(current_sentence)
    current_texts = [e["text"] for e in current_entities]
    
    # 如果前一话语的 Cp 出现在当前句子中，则 Cb = Cp
    # 需要处理代词共指：He/he 指代 John
    pronoun_map = {"He": "John", "he": "John", "She": "Mary", "she": "Mary"}
    current_texts_raw = [e["text"] for e in current_entities]
    current_texts = []
    for t in current_texts_raw:
        current_texts.append(t)
        if t in pronoun_map:
            current_texts.append(pronoun_map[t])
    
    if prev_cf and prev_cf[0] in current_texts:
        return prev_cf[0]
    # 否则找与 prev_cb 匹配的
    if prev_cb and prev_cb in current_texts:
        return prev_cb
    return None

def compute_cp(cf):
    """计算首选中心 Cp(Un)：Cf 中排名最高的成员"""
    return cf[0] if cf else None

def transition_type(prev_cb, current_cb, prev_cp, current_cp):
    """
    判断转移状态（Brennan et al., 1987）：
    - Continue: Cb(Un) = Cp(Un) 且 Cb(Un) ≠ None 且 Cb(Un-1) = Cb(Un)
    - Retain: Cb(Un) = Cp(Un-1) 且 Cb(Un) ≠ Cp(Un)
    - Smooth-Shift: Cb(Un) = Cp(Un) 且 Cb(Un-1) ≠ Cb(Un)
    - Rough-Shift: 其他情况
    """
    if current_cb is not None and current_cb == current_cp and prev_cb == current_cb:
        return "Continue"
    elif current_cb is not None and current_cb == prev_cp and current_cb != current_cp:
        return "Retain"
    elif current_cb is not None and current_cb == current_cp and prev_cb != current_cb:
        return "Smooth-Shift"
    else:
        return "Rough-Shift"

# 书中例句 (25.30) 的模拟（使用英文原名以匹配书中走查）
sentences = [
    "John went to his favorite music store.",  # U1
    "He bought a piano.",                       # U2
    "He was excited, finally he could own a piano."  # U3
]

# 追踪中心
results = []
prev_cf = None
prev_cb = None
prev_cp = None

for i, sent in enumerate(sentences, 1):
    entities = extract_entities(sent)
    cf = compute_cf(entities)
    cb = compute_cb(sent, prev_cf, prev_cb) if i > 1 else None
    cp = compute_cp(cf)
    trans = transition_type(prev_cb, cb, prev_cp, cp) if i > 1 else "Start"
    
    results.append({
        "utterance": f"U{i}",
        "sentence": sent,
        "entities": entities,
        "Cf": cf,
        "Cb": cb,
        "Cp": cp,
        "transition": trans
    })
    
    prev_cf = cf
    prev_cb = cb
    prev_cp = cp

# 保存结果
output_file = os.path.join(out_dir, 'centering_trace.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        "sentences": sentences,
        "trace": results,
        "note": "简化实现：语法角色用规则模拟，实际应用应使用 spaCy"
    }, f, ensure_ascii=False, indent=2)

print("中心理论追踪完成")
print(f"结果已保存到 {output_file}")
print()
for r in results:
    print(f"{r['utterance']}: {r['sentence']}")
    print(f"  Cf = {r['Cf']}")
    print(f"  Cb = {r['Cb']}")
    print(f"  Cp = {r['Cp']}")
    print(f"  转移 = {r['transition']}")
    print()

# 连贯性评估：Continue > Retain > Smooth-Shift > Rough-Shift
preference_order = ["Continue", "Retain", "Smooth-Shift", "Rough-Shift"]
transitions = [r["transition"] for r in results if r["transition"] != "Start"]
coherence_score = sum(
    len(preference_order) - preference_order.index(t)
    for t in transitions
) / len(transitions) if transitions else 0

print(f"连贯性评分（越高越连贯）: {coherence_score:.2f}")
