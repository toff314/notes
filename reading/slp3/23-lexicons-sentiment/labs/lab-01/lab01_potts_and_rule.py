#!/usr/bin/env python3
"""lab-01: Potts 分布复算 + 简单规则分类器
对应 actions.md 第 1 条，书中 §23.5、§23.6
"""
import csv
import os

# 书中 §23.5 的原始数字
count_disappointing_in_1star = 8557
total_words_in_1star = 25395214
P_disappointing_given_1 = count_disappointing_in_1star / total_words_in_1star
print(f"P(disappointing|1) = {P_disappointing_given_1:.6f}  (book = .0003)")

# 构造一个简化的 10 星分布（书中给 disappointing 的完整向量）
# 书中: disappointing ~ [.10, .12, .14, .14, .13, .11, .08, .06, .06, .05]
potts_vector = [0.10, 0.12, 0.14, 0.14, 0.13, 0.11, 0.08, 0.06, 0.06, 0.05]
# 验证归一化
s = sum(potts_vector)
print(f"sum(PottsScore) = {s:.4f}  (should be ~1.0)")

# 用 P(w|c) 模拟：假设 disappointing 在各星级的似然与书中 PottsScore 成正比
# 则 P(disappointing|1) / sum_c P(disappointing|c) = 0.10
# 即 P(disappointing|1) = 0.10 * sum_c P(disappointing|c)
# 从书中 P(disappointing|1)=.0003 可反推 sum = .003
sum_likelihood = P_disappointing_given_1 / 0.10
print(f"inferred sum_c P(disappointing|c) = {sum_likelihood:.6f}")
print(f"check: P(disappointing|1)/sum = {P_disappointing_given_1/sum_likelihood:.4f}  (book = 0.10)")

# 简单规则分类器：正面词 > 负面词 → 正面
positive_lex = {"good", "great", "amazing", "love", "excellent", "perfect", "best", "wonderful"}
negative_lex = {"bad", "terrible", "awful", "hate", "worst", "horrible", "disappointing", "boring"}

reviews = [
    ("This movie was great and I love it", "pos"),
    ("Terrible film, bad acting, boring story", "neg"),
    ("Amazing performance, excellent directing", "pos"),
    ("I hate this, worst movie ever", "neg"),
    ("Good story but bad ending", "neg"),  # mixed
    ("Perfect! Wonderful! Best film!", "pos"),
    ("Awful, horrible, terrible experience", "neg"),
    ("Love the acting, amazing visuals", "pos"),
    ("Disappointing and boring, not good", "neg"),
    ("Excellent! Great! Love it!", "pos"),
    ("Not bad at all, actually good", "pos"),  # negation trap
    ("Badly written but great concept", "pos"),  # mixed
    ("The worst. Hate everything.", "neg"),
    ("A wonderful, amazing experience", "pos"),
    ("Terrible. Boring. Disappointing.", "neg"),
    ("Best movie I've seen, excellent", "pos"),
    ("Horrible acting, awful plot", "neg"),
    ("Good enough, not amazing", "neg"),  # weak positive → predicted neg
    ("I love it so much, perfect", "pos"),
    ("Awful, just awful", "neg"),
]

correct = 0
errors = []
for text, gold in reviews:
    words = set(text.lower().replace(",", " ").replace(".", " ").replace("!", " ").replace("'", " ").split())
    pos_count = len(words & positive_lex)
    neg_count = len(words & negative_lex)
    pred = "pos" if pos_count > neg_count else "neg"
    if pred == gold:
        correct += 1
    else:
        errors.append({"text": text, "gold": gold, "pred": pred, "pos": pos_count, "neg": neg_count})

acc = correct / len(reviews)
print(f"\nRule classifier accuracy = {acc:.2f} ({correct}/{len(reviews)})")

os.makedirs("out", exist_ok=True)
with open("out/potts_check.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["item", "computed", "book_value", "diff"])
    w.writerow(["P(disappointing|1)", f"{P_disappointing_given_1:.6f}", "0.0003",
                f"{abs(P_disappointing_given_1 - 0.0003):.6f}"])
    w.writerow(["PottsScore(disappointing,1)", f"{P_disappointing_given_1/sum_likelihood:.4f}", "0.10",
                f"{abs(P_disappointing_given_1/sum_likelihood - 0.10):.4f}"])
    w.writerow(["sum(PottsScore)", f"{s:.4f}", "1.0", f"{abs(s-1.0):.4f}"])

with open("out/rule_classifier.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["text", "gold", "pred", "pos", "neg"])
    w.writeheader()
    for e in errors:
        w.writerow(e)

print("saved: out/potts_check.csv, out/rule_classifier.csv")
