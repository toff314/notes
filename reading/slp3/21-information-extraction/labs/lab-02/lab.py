#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""lab-02：三类特征的关系分类器 + 特征消融

对应 §21.2.2「有监督的关系抽取」。
特征三类：两端词（head words）、中间词（between words）、实体类型组合（entity type pair）。
模型：逻辑回归（sklearn）。对比「全特征」 vs 「去掉实体类型特征」的 macro-F1。
"""
import csv, json, os
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, f1_score, classification_report
from sklearn.pipeline import Pipeline

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

REL = ["founder-of", "located-in", "employed-by", "no-relation"]

# (entity1, entity2, type1, type2, between_words, label)
SENTS = [
    # founder-of
    ("马云", "阿里巴巴", "PERSON", "ORG", ["创办", "了"], "founder-of"),
    ("马化腾", "腾讯", "PERSON", "ORG", ["创立", "了"], "founder-of"),
    ("李彦宏", "百度", "PERSON", "ORG", ["创建", "了"], "founder-of"),
    ("任正非", "华为", "PERSON", "ORG", ["创办", "了"], "founder-of"),
    ("雷军", "小米", "PERSON", "ORG", ["创立", "了"], "founder-of"),
    ("王兴", "美团", "PERSON", "ORG", ["创建", "了"], "founder-of"),
    ("乔布斯", "苹果", "PERSON", "ORG", ["创办", "了"], "founder-of"),
    ("盖茨", "微软", "PERSON", "ORG", ["创立", "了"], "founder-of"),
    # located-in
    ("北京", "中国", "GPE", "GPE", ["位于", "华北"], "located-in"),
    ("上海", "中国", "GPE", "GPE", ["地处", "华东"], "located-in"),
    ("广州", "广东", "GPE", "GPE", ["位于", "珠江"], "located-in"),
    ("深圳", "广东", "GPE", "GPE", ["地处", "珠江"], "located-in"),
    ("杭州", "浙江", "GPE", "GPE", ["位于", "钱塘"], "located-in"),
    ("巴黎", "法国", "GPE", "GPE", ["位于", "北部"], "located-in"),
    ("伦敦", "英国", "GPE", "GPE", ["地处", "东南"], "located-in"),
    ("东京", "日本", "GPE", "GPE", ["位于", "本州"], "located-in"),
    # employed-by
    ("张三", "华为", "PERSON", "ORG", ["在", "工作"], "employed-by"),
    ("李四", "腾讯", "PERSON", "ORG", ["在", "任职"], "employed-by"),
    ("王五", "百度", "PERSON", "ORG", ["在", "工作"], "employed-by"),
    ("赵六", "阿里", "PERSON", "ORG", ["在", "任职"], "employed-by"),
    ("小明", "字节", "PERSON", "ORG", ["在", "工作"], "employed-by"),
    ("小红", "美团", "PERSON", "ORG", ["在", "任职"], "employed-by"),
    ("刘强", "京东", "PERSON", "ORG", ["在", "工作"], "employed-by"),
    ("陈晨", "网易", "PERSON", "ORG", ["在", "任职"], "employed-by"),
    # no-relation
    ("马云", "北京", "PERSON", "GPE", ["在", "演讲"], "no-relation"),
    ("马化腾", "深圳", "PERSON", "GPE", ["在", "开会"], "no-relation"),
    ("李彦宏", "上海", "PERSON", "GPE", ["在", "参观"], "no-relation"),
    ("任正非", "广州", "PERSON", "GPE", ["在", "出差"], "no-relation"),
    ("雷军", "杭州", "PERSON", "GPE", ["在", "演讲"], "no-relation"),
    ("北京", "华为", "GPE", "ORG", ["与", "合作"], "no-relation"),
    ("上海", "腾讯", "GPE", "ORG", ["和", "合作"], "no-relation"),
    ("广州", "百度", "GPE", "ORG", ["与", "合作"], "no-relation"),
    # 测试集泛化样本：训练中未出现的实体对（模拟真实部署时的未登录实体）
    # founder-of 测试
    ("周鸿祎", "360", "PERSON", "ORG", ["创办", "了"], "founder-of"),
    ("贝索斯", "亚马逊", "PERSON", "ORG", ["创立", "了"], "founder-of"),
    # located-in 测试
    ("南京", "江苏", "GPE", "GPE", ["位于", "长江"], "located-in"),
    ("柏林", "德国", "GPE", "GPE", ["位于", "中欧"], "located-in"),
    # employed-by 测试
    ("孙七", "拼多多", "PERSON", "ORG", ["在", "工作"], "employed-by"),
    ("周八", "快手", "PERSON", "ORG", ["在", "任职"], "employed-by"),
    # no-relation 测试（关键陷阱：PERSON-GPE 介词相同但语义不是 employed-by）
    ("张三", "上海", "PERSON", "GPE", ["在", "演讲"], "no-relation"),
    ("王五", "北京", "PERSON", "GPE", ["在", "参观"], "no-relation"),
    # 关键消融样本：between words 相同「在/是」，关系由实体类型组合决定
    # PERSON-ORG + 「是...的」 -> employed-by（PERSON 是 ORG 的员工/成员）
    ("张三", "华为", "PERSON", "ORG", ["是", "的"], "employed-by"),
    ("李四", "腾讯", "PERSON", "ORG", ["是", "的"], "employed-by"),
    # GPE-GPE + 「是...的」 -> located-in（GPE 是 GPE 的一部分）
    ("南京", "江苏", "GPE", "GPE", ["是", "的"], "located-in"),
    ("苏州", "江苏", "GPE", "GPE", ["是", "的"], "located-in"),
    # 训练集中也加入对应的训练样本，让 typepair 特征有学习信号
    # 关键陷阱：PERSON-GPE + 「是...的」 -> no-relation（某人在某地，不是雇佣也不是位于）
    ("马云", "杭州", "PERSON", "GPE", ["是", "的"], "no-relation"),
    ("马化腾", "深圳", "PERSON", "GPE", ["是", "的"], "no-relation"),
]

# 在训练集中也加入「是...的」样本，让 typepair 特征有学习信号
SENTS_TRAIN_EXTRA = [
    ("王五", "百度", "PERSON", "ORG", ["是", "的"], "employed-by"),
    ("赵六", "阿里", "PERSON", "ORG", ["是", "的"], "employed-by"),
    ("小明", "字节", "PERSON", "ORG", ["是", "的"], "employed-by"),
    ("小红", "美团", "PERSON", "ORG", ["是", "的"], "employed-by"),
    ("杭州", "浙江", "GPE", "GPE", ["是", "的"], "located-in"),
    ("宁波", "浙江", "GPE", "GPE", ["是", "的"], "located-in"),
    ("广州", "广东", "GPE", "GPE", ["是", "的"], "located-in"),
    ("深圳", "广东", "GPE", "GPE", ["是", "的"], "located-in"),
    # PERSON-GPE + 「是...的」的训练样本：标为 no-relation
    ("李彦宏", "北京", "PERSON", "GPE", ["是", "的"], "no-relation"),
    ("任正非", "深圳", "PERSON", "GPE", ["是", "的"], "no-relation"),
    ("雷军", "武汉", "PERSON", "GPE", ["是", "的"], "no-relation"),
    ("周鸿祎", "北京", "PERSON", "GPE", ["是", "的"], "no-relation"),
    # GPE-ORG + 「是...的」的训练样本：也标为 no-relation（城市与公司无关）
    ("北京", "华为", "GPE", "ORG", ["是", "的"], "no-relation"),
    ("上海", "腾讯", "GPE", "ORG", ["是", "的"], "no-relation"),
    ("杭州", "阿里", "GPE", "ORG", ["是", "的"], "no-relation"),
    ("深圳", "字节", "GPE", "ORG", ["是", "的"], "no-relation"),
]

# 拆训练/测试：前 32 条 + 8 条额外训练样本 = 40 条训练，后 12 条为泛化测试
TRAIN = SENTS[:32] + SENTS_TRAIN_EXTRA
TEST  = SENTS[32:]


def feats(e1, e2, t1, t2, between, use_type=True):
    f = {
        f"head1={e1}": 1, f"head2={e2}": 1,
        f"heads={e1}|{e2}": 1,
    }
    for w in between:
        f[f"between={w}"] = 1
    f[f"len={len(between)}"] = 1
    if use_type:
        f[f"typepair={t1}-{t2}"] = 1
    return f


def run(use_type, tag):
    Xtr = [feats(*s[:5], use_type=use_type) for s in TRAIN]
    ytr = [s[5] for s in TRAIN]
    Xte = [feats(*s[:5], use_type=use_type) for s in TEST]
    yte = [s[5] for s in TEST]
    pipe = Pipeline([("vec", DictVectorizer()),
                     ("clf", LogisticRegression(max_iter=200, C=1.0))])
    pipe.fit(Xtr, ytr)
    yp = pipe.predict(Xte)
    f1s = f1_score(yte, yp, average="macro", zero_division=0)
    labels = sorted(set(ytr) | set(yp))
    cm = confusion_matrix(yte, yp, labels=labels)
    rep = classification_report(yte, yp, labels=labels, zero_division=0, output_dict=True)
    # 写预测明细
    rows = []
    for s, pred in zip(TEST, yp):
        rows.append([tag, s[0], s[1], s[5], pred, "OK" if pred == s[5] else "ERR"])
    return {"tag": tag, "macro_f1": round(f1s, 4), "labels": labels,
            "cm": cm.tolist(), "report": rep, "rows": rows,
            "n_feat_dim": len(pipe.named_steps["vec"].vocabulary_)}


def main():
    full = run(True, "full")
    no_type = run(False, "no_type")
    delta = round(full["macro_f1"] - no_type["macro_f1"], 4)

    # 汇总
    summary = {
        "n_train": len(TRAIN), "n_test": len(TEST),
        "n_classes": len(REL),
        "full_macro_f1": full["macro_f1"],
        "no_type_macro_f1": no_type["macro_f1"],
        "delta": delta,
        "full_feature_dim": full["n_feat_dim"],
        "no_type_feature_dim": no_type["n_feat_dim"],
        "full_confusion": full["cm"],
        "full_labels": full["labels"],
    }
    with open(os.path.join(OUT, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    with open(os.path.join(OUT, "predictions.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["config", "e1", "e2", "gold", "pred", "ok"])
        for r in full["rows"]:
            w.writerow(r)
        for r in no_type["rows"]:
            w.writerow(r)

    # 打印关键输出
    print(f"train={len(TRAIN)} test={len(TEST)}")
    print(f"full macro-F1   = {full['macro_f1']}  (dim={full['n_feat_dim']})")
    print(f"no-type macro-F1= {no_type['macro_f1']}  (dim={no_type['n_feat_dim']})")
    print(f"delta           = {delta}")
    print("\n[full confusion matrix]")
    print("labels:", full["labels"])
    for row, lab in zip(full["cm"], full["labels"]):
        print(f"  {lab:>12}: {row}")
    print("\n[per-class F1 full]")
    for lab in full["labels"]:
        d = full["report"][lab]
        print(f"  {lab:>12}: P={d['precision']:.3f} R={d['recall']:.3f} F1={d['f1-score']:.3f}")
    print("\n[per-class F1 no_type]")
    for lab in no_type["labels"]:
        d = no_type["report"][lab]
        print(f"  {lab:>12}: P={d['precision']:.3f} R={d['recall']:.3f} F1={d['f1-score']:.3f}")

    err = [r for r in full["rows"] if r[5] == "ERR"]
    print(f"\nerrors(full): {len(err)}")
    for r in err:
        print(f"  {r[1]}-{r[2]} gold={r[3]} pred={r[4]}")


if __name__ == "__main__":
    main()
