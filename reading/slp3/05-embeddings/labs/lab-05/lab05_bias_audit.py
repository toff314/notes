#!/usr/bin/env python3
"""lab-05: 性别—属性偏差审计（IAT 式余弦差 + 置换检验）。

对应《Speech and Language Processing》第 3 版 §5.8（偏见会再现并放大）、
§5.9（语料/随机性导致结论不稳定，本语料的样本量必须被报告）。

做法：
  1. 复用 lab-04 的语料与 PPMI-SVD 向量（同一份本章英文原文，窗口 ±5）。
  2. 计算「男性词 vs 属性词」「女性词 vs 属性词」的平均余弦，
     以差值衡量刻板关联（Caliskan 等 2017 的做法）。
  3. 关键补充：置换检验——从词表随机抽同样大小的词组 1000 次，
     看观测差值是否只是噪声；同时报告每个词的实际出现次数。

运行：python3 lab05_bias_audit.py
产物：out/bias_audit.csv, out/bias_permutation.csv, out/bias_counts.json, out/bias_effect.png
"""
import csv
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
sys.path.insert(0, os.path.join(HERE, "..", "lab-04"))

from lab04_normalization_and_bias import DUAL, build, load_sentences  # noqa: E402

MALE = ["man", "male", "he", "his", "him", "boy", "father", "king"]
FEMALE = ["woman", "female", "she", "her", "girl", "mother", "queen"]
SCIENCE = ["computer", "science", "algorithm", "math", "engineering", "data"]
ARTS = ["art", "poetry", "emotion", "family", "home", "literature"]


def mean_pair(cd, a, b):
    if not a or not b:
        return float("nan")
    return float(np.mean([cd[x] @ cd[y] for x in a for y in b]))


def main():
    os.makedirs(OUT, exist_ok=True)
    sents = load_sentences(DUAL)
    vocab, freq, mat, raw, unit = build(sents)
    cd = {w: unit[i] for i, w in enumerate(vocab)}

    def present(words):
        return [w for w in words if w in cd]

    mp, fp, sp, ap = present(MALE), present(FEMALE), present(SCIENCE), present(ARTS)

    rows = []
    for group_name, group, other in (("male", mp, fp), ("female", fp, mp)):
        for attr_name, attr in (("science", sp), ("arts", ap)):
            rows.append([group_name, attr_name, len(group), len(attr),
                         f"{mean_pair(cd, group, attr):.4f}",
                         f"{mean_pair(cd, other, attr):.4f}",
                         f"{mean_pair(cd, group, attr) - mean_pair(cd, other, attr):+.4f}"])

    rng = np.random.default_rng(0)
    perm = []
    effects = {}
    for attr_name, attr in (("science", sp), ("arts", ap)):
        if not attr:
            continue
        observed = abs(mean_pair(cd, mp, attr) - mean_pair(cd, fp, attr))
        effects[attr_name] = observed
        null = []
        for _ in range(1000):
            a = [vocab[i] for i in rng.choice(len(vocab), size=len(mp), replace=False)]
            b = [vocab[i] for i in rng.choice(len(vocab), size=len(fp), replace=False)]
            null.append(abs(mean_pair(cd, a, attr) - mean_pair(cd, b, attr)))
        null = np.array(null)
        perm.append([attr_name, len(mp), len(attr), f"{observed:.4f}",
                     f"{null.mean():.4f}", f"{null.std():.4f}",
                     f"{float((null >= observed).mean()):.3f}"])

    with open(os.path.join(OUT, "bias_audit.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["group", "attribute_set", "n_group", "n_attr",
                    "mean_cos_group_attr", "mean_cos_other_attr", "difference"])
        w.writerows(rows)
    with open(os.path.join(OUT, "bias_permutation.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["attribute_set", "n_group", "n_attr", "observed_abs_diff",
                    "null_mean", "null_sd", "perm_p_value"])
        w.writerows(perm)
    counts = {name: {x: freq.get(x, 0) for x in words} for name, words in
              (("male", MALE), ("female", FEMALE), ("science", SCIENCE), ("arts", ARTS))}
    with open(os.path.join(OUT, "bias_counts.json"), "w", encoding="utf-8") as f:
        json.dump(counts, f, ensure_ascii=False, indent=2)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 4), dpi=150)
    labels, vals = [], []
    for attr_name in ("science", "arts"):
        labels += [f"male-{attr_name}", f"female-{attr_name}"]
        attr = sp if attr_name == "science" else ap
        vals += [mean_pair(cd, mp, attr), mean_pair(cd, fp, attr)]
    ax.bar(labels, vals, color=["#2c6fbb", "#c0392b", "#2c6fbb", "#c0392b"])
    for p in perm:
        ax.set_title(f"Gender-attribute cosine (perm p={float(p[6]):.2f}, n_group={p[1]})")
    ax.set_ylabel("mean cosine")
    ax.tick_params(axis="x", labelrotation=15)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "bias_effect.png"))
    plt.close(fig)

    print(f"tokens={sum(len(s) for s in sents)} vocab={len(vocab)}")
    print("audit:")
    for r in rows:
        print("  ", r)
    print("permutation:")
    for p in perm:
        print("  ", p)
    print("counts:", json.dumps(counts, ensure_ascii=False))


if __name__ == "__main__":
    main()
