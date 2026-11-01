#!/usr/bin/env python3
"""lab-05 会话含义推理链模拟（对应 §26.1.6）。

基于 Grice 关联准则，模拟书中例子：
客户说「我有个会议从 12 号到 15 号」 → 代理推断「建议订 11 号的航班」。
展示完整推理链。
"""

CHAIN = [
    {
        "step": 1,
        "rule": "关联准则：说话人所述必与话题相关",
        "input": "客户提到「我有个会议从 12 号到 15 号」",
        "inference": "提到会议不是闲聊，必与「何时出行」有关",
        "needs_knowledge": "Grice 关联准则（§26.1.6）",
    },
    {
        "step": 2,
        "rule": "世界知识：开会的先决条件是人要身处会议举行地",
        "input": "会议从 12 号到 15 号",
        "inference": "客户需要在 12 号之前抵达",
        "needs_knowledge": "开会的空间前提（§26.1.6 括号：至少在网络会议出现之前）",
    },
    {
        "step": 3,
        "rule": "常识：人们通常喜欢在会议前一天到达",
        "input": "需要在 12 号之前抵达",
        "inference": "建议在 11 号抵达",
        "needs_knowledge": "旅行常识（§26.1.6 原文）",
    },
    {
        "step": 4,
        "rule": "推理输出",
        "input": "建议在 11 号抵达",
        "inference": "建议订 11 号的航班（甚至 11 号前一天晚上 5 点左右，即图 26.1 C11 的选择）",
        "needs_knowledge": "—",
    },
]


def main():
    import os
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(out_dir, exist_ok=True)

    lines = ["# lab-05 会话含义推理链（基于 Grice 关联准则）", ""]
    lines.append("输入：客户说「我有个会议从 12 号到 15 号」（未直接回答「你想哪天出行」）")
    lines.append("输出：建议订 11 号的航班（或前一天晚上）")
    lines.append("")
    for c in CHAIN:
        lines.append(f"## Step {c['step']}")
        lines.append(f"- 规则：{c['rule']}")
        lines.append(f"- 输入：{c['input']}")
        lines.append(f"- 推断：{c['inference']}")
        lines.append(f"- 依赖知识：{c['needs_knowledge']}")
        lines.append("")

    text = "\n".join(lines)
    print(text)

    out_path = os.path.join(out_dir, "reasoning_chain.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"saved: {out_path}")


if __name__ == "__main__":
    main()
