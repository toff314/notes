"""lab-03: BIO 标注、子词对齐与实体级评估
把词级 BIO 标签复制到 WordPiece 式子词上，再按首子词解码回词级；
比较词级准确率与实体级 P/R/F1，并用句子级自助法给出 F1 的 95% 区间。

运行: python3 lab03_bio_alignment.py
"""
import csv
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(11)

# ---------- 数据：词 + 词级 BIO ----------
DATA = [
    (["Mt.", "Sanitas", "is", "in", "Sunshine", "Canyon", "."],
     ["B-LOC", "I-LOC", "O", "O", "B-LOC", "I-LOC", "O"]),
    (["Jane", "Villanueva", "works", "at", "United", "Airlines", "Holding", "."],
     ["B-PER", "I-PER", "O", "O", "B-ORG", "I-ORG", "I-ORG", "O"]),
    (["Tim", "Wagner", "spoke", "in", "Chicago", "."],
     ["B-PER", "I-PER", "O", "O", "B-LOC", "O"]),
    (["AMR", "Corp.", "raised", "fares", "on", "Friday", "."],
     ["B-ORG", "I-ORG", "O", "O", "O", "B-TIME", "O"]),
    (["The", "Denver", "flight", "costs", "$6", "."],
     ["O", "B-LOC", "O", "O", "B-MONEY", "O"]),
    (["Apple", "opened", "a", "store", "in", "Palo", "Alto", "."],
     ["B-ORG", "O", "O", "O", "O", "B-GPE", "I-GPE", "O"]),
]

PIECES = {
    "Sanitas": ["San", "##itas"],
    "Villanueva": ["Villan", "##ueva"],
    "Sunshine": ["Sun", "##shine"],
    "Airlines": ["Air", "##lines"],
    "Holding": ["Hold", "##ing"],
    "Denver": ["Den", "##ver"],
    "Palo": ["Pa", "##lo"],
}


def tokenize_word(w):
    if w in PIECES:
        return PIECES[w]
    if len(w) > 8:
        return [w[:4], "##" + w[4:]]
    return [w]


def build_tokens(words):
    tokens, owner = [], []
    for wi, w in enumerate(words):
        ps = tokenize_word(w)
        tokens.extend(ps)
        owner.extend([wi] * len(ps))
    return tokens, owner


def align_labels(words, word_labels):
    tokens, owner = build_tokens(words)
    sub_labels = [word_labels[o] for o in owner]
    return tokens, owner, sub_labels


def decode_first_subtoken(tokens, owner, sub_labels, n_words):
    """解码：用每个词第一个子词的标签作为该词的标签。"""
    out = [None] * n_words
    seen = set()
    for t, o, lab in zip(tokens, owner, sub_labels):
        if o not in seen:
            out[o] = lab
            seen.add(o)
    return out


def bio_to_spans(labels, words):
    spans, start, cur = [], None, None
    for i, lab in enumerate(labels):
        if lab.startswith("B-"):
            if start is not None:
                spans.append((start, i - 1, cur))
            start, cur = i, lab[2:]
        elif lab.startswith("I-"):
            if start is None or cur != lab[2:]:
                if start is not None:
                    spans.append((start, i - 1, cur))
                start, cur = i, lab[2:]
        else:
            if start is not None:
                spans.append((start, i - 1, cur))
                start, cur = None, None
    if start is not None:
        spans.append((start, len(labels) - 1, cur))
    return set(spans)


def entity_scores(gold_spans, pred_spans):
    tp = len(gold_spans & pred_spans)
    fp = len(pred_spans - gold_spans)
    fn = len(gold_spans - pred_spans)
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return tp, fp, fn, p, r, f


def word_accuracy(gold, pred):
    return float(np.mean([g == p for g, p in zip(gold, pred)]))


# ---------- 1. 对照表：词级标签 -> 子词标签 ----------
align_rows = []
for words, labels in DATA:
    tokens, owner, sub = align_labels(words, labels)
    align_rows.append({
        "words": " ".join(words),
        "tokens": " ".join(tokens),
        "word_bio": " ".join(labels),
        "subtokens_bio": " ".join(sub),
    })
with open(os.path.join(OUT, "alignment.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(align_rows[0]))
    w.writeheader(); w.writerows(align_rows)

# ---------- 2. 往返一致性 ----------
roundtrip_ok, roundtrip_total = 0, 0
for words, labels in DATA:
    tokens, owner, sub = align_labels(words, labels)
    dec = decode_first_subtoken(tokens, owner, sub, len(words))
    roundtrip_ok += sum(a == b for a, b in zip(dec, labels))
    roundtrip_total += len(labels)
print(f"词级→子词→词级往返一致率: {roundtrip_ok}/{roundtrip_total} = {roundtrip_ok / roundtrip_total:.3f}")

# ---------- 3. 四种预测变体 ----------
def variant_gold(words, labels):
    return list(labels)


def variant_boundary(words, labels):
    """Jane 而非 Jane Villanueva：把第二个词的标签改成 O。"""
    out = list(labels)
    for i, w in enumerate(words):
        if w == "Villanueva":
            out[i] = "O"
    return out


def variant_type(words, labels):
    """把 United Airlines Holding 的类型从 ORG 改成 LOC。"""
    out = list(labels)
    for i, w in enumerate(words):
        if w in ("United", "Airlines", "Holding"):
            out[i] = out[i].replace("ORG", "LOC")
    return out


def variant_noise(labels, rate=0.15):
    out = list(labels)
    tagset = ["O", "B-PER", "I-PER", "B-LOC", "I-LOC", "B-ORG", "I-ORG", "B-TIME"]
    for i in range(len(out)):
        if rng.random() < rate:
            out[i] = tagset[rng.integers(len(tagset))]
    return out


variants = {}
for name, fn in [("gold", variant_gold),
                 ("boundary(Jane)", lambda w, l: variant_boundary(w, l)),
                 ("type(ORG→LOC)", lambda w, l: variant_type(w, l)),
                 ("noise15%", lambda w, l: variant_noise(l))]:
    per_sentence = []
    for words, labels in DATA:
        pred_words = fn(words, labels)
        tokens, owner, _ = align_labels(words, labels)
        # 把词级预测复制到子词，模拟「子词分类器输出」
        sub_pred = [pred_words[o] for o in owner]
        dec = decode_first_subtoken(tokens, owner, sub_pred, len(words))
        gs = bio_to_spans(labels, words)
        ps = bio_to_spans(dec, words)
        per_sentence.append((words, labels, dec, gs, ps))
    tp = sum(entity_scores(gs, ps)[0] for _, _, _, gs, ps in per_sentence)
    fp = sum(entity_scores(gs, ps)[1] for _, _, _, gs, ps in per_sentence)
    fn_ = sum(entity_scores(gs, ps)[2] for _, _, _, gs, ps in per_sentence)
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn_) if tp + fn_ else 0.0
    f1 = 2 * p * r / (p + r) if p + r else 0.0
    acc = float(np.mean([word_accuracy(l, d) for _, l, d, _, _ in per_sentence]))
    variants[name] = {"acc": acc, "p": p, "r": r, "f1": f1, "tp": tp, "fp": fp, "fn": fn_}

print("\n变体          词级准确率  entity-P  entity-R  entity-F1  (TP/FP/FN)")
for k, v in variants.items():
    print(f"{k:14s} {v['acc']:.3f}      {v['p']:.3f}     {v['r']:.3f}     {v['f1']:.3f}   ({v['tp']}/{v['fp']}/{v['fn']})")

# ---------- 4. 自助法：句子级重采样 ----------
def corpus_f1(rows_idx):
    tp = fp = fn_ = 0
    for i in rows_idx:
        _, _, _, gs, ps = noisy_rows[i]
        a, b, c, _, _, _ = entity_scores(gs, ps)
        tp += a; fp += b; fn_ += c
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn_) if tp + fn_ else 0.0
    return 2 * p * r / (p + r) if p + r else 0.0


noisy_rows = []
for words, labels in DATA:
    pred_words = variant_noise(labels)
    tokens, owner, _ = align_labels(words, labels)
    sub_pred = [pred_words[o] for o in owner]
    dec = decode_first_subtoken(tokens, owner, sub_pred, len(words))
    noisy_rows.append((words, labels, dec, bio_to_spans(labels, words), bio_to_spans(dec, words)))

boot = []
n = len(noisy_rows)
for _ in range(2000):
    idx = rng.integers(0, n, size=n)
    boot.append(corpus_f1(idx))
lo, hi = np.percentile(boot, [2.5, 97.5])
print(f"\nnoise15% 实体级 F1 = {variants['noise15%']['f1']:.3f}，句子级自助 95% 区间 [{lo:.3f}, {hi:.3f}]（{n} 句）")

with open(os.path.join(OUT, "metrics.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["variant", "word_acc", "precision", "recall", "f1", "tp", "fp", "fn"])
    for k, v in variants.items():
        w.writerow([k, v["acc"], v["p"], v["r"], v["f1"], v["tp"], v["fp"], v["fn"]])
with open(os.path.join(OUT, "bootstrap.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["metric", "point", "ci_low", "ci_high", "n_sentences", "n_resamples"])
    w.writerow(["entity_f1_noise15", variants["noise15%"]["f1"], lo, hi, n, 2000])

errors = []
for words, labels, dec, gs, ps in noisy_rows:
    for span in sorted(ps - gs):
        errors.append({"sentence": " ".join(words), "error": "FP",
                       "span": " ".join(words[span[0]:span[1] + 1]) + f" [{span[2]}]"})
    for span in sorted(gs - ps):
        errors.append({"sentence": " ".join(words), "error": "FN",
                       "span": " ".join(words[span[0]:span[1] + 1]) + f" [{span[2]}]"})
with open(os.path.join(OUT, "errors.json"), "w", encoding="utf-8") as f:
    json.dump(errors[:20], f, ensure_ascii=False, indent=2)

fig, ax = plt.subplots(figsize=(7.2, 4))
names = list(variants)
accs = [variants[k]["acc"] for k in names]
f1s = [variants[k]["f1"] for k in names]
x = np.arange(len(names)); wd = 0.36
ax.bar(x - wd / 2, accs, wd, label="词级准确率")
ax.bar(x + wd / 2, f1s, wd, label="实体级 F1")
ax.set_xticks(x); ax.set_xticklabels(names, fontsize=9)
ax.set_ylim(0, 1.05); ax.set_ylabel("分数")
ax.set_title("词级指标掩盖了实体级错误")
ax.legend()
fig.tight_layout()
fig.savefig(os.path.join(OUT, "word_vs_entity.png"), dpi=150)
print("产物已写入", OUT)
