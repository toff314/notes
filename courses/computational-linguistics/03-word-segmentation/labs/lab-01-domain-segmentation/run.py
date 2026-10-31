# -*- coding: utf-8 -*-
"""通用 vs 专用分词实测：jieba 通用 / jieba+领域词典 / FMM+领域词典，带 P/R/F1"""
import jieba, json

DOMAIN_TERMS = ["等保测评","零信任","容器逃逸","态势感知","数据脱敏","护网行动","基线核查"]

# (句子, 金标准切分) —— 金标准按云安全领域口径
CASES = [
    ("等保测评要求做基线核查和漏洞扫描",
     ["等保测评","要求","做","基线核查","和","漏洞扫描"]),
    ("零信任架构下容器逃逸风险需要态势感知",
     ["零信任","架构","下","容器逃逸","风险","需要","态势感知"]),
    ("护网行动期间数据脱敏必须到位",
     ["护网行动","期间","数据脱敏","必须","到位"]),
]

def prf(pred, gold):
    pred_set = set(enumerate(pred)) - set()
    # 用 (起始下标, 词) 对齐比较，避免位置错位
    def spans(seg):
        out, i = set(), 0
        for w in seg:
            out.add((i, w)); i += len(w)
        return out
    p, g = spans(pred), spans(gold)
    tp = len(p & g)
    P = tp/len(p) if p else 0; R = tp/len(g) if g else 0
    F = 2*P*R/(P+R) if P+R else 0
    return round(P,3), round(R,3), round(F,3)

def fmm(text, lexicon, maxlen=6):
    res, i = [], 0
    while i < len(text):
        hit = None
        for L in range(min(maxlen, len(text)-i), 0, -1):
            if text[i:i+L] in lexicon: hit = text[i:i+L]; break
        if hit: res.append(hit); i += len(hit)
        else: res.append(text[i]); i += 1
    return res

results = {}
# 方案A：jieba 默认（通用）
jieba.initialize()
resA = [list(jieba.cut(s)) for s, _ in CASES]
# 方案B：jieba + 领域词典（专用化）
for t in DOMAIN_TERMS: jieba.add_word(t)
resB = [list(jieba.cut(s)) for s, _ in CASES]
# 方案C：FMM + 领域词典（规则专用，课堂方法）
lex = set(jieba.dt.FREQ.keys()) | set(DOMAIN_TERMS)  # jieba 主词典 ∪ 领域词
resC = [fmm(s, lex) for s, _ in CASES]

for name, res in [("A_jieba通用", resA), ("B_jieba加领域词典", resB), ("C_FMM加领域词典", resC)]:
    Ps, Rs, Fs = [], [], []
    detail = []
    for (s, gold), pred in zip(CASES, res):
        P, R, F = prf(pred, gold)
        Ps.append(P); Rs.append(R); Fs.append(F)
        detail.append({"句": s, "预测": pred, "P": P, "R": R, "F1": F})
    results[name] = {"avgF1": round(sum(Fs)/len(Fs),3), "detail": detail}

print(json.dumps(results, ensure_ascii=False, indent=1))
