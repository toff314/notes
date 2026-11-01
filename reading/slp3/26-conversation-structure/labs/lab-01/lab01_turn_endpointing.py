#!/usr/bin/env python3
"""lab-01 话轮切分与断点检测模拟（对应 §26.1.1）。

对图 26.1 的 20 个话轮做切分：把整段对话按「停顿+句末标点」规则切分话轮，
与手工标注的真实话轮边界对照，输出 precision/recall/F1。
"""
import json
import os
import re

# 图 26.1 整段对话（按出现顺序拼接），手工标注的话轮边界（按话语 ID）
GOLD_TURNS = [
    ("C1", "我需要在五月出行。"),
    ("A2", "那么，你想在五月哪一天出行？"),
    ("C3", "好的，呃，我需要到那里参加一个从 12 号到 15 号的会议。"),
    ("A4", "你要飞往哪个城市？"),
    ("C5", "西雅图。"),
    ("A6", "你想什么时候离开匹兹堡？"),
    ("C7", "呃，嗯，我觉得直飞的选项不多。"),
    ("A8", "对。今天有三个直飞航班。"),
    ("C9", "是哪几个？"),
    ("A10", "第一个 10:00am 从 PGH 起飞，当地时间 12:05 抵达西雅图。第二个航班 5:55pm 从 PGH 起飞，8pm 抵达西雅图。最后一个航班 8:15pm 从 PGH 起飞，10:28pm 抵达西雅图。"),
    ("C11", "好的，我要 11 号前一天晚上那班 5 点左右的航班。"),
    ("A12", "11 号？好的。5:55pm 起飞，8pm 抵达西雅图，U.S. Air 航班 115。"),
    ("C13", "好的。"),
    ("A14", "你刚说是 5 月 15 号返回？"),
    ("C15", "呃，对，在当天结束时。"),
    ("A16", "好的。有 #两个直飞……#"),
    ("C17", "#实……其实#，15 号是星期几？"),
    ("A18", "是星期五。"),
    ("C19", "呃，嗯。我会考虑在那里多待一天，待到星期天。"),
    ("A20", "好的……好的。星期天我有……"),
]

# 模拟：将每段话轮按句子切分，规则是「停顿 >0.5s 且句末为标点」算一次话轮结束
# 简单模拟：每条 GOLD 中如果出现多个完整句且以 。！？ 结尾的连续块，
# 我们的规则可能切过头；用启发式：每段 GOLD 算 1 个真实话轮，
# 但把「话轮内带明显填充停顿（呃/嗯）」的段落标记为「规则易错点」。

FILLER_TOKENS = ("呃", "嗯")

def rule_predict(turns):
    """规则预测：每个 GOLD 话轮算 1 个预测边界；
    若话轮以填充词开头且包含 >1 个句子，则规则会误判为 2 个话轮。"""
    pred_boundaries = set()
    errors = []
    for i, (tid, text) in enumerate(turns):
        # 预测边界：每个 GOLD 末尾
        pred_boundaries.add(i)
        # 误判：以填充词开头且内部有 >1 个完整句
        sentences = [s for s in re.split(r"[。！？]", text) if s.strip()]
        if text.startswith(FILLER_TOKENS) and len(sentences) > 1 and i > 0:
            # 规则在第一个句子后插入了边界 → 多算 1 个
            pred_boundaries.add(i - 0.5)  # 半整数表示误插入的边界
            errors.append({
                "turn_id": tid,
                "text": text[:40],
                "reason": "以填充词开头且包含多句，规则在首个句末误切",
            })
    return pred_boundaries, errors


def main():
    n = len(GOLD_TURNS)
    pred, errors = rule_predict(GOLD_TURNS)
    gold_set = set(range(n))

    # 把半整数边界转换成「多预测的边界」
    pred_real = {p for p in pred if isinstance(p, int) or float(p).is_integer()}
    pred_extra = pred - pred_real

    tp = len(pred_real & gold_set)
    fp = len(pred_extra)
    fn = 0  # 我们没有漏切（每个 GOLD 末尾都预测了）
    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / (tp + fn) if (tp + fn) else 1.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(out_dir, exist_ok=True)
    result = {
        "gold_turns": n,
        "predicted_boundaries": len(pred_real),
        "false_positive_boundaries": fp,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "errors": errors,
        "note": "规则：每段 GOLD 末尾预测一个边界；以填充词开头且含多句的段落在首个句末误插一个边界。",
    }
    out_path = os.path.join(out_dir, "turn_metrics.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"gold_turns={n}")
    print(f"predicted={len(pred_real)} false_positive={fp}")
    print(f"precision={precision:.4f} recall={recall:.4f} f1={f1:.4f}")
    print(f"errors={len(errors)}")
    for e in errors:
        print(f"  - {e['turn_id']}: {e['text']}... ({e['reason']})")
    print(f"saved: {out_path}")


if __name__ == "__main__":
    main()
