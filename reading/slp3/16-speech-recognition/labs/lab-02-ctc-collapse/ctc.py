#!/usr/bin/env python3
"""lab-02: CTC 折叠函数与「对所有对齐求和」（SLP3 §16.5–16.5.2）

1. T=3、字母表 {a,b,ε}，穷举 3^3=27 条对齐，按折叠函数 B 聚合出每个输出串的概率
2. 用前向 DP 复算同一概率，与暴力枚举对照（检验实现）
3. 随机搜索「逐帧 argmax 所属输出 ≠ 概率最大的输出」的实例（书中 §16.5.1 的结论）
4. dinner → diner：演示空白符作为重复字母分隔符的作用
输出：out/alignments.csv、out/summary.json
"""
import csv, itertools, json, os
import numpy as np

SYM = ["a", "b", "ε"]


def collapse(seq):
    out, prev = [], None
    for s in seq:
        if s != prev and s != "ε":
            out.append(s)
        prev = s
    return "".join(out)


def brute(probs):
    """probs: T×C 概率矩阵 -> {输出串: 概率}"""
    T, _ = probs.shape
    agg = {}
    for path in itertools.product(range(len(SYM)), repeat=T):
        p = 1.0
        for t, k in enumerate(path):
            p *= probs[t, k]
        y = collapse([SYM[k] for k in path])
        agg[y] = agg.get(y, 0.0) + p
    return agg


def forward(y, probs):
    """CTC 前向算法：对所有折叠为 y 的路径求和"""
    T, _ = probs.shape
    if y == "":
        return float(np.prod(probs[:, SYM.index("ε")]))
    ext = ["ε"]
    for c in y:
        ext += [c, "ε"]
    S = len(ext)
    idx = {s: [i for i, c in enumerate(ext) if c == s] for s in SYM}
    al = np.zeros((T, S))
    al[0, 0] = probs[0, SYM.index("ε")]
    if S > 1:
        al[0, 1] = probs[0, SYM.index(y[0])]
    for t in range(1, T):
        for s in range(S):
            p = probs[t, SYM.index(ext[s])]
            acc = al[t - 1, s]
            if s >= 1:
                acc += al[t - 1, s - 1]
            if s >= 2 and ext[s] != "ε" and ext[s] != ext[s - 2]:
                acc += al[t - 1, s - 2]
            al[t, s] = acc * p
    return al[T - 1, S - 1] + (al[T - 1, S - 2] if S > 1 else 0.0)


def main():
    os.makedirs("out", exist_ok=True)
    # 书中 §16.5.1 的三帧例子（自定数值，仅用于演示）
    probs = np.array([[0.50, 0.40, 0.10],
                      [0.10, 0.50, 0.40],
                      [0.10, 0.30, 0.60]])
    agg = brute(probs)
    rows = []
    for y in sorted(agg):
        fw = forward(y, probs) if y else 0.0
        rows.append([y or "(空)", round(agg[y], 8), round(fw, 8), abs(agg[y] - fw)])
    with open("out/alignments.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["输出串Y", "暴力枚举P(Y|X)", "前向DP P(Y|X)", "绝对差"])
        w.writerows(rows)
    max_diff = max(r[3] for r in rows)

    # 逐帧 argmax 的解码结果
    greedy = "".join(SYM[k] for k in probs.argmax(axis=1))
    greedy_y = collapse(list(greedy))

    # 随机搜索 argmax 不一致的实例
    rng = np.random.default_rng(0)
    n_try, mismatch, best = 20000, 0, None
    for _ in range(n_try):
        P = rng.dirichlet([1, 1, 1], size=3)
        a = brute(P)
        g = collapse([SYM[k] for k in P.argmax(axis=1)])
        y_best = max(a, key=a.get)
        if g != y_best:
            mismatch += 1
            gap = a[y_best] - a.get(g, 0.0)
            if best is None or gap > best["gap"]:
                best = {"gap": float(gap), "greedy": g, "best": y_best,
                        "p_best": float(a[y_best]), "p_greedy": float(a.get(g, 0.0)),
                        "probs": P.round(3).tolist()}

    # dinner / diner
    dinner_frames = ["d", "i", "n", "ε", "n", "ε", "e", "r"]
    diner_frames = ["d", "i", "n", "n", "e", "r"]
    demo = {"有空白符": {"frames": dinner_frames, "collapse": collapse(dinner_frames)},
            "无空白符": {"frames": diner_frames, "collapse": collapse(diner_frames)}}

    summary = {
        "T": 3, "alphabet": SYM, "n_alignments": 3 ** 3,
        "n_distinct_outputs": len(agg),
        "brute_vs_dp_max_abs_diff": float(max_diff),
        "greedy_path": greedy, "greedy_output": greedy_y,
        "argmax_output": max(agg, key=agg.get),
        "random_trials": n_try, "mismatch_count": mismatch,
        "mismatch_rate": round(mismatch / n_try, 4),
        "max_gap_example": best,
        "dinner_demo": demo,
    }
    json.dump(summary, open("out/summary.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"对齐 {summary['n_alignments']} 条 → 不同输出 {len(agg)} 个")
    print(f"暴力枚举 vs 前向 DP 最大绝对差 = {max_diff:.2e}")
    print(f"逐帧 argmax: {greedy} → Y={greedy_y!r}；求和后最大 Y={max(agg, key=agg.get)!r}")
    print(f"随机 {n_try} 组：argmax 不一致 {mismatch} 次（{100*mismatch/n_try:.1f}%）")
    print("dinner:", demo)


if __name__ == "__main__":
    main()
