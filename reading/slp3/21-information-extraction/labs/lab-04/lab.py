#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""lab-04：远程监督噪声率实验

对应 §21.2.4「远程监督（distant supervision）」。

用一份小型 KB（30 条 is-a / located-in 事实）去语料里找共现句自动打标。
对比两种聚合策略：
  A) 「任一句共现即正」（Mintz et al. 2009 的默认假设）
  B) 「至少一句含明确模式才正」（加模式过滤）
量化两种策略的噪声率（假阳性率），并列出典型假阳性。
"""
import csv, json, os, re
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. 小型 KB：30 条事实（15 条 is-a + 15 条 located-in）
# ---------------------------------------------------------------------------
KB = [
    # is-a
    ("紫菜", "红藻"), ("石花菜", "红藻"), ("江蓠", "红藻"),
    ("国航", "航空公司"), ("东航", "航空公司"), ("南航", "航空公司"),
    ("Python", "编程语言"), ("Rust", "编程语言"), ("Java", "编程语言"),
    ("MySQL", "数据库"), ("PostgreSQL", "数据库"), ("Oracle", "数据库"),
    ("苹果", "水果"), ("香蕉", "水果"), ("橙子", "水果"),
    # located-in
    ("北京", "中国"), ("上海", "中国"), ("广州", "中国"),
    ("深圳", "中国"), ("杭州", "中国"), ("南京", "中国"),
    ("巴黎", "法国"), ("伦敦", "英国"), ("东京", "日本"),
    ("柏林", "德国"), ("莫斯科", "俄罗斯"), ("首尔", "韩国"),
    ("纽约", "美国"), ("洛杉矶", "美国"), ("芝加哥", "美国"),
]

# ---------------------------------------------------------------------------
# 2. 语料：50 句，其中 30 句包含 KB 实体对（正例来源），20 句为干扰
# ---------------------------------------------------------------------------
CORPUS = [
    # 包含 KB 实体对的句子（正例候选）
    "紫菜等红藻富含碘。",                           # 紫菜-红藻 ✓ is-a
    "石花菜等红藻可用于提取琼胶。",                 # 石花菜-红藻 ✓
    "江蓠等红藻在浅海生长。",                       # 江蓠-红藻 ✓
    "国航等航空公司上调了票价。",                   # 国航-航空公司 ✓
    "东航等航空公司随即跟进。",                     # 东航-航空公司 ✓
    "南航等航空公司也宣布涨价。",                   # 南航-航空公司 ✓
    "Python 等编程语言在本课程中使用。",             # Python-编程语言 ✓
    "Rust 等编程语言适合写系统软件。",               # Rust-编程语言 ✓
    "Java 等编程语言在企业中广泛应用。",             # Java-编程语言 ✓
    "MySQL 等数据库支撑了大量网站。",                # MySQL-数据库 ✓
    "PostgreSQL 等数据库支持复杂查询。",             # PostgreSQL-数据库 ✓
    "Oracle 等数据库在商业领域很常见。",             # Oracle-数据库 ✓
    "苹果等水果富含维生素。",                       # 苹果-水果 ✓
    "香蕉等水果在热带地区生长。",                   # 香蕉-水果 ✓
    "橙子等水果可以榨汁。",                         # 橙子-水果 ✓
    "北京位于中国华北。",                           # 北京-中国 ✓ located-in
    "上海地处中国华东。",                           # 上海-中国 ✓
    "广州位于中国华南。",                           # 广州-中国 ✓
    "深圳地处中国南方。",                           # 深圳-中国 ✓
    "杭州位于中国东南沿海。",                       # 杭州-中国 ✓
    "南京位于中国长江下游。",                       # 南京-中国 ✓
    "巴黎位于法国北部。",                           # 巴黎-法国 ✓
    "伦敦地处英国东南部。",                         # 伦敦-英国 ✓
    "东京位于日本本州。",                           # 东京-日本 ✓
    "柏林位于德国东北部。",                         # 柏林-德国 ✓
    "莫斯科位于俄罗斯西部。",                       # 莫斯科-俄罗斯 ✓
    "首尔位于韩国西北部。",                         # 首尔-韩国 ✓
    "纽约位于美国东海岸。",                         # 纽约-美国 ✓
    "洛杉矶位于美国西海岸。",                       # 洛杉矶-美国 ✓
    "芝加哥位于美国中西部。",                       # 芝加哥-美国 ✓
    # 干扰句：包含 KB 实体但关系不是 KB 中的关系（远程监督的假阳性来源）
    "马云在北京演讲。",                             # 马云-北京：人-地，不是 located-in
    "马化腾在深圳开会。",                           # 马化腾-深圳：人-地
    "李彦宏参观了上海。",                           # 李彦宏-上海：人-地
    "任正非去过莫斯科。",                           # 任正非-莫斯科：人-地
    "雷军在杭州演讲。",                             # 雷军-杭州：人-地
    "北京举办了水果展览会。",                       # 北京-水果：地-物
    "上海的冬天很冷。",                             # 上海-冬天：地-时间
    "广州和深圳是一线城市。",                       # 广州-深圳：并列
    "Python 比 Java 更简洁。",                       # Python-Java：并列比较
    "MySQL 和 Oracle 都是数据库。",                 # MySQL-Oracle：并列
    "苹果和香蕉都是常见水果。",                     # 苹果-香蕉：并列
    "紫菜汤很美味。",                               # 紫菜-汤：整体-部分
    "国航的航班准点率高。",                         # 国航-航班：整体-部分
    "Python 的语法很简单。",                         # Python-语法：整体-部分
    "北京的人口超过两千万。",                       # 北京-人口：整体-部分
    "巴黎是浪漫之都。",                             # 巴黎-浪漫之都：同义/隐喻
    "红藻富含碘元素。",                             # 红藻-碘：整体-部分
    "航空公司面临油价压力。",                       # 航空公司-油价：无关
    "编程语言不断发展。",                           # 编程语言-发展：主谓
    "数据库需要定期备份。",                         # 数据库-备份：主谓
]

# ---------------------------------------------------------------------------
# 3. 远程监督打标
# ---------------------------------------------------------------------------

# 判断句子是否表达 is-a 关系（简单模式）
IS_A_PAT = re.compile(r"(\S{2,10})\s*等\s*(\S{2,10})|(\S{2,10})包括(\S{2,10})|(\S{2,10})是(\S{2,10})的一种")

# 判断句子是否表达 located-in 关系
LOC_IN_PAT = re.compile(r"(\S{2,10})\s*(?:位于|地处|在)\s*(\S{2,10})")


# 所有 KB 中涉及的实体
ALL_ENTS = set()
for e1, e2 in KB:
    ALL_ENTS.add(e1)
    ALL_ENTS.add(e2)


IS_A_TRIGGERS = ["等", "包括", "的一种", "例如", "如"]
LOC_IN_TRIGGERS = ["位于", "地处", "坐落在", "在"]
PERSONS = {"马云", "马化腾", "李彦宏", "任正非", "雷军"}


def has_explicit_pattern(sent, e1, e2, rel_type):
    """判断句子是否含明确的关系模式，且实体对匹配"""
    if rel_type == "is-a":
        return any(t in sent for t in IS_A_TRIGGERS) and e1 in sent and e2 in sent
    elif rel_type == "located-in":
        for trig in ["位于", "地处", "坐落在"]:
            if trig in sent and e1 in sent and e2 in sent:
                return True
        if "在" in sent and e1 in sent and e2 in sent:
            if e1 not in PERSONS:
                return True
        return False
    return False


def extract_entity_pairs(sent):
    """从句中提取所有 KB 实体对（按 KB 中的顺序匹配）"""
    pairs = []
    for (k1, k2) in KB:
        if k1 in sent and k2 in sent:
            rel_type = "is-a" if k2 in ["红藻", "航空公司", "编程语言", "数据库", "水果"] else "located-in"
            pairs.append((k1, k2))
    return pairs


def label_corpus(strategy):
    """对语料打标。strategy: 'any' 或 'pattern'"""
    labels = []
    for sent in CORPUS:
        pairs = extract_entity_pairs(sent)
        for (e1, e2) in pairs:
            rel_type = "is-a" if (e1, e2) in KB and any(e2 == p for c, p in KB if c == e1 and p in ["红藻", "航空公司", "编程语言", "数据库", "水果"]) else "located-in"
            # 判断正例
            if strategy == "any":
                # 策略 A：任一句共现即正
                is_pos = True
            else:
                # 策略 B：至少一句含明确模式才正
                is_pos = has_explicit_pattern(sent, e1, e2, rel_type)
            labels.append({
                "sent": sent, "e1": e1, "e2": e2, "rel": rel_type,
                "is_pos": is_pos, "strategy": strategy,
            })
    return labels


def evaluate(labels):
    """计算噪声率。正例 = 真正表达 KB 关系的句子；负例 = 共现但不表达关系的句子"""
    # 手动标注 gold：哪些句子真的表达了 KB 关系
    # 前 30 句是正例，后 20 句是干扰（负例）
    n_total = len(labels)
    n_pos_pred = sum(1 for l in labels if l["is_pos"])
    n_neg_pred = n_total - n_pos_pred

    # 真实正例：前 30 句中每句恰好 1 对
    gold_pos = set()
    for i, sent in enumerate(CORPUS[:30]):
        pairs = extract_entity_pairs(sent)
        if pairs:
            gold_pos.add((sent, pairs[0][0], pairs[0][1]))

    # 预测正例中，多少是真的
    tp = sum(1 for l in labels if l["is_pos"] and (l["sent"], l["e1"], l["e2"]) in gold_pos)
    fp = n_pos_pred - tp
    fn = len(gold_pos) - tp

    precision = tp / n_pos_pred if n_pos_pred else 0.0
    recall = tp / len(gold_pos) if gold_pos else 0.0
    noise_rate = fp / n_pos_pred if n_pos_pred else 0.0  # 假阳性率 = 噪声率

    return {
        "n_total": n_total, "n_pos_pred": n_pos_pred, "n_neg_pred": n_neg_pred,
        "tp": tp, "fp": fp, "fn": fn,
        "precision": round(precision, 4), "recall": round(recall, 4),
        "noise_rate": round(noise_rate, 4),
    }


def main():
    # 两种策略打标
    labels_any = label_corpus("any")
    labels_pat = label_corpus("pattern")

    # 评估
    eval_any = evaluate(labels_any)
    eval_pat = evaluate(labels_pat)

    # 收集典型假阳性
    fp_examples = []
    gold_pos_sents = set(CORPUS[:30])
    for l in labels_any:
        if l["is_pos"] and l["sent"] not in gold_pos_sents:
            fp_examples.append(l)

    # 汇总
    summary = {
        "kb_size": len(KB),
        "corpus_size": len(CORPUS),
        "strategy_any": eval_any,
        "strategy_pattern": eval_pat,
        "delta_noise": round(eval_any["noise_rate"] - eval_pat["noise_rate"], 4),
        "fp_examples": fp_examples[:5],
    }

    with open(os.path.join(OUT, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    # CSV
    with open(os.path.join(OUT, "labels_any.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sent", "e1", "e2", "rel", "is_pos"])
        for l in labels_any:
            w.writerow([l["sent"], l["e1"], l["e2"], l["rel"], l["is_pos"]])

    with open(os.path.join(OUT, "labels_pattern.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sent", "e1", "e2", "rel", "is_pos"])
        for l in labels_pat:
            w.writerow([l["sent"], l["e1"], l["e2"], l["rel"], l["is_pos"]])

    # 打印
    print("=" * 60)
    print("Distant supervision noise rate experiment")
    print("=" * 60)
    print(f"KB size: {len(KB)} facts")
    print(f"Corpus size: {len(CORPUS)} sentences")
    print(f"  - Positive candidate sentences: 30")
    print(f"  - Distractor sentences: 20")
    print()

    print("Strategy A: 'any co-occurrence is positive' (Mintz et al. 2009)")
    print(f"  Total labeled: {eval_any['n_total']}")
    print(f"  Predicted positive: {eval_any['n_pos_pred']}")
    print(f"  TP={eval_any['tp']} FP={eval_any['fp']} FN={eval_any['fn']}")
    print(f"  Precision: {eval_any['precision']}")
    print(f"  Recall: {eval_any['recall']}")
    print(f"  Noise rate (FP / predicted positive): {eval_any['noise_rate']}")
    print()

    print("Strategy B: 'at least one explicit pattern' (filtered)")
    print(f"  Total labeled: {eval_pat['n_total']}")
    print(f"  Predicted positive: {eval_pat['n_pos_pred']}")
    print(f"  TP={eval_pat['tp']} FP={eval_pat['fp']} FN={eval_pat['fn']}")
    print(f"  Precision: {eval_pat['precision']}")
    print(f"  Recall: {eval_pat['recall']}")
    print(f"  Noise rate (FP / predicted positive): {eval_pat['noise_rate']}")
    print()

    print(f"Delta noise rate (A - B): {summary['delta_noise']}")
    print()

    print("Typical false positives (Strategy A):")
    for i, fp in enumerate(fp_examples[:5], 1):
        print(f"  {i}. [{fp['e1']}-{fp['e2']}] {fp['sent']}")
        print(f"     Reason: entities co-occur but relation is not '{fp['rel']}'")


if __name__ == "__main__":
    main()
