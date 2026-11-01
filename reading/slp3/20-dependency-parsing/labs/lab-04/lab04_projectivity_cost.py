#!/usr/bin/env python3
"""lab-04: 投射约束的代价（§20.1.2 / §20.3.2）。

做法：n≤6 的随机图上穷举所有树，再筛出「无交叉弧」的投射树，
比较「全树最优」与「投射最优」的分数差 —— 这就是投射解析器
（Eisner 之类 O(n^3) 算法）相对于 MST 的结构性上限。
"""
import csv, itertools, json, os, random

INF = -10 ** 9
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)


def all_trees(n):
    """枚举所有以 0 为唯一根的树。"""
    words = list(range(1, n + 1))
    for choice in itertools.product(range(0, n + 1), repeat=n):
        heads = dict(zip(words, choice))
        if any(h == v for v, h in heads.items()):
            continue
        if sum(1 for h in heads.values() if h == 0) != 1:
            continue
        ok = True
        for v in words:
            seen, cur = set(), v
            while cur != 0:
                if cur in seen:
                    ok = False
                    break
                seen.add(cur)
                cur = heads[cur]
            if not ok:
                break
        if ok:
            yield heads


def projective(heads):
    arcs = [(h, d) for d, h in heads.items() if h != 0]
    for i in range(len(arcs)):
        a, b = min(arcs[i]), max(arcs[i])
        for j in range(i + 1, len(arcs)):
            c, d = min(arcs[j]), max(arcs[j])
            if a < c < b < d or c < a < d < b:
                return False
    return True


def best_both(score, n):
    """一次遍历同时求「全树最优」与「投射最优」。"""
    ba = bp = INF
    ha = None
    for h in all_trees(n):
        s = sum(score[(h[v], v)] for v in h)
        if s > ba:
            ba, ha = s, h
        if s > bp and projective(h):
            bp = s
    return ba, bp, ha


def main():
    print("== lab-04 投射 vs 非投射：穷举小图 ==")
    random.seed(20261101)
    rows = []
    for n in (4, 5, 6):
        for trial in range(30):
            sc = {(u, v): random.randint(-9, 9)
                  for u in range(n + 1) for v in range(n + 1) if u != v and v != 0}
            sa, sp, ha = best_both(sc, n)
            rows.append({"n": n, "trial": trial, "best_all": sa, "best_proj": sp,
                         "gap": sa - sp, "best_is_projective": int(projective(ha))})
    with open(os.path.join(OUT, "projective_gap.csv"), "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=["n", "trial", "best_all", "best_proj",
                                           "gap", "best_is_projective"])
        wr.writeheader()
        wr.writerows(rows)
    gaps = [r["gap"] for r in rows]
    lossy = [r for r in rows if r["gap"] > 0]
    print(f"  图数 {len(rows)}，其中最优树非投射 {len(lossy)} 张 "
          f"({len(lossy)/len(rows):.1%})")
    print(f"  平均分数损失 {sum(gaps)/len(gaps):.2f}，最大 {max(gaps)}")
    for n in (4, 5, 6):
        sub = [r for r in rows if r["n"] == n]
        print(f"    n={n}: 非投射最优 {sum(1 for r in sub if r['gap']>0)}/{len(sub)}，"
              f"平均损失 {sum(r['gap'] for r in sub)/len(sub):.2f}")

    # 书中的非投射句：交叉弧检测
    sent = "JetBlue canceled our flight this morning which was already late".split()
    arcs = [(2, 1, "nsubj"), (0, 2, "root"), (2, 4, "obj"), (4, 3, "det"),
            (2, 6, "obl"), (6, 5, "det"), (4, 10, "acl:relcl"), (10, 7, "nsubj"),
            (10, 8, "cop"), (10, 9, "adv")]
    heads = {d: h for h, d, _ in arcs}
    cross = []
    body = [(h, d) for h, d, _ in arcs if h != 0]
    for i in range(len(body)):
        for j in range(i + 1, len(body)):
            a, b = sorted(body[i]); c, e = sorted(body[j])
            if a < c < b < e or c < a < e < b:
                cross.append((body[i], body[j]))
    print(f"  {len(sent)} 词 / {len(arcs)} 弧，交叉对 {len(cross)} → "
          f"projective={not cross}")
    for (h1, d1), (h2, d2) in cross:
        print(f"    交叉: {h1}->{d1}({sent[h1-1]}->{sent[d1-1]}) × "
              f"{h2}->{d2}({sent[h2-1]}->{sent[d2-1]})")
    json.dump({"graphs": len(rows), "lossy": len(lossy),
               "mean_gap": round(sum(gaps) / len(gaps), 2), "max_gap": max(gaps),
               "crossing_pairs": [[list(a), list(b)] for a, b in cross],
               "projective": not cross},
              open(os.path.join(OUT, "summary.json"), "w"), indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
