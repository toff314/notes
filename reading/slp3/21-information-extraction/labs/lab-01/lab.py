#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""lab-01：Hearst 式中文模式抽上下位关系 —— 三种配置的精度/召回权衡

对应 §21.2.1「用模式抽取关系」。
三种配置：
  A 朴素模式           —— 只用 3 条宽松正则
  B 朴素模式 + 类型约束 —— 要求两端实体类型一致（模拟加 NER 约束）
  C 精修模式 + 类型约束 —— 给「等」模式补上终止符前瞻，修掉贪婪吞词
产物：out/metrics.json、out/predictions.csv、out/errors.csv、out/tradeoff.png
"""
import csv
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

SENTS = [
    "紫菜等红藻富含碘元素。",
    "石花菜等红藻可用于提取琼胶。",
    "国航等航空公司本周上调了票价。",
    "东航等航空公司随即跟进。",
    "Python 等编程语言在本课程中使用。",
    "Rust 等编程语言适合写系统软件。",
    "MySQL 等数据库支撑了大量中小网站。",
    "PostgreSQL 等数据库支持复杂查询。",
    "红藻包括紫菜和石花菜。",
    "航空公司包括国航和东航。",
    "编程语言包括 Python 和 Rust。",
    "数据库包括 MySQL 和 PostgreSQL。",
    "紫菜是红藻的一种。",
    "国航是航空公司的一种。",
    # —— 陷阱：结构像 Hearst 模式，语义不是 is-a ——
    "国航等了三小时才起飞。",
    "东航等通知等了一整天。",
    "MySQL 等不到了，先开会。",
    "Python 等脚本跑完再说。",
    "票价包括了燃油和税费。",
    "机票价格包括燃油附加费和税费。",
]

GAZ = {  # 极简地名词典，模拟 NER 约束
    "紫菜": "ALGA", "石花菜": "ALGA", "红藻": "ALGA",
    "国航": "ORG", "东航": "ORG", "航空公司": "ORG",
    "Python": "LANG", "Rust": "LANG", "编程语言": "LANG",
    "MySQL": "DB", "PostgreSQL": "DB", "数据库": "DB",
}

GOLD = {
    ("紫菜", "红藻"), ("石花菜", "红藻"),
    ("国航", "航空公司"), ("东航", "航空公司"),
    ("Python", "编程语言"), ("Rust", "编程语言"),
    ("MySQL", "数据库"), ("PostgreSQL", "数据库"),
}

# 终止符：中文字符里出现这些，说明「等」后面的名词短语已经结束
STOP = "了在随可富支适本，。；：、 "


def _p_deng_naive():
    return re.compile(r"([A-Za-z\u4e00-\u9fa5]{2,10})\s*等\s*([\u4e00-\u9fa5]{2,10})")


def _p_deng_refined():
    # 名词短语后必须紧跟终止符（或句末），避免把动词短语吞进来
    return re.compile(
        r"([A-Za-z\u4e00-\u9fa5]{2,10})\s*等\s*([\u4e00-\u9fa5]{2,6}?)(?=[" + STOP + r"]|$)"
    )


def _p_baohan():
    return re.compile(
        r"([\u4e00-\u9fa5]{2,10})包括([A-Za-z\u4e00-\u9fa5]{2,10})和([A-Za-z\u4e00-\u9fa5]{2,10})"
    )


def _p_yizhong():
    return re.compile(r"([A-Za-z\u4e00-\u9fa5]{2,10})是([\u4e00-\u9fa5]{2,10})的一种")


def build(kind):
    """kind: 'naive' -> A/B 用；'refined' -> C 用。返回 [(child,parent,sentence)]"""
    deng = _p_deng_naive() if kind == "naive" else _p_deng_refined()
    bh, yz = _p_baohan(), _p_yizhong()
    hits = []
    for s in SENTS:
        for m in deng.finditer(s):
            hits.append((m.group(1).strip(), m.group(2).strip(), s))
        for m in bh.finditer(s):
            hits.append((m.group(2).strip(), m.group(1).strip(), s))
            hits.append((m.group(3).strip(), m.group(1).strip(), s))
        for m in yz.finditer(s):
            hits.append((m.group(1).strip(), m.group(2).strip(), s))
    return hits


def constrain(hits):
    """两端类型已知且相同才保留；未知类型一律丢弃。"""
    kept = [(c, p, s) for c, p, s in hits
            if GAZ.get(c) and GAZ.get(p) and GAZ.get(c) == GAZ.get(p)]
    return kept


def prf(pairs):
    pred = set(pairs)
    tp = len(pred & GOLD)
    p = tp / len(pred) if pred else 0.0
    r = tp / len(GOLD) if GOLD else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return {"tp": tp, "n_pred": len(pred), "n_gold": len(GOLD),
            "precision": round(p, 4), "recall": round(r, 4), "f1": round(f, 4)}


CONFIGS = [
    ("A_naive", "naive", False),
    ("B_naive_plus_type", "naive", True),
    ("C_refined_plus_type", "refined", True),
]


def main():
    metrics, all_rows = {}, []
    for name, kind, use_type in CONFIGS:
        hits = build(kind)
        if use_type:
            hits = constrain(hits)
        pairs = [(c, p) for c, p, _ in hits]
        metrics[name] = prf(pairs)
        metrics[name]["n_mentions"] = len(hits)
        for c, p, s in hits:
            all_rows.append([name, c, p, int((c, p) in GOLD), s])

    best = max(metrics, key=lambda k: metrics[k]["f1"])
    metrics["best_config"] = best
    metrics["delta_B_minus_A"] = {
        k: round(metrics["B_naive_plus_type"][k] - metrics["A_naive"][k], 4)
        for k in ("precision", "recall", "f1")
    }
    metrics["delta_C_minus_B"] = {
        k: round(metrics["C_refined_plus_type"][k] - metrics["B_naive_plus_type"][k], 4)
        for k in ("precision", "recall", "f1")
    }
    metrics["n_sentences"] = len(SENTS)

    with open(os.path.join(OUT, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    with open(os.path.join(OUT, "predictions.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["config", "child", "parent", "is_gold", "sentence"])
        w.writerows(all_rows)

    with open(os.path.join(OUT, "errors.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["config", "child", "parent", "sentence"])
        for row in all_rows:
            if not row[3]:
                w.writerow([row[0], row[1], row[2], row[4]])

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        names = [c[0] for c in CONFIGS]
        ps = [metrics[n]["precision"] for n in names]
        rs = [metrics[n]["recall"] for n in names]
        fs = [metrics[n]["f1"] for n in names]
        x = range(len(names))
        plt.figure(figsize=(7, 4))
        plt.plot(x, ps, "o-", label="precision")
        plt.plot(x, rs, "s-", label="recall")
        plt.plot(x, fs, "^-", label="F1")
        plt.xticks(list(x), names, fontsize=9)
        plt.ylim(0, 1.05)
        plt.ylabel("score")
        plt.title("Hearst patterns: type constraint vs refined regex (ch21 lab-01)")
        plt.grid(alpha=.3)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(OUT, "tradeoff.png"), dpi=130)
    except Exception as e:  # 画图失败不影响主产物
        print("plot skipped:", e)

    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
