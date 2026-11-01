#!/usr/bin/env python3
"""lab-05: UAS / LAS / LS 与标注一致性（§20.4）。"""
import csv, json, os
from collections import Counter

ROOT = 0
WORDS = ["Book", "me", "the", "flight", "through", "Houston"]
GOLD = [(0, 1, "root"), (1, 2, "iobj"), (1, 4, "obj"), (4, 3, "det"),
        (4, 5, "nmod"), (5, 6, "pobj")]
# 系统输出：the 的 head 错挂到 Book（头错）；flight 的标签标成 nmod（标错）
SYS = [(0, 1, "root"), (1, 2, "iobj"), (1, 4, "nmod"), (1, 3, "det"),
       (4, 5, "nmod"), (5, 6, "pobj")]


def key(arcs, with_label):
    return {(h, d, l) if with_label else (h, d) for (h, d, l) in arcs}


def main():
    os.makedirs("out", exist_ok=True)
    n = len(WORDS)
    uas_num = len(key(GOLD, False) & key(SYS, False))
    las_num = len(key(GOLD, True) & key(SYS, True))
    ls_num = sum(1 for g, s in zip(sorted(GOLD), sorted(SYS)) if g[2] == s[2])
    metrics = [
        ["UAS", uas_num, n, uas_num / n],
        ["LAS", las_num, n, las_num / n],
        ["LS", ls_num, n, ls_num / n],
        ["EM", int(sorted(GOLD) == sorted(SYS)), 1, float(sorted(GOLD) == sorted(SYS))],
    ]
    with open("out/metrics.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["metric", "correct", "total", "score"])
        for m in metrics:
            w.writerow([m[0], m[1], m[2], f"{m[3]:.4f}"])

    rows = []
    sys_map = {(h, d): l for (h, d, l) in SYS}
    for (h, d, l) in GOLD:
        sh, sl = None, None
        for (h2, d2, l2) in SYS:
            if d2 == d:
                sh, sl = h2, l2
        rows.append([WORDS[d - 1], h, d, l, sh, sl,
                     int(h == sh), int(h == sh and l == sl), int(l == sl)])
    with open("out/per_word.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["word", "gold_head", "dep_index", "gold_label",
                    "sys_head", "sys_label", "uas_hit", "las_hit", "ls_hit"])
        w.writerows(rows)

    conf = Counter((g[2], s[2]) for g, s in zip(sorted(GOLD), sorted(SYS)))
    with open("out/label_confusion.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["gold_label", "sys_label", "count"])
        for (a, b), c in sorted(conf.items()):
            w.writerow([a, b, c])

    print("== lab-05 UAS / LAS / LS ==")
    print(f"  句子: {' '.join(WORDS)}（词数 {n}）")
    for m in metrics:
        print(f"  {m[0]}: {m[1]}/{m[2]} = {m[3]:.4f}")
    print(f"  UAS-LAS 差 = {uas_num/n - las_num/n:.4f}（差 1 条弧：标签错而头对）")
    print("  逐词 UAS 命中:", ", ".join(f"{r[0]}={r[6]}" for r in rows))
    json.dump({"uas": uas_num / n, "las": las_num / n, "ls": ls_num / n,
               "em": float(sorted(GOLD) == sorted(SYS))},
              open("out/summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
