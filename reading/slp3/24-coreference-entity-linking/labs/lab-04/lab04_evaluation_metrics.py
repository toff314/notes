#!/usr/bin/env python3
"""lab-04 共指评价指标：MUC、B³、CEAF-e 实现与对比
复现 §24.8 三种指标在玩具语料上的行为差异。
"""
import json, itertools
from pathlib import Path

OUT = Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)

# 黄金链 vs 预测链（lab-02 entity_based 输出）
# 提及 id: 0=Victoria Chen, 1=Megabucks Banking, 2=her, 3=the 38-year-old,
#          4=the company, 5=she, 6=Lotsabucks, 7=Megabucks
GOLD = [[0, 2, 3, 5], [1, 4, 7], [6]]
PRED = [[0, 2, 3, 5], [1, 4, 7], [6]]  # entity_based 完美预测

# 故意造一个有错误的预测：把 Lotsabucks 错并入 Megabucks 链
PRED_BAD = [[0, 2, 3, 5], [1, 4, 6, 7]]

# ---- MUC ----
def muc_precision_recall(gold, pred):
    # P = sum over pred chains of (|chain| - #gold chains it intersects) / (total pred mentions - #pred chains)
    # R = sum over gold chains of (|chain| - #pred chains it intersects) / (total gold mentions - #gold chains)
    def count_links(chains_a, chains_b):
        # 对 A 中每个链，计算 |chain| - （与 B 中不同链的交集数）
        total = 0
        for ca in chains_a:
            # ca 中每个元素属于 B 的哪个链
            b_chains_of_ca = set()
            for cb in chains_b:
                if set(ca) & set(cb):
                    b_chains_of_ca.add(id(cb))
            total += len(ca) - len(b_chains_of_ca)
        return total
    total_pred_mentions = sum(len(c) for c in pred)
    total_gold_mentions = sum(len(c) for c in gold)
    p_num = count_links(pred, gold)
    p_den = total_pred_mentions - len(pred)
    r_num = count_links(gold, pred)
    r_den = total_gold_mentions - len(gold)
    P = p_num / p_den if p_den else 0
    R = r_num / r_den if r_den else 0
    return P, R

def f1(p, r):
    return 2*p*r/(p+r) if p+r else 0

# ---- B³ ----
def b3_precision_recall(gold, pred):
    # 对每个提及，计算其所在 pred 链与所在 gold 链的交集 / 链大小
    mention_to_gold = {}
    for i, c in enumerate(gold):
        for m in c:
            mention_to_gold[m] = i
    mention_to_pred = {}
    for i, c in enumerate(pred):
        for m in c:
            mention_to_pred[m] = i
    gold_sets = [set(c) for c in gold]
    pred_sets = [set(c) for c in pred]
    P_num, P_den = 0, 0
    R_num, R_den = 0, 0
    for m in mention_to_gold:
        g = gold_sets[mention_to_gold[m]]
        p = pred_sets[mention_to_pred[m]]
        inter = len(g & p)
        P_num += inter / len(p)
        P_den += 1
        R_num += inter / len(g)
        R_den += 1
    P = P_num / P_den if P_den else 0
    R = R_num / R_den if R_den else 0
    return P, R

# ---- CEAF-e（简化版：最优对齐用贪心/匈牙利）----
def ceaf_e_precision_recall(gold, pred):
    """CEAF-e: 对齐 pred 链到 gold 链，最大化提及交集总和"""
    # 简化：贪心对齐（小数据够用）
    gold_sets = [set(c) for c in gold]
    pred_sets = [set(c) for c in pred]
    # 计算所有交集
    inter = [[len(g & p) for p in pred_sets] for g in gold_sets]
    # 贪心：每次取最大交集
    used_g, used_p = set(), set()
    pairs = []
    for _ in range(min(len(gold_sets), len(pred_sets))):
        best, best_i, best_j = 0, -1, -1
        for i in range(len(gold_sets)):
            for j in range(len(pred_sets)):
                if i in used_g or j in used_p:
                    continue
                if inter[i][j] > best:
                    best, best_i, best_j = inter[i][j], i, j
        if best_i >= 0:
            used_g.add(best_i); used_p.add(best_j)
            pairs.append((best_i, best_j, best))
    # P = sum(inter) / total pred mentions
    # R = sum(inter) / total gold mentions
    total_inter = sum(p[2] for p in pairs)
    P = total_inter / sum(len(c) for c in pred_sets)
    R = total_inter / sum(len(c) for c in gold_sets)
    return P, R

def evaluate(gold, pred, name):
    muc_p, muc_r = muc_precision_recall(gold, pred)
    b3_p, b3_r = b3_precision_recall(gold, pred)
    ceaf_p, ceaf_r = ceaf_e_precision_recall(gold, pred)
    result = {
        "MUC": {"P": round(muc_p,3), "R": round(muc_r,3), "F1": round(f1(muc_p, muc_r),3)},
        "B3":  {"P": round(b3_p,3), "R": round(b3_r,3), "F1": round(f1(b3_p, b3_r),3)},
        "CEAFe": {"P": round(ceaf_p,3), "R": round(ceaf_r,3), "F1": round(f1(ceaf_p, ceaf_r),3)},
    }
    conll_f1 = round((result["MUC"]["F1"] + result["B3"]["F1"] + result["CEAFe"]["F1"]) / 3, 3)
    result["CoNLL_F1"] = conll_f1
    return result

# ---- 实验 ----
results = {
    "gold_vs_pred_perfect": evaluate(GOLD, PRED, "perfect"),
    "gold_vs_pred_bad": evaluate(GOLD, PRED_BAD, "bad"),
    "metric_differences": {
        "MUC_bias": "MUC 偏好产生大链：对 PRED_BAD 的 F1 比 B³ 高，因为 MUC 奖励把更多提及并入同一链",
        "B3_mention_based": "B³ 基于提及而非链接，对单例和错误合并更敏感",
        "CEAFe_entity_alignment": "CEAFe 通过实体对齐，介于 MUC 和 B³ 之间，是 CoNLL 标准"
    }
}

(OUT / "metric_comparison.json").write_text(json.dumps(results, ensure_ascii=False, indent=2))

print("=== 共指评价指标对比 ===")
print("\n--- 完美预测 (entity_based) ---")
for k, v in results["gold_vs_pred_perfect"].items():
    print(f"  {k}: {v}")
print("\n--- 有错误的预测 (Lotsabucks 错并入 Megabucks) ---")
for k, v in results["gold_vs_pred_bad"].items():
    print(f"  {k}: {v}")
print("\n--- 指标差异 ---")
for k, v in results["metric_differences"].items():
    print(f"  {k}: {v}")
