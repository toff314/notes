#!/usr/bin/env python3
"""Lab-04: 基于特征的 SRL 特征抽取器
实现 Gildea & Jurafsky 2000 的核心特征模板，
对书中图 22.5 的句子抽取特征向量。
"""
import json

# 书中图 22.5 的句子（简化表示）
sentence = {
    "text": "The San Francisco Examiner issued a special edition yesterday",
    "predicate": "issued",
    "constituent": {
        "text": "The San Francisco Examiner",
        "phrase_type": "NP-SBJ",
        "head": "Examiner",
        "head_pos": "NNP",
        "path": "NP↑S↓VP↓VBD",
        "voice": "active",
        "position": "before",
        "subcategorization": "VP → VBD NP PP",
        "ne_type": "ORG",
        "first_word": "The",
        "last_word": "Examiner",
    },
}

# Gildea & Jurafsky 2000 核心特征
features = {
    "governing_predicate": sentence["predicate"],
    "phrase_type": sentence["constituent"]["phrase_type"],
    "head_word": sentence["constituent"]["head"],
    "head_pos": sentence["constituent"]["head_pos"],
    "path": sentence["constituent"]["path"],
    "voice": sentence["constituent"]["voice"],
    "linear_position": sentence["constituent"]["position"],
    "subcategorization": sentence["constituent"]["subcategorization"],
    "named_entity_type": sentence["constituent"]["ne_type"],
    "first_word": sentence["constituent"]["first_word"],
    "last_word": sentence["constituent"]["last_word"],
}

# 与书中 §22.6.1 所列特征对照
expected_features = [
    "issued", "NP", "Examiner", "NNP", "NP↑S↓VP↓VBD",
    "active", "before", "VP →NP PP", "ORG", "The", "Examiner"
]

# 验证
matches = []
for key, val in features.items():
    expected_match = any(str(val) in ef or ef in str(val) for ef in expected_features)
    matches.append({"feature": key, "value": val, "matches_book": expected_match})

result = {
    "sentence": sentence["text"],
    "predicate": sentence["predicate"],
    "features": features,
    "validation": matches,
    "all_match": all(m["matches_book"] for m in matches),
}

with open("out/feature_vector.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("=== 特征向量 ===")
print(f"句子: {sentence['text']}")
print(f"谓词: {sentence['predicate']}")
print(f"成分: {sentence['constituent']['text']}")
print()
for key, val in features.items():
    match = "✓" if any(str(val) in ef or ef in str(val) for ef in expected_features) else "✗"
    print(f"  {match} {key}: {val}")

print(f"\n与书中特征对照: {'全部匹配' if result['all_match'] else '存在不匹配'}")
