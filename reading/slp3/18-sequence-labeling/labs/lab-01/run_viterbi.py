#!/usr/bin/env python3
"""lab-01: 用书中图 18.12 的 A 表与图 18.13 的 B 表，手推一遍 bigram HMM 维特比。

输出:
  out/viterbi_grid.csv      每个 (t, tag) 的 log 分数与回溯来源
  out/path.txt              解码路径 + 两种基线对照
  out/checks.json           行归一化、金标准路径、2.772e-8 复现偏差
"""
import csv
import json
import os

import numpy as np

TAGS = ["NNP", "MD", "VB", "JJ", "NN", "RB", "DT"]
WORDS = ["Janet", "will", "back", "the", "bill"]

# 图 18.12：A[t_prev, t]，行为条件事件；最后一行 <s> 移出单列
A_ROWS = {
    "<s>": [0.2767, 0.0006, 0.0031, 0.0453, 0.0449, 0.0510, 0.2026],
    "NNP": [0.3777, 0.0110, 0.0009, 0.0084, 0.0584, 0.0090, 0.0025],
    "MD":  [0.0008, 0.0002, 0.7968, 0.0005, 0.0008, 0.1698, 0.0041],
    "VB":  [0.0322, 0.0005, 0.0050, 0.0837, 0.0615, 0.0514, 0.2231],
    "JJ":  [0.0366, 0.0004, 0.0001, 0.0733, 0.4509, 0.0036, 0.0036],
    "NN":  [0.0096, 0.0176, 0.0014, 0.0086, 0.1216, 0.0177, 0.0068],
    "RB":  [0.0068, 0.0102, 0.1011, 0.1012, 0.0120, 0.0728, 0.0479],
    "DT":  [0.1147, 0.0021, 0.0002, 0.2157, 0.4744, 0.0102, 0.0017],
}
# 图 18.13：B[t, word]
B = np.array([
    [0.000032, 0, 0, 0.000048, 0],
    [0, 0.308431, 0, 0, 0],
    [0, 0.000028, 0.000672, 0, 0.000028],
    [0, 0, 0.000340, 0, 0],
    [0, 0.000200, 0.000223, 0, 0.002337],
    [0, 0, 0.010446, 0, 0],
    [0, 0, 0, 0.506099, 0],
])
A = np.array([A_ROWS[t] for t in TAGS])
PI = np.array(A_ROWS["<s>"])
GOLD = ["NNP", "MD", "VB", "DT", "NN"]


def viterbi(logA, logB, logpi):
    """分数与回溯指针分开存：指针必须在取 max 的那一刻落下。"""
    n, T = logB.shape
    V = np.full((T, n), -np.inf)
    bp = np.full((T, n), -1, dtype=int)
    V[0] = logpi + logB[:, 0]
    for t in range(1, T):
        for j in range(n):
            cand = V[t - 1] + logA[:, j]
            i = int(np.argmax(cand))
            V[t, j] = cand[i] + logB[j, t]
            bp[t, j] = i
    j = int(np.argmax(V[T - 1]))
    path = [j]
    for t in range(T - 1, 0, -1):
        j = bp[t, j]
        path.append(j)
    return V, bp, [TAGS[k] for k in path[::-1]]


def main():
    os.makedirs("out", exist_ok=True)
    with np.errstate(divide="ignore"):
        logA, logB, logpi = np.log(A), np.log(B), np.log(PI)
    V, bp, path = viterbi(logA, logB, logpi)

    with open("out/viterbi_grid.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "word"] + TAGS)
        for t in range(len(WORDS)):
            w.writerow([t, WORDS[t]] + [f"{v:.6e}" for v in V[t]])
        w.writerow([])
        w.writerow(["backpointer(t>=1)"] + TAGS)
        for t in range(1, len(WORDS)):
            w.writerow([t] + [TAGS[i] if i >= 0 else "-" for i in bp[t]])

    row_sums = A.sum(axis=1)
    # 两种基线：全标 NNP；逐词取发射表里最大的标签
    all_nnp = ["NNP"] * len(WORDS)
    mft = [TAGS[int(np.argmax(B[:, k]))] for k in range(len(WORDS))]
    acc = lambda p: sum(x == y for x, y in zip(p, GOLD)) / len(GOLD)

    checks = {
        "row_sums": {t: round(float(s), 4) for t, s in zip(TAGS, row_sums)},
        "row_sum_max_dev": float(np.abs(row_sums - 1).max()),
        "rows_not_normalized": [t for t, s in zip(TAGS, row_sums) if abs(s - 1) > 1e-3],
        "gold_path_recovered": path == GOLD,
        "decoded_path": path,
        "final_log_score": float(V[-1].max()),
        "final_prob": float(np.exp(V[-1].max())),
        "book_value_2.772e-8": 2.772e-8,
        "rel_diff_will_MD_vs_book": float(
            abs(np.exp(V[1][TAGS.index("MD")]) - 2.772e-8) / 2.772e-8),
        "will_MD_cell_prob": float(np.exp(V[1][TAGS.index("MD")])),
        "baseline_all_NNP_acc": acc(all_nnp),
        "baseline_most_frequent_tag_acc": acc(mft),
        "baseline_mft_path": mft,
        "hmm_acc": acc(path),
    }
    with open("out/checks.json", "w") as f:
        json.dump(checks, f, ensure_ascii=False, indent=2)
    with open("out/path.txt", "w") as f:
        f.write("gold   : " + " ".join(f"{w}/{t}" for w, t in zip(WORDS, GOLD)) + "\n")
        f.write("viterbi: " + " ".join(f"{w}/{t}" for w, t in zip(WORDS, path)) + "\n")
        f.write("MFT基线: " + " ".join(f"{w}/{t}" for w, t in zip(WORDS, mft)) + "\n")
        f.write(f"最终概率 {checks['final_prob']:.4e}；书中 will/MD 格 2.772e-8，"
                f"本表复算 {checks['will_MD_cell_prob']:.4e}\n")
    print(json.dumps(checks, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
