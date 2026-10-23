#!/usr/bin/env python3
"""Lab 03: 复现书 §11.2 的排序评价 —— 逐排名精确率/召回率、AP、11 点插值精确率。

判定序列取自图 11.7（25 篇文档，9 篇相关，R/N 逐条列出）。
书上给出的两个可核对数字：AP = 0.6；11 点插值表的首尾为 1.0 与 0.36。

运行: python3 pr_metrics.py
产物: out/per_rank.csv, out/interpolated.csv, out/summary.json,
      out/pr_curve.png, out/interpolated_curve.png
"""
import json
import os

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

for _fp in ("/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/google-noto-cjk/NotoSansCJK-DemiLight.ttc"):
    if os.path.exists(_fp):
        font_manager.fontManager.addfont(_fp)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

# 图 11.7 的 judgment 列，rank 1..25
JUDGMENTS = list("RNRNRRNRNN" + "RNNNRNNRNN" + "NNNNR")
TOTAL_RELEVANT = 9

# 图 11.9 / 11.10 的 11 点插值表（召回率 -> 精确率），用于对照
BOOK_TABLE = [1.0, 1.0, 0.66, 0.66, 0.66, 0.63, 0.55, 0.47, 0.44, 0.36, 0.36]


def main():
    os.makedirs(OUT, exist_ok=True)
    assert len(JUDGMENTS) == 25, len(JUDGMENTS)
    assert sum(j == "R" for j in JUDGMENTS) == TOTAL_RELEVANT

    rows = []
    hits = 0
    for i, j in enumerate(JUDGMENTS, 1):
        hits += j == "R"
        rows.append({
            "rank": i,
            "judgment": j,
            "precision": hits / i,
            "recall": hits / TOTAL_RELEVANT,
        })

    # AP = 只在与相关文档相遇的位置取精确率，再平均
    ap_terms = [r["precision"] for r in rows if r["judgment"] == "R"]
    ap = sum(ap_terms) / TOTAL_RELEVANT

    # 11 点插值：每个召回率水平取"该水平及更高处"的最大精确率
    levels = [i / 10 for i in range(11)]
    interp = []
    for lv in levels:
        candidates = [r["precision"] for r in rows if r["recall"] >= lv - 1e-9]
        interp.append({
            "recall_level": lv,
            "interpolated_precision": max(candidates) if candidates else 0.0,
        })

    # 与书表对照（书表值保留两位，容差 0.01）
    diffs = [abs(round(x["interpolated_precision"], 2) - b)
             for x, b in zip(interp, BOOK_TABLE)]

    with open(os.path.join(OUT, "per_rank.csv"), "w", encoding="utf-8") as f:
        f.write("rank,judgment,precision,recall\n")
        for r in rows:
            f.write(f"{r['rank']},{r['judgment']},{r['precision']:.4f},{r['recall']:.4f}\n")

    with open(os.path.join(OUT, "interpolated.csv"), "w", encoding="utf-8") as f:
        f.write("recall_level,interpolated_precision,book_table\n")
        for x, b in zip(interp, BOOK_TABLE):
            f.write(f"{x['recall_level']:.1f},{x['interpolated_precision']:.4f},{b:.2f}\n")

    summary = {
        "n_docs": len(JUDGMENTS),
        "n_relevant": TOTAL_RELEVANT,
        "average_precision": ap,
        "book_average_precision": 0.6,
        "map_single_query": ap,
        "max_abs_diff_vs_book_table": max(diffs),
        "interpolated": interp,
        "book_table": BOOK_TABLE,
    }
    with open(os.path.join(OUT, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    plt.rcParams["font.family"] = ["Noto Sans CJK JP", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

    # 图 1：原始精确率-召回率折线 + 散点
    rec = [r["recall"] for r in rows]
    prec = [r["precision"] for r in rows]
    fig, ax = plt.subplots(figsize=(6.8, 4.4))
    ax.plot(rec, prec, "-o", ms=4, lw=1.4, color="#4C78A8", label="逐排名测得")
    for r in rows:
        if r["judgment"] == "R":
            ax.annotate(f"r{r['rank']}", (r["recall"], r["precision"]),
                        textcoords="offset points", xytext=(4, 5), fontsize=7)
    ax.set_xlabel("召回率")
    ax.set_ylabel("精确率")
    ax.set_xlim(0, 1.05)
    ax.set_ylim(0, 1.05)
    ax.set_title(f"图 11.7 数据的精确率-召回率曲线（AP={ap:.3f}）")
    ax.grid(alpha=0.25, ls="--")
    ax.legend(frameon=False, loc="lower left")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "pr_curve.png"), dpi=160)

    # 图 2：11 点插值 vs 书表
    lv = [x["recall_level"] for x in interp]
    ip = [x["interpolated_precision"] for x in interp]
    fig, ax = plt.subplots(figsize=(6.8, 4.4))
    ax.step(lv, ip, where="post", lw=2.0, color="#E45756", label="本 lab 计算")
    ax.plot(lv, BOOK_TABLE, "s", ms=5, color="#54A24B", label="书图 11.9 读数")
    ax.set_xlabel("召回率")
    ax.set_ylabel("插值精确率")
    ax.set_xlim(-0.03, 1.03)
    ax.set_ylim(0, 1.1)
    ax.set_title("11 点插值精确率：计算结果与书上表格重合")
    ax.grid(alpha=0.25, ls="--")
    ax.legend(frameon=False, loc="lower left")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "interpolated_curve.png"), dpi=160)

    print(f"AP = {ap:.4f}（书 §11.2 报 0.6）")
    print(f"11 点插值 max|diff| vs 书表 = {max(diffs):.3f}")
    print("插值表:", [round(x, 3) for x in ip])
    print("wrote", OUT)


if __name__ == "__main__":
    main()
