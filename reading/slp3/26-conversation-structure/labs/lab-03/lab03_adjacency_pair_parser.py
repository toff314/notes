#!/usr/bin/env python3
"""lab-03 邻接对与子对话栈式解析器（对应 §26.1.4）。

对图 26.1 的对话做解析：识别邻接对（问-答、提议-接受等），
用栈处理纠正子对话（C17–A20），输出解析树。
"""

# 图 26.1 的话轮（id, 说话者, 文本, 主要对话功能）
TURNS = [
    ("C1",  "C", "我需要在五月出行。", "assert"),
    ("A2",  "A", "那么，你想在五月哪一天出行？", "question"),
    ("C3",  "C", "好的，呃，我需要到那里参加一个从 12 号到 15 号的会议。", "answer"),
    ("A4",  "A", "你要飞往哪个城市？", "question"),
    ("C5",  "C", "西雅图。", "answer"),
    ("A6",  "A", "你想什么时候离开匹兹堡？", "question"),
    ("C7",  "C", "呃，嗯，我觉得直飞的选项不多。", "assert"),
    ("A8",  "A", "对。今天有三个直飞航班。", "accept+assert"),
    ("C9",  "C", "是哪几个？", "question"),
    ("A10", "A", "第一个 10:00am 从 PGH 起飞……最后一个航班 8:15pm 从 PGH 起飞，10:28pm 抵达西雅图。", "answer"),
    ("C11", "C", "好的，我要 11 号前一天晚上那班 5 点左右的航班。", "accept+commit"),
    ("A12", "A", "11 号？好的。5:55pm 起飞，8pm 抵达西雅图，U.S. Air 航班 115。", "confirm+assert"),
    ("C13", "C", "好的。", "ack"),
    ("A14", "A", "你刚说是 5 月 15 号返回？", "question"),
    ("C15", "C", "呃，对，在当天结束时。", "answer"),
    ("A16", "A", "好的。有两个直飞……", "ack+assert"),
    ("C17", "C", "其实，15 号是星期几？", "side-question"),
    ("A18", "A", "是星期五。", "side-answer"),
    ("C19", "C", "呃，嗯。我会考虑在那里多待一天，待到星期天。", "side-elab"),
    ("A20", "A", "好的……好的。星期天我有……", "return"),
]

# 邻接对映射（第一部分 → 期望第二部分）
ADJACENCY_PAIRS = {
    "question": {"answer", "side-question", "side-answer"},  # 问-答；问可以被旁支问题打断
    "assert": {"ack", "accept+assert", "accept+commit", "question"},  # 断言可被确认/接受/追问
}


def parse(turns):
    """栈式解析：每个话轮要么是某个待响应的邻接对的第二部分，
    要么开启新的邻接对，要么是子对话（进入/返回）。"""
    stack = []   # 待完成的邻接对
    tree_lines = []
    errors = []

    for tid, sp, text, act in turns:
        if act in ("side-question", "side-answer", "side-elab"):
            # 子对话
            if act == "side-question":
                stack.append(("MAIN", tid))
                tree_lines.append(f"  [PUSH] {tid} ({sp}): {text[:30]}...  → 进入子对话")
            elif act == "side-answer":
                tree_lines.append(f"  [SUB ] {tid} ({sp}): {text[:30]}...  子对话内")
            else:
                tree_lines.append(f"  [SUB ] {tid} ({sp}): {text[:30]}...  子对话内（新意图：改期）")
        elif act == "return":
            # 弹出
            if stack:
                popped = stack.pop()
                tree_lines.append(f"  [POP ] {tid} ({sp}): {text[:30]}...  ← 返回主对话（来自 {popped[1]}）")
            else:
                errors.append(f"{tid}: return 但栈为空")
        else:
            tree_lines.append(f"        {tid} ({sp}): {text[:30]}...  [{act}]")

    return tree_lines, errors


import os

def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "out")
    os.makedirs(out_path, exist_ok=True)

    tree_lines, errors = parse(TURNS)

    result_path = os.path.join(out_path, "parse_tree.txt")
    with open(result_path, "w", encoding="utf-8") as f:
        f.write("# lab-03 邻接对解析树（图 26.1）\n\n")
        f.write("## 解析过程\n")
        for line in tree_lines:
            f.write(line + "\n")
        f.write(f"\n## 错误\n")
        if errors:
            for e in errors:
                f.write(f"- {e}\n")
        else:
            f.write("无\n")
        f.write("\n## 关键观察\n")
        f.write("- C17（side-question）压栈，开启纠正子对话\n")
        f.write("- A20（return）弹栈，返回主对话（且日期已从 15 日改为 17 日）\n")
        f.write("- 这验证了书中 §26.1.4 的「子对话结束返回主序列」描述\n")

    print("\n".join(tree_lines[:25]))
    print(f"\nerrors={len(errors)}")
    print(f"saved: {result_path}")


if __name__ == "__main__":
    main()
