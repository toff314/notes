#!/usr/bin/env python3
"""Lab 01: sparse (tf-idf / BM25) vs dense (PPMI co-occurrence + SVD) retrieval.

对应 actions.md 行动 1。语料是 24 篇关于信息检索/问答的玩具文档，
查询刻意改写成不含原词的说法，用来观察词汇不匹配（§11.3）。

运行: python3 sparse_vs_dense.py
产物: out/metrics.csv, out/per_query.csv, out/scores.json, out/metrics.png
"""
import json
import math
import os
import re
from collections import Counter, defaultdict

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
BG_PATH = "/home/yuanwu/books/slp3/zh/md/11-retrieval-based-models.md"

DOCS = [
    ("d01", "信息检索", "信息检索研究如何根据用户的信息需求从大规模文档集合中找出相关文本并排序返回。"),
    ("d02", "倒排索引", "倒排索引以词项为入口，记录每个词出现在哪些文档中，使查找候选文档只需读取对应的文档编号列表。"),
    ("d03", "tf-idf", "tf-idf 用词频乘以逆文档频率给词项加权，常见词因为出现在很多文档中而权重接近零。"),
    ("d04", "BM25", "BM25 在 tf-idf 基础上加入词频饱和参数与文档长度归一化参数，避免长文档天然占优。"),
    ("d05", "余弦相似度", "余弦相似度把查询和文档都看成向量，用夹角衡量方向一致程度，对向量长度不敏感。"),
    ("d06", "精确率与召回率", "精确率统计返回结果里真正相关的比例，召回率统计全部相关文档中被找回来的比例。"),
    ("d07", "平均精确率均值", "平均精确率均值先对每个查询算平均精确率，再对所有查询取平均，得到一个可比较的单一数字。"),
    ("d08", "稠密检索", "稠密检索用语言模型输出的嵌入表示查询与文档，再在向量空间里算点积或余弦。"),
    ("d09", "双编码器", "双编码器分别编码查询和文档，文档向量可以离线算好存起来，查询到来时只编码一次。"),
    ("d10", "ColBERT", "ColBERT 保留每个词元的上下文向量，用最大相似度求和做后期交互，介于单塔与双塔之间。"),
    ("d11", "词汇不匹配", "词汇不匹配指提问者与写作者选用不同说法，导致字面上没有共同词项而检索失败。"),
    ("d12", "检索增强生成", "检索增强生成先取出相关段落，再让大语言模型以这些段落为条件组织答案。"),
    ("d13", "幻觉", "幻觉指模型给出与世界事实不符的内容，但措辞听起来合理，用户难以当场识破。"),
    ("d14", "知识引证", "知识引证在答案旁边附上可核查的来源地址或文献条目，方便用户回查原文。"),
    ("d15", "开卷问答", "开卷问答允许系统使用检索到的文档来作答，答案可以指向具体段落。"),
    ("d16", "闭卷问答", "闭卷问答不使用任何外部文档，只依靠模型参数里记住的知识直接作答。"),
    ("d17", "精确匹配与 F1", "精确匹配要求预测与标准答案完全一致，词元 F1 则统计两者之间部分重叠的程度。"),
    ("d18", "Natural Questions", "Natural Questions 收集真实搜索引擎查询，并为每个问题标注维基百科里的长答案与短片段。"),
    ("d19", "MS MARCO", "MS MARCO 包含大量来自必应日志的真实问题、人工答案以及成规模的段落集合。"),
    ("d20", "Faiss", "Faiss 用近似最近邻搜索代替逐一比对，在稠密向量集合里快速找出最接近的若干条。"),
    ("d21", "停用词表", "停用词表列出检索前要去掉的高频虚词，收缩索引规模的代价是短语查询会失真。"),
    ("d22", "词袋模型", "词袋模型忽略词的先后位置，只记录每个词在一段文本里出现了多少次。"),
    ("d23", "重排器", "重排器在初步召回之后对候选段落重新打分，用更贵的模型换更准的顺序。"),
    ("d24", "多跳检索", "多跳检索把第一轮找到的文档追加进查询，再做第二轮查找，用于需要串联多条事实的问题。"),
]

QUERIES = [
    ("q01", "搜索时怎么快速找到含有某个词的文档", {"d02": 2}),
    ("q02", "怎样让很少出现的词获得更高权重", {"d03": 2}),
    ("q03", "长文档总是排在前面该怎么办", {"d04": 2}),
    ("q04", "两段文字方向接近就算相似吗", {"d05": 2}),
    ("q05", "排序结果该用哪个单一数字评价", {"d07": 2, "d06": 1}),
    ("q06", "用户和作者用词不一样导致搜不到", {"d11": 2}),
    ("q07", "让模型先查资料再回答", {"d12": 2}),
    ("q08", "模型一本正经地说错事实", {"d13": 2}),
    ("q09", "回答时给出可以回查的出处", {"d14": 2}),
    ("q10", "文档太多时怎样加速向量比对", {"d20": 2}),
]

ASCII_WORD = re.compile(r"[a-zA-Z][a-zA-Z0-9\-\.]*")
CJK = re.compile(r"[\u4e00-\u9fff]")


def tokenize(text):
    """中文按字符二元组切，英文/数字按词切。"""
    text = text.lower()
    toks = [w for w in ASCII_WORD.findall(text)]
    chars = CJK.findall(text)
    toks += ["".join(chars[i:i + 2]) for i in range(len(chars) - 1)]
    return toks


def build_index(docs):
    doc_tokens = {d: tokenize(t + " " + body) for d, t, body in docs}
    df = Counter()
    for toks in doc_tokens.values():
        df.update(set(toks))
    N = len(docs)
    return doc_tokens, df, N


def tfidf_vector(tokens, df, N):
    tf = Counter(tokens)
    vec = {}
    for t, c in tf.items():
        vec[t] = (1.0 + math.log10(c)) * math.log10(N / max(df.get(t, 0), 1))
    return vec


def cosine(a, b):
    if not a or not b:
        return 0.0
    common = set(a) & set(b)
    num = sum(a[t] * b[t] for t in common)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return num / (na * nb) if na and nb else 0.0


def bm25_scores(qtokens, doc_tokens, df, N, k1=1.5, b=0.75):
    lengths = {d: len(t) for d, t in doc_tokens.items()}
    avgdl = sum(lengths.values()) / len(lengths)
    q = list(dict.fromkeys(qtokens))
    scores = {}
    for d, toks in doc_tokens.items():
        tf = Counter(toks)
        s = 0.0
        for t in q:
            if tf[t] == 0:
                continue
            idf = math.log((N - df[t] + 0.5) / (df[t] + 0.5) + 1)
            denom = tf[t] + k1 * (1 - b + b * lengths[d] / avgdl)
            s += idf * tf[t] * (k1 + 1) / denom
        scores[d] = s
    return scores


def load_background():
    if os.path.exists(BG_PATH):
        with open(BG_PATH, encoding="utf-8", errors="ignore") as f:
            return f.read(), "chapter-11-md"
    joined = " ".join(t + body for _, t, body in DOCS)
    return joined, "toy-docs-fallback"


def ppmi_svd(doc_tokens, df, N, dim=100, window=5):
    """在背景语料上学 PPMI 共现，再做截断 SVD；文档向量 = idf 加权词向量平均。"""
    bg, src = load_background()
    toks = tokenize(bg)
    vocab = sorted({t for ts in doc_tokens.values() for t in ts})
    vidx = {t: i for i, t in enumerate(vocab)}
    co = np.zeros((len(vocab), len(vocab)), dtype=np.float64)
    keep = [vidx[t] for t in toks if t in vidx]
    for pos, ti in enumerate(keep):
        lo, hi = max(0, pos - window), min(len(keep), pos + window + 1)
        for j in range(lo, hi):
            if j != pos:
                co[ti, keep[j]] += 1.0
    total = co.sum()
    row = co.sum(axis=1, keepdims=True)
    col = co.sum(axis=0, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        pmi = np.log((co * total) / (row @ col))
    ppmi = np.nan_to_num(np.maximum(pmi, 0.0))
    k = min(dim, min(ppmi.shape) - 1)
    u, s, _ = np.linalg.svd(ppmi, full_matrices=False)
    emb = u[:, :k] * np.sqrt(s[:k])
    # 文档向量
    doc_vecs = {}
    for d, ts in doc_tokens.items():
        tf = Counter(ts)
        acc = np.zeros(k)
        wsum = 0.0
        for t, c in tf.items():
            w = (1.0 + math.log10(c)) * math.log10(N / max(df.get(t, 0), 1))
            acc += w * emb[vidx[t]]
            wsum += w
        doc_vecs[d] = acc / wsum if wsum else acc
    return doc_vecs, emb, vidx, k, src


def rank_from_scores(scores):
    return [d for d, _ in sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))]


def main():
    os.makedirs(OUT, exist_ok=True)
    doc_tokens, df, N = build_index(DOCS)
    ids = [d for d, _, _ in DOCS]

    # 稀疏：tf-idf 余弦
    doc_vec = {d: tfidf_vector(ts, df, N) for d, ts in doc_tokens.items()}
    tfidf_rank = {}
    for qid, qtext, _ in QUERIES:
        qv = tfidf_vector(tokenize(qtext), df, N)
        tfidf_rank[qid] = rank_from_scores({d: cosine(qv, doc_vec[d]) for d in ids})

    # 稀疏：BM25
    bm25_rank = {}
    for qid, qtext, _ in QUERIES:
        bm25_rank[qid] = rank_from_scores(bm25_scores(tokenize(qtext), doc_tokens, df, N))

    # 稠密：PPMI + SVD
    dvec, emb, vidx, dim, src = ppmi_svd(doc_tokens, df, N)
    dense_rank = {}
    for qid, qtext, _ in QUERIES:
        qt = tokenize(qtext)
        tf = Counter(qt)
        acc = np.zeros(dim)
        wsum = 0.0
        for t, c in tf.items():
            if t in vidx:
                w = (1.0 + math.log10(c)) * math.log10(N / max(df.get(t, 0), 1))
                acc += w * emb[vidx[t]]
                wsum += w
        qv = acc / wsum if wsum else acc
        scores = {}
        for d in ids:
            dv = dvec[d]
            denom = (np.linalg.norm(qv) * np.linalg.norm(dv))
            scores[d] = float(qv @ dv / denom) if denom else 0.0
        dense_rank[qid] = rank_from_scores(scores)

    def metrics(rank, rel, ks=(1, 3, 5)):
        out = {}
        for k in ks:
            hit = len(set(rank[:k]) & set(rel))
            out[f"recall@{k}"] = hit / len(rel)
        rr = 0.0
        for i, d in enumerate(rank, 1):
            if d in rel:
                rr = 1.0 / i
                break
        out["mrr"] = rr
        return out

    systems = {"tfidf": tfidf_rank, "bm25": bm25_rank, "dense_ppmi_svd": dense_rank}
    rows = []
    per_query = []
    for name, ranks in systems.items():
        agg = defaultdict(list)
        for qid, qtext, rel in QUERIES:
            m = metrics(ranks[qid], rel)
            for k, v in m.items():
                agg[k].append(v)
            per_query.append({
                "system": name, "query": qid, "text": qtext,
                "top1": ranks[qid][0], "gold": "|".join(rel),
                "top1_correct": int(ranks[qid][0] in rel),
                "rr": m["mrr"],
            })
        row = {"system": name}
        row.update({k: sum(v) / len(v) for k, v in agg.items()})
        rows.append(row)

    with open(os.path.join(OUT, "metrics.csv"), "w", encoding="utf-8") as f:
        cols = list(rows[0].keys())
        f.write(",".join(cols) + "\n")
        for r in rows:
            f.write(",".join(str(round(r[c], 4)) if isinstance(r[c], float) else str(r[c]) for c in cols) + "\n")

    with open(os.path.join(OUT, "per_query.csv"), "w", encoding="utf-8") as f:
        cols = list(per_query[0].keys())
        f.write(",".join(cols) + "\n")
        for r in per_query:
            f.write(",".join(str(r[c]) for c in cols) + "\n")

    # 上限检验：把查询换成金标准文档的标题（无词汇鸿沟）
    title_of = {d: t for d, t, _ in DOCS}
    oracle = []
    for name, ranks in systems.items():
        hits = 0
        for d, t, _ in DOCS:
            qt = tokenize(t)
            if name == "tfidf":
                qv = tfidf_vector(qt, df, N)
                rank = rank_from_scores({x: cosine(qv, doc_vec[x]) for x in ids})
            elif name == "bm25":
                rank = rank_from_scores(bm25_scores(qt, doc_tokens, df, N))
            else:
                tf = Counter(qt)
                acc = np.zeros(dim)
                wsum = 0.0
                for tk, c in tf.items():
                    if tk in vidx:
                        w = (1.0 + math.log10(c)) * math.log10(N / max(df.get(tk, 0), 1))
                        acc += w * emb[vidx[tk]]
                        wsum += w
                qv = acc / wsum if wsum else acc
                sc = {}
                for x in ids:
                    dv = dvec[x]
                    den = np.linalg.norm(qv) * np.linalg.norm(dv)
                    sc[x] = float(qv @ dv / den) if den else 0.0
                rank = rank_from_scores(sc)
            hits += int(rank[0] == d)
        oracle.append({"system": name, "title_recall@1": hits / len(DOCS)})

    with open(os.path.join(OUT, "oracle.csv"), "w", encoding="utf-8") as f:
        f.write("system,title_recall@1\n")
        for r in oracle:
            f.write(f"{r['system']},{r['title_recall@1']:.4f}\n")

    summary = {
        "corpus": {"n_docs": len(DOCS), "n_queries": len(QUERIES), "n_relevant": sum(len(r) for _, _, r in QUERIES)},
        "dense_background": src,
        "svd_dim": dim,
        "bm25_params": {"k1": 1.5, "b": 0.75},
        "metrics": rows,
        "oracle_title_recall@1": oracle,
        "dense_wins": [q for q, t, rel in QUERIES
                       if dense_rank[q][0] in rel and (tfidf_rank[q][0] not in rel or bm25_rank[q][0] not in rel)],
    }
    with open(os.path.join(OUT, "scores.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)


    # 图：三系统 × 三个指标
    plt.rcParams["font.family"] = ["Noto Sans CJK JP", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    labels = ["Recall@1", "Recall@3", "Recall@5", "MRR"]
    keys = ["recall@1", "recall@3", "recall@5", "mrr"]
    x = np.arange(len(labels))
    width = 0.26
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    colors = ["#4C78A8", "#F58518", "#54A24B"]
    for i, r in enumerate(rows):
        vals = [r[k] for k in keys]
        bars = ax.bar(x + (i - 1) * width, vals, width, label=r["system"], color=colors[i])
        ax.bar_label(bars, fmt="%.2f", fontsize=8, padding=2)
    ax.set_xticks(x, labels)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("分数")
    ax.set_title("玩具语料上三种检索器的排序指标（24 文档 / 10 查询）")
    ax.legend(frameon=False, ncol=3, loc="upper left")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "metrics.png"), dpi=160)

    # 图 2：改写查询 vs 标题查询的 Recall@1（词汇鸿沟）
    fig, ax = plt.subplots(figsize=(7.4, 4.0))
    names = [r["system"] for r in rows]
    para = [r["recall@1"] for r in rows]
    orac = [r["title_recall@1"] for r in oracle]
    x = np.arange(len(names))
    b1 = ax.bar(x - 0.18, para, 0.36, label="改写查询（有词汇鸿沟）", color="#E45756")
    b2 = ax.bar(x + 0.18, orac, 0.36, label="标题查询（无鸿沟）", color="#72B7B2")
    ax.bar_label(b1, fmt="%.2f", fontsize=9)
    ax.bar_label(b2, fmt="%.2f", fontsize=9)
    ax.set_xticks(x, names)
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("Recall@1")
    ax.set_title("同一批文档，换一种问法：召回率的落差")
    ax.legend(frameon=False, loc="lower right")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "gap_analysis.png"), dpi=160)

    print("dense background:", src, "| svd dim:", dim)
    print(f"{'system':<14} " + " ".join(f"{k:>10}" for k in keys))
    for r in rows:
        print(f"{r['system']:<14} " + " ".join(f"{r[k]:>10.3f}" for k in keys))
    print("dense-only top1 wins:", summary["dense_wins"])
    print("title-query Recall@1:", {r["system"]: round(r["title_recall@1"], 3) for r in oracle})
    print("wrote", OUT)


if __name__ == "__main__":
    main()
