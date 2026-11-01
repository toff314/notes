#!/usr/bin/env python3
"""Lab-05: BIO 序列标注 + Viterbi 解码
实现简化的 BIO 序列标注器，对测试句子输出标签序列并计算 F1。
"""
import json
from collections import defaultdict

# 5 个测试句子（含谓词和 BIO 标签）
test_data = [
    {
        "words": ["John", "broke", "the", "window", "with", "a", "stone"],
        "predicate": "broke",
        "gold": ["B-ARG0", "O", "B-ARG1", "I-ARG1", "B-ARGM-MNR", "I-ARGM-MNR", "I-ARGM-MNR"],
    },
    {
        "words": ["The", "window", "broke"],
        "predicate": "broke",
        "gold": ["B-ARG1", "I-ARG1", "O"],
    },
    {
        "words": ["Doris", "gave", "the", "book", "to", "Cary"],
        "predicate": "gave",
        "gold": ["B-ARG0", "O", "B-ARG1", "I-ARG1", "B-ARG2", "I-ARG2"],
    },
    {
        "words": ["Sales", "fell", "to", "25", "million"],
        "predicate": "fell",
        "gold": ["B-ARG1", "O", "B-ARG4", "I-ARG4", "I-ARG4"],
    },
    {
        "words": ["Big", "Fruit", "Co.", "increased", "the", "price", "of", "bananas"],
        "predicate": "increased",
        "gold": ["B-ARG0", "I-ARG0", "I-ARG0", "O", "B-ARG1", "I-ARG1", "I-ARG1", "I-ARG1"],
    },
]

# 简化的发射概率：基于词性和位置规则
def predict_bio(words, predicate):
    """基于规则的 BIO 预测（简化版）"""
    pred_idx = words.index(predicate) if predicate in words else -1
    tags = []
    for i, w in enumerate(words):
        if i == pred_idx:
            tags.append("O")
        elif i < pred_idx:
            # 谓词前：可能是 ARG0（施事）或 ARG1（主题）
            if w[0].isupper() and i == 0:
                tags.append("B-ARG0")
            elif tags and tags[-1].startswith("B-ARG0"):
                tags.append("I-ARG0")
            else:
                tags.append("B-ARG1")
        else:
            # 谓词后：可能是 ARG1、ARG2、ARG4 或修饰语
            if w in ("to", "from", "by", "with"):
                tags.append("B-ARGM")
            elif w[0].isdigit():
                tags.append("B-ARG2")
            else:
                tags.append("B-ARG1")
    return tags

# Viterbi 解码（简化：基于规则的转移概率）
def viterbi_decode(words, predicate, emissions):
    """简化 Viterbi：用规则预测 + 局部一致性检查"""
    # 规则：I-X 不能跟在 O 或不同标签的 I-Y 后面
    decoded = []
    prev = "O"
    for i, tag in enumerate(emissions):
        if tag.startswith("I-") and prev not in (tag, tag.replace("I-", "B-")):
            tag = tag.replace("I-", "B-")
        decoded.append(tag)
        prev = tag
    return decoded

# 评估
def compute_f1(gold, pred):
    """计算完全匹配 F1"""
    tp, fp, fn = 0, 0, 0
    for g, p in zip(gold, pred):
        if g == p and g != "O":
            tp += 1
        elif p != "O" and g != p:
            fp += 1
        elif g != "O" and p == "O":
            fn += 1
    precision = tp / (tp + fp) if tp + fp > 0 else 0
    recall = tp / (tp + fn) if tp + fn > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0
    return {"tp": tp, "fp": fp, "fn": fn, "precision": round(precision, 3), "recall": round(recall, 3), "f1": round(f1, 3)}

results = []
for item in test_data:
    emissions = predict_bio(item["words"], item["predicate"])
    decoded = viterbi_decode(item["words"], item["predicate"], emissions)
    metrics = compute_f1(item["gold"], decoded)
    results.append({
        "sentence": " ".join(item["words"]),
        "predicate": item["predicate"],
        "gold": item["gold"],
        "predicted": decoded,
        "metrics": metrics,
    })

overall = {
    "total_tp": sum(r["metrics"]["tp"] for r in results),
    "total_fp": sum(r["metrics"]["fp"] for r in results),
    "total_fn": sum(r["metrics"]["fn"] for r in results),
}
overall["precision"] = round(overall["total_tp"] / (overall["total_tp"] + overall["total_fp"]), 3) if overall["total_tp"] + overall["total_fp"] > 0 else 0
overall["recall"] = round(overall["total_tp"] / (overall["total_tp"] + overall["total_fn"]), 3) if overall["total_tp"] + overall["total_fn"] > 0 else 0
overall["f1"] = round(2 * overall["precision"] * overall["recall"] / (overall["precision"] + overall["recall"]), 3) if overall["precision"] + overall["recall"] > 0 else 0

output = {"results": results, "overall": overall}
with open("out/bio_viterbi_output.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("=== BIO 标注 + Viterbi 解码 ===")
for r in results:
    print(f"\n句子: {r['sentence']}")
    print(f"谓词: {r['predicate']}")
    print(f"金标: {r['gold']}")
    print(f"预测: {r['predicted']}")
    print(f"F1: {r['metrics']['f1']}")

print(f"\n=== 总体 ===")
print(f"Precision: {overall['precision']}, Recall: {overall['recall']}, F1: {overall['f1']}")
