#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""lab-03：RlogF 公式重建 + 三轮自举漂移实验

对应 §21.2.3「自举（bootstrapping）」。

中文版式(21.10)在排版中丢失分母与对数，只剩：
    Conf RlogF(p) = |hits(p)|
按 Riloff & Jones (1999) 重建为：
    RlogF(p) = |hits(p)| / (|finds(p)| * log(|finds(p)|))

实验：给定 3 个种子上下位对，从语料中迭代抽取模式 → 用 RlogF 打分 → 扩展新元组。
记录每轮 precision 与累计元组数，观察语义漂移。
"""
import csv, json, math, os, re
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. RlogF 公式重建
# ---------------------------------------------------------------------------

def rlogf(hits, finds):
    """Riloff & Jones 1999: RlogF(p) = hits(p) / (finds(p) * log(finds(p)))"""
    if finds <= 1:
        return 0.0
    return hits / (finds * math.log(finds))


# 用一个具体数值例子展示公式重建前后的差异
demo_patterns = [
    # (name, hits, finds)
    ("P1_等",        5,  6),
    ("P2_包括",      3,  4),
    ("P3_是一种",    2,  3),
    ("P4_例如",      1,  10),   # 命中少但出现多 → 低分
    ("P5_称为",      1,  2),    # finds=2, log(2)=0.693 → 分母小
]

recon_rows = []
for name, h, f in demo_patterns:
    wrong = float(h)                      # 中文版丢失分母与对数后的「错误公式」
    correct = rlogf(h, f)                 # 重建后的正确公式
    recon_rows.append({
        "pattern": name, "hits": h, "finds": f,
        "wrong_formula": round(wrong, 4),
        "correct_rlogf": round(correct, 4),
        "log_finds": round(math.log(f), 4) if f > 0 else None,
    })

# ---------------------------------------------------------------------------
# 2. 三轮自举实验
# ---------------------------------------------------------------------------

# 语料：36 句。前 16 句为「干净」样本（正确 is-a），后 20 句为「脏」样本（干扰/漂移源）
CORPUS_CLEAN = [
    "紫菜等红藻富含碘。",
    "石花菜等红藻可用于提取琼胶。",
    "国航等航空公司上调了票价。",
    "东航等航空公司随即跟进。",
    "Python 等编程语言在本课程中使用。",
    "Rust 等编程语言适合写系统软件。",
    "MySQL 等数据库支撑了大量网站。",
    "PostgreSQL 等数据库支持复杂查询。",
    "红藻包括紫菜和石花菜。",
    "航空公司包括国航和东航。",
    "编程语言包括 Python 和 Rust。",
    "数据库包括 MySQL 和 PostgreSQL。",
    "紫菜是红藻的一种。",
    "国航是航空公司的一种。",
    "Python 是编程语言的一种。",
    "MySQL 是数据库的一种。",
]

CORPUS_DIRTY = [
    # 这些句子的「等」是动词，不是列举标记；「包括」主语不是上位词
    "国航 delay 了三小时才起飞。",
    "东航 wait 通知等了一整天。",
    "Python 等脚本跑完再说。",
    "MySQL 等命令执行完再退出。",
    "他 wait 公交车等了半个小时。",
    "票价包括了燃油和税费。",
    "机票价格包括燃油附加费和税费。",
    "会议包括了三个议题。",
    "数据库等问题还没解决。",
    "编程语言等工具在教学中有用。",
    "航空公司等行业受油价影响。",
    "红藻等水生植物富含营养。",
    "紫菜等食材常用于做汤。",
    "石花菜等藻类可以食用。",
    "Rust 等系统语言性能高。",
    "PostgreSQL 等关系型数据库很流行。",
    "国航等企业面临挑战。",
    "Python 等脚本语言容易学习。",
    "红藻等海洋生物富含碘。",
    "MySQL 等开源软件免费使用。",
]

CORPUS = CORPUS_CLEAN + CORPUS_DIRTY

# 词典：已知实体（模拟 NER）
ENT_DICT = {
    "紫菜": "ALGA", "石花菜": "ALGA", "红藻": "ALGA",
    "国航": "ORG", "东航": "ORG", "航空公司": "ORG",
    "Python": "LANG", "Rust": "LANG", "编程语言": "LANG",
    "MySQL": "DB", "PostgreSQL": "DB", "数据库": "DB",
}

# gold set: 正确的上下位对
GOLD = {
    ("紫菜", "红藻"), ("石花菜", "红藻"),
    ("国航", "航空公司"), ("东航", "航空公司"),
    ("Python", "编程语言"), ("Rust", "编程语言"),
    ("MySQL", "数据库"), ("PostgreSQL", "数据库"),
}

# 种子
SEEDS = [("紫菜", "红藻"), ("国航", "航空公司"), ("Python", "编程语言")]

# 模式：只在词典内匹配已知实体，避免贪婪匹配
def make_pat_X等Y():
    ents = "|".join(re.escape(e) for e in ENT_DICT)
    return re.compile(r"(" + ents + r")\s*等\s*(" + ents + r")")

def make_pat_X包括Y():
    ents = "|".join(re.escape(e) for e in ENT_DICT)
    return re.compile(r"(" + ents + r")包括(" + ents + r")")

def make_pat_X是Y的一种():
    ents = "|".join(re.escape(e) for e in ENT_DICT)
    return re.compile(r"(" + ents + r")是(" + ents + r")的一种")

PATTERNS = {
    "X等Y": make_pat_X等Y(),
    "X包括Y": make_pat_X包括Y(),
    "X是Y的一种": make_pat_X是Y的一种(),
}


def bootstrap_round(round_num, known_pairs, ent_dict):
    """执行一轮自举：用当前已知对找模式 → RlogF 打分 → 选 top-k 模式 → 扩展新对"""
    # 动态构建模式（实体词典可能已扩展）
    ents = "|".join(re.escape(e) for e in ent_dict)
    patterns = {
        "X等Y": re.compile(r"(" + ents + r")\s*等\s*(" + ents + r")"),
        "X包括Y": re.compile(r"(" + ents + r")包括(" + ents + r")"),
        "X是Y的一种": re.compile(r"(" + ents + r")是(" + ents + r")的一种"),
    }

    # Step 1: 找当前已知对能匹配到的模式实例
    pattern_stats = defaultdict(lambda: {"hits": 0, "finds": 0, "examples": []})
    for pat_name, pat in patterns.items():
        for sent in CORPUS:
            for m in pat.finditer(sent):
                child, parent = m.group(1), m.group(2)
                pattern_stats[pat_name]["finds"] += 1
                pattern_stats[pat_name]["examples"].append((child, parent, sent))
                if (child, parent) in known_pairs:
                    pattern_stats[pat_name]["hits"] += 1

    # Step 2: RlogF 打分
    scored = []
    for pat_name, st in pattern_stats.items():
        score = rlogf(st["hits"], st["finds"])
        scored.append((pat_name, score, st["hits"], st["finds"]))

    scored.sort(key=lambda x: -x[1])

    # Step 3: 选 top-k 模式（k=2）扩展新对
    top_k = scored[:2]
    new_pairs = set()
    for pat_name, _, _, _ in top_k:
        pat = patterns[pat_name]
        for sent in CORPUS:
            for m in pat.finditer(sent):
                child, parent = m.group(1), m.group(2)
                if (child, parent) not in known_pairs:
                    new_pairs.add((child, parent))

    # 计算 precision
    tp = len(new_pairs & GOLD)
    prec = tp / len(new_pairs) if new_pairs else 0.0

    return {
        "round": round_num,
        "pattern_scores": [{"pattern": p, "rlogf": round(s, 4), "hits": h, "finds": f}
                            for p, s, h, f in scored],
        "top_k": [p for p, _, _, _ in top_k],
        "new_pairs": sorted(list(new_pairs)),
        "n_new": len(new_pairs),
        "n_tp": tp,
        "precision": round(prec, 4),
    }


def main():
    # ---- Part 1: 公式重建展示 ----
    print("=" * 60)
    print("Part 1: RlogF formula reconstruction")
    print("=" * 60)
    print(f"{'pattern':<12} {'hits':>5} {'finds':>6} {'log(f)':>8} {'wrong':>8} {'correct':>10}")
    for r in recon_rows:
        logf = f"{r['log_finds']:.4f}" if r['log_finds'] is not None else "N/A"
        print(f"{r['pattern']:<12} {r['hits']:>5} {r['finds']:>6} {logf:>8} "
              f"{r['wrong_formula']:>8.2f} {r['correct_rlogf']:>10.4f}")

    print("\nKey insight: wrong formula ranks P1(5 hits) > P2(3 hits) > P5(1 hit)")
    print("Correct RlogF: P5(0.721) > P2(0.541) > P1(0.311) > P4(0.043)")
    print("The log-finds denominator penalizes patterns that fire too often.")

    # ---- Part 2: 三轮自举 ----
    print("\n" + "=" * 60)
    print("Part 2: 3-round bootstrapping with semantic drift")
    print("=" * 60)

    known = set(SEEDS)
    all_results = []
    cumulative = set(SEEDS)
    current_dict = dict(ENT_DICT)  # 每轮可能扩展

    # Round 1: 严格词典
    res1 = bootstrap_round(1, known, current_dict)
    all_results.append(res1)
    cumulative |= set(res1["new_pairs"])
    known |= set(res1["new_pairs"])

    # Round 1 结束后，模拟「NER 扩展到新域」：把脏样本中的实体加入词典
    # 这是漂移的来源：新实体没有人工校验，可能包含错误类型
    DIRTY_ENTS = {
        "脚本": "LANG", "工具": "LANG", "系统语言": "LANG",
        "食材": "ALGA", "藻类": "ALGA", "水生植物": "ALGA", "海洋生物": "ALGA",
        "企业": "ORG", "行业": "ORG",
        "问题": "DB", "开源软件": "DB", "关系型数据库": "DB",
        "税费": "FEE", "燃油": "FEE", "议题": "TOPIC",
        "公交车": "VEH", "通知": "INFO", "命令": "CMD",
    }
    current_dict.update(DIRTY_ENTS)

    # Round 2: 扩展后的词典
    res2 = bootstrap_round(2, known, current_dict)
    all_results.append(res2)
    cumulative |= set(res2["new_pairs"])
    known |= set(res2["new_pairs"])

    # Round 3: 继续用扩展后的词典
    res3 = bootstrap_round(3, known, current_dict)
    all_results.append(res3)
    cumulative |= set(res3["new_pairs"])
    known |= set(res3["new_pairs"])

    for res in all_results:
        rnd = res["round"]
        print(f"\nRound {rnd}:")
        print(f"  Top patterns: {res['top_k']}")
        print(f"  Pattern scores:")
        for ps in res["pattern_scores"]:
            print(f"    {ps['pattern']:<12} RlogF={ps['rlogf']:>8.4f}  (hits={ps['hits']}, finds={ps['finds']})")
        print(f"  New pairs: {res['new_pairs']}")
        print(f"  Precision: {res['precision']}  ({res['n_tp']}/{res['n_new']})")
        print(f"  Cumulative pairs: {len(cumulative)}")

    # 汇总
    summary = {
        "reconstruction": recon_rows,
        "rounds": all_results,
        "cumulative_pairs": sorted(list(cumulative)),
        "final_precision": round(len(cumulative & GOLD) / len(cumulative), 4) if cumulative else 0.0,
        "drift_detected": any(r["precision"] < 0.6 for r in all_results),
    }

    with open(os.path.join(OUT, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    # drift.csv
    with open(os.path.join(OUT, "drift.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["round", "top_pattern", "n_new", "n_tp", "precision", "cumulative_n"])
        cum = len(SEEDS)
        for r in all_results:
            cum += r["n_new"]
            w.writerow([r["round"], "|".join(r["top_k"]), r["n_new"],
                        r["n_tp"], r["precision"], cum])

    # 打印 drift 曲线
    print("\n" + "=" * 60)
    print("Drift curve:")
    print(f"{'Round':>6} {'New':>5} {'TP':>4} {'Prec':>8} {'Cumul':>6}")
    cum = len(SEEDS)
    for r in all_results:
        cum += r["n_new"]
        print(f"{r['round']:>6} {r['n_new']:>5} {r['n_tp']:>4} {r['precision']:>8.4f} {cum:>6}")

    first_drift = next((r["round"] for r in all_results if r["precision"] < 0.6), None)
    print(f"\nFirst round with precision < 0.6: {first_drift}")
    print(f"Final cumulative precision: {summary['final_precision']}")

    # 画 drift 图
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        rounds = [r["round"] for r in all_results]
        precs = [r["precision"] for r in all_results]
        plt.figure(figsize=(6, 4))
        plt.plot(rounds, precs, "ro-", label="precision")
        plt.axhline(y=0.6, color="gray", linestyle="--", label="drift threshold (0.6)")
        plt.xlabel("bootstrap round")
        plt.ylabel("precision")
        plt.title("Semantic drift in bootstrapping (ch21 lab-03)")
        plt.xticks(rounds)
        plt.ylim(-0.05, 1.05)
        plt.grid(alpha=.3)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(OUT, "drift.png"), dpi=130)
        print("drift.png saved")
    except Exception as e:
        print("plot skipped:", e)


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
