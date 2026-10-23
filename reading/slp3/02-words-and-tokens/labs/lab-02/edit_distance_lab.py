#!/usr/bin/env python3
"""Lab 02: 最小编辑距离（Levenshtein DP）+ 回溯对齐。

对应 actions.md 行动 3；对应《Speech and Language Processing》§2.9。
插/删代价 1、替换代价 2（书中的版本），同时给出替换代价 1 的对照。
只依赖标准库 + numpy + matplotlib。
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
OUT.mkdir(parents=True, exist_ok=True)

PAIRS = [
    ("intention", "execution"),
    ("recieve", "receive"),
    ("seperate", "separate"),
    ("definately", "definitely"),
    ("accomodate", "accommodate"),
    ("teh", "the"),
    ("词元化", "词原化"),
]


def edit_distance(source: str, target: str, sub_cost: int = 2) -> tuple[int, np.ndarray, list[list[str]]]:
    n, m = len(source), len(target)
    D = np.zeros((n + 1, m + 1), dtype=int)
    for i in range(1, n + 1):
        D[i][0] = i
    for j in range(1, m + 1):
        D[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            diag = D[i - 1][j - 1] + (0 if source[i - 1] == target[j - 1] else sub_cost)
            D[i][j] = min(D[i - 1][j] + 1, D[i][j - 1] + 1, diag)
    return int(D[n][m]), D, backtrace(source, target, D, sub_cost)


def backtrace(source: str, target: str, D: np.ndarray, sub_cost: int) -> list[list[str]]:
    i, j = len(source), len(target)
    ops: list[list[str]] = []
    while i > 0 or j > 0:
        if i > 0 and j > 0 and source[i - 1] == target[j - 1] and D[i][j] == D[i - 1][j - 1]:
            ops.append(["=", source[i - 1], target[j - 1]])
            i, j = i - 1, j - 1
        elif i > 0 and j > 0 and D[i][j] == D[i - 1][j - 1] + sub_cost:
            ops.append(["s", source[i - 1], target[j - 1]])
            i, j = i - 1, j - 1
        elif i > 0 and D[i][j] == D[i - 1][j] + 1:
            ops.append(["d", source[i - 1], ""])
            i -= 1
        else:
            ops.append(["i", "", target[j - 1]])
            j -= 1
    ops.reverse()
    return ops


def render_path(source: str, target: str, ops: list[list[str]]) -> list[tuple[int, int]]:
    i = j = 0
    path = [(0, 0)]
    for op, s_ch, t_ch in ops:
        if op in ("=", "s"):
            i, j = i + 1, j + 1
        elif op == "d":
            i += 1
        else:
            j += 1
        path.append((i, j))
    return path


def main() -> None:
    results = []
    alignment_rows = []
    for source, target in PAIRS:
        d2, D2, ops2 = edit_distance(source, target, sub_cost=2)
        d1, _, _ = edit_distance(source, target, sub_cost=1)
        results.append(
            {
                "source": source,
                "target": target,
                "distance_sub2": d2,
                "distance_sub1": d1,
                "n_ops": len([o for o in ops2 if o[0] != "="]),
                "substitutions": sum(1 for o in ops2 if o[0] == "s"),
                "deletions": sum(1 for o in ops2 if o[0] == "d"),
                "insertions": sum(1 for o in ops2 if o[0] == "i"),
            }
        )
        alignment_rows.append(
            {
                "source": source,
                "target": target,
                "operations": " ".join(o[0] for o in ops2),
                "alignment": " ".join(
                    (o[1] if o[1] else "-") + "/" + (o[2] if o[2] else "-") for o in ops2
                ),
            }
        )

    with (OUT / "distances.json").open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    with (OUT / "alignments.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["source", "target", "operations", "alignment"])
        writer.writeheader()
        writer.writerows(alignment_rows)

    # 书中的例子：完整保存 DP 表与回溯路径。
    source, target = "intention", "execution"
    d2, D, ops = edit_distance(source, target, sub_cost=2)
    with (OUT / "dp_matrix_intention_execution.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["#"] + list(target))
        writer.writerow(["#"] + [int(x) for x in D[0]])
        for i, ch in enumerate(source, 1):
            writer.writerow([ch] + [int(x) for x in D[i]])

    path = render_path(source, target, ops)
    fig, ax = plt.subplots(figsize=(6.6, 5.4))
    im = ax.imshow(D, cmap="Blues", origin="upper")
    for i in range(D.shape[0]):
        for j in range(D.shape[1]):
            ax.text(j, i, int(D[i][j]), ha="center", va="center", fontsize=8, color="#1a202c")
    xs = [p[1] for p in path]
    ys = [p[0] for p in path]
    ax.plot(xs, ys, color="#e53e3e", lw=2.2, marker="o", ms=4)
    ax.set_xticks(range(len(target) + 1))
    ax.set_xticklabels(["#"] + list(target))
    ax.set_yticks(range(len(source) + 1))
    ax.set_yticklabels(["#"] + list(source))
    ax.set_xlabel("target: execution")
    ax.set_ylabel("source: intention")
    ax.set_title(f"Levenshtein DP (sub=2), distance={d2}")
    fig.colorbar(im, ax=ax, shrink=0.8)
    fig.tight_layout()
    fig.savefig(OUT / "edit_distance_matrix.png", dpi=160)
    plt.close(fig)

    # 距离对比条形图，便于检查拼写纠错候选。
    labels = [f"{s}->{t}" if s.isascii() and t.isascii() else "ZH pair" for s, t in PAIRS]
    vals2 = [r["distance_sub2"] for r in results]
    vals1 = [r["distance_sub1"] for r in results]
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(x - 0.2, vals2, 0.4, label="sub cost 2", color="#2b6cb0")
    ax.bar(x + 0.2, vals1, 0.4, label="sub cost 1", color="#dd6b20")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=8)
    ax.set_ylabel("edit distance")
    ax.set_title("Spelling pairs under two Levenshtein variants")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "distance_comparison.png", dpi=160)
    plt.close(fig)

    assert d2 == 8, "书中 intention→execution 的替换代价 2 版本应为 8"
    print(json.dumps({"book_example_distance": d2, "results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
