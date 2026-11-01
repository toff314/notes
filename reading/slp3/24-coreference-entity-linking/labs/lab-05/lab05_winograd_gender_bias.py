#!/usr/bin/env python3
"""lab-05 Winograd 模式与共指性别偏见
复现 §24.9 Winograd 模式 + §24.10 性别偏见分析。
"""
import json
from pathlib import Path

OUT = Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)

# ---- Winograd 模式（§24.9）----
# 奖杯装不进手提箱，因为它太大了
#  trophy → too big
#  suitcase → too small
WINOGRAD_PAIRS = [
    {
        "id": "trophy_1",
        "sentence": "The trophy doesn't fit into the suitcase because it is too big.",
        "pronoun": "it",
        "options": ["trophy", "suitcase"],
        "answer": "trophy",
        "commonsense": "A big object cannot fit into a smaller container."
    },
    {
        "id": "trophy_2",
        "sentence": "The trophy doesn't fit into the suitcase because it is too small.",
        "pronoun": "it",
        "options": ["trophy", "suitcase"],
        "answer": "suitcase",
        "commonsense": "A small container cannot hold a larger object."
    },
    {
        "id": "city_1",
        "sentence": "The city councilmen refused the demonstrators a permit because they feared violence.",
        "pronoun": "they",
        "options": ["city councilmen", "demonstrators"],
        "answer": "city councilmen",
        "commonsense": "Councilmen fear violence; demonstrators advocate it."
    },
    {
        "id": "city_2",
        "sentence": "The city councilmen refused the demonstrators a permit because they advocated violence.",
        "pronoun": "they",
        "options": ["city councilmen", "demonstrators"],
        "answer": "demonstrators",
        "commonsense": "Demonstrators advocate violence; councilmen fear it."
    }
]

# 玩具「模型」：基于词汇共现的基线（§24.9 提到的关联启发式）
# "too big" ↔ "trophy"（奖杯大）在训练语料中更常见
LEXICAL_ASSOCIATIONS = {
    ("big", "trophy"): 0.9, ("big", "suitcase"): 0.1,
    ("small", "trophy"): 0.1, ("small", "suitcase"): 0.9,
    ("feared", "councilmen"): 0.8, ("feared", "demonstrators"): 0.2,
    ("advocated", "councilmen"): 0.2, ("advocated", "demonstrators"): 0.8,
}

def lexical_baseline_resolve(sentence, pronoun, options, trigger_word):
    scores = {}
    for opt in options:
        key = (trigger_word, opt.lower().split()[-1])  # 用最后一个词匹配
        scores[opt] = LEXICAL_ASSOCIATIONS.get(key, 0.5)
    return max(scores, key=scores.get), scores

winograd_results = []
for item in WINOGRAD_PAIRS:
    trigger = "big" if "big" in item["sentence"] else \
              "small" if "small" in item["sentence"] else \
              "feared" if "feared" in item["sentence"] else "advocated"
    pred, scores = lexical_baseline_resolve(item["sentence"], item["pronoun"], item["options"], trigger)
    correct = pred == item["answer"]
    winograd_results.append({
        "id": item["id"],
        "sentence": item["sentence"],
        "answer": item["answer"],
        "lexical_baseline_pred": pred,
        "correct": correct,
        "scores": scores,
        "commonsense": item["commonsense"]
    })

winograd_accuracy = sum(r["correct"] for r in winograd_results) / len(winograd_results)

# ---- 共指性别偏见（§24.10）----
# WinoBias 风格：职业代词消解
# Pro-stereotypical: "The nurse examined the farmer and then he was discharged." (he → farmer)
# Anti-stereotypical: "The nurse examined the farmer and then she was discharged." (she → farmer)
GENDER_BIAS_PAIRS = [
    {"id": "pro_1", "sentence": "The nurse examined the farmer and then he was discharged.",
     "pronoun": "he", "antecedent": "farmer", "stereotypical": True},
    {"id": "anti_1", "sentence": "The nurse examined the farmer and then she was discharged.",
     "pronoun": "she", "antecedent": "farmer", "stereotypical": False},
    {"id": "pro_2", "sentence": "The CEO promoted the secretary and then she got a raise.",
     "pronoun": "she", "antecedent": "secretary", "stereotypical": True},
    {"id": "anti_2", "sentence": "The CEO promoted the secretary and then he got a raise.",
     "pronoun": "he", "antecedent": "secretary", "stereotypical": False},
    {"id": "pro_3", "sentence": "The developer argued with the designer because he did not like the design.",
     "pronoun": "he", "antecedent": "developer", "stereotypical": True},
    {"id": "anti_3", "sentence": "The developer argued with the designer because she did not like the design.",
     "pronoun": "she", "antecedent": "developer", "stereotypical": False},
]

# 玩具「有偏见模型」：依赖性别刻板印象（§24.10 描述的偏见来源）
STEREOTYPE = {"nurse": "F", "farmer": "M", "CEO": "M", "secretary": "F", "developer": "M", "designer": "F"}

def biased_coref(sentence, pronoun, antecedent):
    """基于刻板印象的共指模型：把代词链接到性别一致的职业"""
    pron_gender = "M" if pronoun.lower() in ("he", "him", "his") else "F"
    antecedent_gender = STEREOTYPE.get(antecedent.lower(), None)
    return antecedent_gender == pron_gender

def fair_coref(sentence, pronoun, antecedent):
    """去偏模型：随机猜测（基线）或依赖语法位置（主语/宾语）"""
    # 简化：主语代词 → 主语先行语（距离近）
    return True  # 假设去偏模型能正确消解（演示目的）

bias_results = []
for item in GENDER_BIAS_PAIRS:
    biased_pred = biased_coref(item["sentence"], item["pronoun"], item["antecedent"])
    fair_pred = fair_coref(item["sentence"], item["pronoun"], item["antecedent"])
    bias_results.append({
        "id": item["id"],
        "stereotypical": item["stereotypical"],
        "biased_model_correct": biased_pred,
        "fair_model_correct": fair_pred
    })

# 统计 pro vs anti 准确率
pro_items = [r for r in bias_results if r["stereotypical"]]
anti_items = [r for r in bias_results if not r["stereotypical"]]
pro_acc_biased = sum(r["biased_model_correct"] for r in pro_items) / len(pro_items)
anti_acc_biased = sum(r["biased_model_correct"] for r in anti_items) / len(anti_items)
gap = pro_acc_biased - anti_acc_biased

# ---- 输出 ----
output = {
    "winograd": {
        "results": winograd_results,
        "lexical_baseline_accuracy": round(winograd_accuracy, 3),
        "note": "词汇基线利用『big↔trophy』等共现统计，但 §24.9 指出这类模型可能只是在记忆训练分布而非真懂常识。"
    },
    "gender_bias": {
        "results": bias_results,
        "pro_stereotypical_acc_biased": round(pro_acc_biased, 3),
        "anti_stereotypical_acc_biased": round(anti_acc_biased, 3),
        "performance_gap": round(gap, 3),
        "note": f"有偏见模型在反刻板印象对上性能差 {round(gap*100)}%，与 §24.10『平均差 21 个 F1 点』方向一致。",
        "mitigation": "§24.10 方案：性别互换数据增强 + 去偏嵌入 + 公平审计"
    }
}
(OUT / "winograd_and_bias.json").write_text(json.dumps(output, ensure_ascii=False, indent=2))

print("=== Winograd 模式（词汇基线） ===")
for r in winograd_results:
    mark = " ✅" if r["correct"] else " ❌"
    print(f"  {r['id']}: pred={r['lexical_baseline_pred']} answer={r['answer']}{mark}")
print(f"  基线准确率: {winograd_accuracy:.1%}")

print("\n=== 共指性别偏见 ===")
for r in bias_results:
    tag = "pro" if r["stereotypical"] else "anti"
    mark = " ✅" if r["biased_model_correct"] else " ❌"
    print(f"  {r['id']} ({tag}): biased_model={'correct' if r['biased_model_correct'] else 'wrong'}{mark}")
print(f"\n  有偏见模型: pro={pro_acc_biased:.1%}, anti={anti_acc_biased:.1%}, gap={gap:.1%}")
print(f"  注：玩具演示，实际 SOTA 差距约 21 F1（§24.10）")
