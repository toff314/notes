#!/usr/bin/env python3
"""Lab 04: 代理指标（token 集合 F1）如何被"刷分"，复现古德哈特定律。

说明：句对与 adequacy 分数是**构造的教学样例**（adequacy 为人工设定的示意值），
但 overlap 由脚本真实计算，选择过程与结论可复现。目的是演示 §1.9.4 的逻辑，
不是报告真实翻译系统的质量。

输出：out/candidates.csv、out/summary.json、out/overlap_vs_adequacy.png
"""
from __future__ import annotations

import csv
import json
import statistics
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# (源句, 参考译文, [(候选译文, 示意 adequacy 1-5, 是否刷分候选), ...])
DATA = [
    ("猫坐在垫子上。", "the cat sat on the mat", [
        ("a cat was sitting on the mat", 5, False),
        ("a cat sat on the mat", 4, False),
        ("the cat is on the mat", 4, False),
        ("the the cat cat sat sat on on the the mat mat", 1, True),
    ]),
    ("她昨天买了一本书。", "she bought a book yesterday", [
        ("yesterday she bought a book", 5, False),
        ("she purchased a book yesterday", 5, False),
        ("she bought one book yesterday", 4, False),
        ("she she bought bought a a book book yesterday yesterday", 1, True),
    ]),
    ("会议推迟到下周一。", "the meeting was postponed until next monday", [
        ("the meeting was put off until next monday", 5, False),
        ("next monday the meeting was postponed", 5, False),
        ("the meeting postponed to next monday", 4, False),
        ("until until next next monday monday the the meeting meeting was was postponed postponed", 1, True),
    ]),
    ("他没有通过考试。", "he did not pass the exam", [
        ("he failed the exam", 5, False),
        ("he did not succeed in the exam", 4, False),
        ("he did not pass exam", 3, False),
        ("he he did did not not pass pass the the exam exam", 1, True),
    ]),
    ("请把窗户关上。", "please close the window", [
        ("could you please close the window", 5, False),
        ("close the window please", 5, False),
        ("please shut the window", 5, False),
        ("window window please please close close the the", 1, True),
    ]),
    ("孩子们在花园里玩。", "the children are playing in the garden", [
        ("the kids are playing in the garden", 5, False),
        ("in the garden the children are playing", 5, False),
        ("the children play in the garden", 4, False),
        ("garden garden the the children children are are playing playing in in", 1, True),
    ]),
]


def token_f1(candidate: str, reference: str) -> float:
    """集合式 token F1：只看用了哪些词，不看顺序与次数。"""
    c, r = set(candidate.split()), set(reference.split())
    if not c or not r:
        return 0.0
    precision, recall = len(c & r) / len(c), len(c & r) / len(r)
    return 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)


def main() -> None:
    out = Path(__file__).parent / "out"
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for sid, (source, ref, cands) in enumerate(DATA, 1):
        for cid, (text, adequacy, gamed) in enumerate(cands, 1):
            rows.append({
                "source_id": sid,
                "candidate_id": cid,
                "source": source,
                "reference": ref,
                "candidate": text,
                "overlap_f1": round(token_f1(text, ref), 4),
                "adequacy": adequacy,
                "gamed": int(gamed),
                "selected_by_overlap": 0,
            })

    selected = []
    for sid in range(1, len(DATA) + 1):
        group = [r for r in rows if r["source_id"] == sid]
        best = max(group, key=lambda r: r["overlap_f1"])  # 平局取先出现者
        best["selected_by_overlap"] = 1
        selected.append(best)

    with (out / "candidates.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    oracle = [max(r["adequacy"] for r in rows if r["source_id"] == sid)
              for sid in range(1, len(DATA) + 1)]
    xs = [r["overlap_f1"] for r in rows]
    ys = [r["adequacy"] for r in rows]
    mean_x, mean_y = statistics.fmean(xs), statistics.fmean(ys)
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    denom = (sum((x - mean_x) ** 2 for x in xs) * sum((y - mean_y) ** 2 for y in ys)) ** 0.5
    summary = {
        "note": "句对与 adequacy 为构造的教学样例；overlap 由脚本计算，选择和结论可复现。",
        "n_sources": len(DATA),
        "n_candidates": len(rows),
        "mean_overlap_selected_adequacy": round(statistics.fmean(r["adequacy"] for r in selected), 3),
        "mean_oracle_adequacy": round(statistics.fmean(oracle), 3),
        "n_gamed_selected": sum(r["gamed"] for r in selected),
        "pearson_overlap_vs_adequacy": round(cov / denom, 4) if denom else None,
        "selected": [
            {"source_id": r["source_id"], "candidate": r["candidate"],
             "overlap_f1": r["overlap_f1"], "adequacy": r["adequacy"], "gamed": bool(r["gamed"])}
            for r in selected
        ],
    }
    (out / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    plt.rcParams["font.sans-serif"] = ["Noto Sans CJK JP", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4))
    for i, r in enumerate(rows):
        color = "#c0392b" if r["gamed"] else "#2c7fb8"
        marker = "*" if r["selected_by_overlap"] else "o"
        # 仅绘图抖动，避免同分点完全重叠；CSV/JSON 中仍是精确值
        dx = ((i % 3) - 1) * 0.006
        dy = ((i // 3) % 3 - 1) * 0.06
        ax1.scatter(r["overlap_f1"] + dx, r["adequacy"] + dy, c=color, marker=marker,
                    s=150 if r["selected_by_overlap"] else 55)
    ax1.text(0.01, 0.02, "为避免同分重叠，绘图点有 ±0.006/±0.06 抖动；数值见 CSV",
             transform=ax1.transAxes, fontsize=7, color="#555")
    ax1.set_xlabel("token 集合 F1（代理指标）")
    ax1.set_ylabel("adequacy（示意的人工分）")
    ax1.set_title("代理指标高 ≠ 质量高（星号=按 overlap 选中）")
    ax1.grid(alpha=0.3)

    labels = ["按 overlap 选", "按人工分最优"]
    values = [summary["mean_overlap_selected_adequacy"], summary["mean_oracle_adequacy"]]
    bars = ax2.bar(labels, values, color=["#c0392b", "#2c7fb8"])
    for b, v in zip(bars, values):
        ax2.text(b.get_x() + b.get_width() / 2, v + 0.08, f"{v:.2f}", ha="center")
    ax2.set_ylim(0, 5.5)
    ax2.set_ylabel("平均 adequacy")
    ax2.set_title(f"6 组候选中，刷分候选被选中 {summary['n_gamed_selected']} 次")
    fig.tight_layout()
    fig.savefig(out / "overlap_vs_adequacy.png", dpi=160)

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
