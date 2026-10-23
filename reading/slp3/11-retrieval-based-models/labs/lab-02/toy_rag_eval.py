#!/usr/bin/env python3
"""Lab 02: 玩具 RAG + 问答评估（开卷 / 闭卷 / 给对段落）。

对应 actions.md 行动 3。三个条件：
  closed_book     —— 模拟"参数记忆"：只记住一部分事实，其余凭同类型答案编造（无引用）
  open_book_top1  —— BM25 检索 top-1 段落 -> 模板阅读器抽出答案并给出引用
  open_book_oracle—— 直接给金标准段落 -> 模板阅读器（隔离检索错误与阅读错误）

指标：答案命中率、EM、字符二元组 F1、引用率、引用正确率、检索 Recall@1。
这是**模拟实验**：阅读器是模板抽取器，不是真实 LLM；结论只用于看清
"检索错 / 读错 / 记错"三种损失如何分开计量。

运行: python3 toy_rag_eval.py
产物: out/per_question.csv, out/metrics.csv, out/summary.json, out/rag_compare.png
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

# (id, question, answer, passage, answer_type)
FACTS = [
    ("f01", "《魔笛》的首演是在哪一年？", "1791 年", "莫扎特的歌剧《魔笛》于 1791 年在维也纳首演。", "year"),
    ("f02", "卢浮宫博物馆位于哪座城市？", "巴黎", "卢浮宫博物馆位于法国首都巴黎，原为王家宫殿。", "city"),
    ("f03", "《蒙娜丽莎》是谁的作品？", "达·芬奇", "《蒙娜丽莎》是列奥纳多·达·芬奇创作的油画。", "person"),
    ("f04", "埃菲尔铁塔建成的年份是哪一年？", "1889 年", "埃菲尔铁塔为 1889 年巴黎世界博览会而建。", "year"),
    ("f05", "孙悟空出自哪部小说？", "西游记", "孙悟空是小说《西游记》中的主要角色之一。", "work"),
    ("f06", "《论语》主要记录谁的言行？", "孔子", "《论语》由孔子弟子及再传弟子编纂，记录孔子及其弟子的言行。", "person"),
    ("f07", "光在真空中的速度约为每秒多少？", "30 万公里", "光在真空中的传播速度约为每秒 30 万公里。", "quantity"),
    ("f08", "地球唯一的天然卫星是什么？", "月球", "月球是地球唯一的天然卫星，平均距离约 38 万公里。", "object"),
    ("f09", "水的化学式是什么？", "H2O", "水由两个氢原子和一个氧原子构成，化学式为 H2O。", "formula"),
    ("f10", "中国农历新年通常称为什么？", "春节", "中国农历新年通常称为春节，是重要的传统节日。", "name"),
    ("f11", "《物种起源》的作者是谁？", "达尔文", "《物种起源》由查尔斯·达尔文于 1859 年出版。", "person"),
    ("f12", "第一次世界大战爆发于哪一年？", "1914 年", "第一次世界大战于 1914 年爆发，持续四年多。", "year"),
    ("f13", "珠穆朗玛峰位于哪两国边界？", "中国与尼泊尔", "珠穆朗玛峰位于中国与尼泊尔两国边界之上。", "country"),
    ("f14", "《向日葵》系列的作者是谁？", "梵高", "《向日葵》系列是文森特·梵高在阿尔勒创作的油画。", "person"),
    ("f15", "国际单位制中长度的基本单位是什么？", "米", "国际单位制中长度的基本单位是米，符号为 m。", "unit"),
    ("f16", "血液中负责运输氧气的是什么蛋白？", "血红蛋白", "血液中的血红蛋白负责把氧气从肺部运输到全身组织。", "protein"),
    ("f17", "《哈姆雷特》的作者是谁？", "莎士比亚", "《哈姆雷特》是威廉·莎士比亚创作的悲剧。", "person"),
    ("f18", "太阳系中体积最大的行星是哪一颗？", "木星", "木星是太阳系中体积和质量最大的行星。", "object"),
    ("f19", "长江最终注入哪个海？", "东海", "长江自西向东流，最终注入东海。", "sea"),
    ("f20", "联合国成立于哪一年？", "1945 年", "联合国于 1945 年成立，总部设在纽约。", "year"),
]

# 同实体、错误事实的干扰段落（模拟"检索到看似相关但内容错误"的来源）
DISTRACTORS = [
    ("x01", "莫扎特的歌剧《魔笛》于 1786 年在维也纳首演，由席卡内德编剧。", "1786 年", "f01"),
    ("x02", "卢浮宫博物馆位于法国城市里昂，馆藏以绘画为主。", "里昂", "f02"),
    ("x03", "《物种起源》的主要结论由华莱士首先完整提出。", "华莱士", "f11"),
    ("x04", "珠穆朗玛峰位于中国与印度两国边界之上。", "中国与印度", "f13"),
    ("x05", "联合国于 1919 年成立，总部设在日内瓦。", "1919 年", "f20"),
]

# 闭卷模拟：假设参数里只记住了这 12 条（其余会编造）
REMEMBERED = {"f01", "f02", "f03", "f04", "f06", "f08", "f09", "f11",
              "f12", "f15", "f17", "f19"}

# 闭卷编造时同类型答案池
WRONG_POOL = {
    "year": ["1786 年", "1888 年", "1919 年", "1950 年"],
    "city": ["里昂", "马赛", "威尼斯", "维也纳"],
    "person": ["华莱士", "席卡内德", "高更", "培根"],
    "work": ["三国演义", "水浒传", "红楼梦", "聊斋志异"],
    "quantity": ["3 万公里", "300 公里", "3000 公里", "30 公里"],
    "object": ["火星", "金星", "土星", "太阳"],
    "formula": ["CO2", "H2O2", "CH4", "O2"],
    "name": ["元旦", "元宵节", "清明节", "中秋节"],
    "country": ["中国与印度", "印度与不丹", "尼泊尔与不丹", "中国与巴基斯坦"],
    "unit": ["克", "秒", "升", "摄氏度"],
    "protein": ["白蛋白", "肌红蛋白", "胶原蛋白", "球蛋白"],
    "sea": ["黄海", "南海", "渤海", "日本海"],
}

ASCII_WORD = re.compile(r"[a-zA-Z][a-zA-Z0-9\-\.]*")
CJK = re.compile(r"[\u4e00-\u9fff]")
PUNCT = re.compile(r"[\s，。！？、；：“”‘’（）《》〈〉·,\.!\?;:'\"()\[\]-]+")


def tokenize(text):
    text = text.lower()
    toks = ASCII_WORD.findall(text)
    chars = CJK.findall(text)
    toks += ["".join(chars[i:i + 2]) for i in range(len(chars) - 1)]
    return toks


def normalize(text):
    return PUNCT.sub("", text.lower())


def char_f1(pred, gold):
    a, b = normalize(pred), normalize(gold)
    if not a or not b:
        return float(a == b)
    ca, cb = Counter(a), Counter(b)
    overlap = sum((ca & cb).values())
    if overlap == 0:
        return 0.0
    p = overlap / len(a)
    r = overlap / len(b)
    return 2 * p * r / (p + r)


def build_corpus():
    docs = [(f[0], f[3], f[2]) for f in FACTS]          # id, text, gold_answer
    docs += [(d[0], d[1], d[2]) for d in DISTRACTORS]    # id, text, (wrong) answer
    return docs


def bm25_rank(query, docs, k1=1.5, b=0.75):
    toks = {d: tokenize(t) for d, t, _ in docs}
    N = len(docs)
    df = Counter()
    for ts in toks.values():
        df.update(set(ts))
    avgdl = sum(len(t) for t in toks.values()) / N
    q = tokenize(query)
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


def main():
    os.makedirs(OUT, exist_ok=True)
    docs = build_corpus()
    answer_of = {d: a for d, _, a in docs}
    text_of = {d: t for d, t, _ in docs}
    gold_doc = {f[0]: f[0] for f in FACTS}
    rows = []

    for idx, (fid, q, ans, passage, atype) in enumerate(FACTS):
        rank = bm25_rank(q, docs)
        top1 = rank[0]

        # 条件 1：闭卷
        if fid in REMEMBERED:
            cb_ans = ans
        else:
            pool = WRONG_POOL[atype]
            cb_ans = pool[idx % len(pool)]
        cb = {"condition": "closed_book", "qid": fid, "question": q,
              "answer": cb_ans, "citation": "", "correct": int(normalize(cb_ans) == normalize(ans)),
              "cited_gold": 0, "em": int(normalize(cb_ans) == normalize(ans)),
              "f1": char_f1(cb_ans, ans), "retrieved": ""}

        # 条件 2：开卷 top-1
        ob_ans = answer_of[top1]
        ob = {"condition": "open_book_top1", "qid": fid, "question": q,
              "answer": ob_ans, "citation": top1,
              "correct": int(normalize(ob_ans) == normalize(ans)),
              "cited_gold": int(top1 == gold_doc[fid]),
              "em": int(normalize(ob_ans) == normalize(ans)),
              "f1": char_f1(ob_ans, ans), "retrieved": top1}

        # 条件 3：给对段落（oracle）
        orc = {"condition": "open_book_oracle", "qid": fid, "question": q,
               "answer": ans, "citation": fid, "correct": 1, "cited_gold": 1,
               "em": 1, "f1": 1.0, "retrieved": fid}

        rows += [cb, ob, orc]

    with open(os.path.join(OUT, "per_question.csv"), "w", encoding="utf-8") as f:
        cols = list(rows[0].keys())
        f.write(",".join(cols) + "\n")
        for r in rows:
            f.write(",".join(str(r[c]) for c in cols) + "\n")

    metrics = []
    for cond in ("closed_book", "open_book_top1", "open_book_oracle"):
        sub = [r for r in rows if r["condition"] == cond]
        n = len(sub)
        metrics.append({
            "condition": cond,
            "accuracy": sum(r["correct"] for r in sub) / n,
            "EM": sum(r["em"] for r in sub) / n,
            "F1": sum(r["f1"] for r in sub) / n,
            "citation_rate": sum(1 for r in sub if r["citation"]) / n,
            "citation_precision": (sum(r["cited_gold"] for r in sub if r["citation"]) /
                                   max(1, sum(1 for r in sub if r["citation"]))),
            "grounded_accuracy": sum(1 for r in sub if r["correct"] and r["cited_gold"]) / n,
        })

    with open(os.path.join(OUT, "metrics.csv"), "w", encoding="utf-8") as f:
        cols = list(metrics[0].keys())
        f.write(",".join(cols) + "\n")
        for r in metrics:
            f.write(",".join(str(round(r[c], 4)) if isinstance(r[c], float) else str(r[c]) for c in cols) + "\n")

    open_sub = [r for r in rows if r["condition"] == "open_book_top1"]
    retrieval_recall1 = sum(r["cited_gold"] for r in open_sub) / len(open_sub)
    failures = [r["qid"] for r in open_sub if not r["correct"]]
    cited_wrong = [r["qid"] for r in open_sub if r["citation"] and not r["cited_gold"]]

    summary = {
        "setup": {
            "n_facts": len(FACTS), "n_distractors": len(DISTRACTORS),
            "retrieved_passages_total": len(docs),
            "remembered_by_closed_book": sorted(REMEMBERED),
            "note": "阅读器为模板抽取器；闭卷记忆为模拟，不代表真实 LLM 行为",
        },
        "metrics": metrics,
        "retrieval_recall@1": retrieval_recall1,
        "open_book_failures": failures,
        "open_book_cited_wrong_source": cited_wrong,
    }
    with open(os.path.join(OUT, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    plt.rcParams["font.family"] = ["Noto Sans CJK JP", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    labels = ["答案命中率", "EM", "字符 F1", "引用率", "引用正确率", "有据答对率"]
    keys = ["accuracy", "EM", "F1", "citation_rate", "citation_precision", "grounded_accuracy"]
    names = ["闭卷（参数记忆）", "开卷 top-1", "开卷（给对段落）"]
    colors = ["#B279A2", "#4C78A8", "#54A24B"]
    x = np.arange(len(labels))
    w = 0.26
    fig, ax = plt.subplots(figsize=(9.2, 4.6))
    for i, m in enumerate(metrics):
        vals = [m[k] for k in keys]
        bars = ax.bar(x + (i - 1) * w, vals, w, label=names[i], color=colors[i])
        ax.bar_label(bars, fmt="%.2f", fontsize=7.5, padding=2)
    ax.set_xticks(x, labels)
    ax.set_ylim(0, 1.12)
    ax.set_ylabel("分数")
    ax.set_title(f"玩具 RAG：检索 Recall@1 = {retrieval_recall1:.2f}，20 问")
    ax.legend(frameon=False, ncol=3, loc="upper center", fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "rag_compare.png"), dpi=160)

    for m in metrics:
        print(f"{m['condition']:<18} acc={m['accuracy']:.2f} EM={m['EM']:.2f} "
              f"F1={m['F1']:.3f} cite={m['citation_rate']:.2f} citeP={m['citation_precision']:.2f} "
              f"grounded={m['grounded_accuracy']:.2f}")
    print("retrieval Recall@1:", round(retrieval_recall1, 3))
    print("open-book failures:", failures)
    print("cited a wrong source:", cited_wrong)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
