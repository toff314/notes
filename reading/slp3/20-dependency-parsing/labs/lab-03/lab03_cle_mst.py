#!/usr/bin/env python3
"""lab-03: 最大生成树（Edmonds / Chu-Liu，networkx 实现）与穷举最优树对拍（§20.3.1）。

单根约束：arborescence 只保证「0 无入弧、其余点唯一入弧」，并不禁止
0 有多个孩子；UD 要求恰好一个词挂 ROOT，故对每个候选根孩子各跑一次
Edmonds（n+1 次），取最优，与穷举定义严格对齐。
"""
import csv, itertools, json, os

import networkx as nx

INF = -10 ** 9
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)


def brute(nodes, w, root):
    """穷举所有合法树（唯一根 + 无环），返回最优分数与 heads。"""
    words = [v for v in nodes if v != root]
    best, best_h = INF, None
    for choice in itertools.product(nodes, repeat=len(words)):
        heads = dict(zip(words, choice))
        if any(h == v for v, h in heads.items()):
            continue
        if sum(1 for h in heads.values() if h == root) != 1:
            continue
        ok = True
        for v in words:
            seen, cur = set(), v
            while cur != root:
                if cur in seen:
                    ok = False
                    break
                seen.add(cur)
                cur = heads[cur]
            if not ok:
                break
        if not ok:
            continue
        s = sum(w.get((heads[v], v), INF) for v in words)
        if s > best:
            best, best_h = s, heads
    return best, best_h


def mst_once(nodes, w, root, forbid):
    """Edmonds 算法（networkx 实现，最小化 → 权重取负）；forbid 内的弧禁掉。"""
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    for (u, v), s in w.items():
        if v == root or (u, v) in forbid:
            continue
        G.add_edge(u, v, weight=-s)
    T = nx.minimum_spanning_arborescence(G)
    heads = {v: u for u, v in T.edges()}
    return sum(w[(heads[v], v)] for v in heads), heads


def mst(nodes, w, root):
    """加上「ROOT 恰好一个孩子」的约束：枚举根孩子 r，禁掉其余入根弧。"""
    best, bh = INF, None
    for r in nodes:
        if r == root:
            continue
        forbid = {(root, v) for v in nodes if v not in (root, r)}
        try:
            s, h = mst_once(nodes, w, root, forbid)
        except nx.NetworkXException:
            continue
        if s > best:
            best, bh = s, h
    return best, bh


TOY = "Book that flight"
TOY_W = {(0, 1): 9, (1, 2): 3, (2, 1): 6, (1, 3): 1, (2, 3): 5, (3, 1): 9,
         (0, 2): 8, (0, 3): 9, (3, 2): 7, (2, 0): 0}
# 只保留合法弧（无入根弧）
TOY_W = {k: v for k, v in TOY_W.items() if k[1] != 0}
for u in [0, 1, 2, 3]:
    for v in [1, 2, 3]:
        TOY_W.setdefault((u, v), -3)

CYC_W = {(0, 1): 5, (3, 1): 7, (0, 3): 4, (1, 3): 6, (2, 1): -2, (2, 3): -2,
         (1, 2): -4, (3, 2): -4, (0, 2): 1}
CYC_W = {k: v for k, v in CYC_W.items() if k[1] != 0}


def greedy_heads(nodes, w, root):
    heads = {}
    for v in nodes:
        if v == root:
            continue
        heads[v] = max(((w.get((u, v), INF), u) for u in nodes if u != v))[1]
    return heads


def has_cycle(root, heads):
    for v in heads:
        seen, cur = set(), v
        while cur in heads:
            if cur in seen:
                return sorted(seen)
            seen.add(cur)
            cur = heads[cur]
    return None


def main():
    print("== lab-03 Edmonds/Chu-Liu 最大生成树 ==")
    nodes = [0, 1, 2, 3]
    g = greedy_heads(nodes, TOY_W, 0)
    cyc = has_cycle(0, g)
    print(f"  贪心入弧（Book that flight）: {dict(sorted(g.items()))} 分数 "
          f"{sum(TOY_W[(g[v], v)] for v in g)}  环: {cyc}")
    s_mst, h_mst = mst(nodes, TOY_W, 0)
    s_bf, h_bf = brute(nodes, TOY_W, 0)
    print(f"  Edmonds 最优: {s_mst} heads={ {k: v for k, v in sorted(h_mst.items())} }")
    print(f"  穷举   最优: {s_bf} heads={ {k: v for k, v in sorted(h_bf.items())} }")
    print(f"  一致: {s_mst == s_bf and h_mst == h_bf}")

    g2 = greedy_heads([0, 1, 2, 3], CYC_W, 0)
    print(f"  人造 2 环样例：贪心 {dict(sorted(g2.items()))} 环={has_cycle(0, g2)}")
    s2, h2 = mst([0, 1, 2, 3], CYC_W, 0)
    s2b, h2b = brute([0, 1, 2, 3], CYC_W, 0)
    print(f"  收缩后最优 {s2} vs 穷举 {s2b} 一致={s2 == s2b}")

    # 400 张随机图对拍
    import random
    random.seed(20261101)
    rows, agree = [], 0
    for i in range(150):
        n = random.choice([4, 5, 6])
        ns = list(range(n + 1))
        w = {(u, v): random.randint(-9, 9) for u in ns for v in ns if u != v and v != 0}
        sa, ha = mst(ns, w, 0)
        sb, hb = brute(ns, w, 0)
        agree += (sa == sb)
        rows.append({"trial": i, "n": n, "mst": sa, "brute": sb,
                     "agree": int(sa == sb),
                     "same_heads": int(ha == hb)})
    with open(os.path.join(OUT, "mst_vs_brute.csv"), "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=["trial", "n", "mst", "brute", "agree", "same_heads"])
        wr.writeheader()
        wr.writerows(rows)
    same = sum(r["same_heads"] for r in rows)
    print(f"  随机对拍: 分数一致 {agree}/{len(rows)}；其中树完全相同 {same}（其余为同分不同树）")
    json.dump({"toy": {"greedy": g, "greedy_cycle": cyc, "mst": h_mst, "brute": h_bf,
                       "score": s_mst, "agree": s_mst == s_bf and h_mst == h_bf},
               "random_agree": agree, "random_same_heads": same,
               "random_total": len(rows)},
              open(os.path.join(OUT, "summary.json"), "w"), indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
