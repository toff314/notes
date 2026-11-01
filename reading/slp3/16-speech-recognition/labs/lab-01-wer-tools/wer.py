#!/usr/bin/env python3
"""lab-01: 词级最小编辑距离 / WER 复算（SLP3 §16.6）

- DP 求最小编辑距离并回溯出 S/I/D 序列
- 同一句对用「原始」与「去填充词」两版参考各算一次，量化规范化的影响
- 用两种回溯偏好（优先替换 vs 优先删除）演示对齐歧义：拆分不同、总数相同
- 复算书中 (6S+3I+1D)/13 的词错误率
输出：out/wer.csv、out/alignment.txt
"""
import csv, os

FILL = {"uh", "um", "er", "hmm"}


def norm(s, drop_fill=True):
    s = s.lower().replace(",", "").replace(".", "").replace("?", "")
    toks = [t for t in s.split() if t]
    return [t for t in toks if not (drop_fill and t in FILL)]


def align(ref, hyp, pref="S"):
    n, m = len(ref), len(hyp)
    INF = float("inf")
    D = [[INF] * (m + 1) for _ in range(n + 1)]
    P = [[None] * (m + 1) for _ in range(n + 1)]
    D[0][0] = 0
    for i in range(1, n + 1):
        D[i][0], P[i][0] = i, "D"
    for j in range(1, m + 1):
        D[0][j], P[0][j] = j, "I"
    order = ["C", "S", "D", "I"] if pref == "D" else ["C", "S", "I", "D"]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            sub = 0 if ref[i - 1] == hyp[j - 1] else 1
            cand = {"C" if sub == 0 else "S": D[i - 1][j - 1] + sub,
                    "D": D[i - 1][j] + 1, "I": D[i][j - 1] + 1}
            for op in order:
                if op in cand and cand[op] < D[i][j]:
                    D[i][j], P[i][j] = cand[op], op
    i, j, ops = n, m, []
    while i > 0 or j > 0:
        op = P[i][j]
        if op in ("C", "S"):
            ops.append((op, ref[i - 1], hyp[j - 1])); i -= 1; j -= 1
        elif op == "D":
            ops.append(("D", ref[i - 1], "*")); i -= 1
        else:
            ops.append(("I", "*", hyp[j - 1])); j -= 1
    # 统计最优路径条数：>1 说明该句对存在对齐歧义
    N = [[0] * (m + 1) for _ in range(n + 1)]
    N[0][0] = 1
    for i in range(n + 1):
        for j in range(m + 1):
            if i == 0 and j == 0:
                continue
            sub = 0 if (i > 0 and j > 0 and ref[i - 1] == hyp[j - 1]) else 1
            cand = []
            if i > 0 and j > 0:
                cand.append((D[i - 1][j - 1] + sub, N[i - 1][j - 1]))
            if i > 0:
                cand.append((D[i - 1][j] + 1, N[i - 1][j]))
            if j > 0:
                cand.append((D[i][j - 1] + 1, N[i][j - 1]))
            best = min(c for c, _ in cand)
            N[i][j] = sum(k for c, k in cand if c == best)
    return D[n][m], ops[::-1], N[n][m]


def counts(ops):
    return {k: sum(1 for o in ops if o[0] == k) for k in "CSDI"}


def wer(ops, n_ref):
    c = counts(ops)
    return 100.0 * (c["S"] + c["D"] + c["I"]) / max(n_ref, 1)


CASES = [
    ("A-单替换", "the cat sat on the mat", "the cat sat on a mat"),
    ("B-缩合+多错", "i want to go to the store tomorrow", "i wanna go store tomorrow"),
    ("C-带填充词", "um so the the phone is on the desk uh", "so the phone is on desk"),
    ("D-书中量级", "i the phone is i left the phone upstairs last night uh ok",
     "i got it to the full it i love phone form of stores last night"),
    ("E-对齐歧义", "a b c d", "c d a b"),
]


def main():
    os.makedirs("out", exist_ok=True)
    rows, lines = [], ["# 对齐明细（S=替换 D=删除 I=插入 C=正确）"]
    for name, ref_s, hyp_s in CASES:
        r_raw, h = norm(ref_s, False), norm(hyp_s, False)
        r_nrm = norm(ref_s)
        d1, ops1, npath = align(r_raw, h, "D")
        d2, ops_n, npath_n = align(r_nrm, h, "D")
        c1, c2, cn = counts(ops1), counts(ops2), counts(ops_n)
        rows.append([name, len(r_raw), c1["S"], c1["I"], c1["D"], round(wer(ops1, len(r_raw)), 2),
                     len(r_nrm), round(wer(ops_n, len(r_nrm)), 2),
                     npath, npath_n])
        lines.append(f"\n## {name}  ref={len(r_raw)}词  edit={d1}")
        lines.append("原始: " + " ".join(f"{o[0]}:{o[1]}→{o[2]}" for o in ops1))
        lines.append("规范: " + " ".join(f"{o[0]}:{o[1]}→{o[2]}" for o in ops_n))
        lines.append(f"S/I/D = {c1['S']}/{c1['I']}/{c1['D']}  WER_raw={wer(ops1,len(r_raw)):.2f}%  "
                     f"WER_norm={wer(ops_n,len(r_nrm)):.2f}%")
    with open("out/wer.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["case", "ref_words", "S", "I", "D", "WER_raw%", "ref_words_norm",
                    "WER_norm%", "最优路径条数", "规范化后路径条数"])
        w.writerows(rows)
    book = 100.0 * (6 + 3 + 1) / 13
    lines.append(f"\n## 书中例子复算\n13 词参考，S=6 I=3 D=1 → {book:.2f}%（书中 76.9%）；"
                 f"若分母误用假设词数 15 → {100*10/15:.2f}%，可见分母口径会改变结论。")
    open("out/alignment.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"书中例子: {book:.2f}%  （与书中 76.9% 差 {abs(book-76.9):.2f} 个百分点）")
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
