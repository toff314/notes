#!/usr/bin/env python3
"""lab-03: BIO 序列评估——词元级 vs 实体级，并把错误按边界/类型/虚增/漏标归因。

三个对照预测：
  A 少标一个词（Jane 而非 Jane Villanueva）——书中 §18.6 的例子
  B 多标一个词（同上句，把 of 吞进机构名）
  C 类型错（人名标成机构名）
"""
import csv
import json
import os

GOLD = {
    "s1": "B-PER I-PER O B-ORG I-ORG O O B-LOC".split(),
    "s2": "O B-ORG I-ORG I-ORG O B-LOC".split(),
    "s3": "B-PER I-PER B-PER I-PER O O".split(),
}
PRED = {
    "A_short": {
        "s1": "B-PER O O B-ORG I-ORG O O B-LOC".split(),
        "s2": "O B-ORG I-ORG I-ORG O B-LOC".split(),
        "s3": "B-PER I-PER B-PER I-PER O O".split(),
    },
    "B_long": {
        "s1": "B-PER I-PER O B-ORG I-ORG I-ORG O B-LOC".split(),
        "s2": "O B-ORG I-ORG I-ORG O B-LOC".split(),
        "s3": "B-PER I-PER B-PER I-PER O O".split(),
    },
    "C_type": {
        "s1": "B-PER I-PER O B-ORG I-ORG O O B-LOC".split(),
        "s2": "O B-ORG I-ORG I-ORG O B-LOC".split(),
        "s3": "B-ORG I-ORG B-PER I-PER O O".split(),
    },
}


def spans(seq):
    """BIO -> [(start, end_exclusive, type)]；非法 I 直接开新片段，便于暴露数据问题。"""
    out, cur = [], None
    for i, t in enumerate(seq):
        if t == "O":
            if cur:
                out.append(tuple(cur)); cur = None
            continue
        pre, typ = t.split("-", 1)
        if pre == "B" or cur is None or cur[2] != typ:
            if cur:
                out.append(tuple(cur))
            cur = [i, i + 1, typ]
        else:
            cur[1] = i + 1
    if cur:
        out.append(tuple(cur))
    return out


def score(gold, pred):
    tp = sorted(set(spans(gold)) & set(spans(pred)))
    pg, pp = set(spans(gold)), set(spans(pred))
    fp = sorted(pp - pg)
    fn = sorted(pg - pp)
    p = len(tp) / (len(tp) + len(fp)) if tp or fp else 0.0
    r = len(tp) / (len(tp) + len(fn)) if tp or fn else 0.0
    f1 = 2 * p * r / (p + r) if p + r else 0.0
    toks = sum(a == b for a, b in zip(gold, pred))
    return {"token_acc": round(toks / len(gold), 4), "tp": len(tp), "fp": len(fp),
            "fn": len(fn), "P": round(p, 4), "R": round(r, 4), "F1": round(f1, 4)}


def taxonomy(gold, pred):
    """把每个错误归入：边界(部分重叠)、类型(完全重叠但类型不同)、虚增、漏标"""
    gs, ps = spans(gold), spans(pred)
    kinds = {"boundary": 0, "type": 0, "spurious": 0, "missing": 0}
    used_g, used_p = set(), set()
    for gi, g in enumerate(gs):
        for pi, p in enumerate(ps):
            if pi in used_p:
                continue
            ov = min(g[1], p[1]) - max(g[0], p[0])
            if ov <= 0:
                continue
            used_g.add(gi); used_p.add(pi)
            if (g[0], g[1], g[2]) != (p[0], p[1], p[2]):
                if (g[0], g[1]) != (p[0], p[1]):
                    kinds["boundary"] += 1
                else:
                    kinds["type"] += 1
            break
    kinds["missing"] = len(gs) - len(used_g)
    kinds["spurious"] = len(ps) - len(used_p)
    return kinds


def io_degeneration():
    """相邻两个同类实体：BIO 能切开，抹掉 B 之后无法还原"""
    bio = ["B-PER", "I-PER", "B-PER"]
    io = [t if t == "O" else "I-" + t.split("-")[1] for t in bio]
    return {"bio": bio, "io": io, "bio_spans": spans(bio), "io_spans": spans(io)}


def main():
    os.makedirs("out", exist_ok=True)
    metrics, rows = {}, []
    for name, pred in PRED.items():
        tot = {"tp": 0, "fp": 0, "fn": 0}
        kinds = {"boundary": 0, "type": 0, "spurious": 0, "missing": 0}
        tok = n = 0
        for sid, gold in GOLD.items():
            s = score(gold, pred[sid])
            tok += s["token_acc"] * len(gold); n += len(gold)
            for k in tot:
                tot[k] += s[k]
            for k, v in taxonomy(gold, pred[sid]).items():
                kinds[k] += v
        P = tot["tp"] / (tot["tp"] + tot["fp"]) if tot["tp"] + tot["fp"] else 0.0
        R = tot["tp"] / (tot["tp"] + tot["fn"]) if tot["tp"] + tot["fn"] else 0.0
        metrics[name] = {"token_acc": round(tok / n, 4),
                         "entity_P": round(P, 4), "entity_R": round(R, 4),
                         "entity_F1": round(2 * P * R / (P + R), 4) if P + R else 0.0,
                         **tot, **kinds}
        rows.append([name, metrics[name]["token_acc"], metrics[name]["entity_P"],
                     metrics[name]["entity_R"], metrics[name]["entity_F1"],
                     kinds["boundary"], kinds["type"], kinds["spurious"], kinds["missing"]])
    metrics["io_vs_bio"] = io_degeneration()
    with open("out/metrics.json", "w") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    with open("out/errors.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["case", "token_acc", "P", "R", "F1", "boundary", "type", "spurious", "missing"])
        w.writerows(rows)
    for name, m in metrics.items():
        if name != "io_vs_bio":
            print(f"{name:8} token={m['token_acc']:.3f} P={m['entity_P']:.3f} "
                  f"R={m['entity_R']:.3f} F1={m['entity_F1']:.3f} "
                  f"界={m['boundary']} 型={m['type']} 虚={m['spurious']} 漏={m['missing']}")
    print("IO 退化:", metrics["io_vs_bio"])


if __name__ == "__main__":
    main()
