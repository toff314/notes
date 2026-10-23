#!/usr/bin/env python3
"""Lab 04: BM25 的 k1 / b 网格扫描 —— 复现"长文档天然占优"与两个参数的作用。

对应 actions.md 行动 4，并核对书 §11.1.2 的两句断言：
  1) k1 = 0 时候完全不使用词频（此时 b 应失效）；
  2) b = 1 按文档长度缩放，b = 0 不做长度缩放。

语料：16 篇短文档，其中 8 篇另有一个"三倍重复正文"的长版本（同一主题的干扰项）。
查询的金标准一律是短文档；长版本若排到第一，说明长度归一化没起作用。

运行: python3 bm25_sweep.py
产物: out/grid_mrr.csv, out/grid_r1.csv, out/grid_longwin.csv,
      out/summary.json, out/mrr_heatmap.png, out/b_curve.png
"""
import json
import math
import os
import re
from collections import Counter

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

BASE = [
    ("d01", "倒排索引按词项登记文档编号，查询时只读相关列表。", "倒排索引是怎样加快查询的？"),
    ("d02", "余弦相似度比较两个向量的方向，不关心它们的长度。", "余弦相似度为什么不受向量长度影响？"),
    ("d03", "逆文档频率让罕见词获得更高权重，常见词权重接近零。", "罕见词的权重为什么更高？"),
    ("d04", "词频饱和避免某个词重复一百次就压过其他证据。", "一个词出现很多次会不会过度主导打分？"),
    ("d05", "双编码器把查询和文档分别编码，文档向量可以离线缓存。", "双编码器为什么能离线算好文档向量？"),
    ("d06", "近似最近邻搜索用索引结构换取速度，牺牲少量召回。", "向量数量很大时怎样提速检索？"),
    ("d07", "重排器在召回之后用更贵的模型重新打分，改善顺序。", "为什么要在召回之后再排一次序？"),
    ("d08", "知识引证把答案连接到可核查的来源地址。", "怎样让生成的答案带上可核查的出处？"),
    ("d09", "开卷问答允许系统查阅检索到的文档再作答。", "开卷问答和闭卷问答差别在哪里？"),
    ("d10", "停用词表删除高频虚词，缩小索引但破坏短语匹配。", "去掉停用词会带来什么副作用？"),
    ("d11", "词汇不匹配发生在提问者和写作者选用不同说法的时候。", "提问用词和原文不同为什么就搜不到？"),
    ("d12", "多跳检索把第一轮结果拼进查询，再查第二轮。", "需要串联多条事实的问题怎么检索？"),
    ("d13", "精确匹配统计答案完全一致的题目比例。", "多项选择题通常报告哪个指标？"),
    ("d14", "词元 F1 用重叠程度给自由文本答案部分分数。", "自由文本答案为什么用 F1 而不是精确匹配？"),
    ("d15", "平均精确率均值把每个查询的平均精确率再平均一次。", "怎样用一个数字比较两个排序系统？"),
    ("d16", "插值精确率在固定召回率水平上取右侧最大精确率。", "十一点插值曲线是怎么画出来的？"),
]

FILLER = "这一段落用于模拟冗长的说明文字，它与主题无关，只是把篇幅拉长。"

ASCII_WORD = re.compile(r"[a-zA-Z][a-zA-Z0-9\-\.]*")
CJK = re.compile(r"[\u4e00-\u9fff]")


def tokenize(text):
    text = text.lower()
    toks = ASCII_WORD.findall(text)
    chars = CJK.findall(text)
    toks += ["".join(chars[i:i + 2]) for i in range(len(chars) - 1)]
    return toks


def make_corpus():
    docs = []
    long_ids = set()
    for i, (did, text, q) in enumerate(BASE):
        docs.append((did, text))
        if i % 2 == 0:  # 8 篇有长版本
            long_id = did + "L"
            docs.append((long_id, (text + FILLER) * 3))
            long_ids.add(long_id)
    return docs, long_ids


def bm25_all(query, docs, k1, b):
    toks = {d: tokenize(t) for d, t in docs}
    N = len(docs)
    df = Counter()
    for ts in toks.values():
        df.update(set(ts))
    avgdl = sum(len(t) for t in toks.values()) / N
    q = list(dict.fromkeys(tokenize(query)))
    scores = {}
    for d, ts in toks.items():
        tf = Counter(ts)
        s = 0.0
        for t in q:
            if tf[t] == 0:
                continue
            idf = math.log((N - df[t] + 0.5) / (df[t] + 0.5) + 1)
            s += idf * tf[t] * (k1 + 1) / (tf[t] + k1 * (1 - b + b * len(ts) / avgdl))
        scores[d] = s
    return sorted(scores, key=lambda d: (-scores[d], d))


def evaluate(k1, b, docs, long_ids):
    rr_sum = 0.0
    r1 = 0
    long_win = 0
    for did, text, q in BASE:
        rank = bm25_all(q, docs, k1, b)
        if rank[0] == did:
            r1 += 1
            rr_sum += 1.0
        else:
            for pos, d in enumerate(rank, 1):
                if d == did:
                    rr_sum += 1.0 / pos
                    break
        if rank[0] in long_ids:
            long_win += 1
    n = len(BASE)
    return {"mrr": rr_sum / n, "recall@1": r1 / n, "long_win_rate": long_win / n}


def main():
    os.makedirs(OUT, exist_ok=True)
    docs, long_ids = make_corpus()
    k1s = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0]
    bs = [0.0, 0.25, 0.5, 0.75, 1.0]

    grid = {}
    for k1 in k1s:
        for b in bs:
            grid[(k1, b)] = evaluate(k1, b, docs, long_ids)

    with open(os.path.join(OUT, "grid_mrr.csv"), "w", encoding="utf-8") as f:
        f.write("k1\\b," + ",".join(str(b) for b in bs) + "\n")
        for k1 in k1s:
            f.write(f"{k1}," + ",".join(f"{grid[(k1,b)]['mrr']:.4f}" for b in bs) + "\n")
    with open(os.path.join(OUT, "grid_r1.csv"), "w", encoding="utf-8") as f:
        f.write("k1\\b," + ",".join(str(b) for b in bs) + "\n")
        for k1 in k1s:
            f.write(f"{k1}," + ",".join(f"{grid[(k1,b)]['recall@1']:.4f}" for b in bs) + "\n")
    with open(os.path.join(OUT, "grid_longwin.csv"), "w", encoding="utf-8") as f:
        f.write("k1\\b," + ",".join(str(b) for b in bs) + "\n")
        for k1 in k1s:
            f.write(f"{k1}," + ",".join(f"{grid[(k1,b)]['long_win_rate']:.4f}" for b in bs) + "\n")

    best = max(grid.items(), key=lambda kv: (kv[1]["mrr"], -kv[0][0]))
    rec = grid[(1.5, 0.75)]
    summary = {
        "n_docs": len(docs), "n_short": len(BASE), "n_long_dupes": len(long_ids),
        "k1_grid": k1s, "b_grid": bs,
        "best": {"k1": best[0][0], "b": best[0][1], **best[1]},
        "book_suggestion": {"k1": "1.2–2", "b": 0.75, "mrr_at_1.5_0.75": rec["mrr"],
                            "recall@1_at_1.5_0.75": rec["recall@1"]},
        "k1_zero_flat_across_b": all(abs(grid[(0.0, b)]["mrr"] - grid[(0.0, 0.0)]["mrr"]) < 1e-9 for b in bs),
        "b0_long_win_rate": grid[(1.5, 0.0)]["long_win_rate"],
        "b1_long_win_rate": grid[(1.5, 1.0)]["long_win_rate"],
        "grid": {f"k1={k1},b={b}": v for (k1, b), v in grid.items()},
    }
    with open(os.path.join(OUT, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    plt.rcParams["font.family"] = ["Noto Sans CJK JP", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

    mrr = np.array([[grid[(k, b)]["mrr"] for b in bs] for k in k1s])
    fig, ax = plt.subplots(figsize=(7.0, 4.6))
    im = ax.imshow(mrr, cmap="YlGnBu", vmin=0.5, vmax=1.0, aspect="auto")
    ax.set_xticks(range(len(bs)), [str(b) for b in bs])
    ax.set_yticks(range(len(k1s)), [str(k) for k in k1s])
    ax.set_xlabel("b（文档长度归一化强度）")
    ax.set_ylabel("k1（词频饱和参数）")
    ax.set_title("BM25 网格上的 MRR（16 查询，含 8 个长文档干扰项）")
    for i in range(len(k1s)):
        for j in range(len(bs)):
            v = mrr[i, j]
            ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                    color="white" if v > 0.82 else "black", fontsize=9)
    fig.colorbar(im, ax=ax, label="MRR")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "mrr_heatmap.png"), dpi=160)

    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    for k1, style in zip([0.0, 1.0, 2.0], ["o--", "s-", "^:"]):
        ax.plot(bs, [grid[(k1, b)]["mrr"] for b in bs], style, label=f"k1={k1}")
    ax.axvline(0.75, color="#E45756", lw=1.2, ls="--", alpha=0.8)
    ax.text(0.76, 0.55, "书建议 b=0.75", color="#E45756", fontsize=9)
    ax.set_xlabel("b")
    ax.set_ylabel("MRR")
    ax.set_ylim(0.45, 1.05)
    ax.set_title("长度归一化不足时，长文档干扰项会抢走第一名")
    ax.grid(alpha=0.25, ls="--")
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "b_curve.png"), dpi=160)

    print(f"best: k1={best[0][0]}, b={best[0][1]} -> MRR={best[1]['mrr']:.3f}")
    print(f"book setting k1=1.5,b=0.75 -> MRR={rec['mrr']:.3f}, R@1={rec['recall@1']:.3f}")
    print("k1=0 flat across b:", summary["k1_zero_flat_across_b"])
    print(f"long-doc win rate: b=0 -> {summary['b0_long_win_rate']:.2f}, "
          f"b=1 -> {summary['b1_long_win_rate']:.2f}")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
