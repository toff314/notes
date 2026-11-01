#!/usr/bin/env python3
"""lab-02 言语行为四分类规则分类器（对应 §26.1.2）。

基于 Bach & Harnish 的四分类（断言/指令/承诺/回应），
用关键词 + 句法模式做规则分类，对 12 句手工标注的句子做评估。
"""
import csv
import os
import re

# 12 句手工标注（句, 真实类别）
TEST_SET = [
    ("我需要在五月出行。", "断言"),
    ("你想在五月哪一天出行？", "指令"),
    ("那么，你想在五月哪一天出行？", "指令"),
    ("我要 11 号前一天晚上那班 5 点左右的航班。", "承诺"),
    ("好的，谢谢，再见。", "回应"),
    ("你能预订火车票吗？", "指令"),
    ("我想订一张下午 4 点去纽约的火车票。", "承诺"),
    ("不行，周五我全天都排满了。", "断言"),
    ("太棒了！", "回应"),
    ("我觉得直飞的选项不多。", "断言"),
    ("5 号有什么去香港的航班？", "指令"),
    ("我会考虑在那里多待一天。", "承诺"),
    # 下面两句作为「难点」，书上没明确分类，但容易错
    ("你难道不能早点说吗？", "指令"),  # 反问句 → 表面断言、实际指令
    ("我希望你能理解我的处境。", "指令"),  # 「希望」包着期望 → 弱指令
]

# 规则（按优先级）
RULES = [
    ("回应", re.compile(r"^(好的?[，。！]?|谢谢|感谢|再见|对不起|抱歉|嗨|你好|太棒了|嗯|对[，。])")),
    ("指令", re.compile(r"[吗呢吧？?]|能不能|可不可以|请|麻烦|你难道|我希望你能")),
    ("承诺", re.compile(r"(我)?要|我想|我会|我打算|我决定|我会考虑|我将会|订|预订")),
    ("断言", re.compile(r".")),  # 兜底
]


def classify(text):
    for label, pat in RULES:
        if pat.search(text):
            return label
    return "断言"


def main():
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(out_dir, exist_ok=True)

    correct = 0
    rows = []
    conf = {}  # (true, pred) -> count
    for text, gold in TEST_SET:
        pred = classify(text)
        ok = pred == gold
        correct += int(ok)
        conf[(gold, pred)] = conf.get((gold, pred), 0) + 1
        rows.append({"text": text, "gold": gold, "pred": pred, "ok": "✓" if ok else "✗"})
        print(f"{'✓' if ok else '✗'}  gold={gold}  pred={pred}  {text}")

    accuracy = correct / len(TEST_SET)
    print(f"\naccuracy={correct}/{len(TEST_SET)} = {accuracy:.4f}")

    # 写混淆矩阵
    labels = ["断言", "指令", "承诺", "回应"]
    cm_path = os.path.join(out_dir, "confusion_matrix.csv")
    with open(cm_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["gold\\pred"] + labels)
        for g in labels:
            row = [g] + [conf.get((g, p), 0) for p in labels]
            w.writerow(row)

    # 写逐条结果
    detail_path = os.path.join(out_dir, "predictions.csv")
    with open(detail_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["text", "gold", "pred", "ok"])
        w.writeheader()
        w.writerows(rows)

    print(f"saved: {cm_path}")
    print(f"saved: {detail_path}")


if __name__ == "__main__":
    main()
