#!/usr/bin/env python3
"""Lab-02：嵌入 + MLP 文本分类，对比随机嵌入与共现（PPMI+SVD）嵌入。

对应《Speech and Language Processing》第 6 章 §6.4–§6.5。
数据为按模板构造的小型情感语料（英文词、空格分词），构造方式在 README 说明。
关键设计：训练句只使用 12 个情感词，测试句使用 8 个**训练中从未出现**的情感词；
这些词在无标注语料里出现过，因此共现嵌入能利用分布相似性，随机嵌入不能。

输出：
  out/metrics.json           两种嵌入的准确率、混淆矩阵、超参数
  out/predictions.csv        逐句预测
  out/confusion_matrix.csv   两种嵌入的混淆矩阵
  out/accuracy.png           准确率对比 + 混淆矩阵
  out/embedding_pca.png      共现嵌入的 PCA 投影
"""
import json
import os

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

SEED = 11
DIM = 16
WINDOW = 3
EPOCHS = 400
LR = 0.15
HIDDEN = 24
L2 = 1e-4

POS_TRAIN = ["good", "great", "excellent", "delightful", "superb", "brilliant"]
NEG_TRAIN = ["bad", "terrible", "awful", "boring", "dull", "annoying"]
POS_HELD = ["charming", "enjoyable", "lovely", "impressive"]
NEG_HELD = ["clumsy", "dismal", "tedious", "painful"]
NEUTRAL = ["long", "short", "old", "new", "quiet", "loud", "simple", "strange"]
OBJECTS = ["movie", "film", "book", "story", "play", "show", "acting", "plot",
           "ending", "music", "script", "scene", "cast", "direction"]

TEMPLATES = [
    "the {o} was {s}",
    "i found the {o} {s}",
    "the {o} is {s}",
    "we thought the {o} was {s}",
    "this {o} was really {s}",
    "the {o} felt {s} to me",
    "the {o} was very {s}",
    "i thought the {o} was {s}",
    "the {o} seemed {s}",
    "overall the {o} was {s}",
    "the {o} and the {o2} were {s}",
    "the {o} was {s} and the {o2} was {s2}",
]


def make_sentence(rng, words, neutral=False):
    t = TEMPLATES[rng.integers(len(TEMPLATES))]
    o = OBJECTS[rng.integers(len(OBJECTS))]
    o2 = OBJECTS[rng.integers(len(OBJECTS))]
    w = words[rng.integers(len(words))]
    if neutral:
        w = NEUTRAL[rng.integers(len(NEUTRAL))]
    w2 = words[rng.integers(len(words))]
    return t.format(o=o, o2=o2, s=w, s2=w2)


def build_dataset():
    rng = np.random.default_rng(SEED)
    train, test = [], []
    for _ in range(240):
        label = int(rng.integers(2))
        words = POS_TRAIN if label == 0 else NEG_TRAIN
        train.append((make_sentence(rng, words), label))
    for _ in range(200):
        label = int(rng.integers(2))
        words = POS_HELD if label == 0 else NEG_HELD
        test.append((make_sentence(rng, words), label))
    return train, test


POS_CONTEXT = ["i love this {s} {o}", "we recommend this {s} {o}", "the {s} {o} was a joy",
               "the audience cheered for this {s} {o}", "what a wonderful {s} {o}"]
NEG_CONTEXT = ["i hate this {s} {o}", "we avoid this {s} {o}", "the {s} {o} was a waste",
               "the audience groaned at this {s} {o}", "what a painful {s} {o}"]


def build_corpus(rng):
    """无标注语料：覆盖全部情感词（含 held-out），用于构造共现嵌入。

    情感词只在极性子句中出现（正面词配 love/recommend，负面词配 hate/avoid），
    这样共现统计才携带极性；下游分类句则只用中性模板。
    """
    corpus = []
    for _ in range(900):
        label = int(rng.integers(2))
        words = (POS_TRAIN + POS_HELD) if label == 0 else (NEG_TRAIN + NEG_HELD)
        w = words[rng.integers(len(words))]
        o = OBJECTS[rng.integers(len(OBJECTS))]
        o2 = OBJECTS[rng.integers(len(OBJECTS))]
        if rng.random() < 0.15:
            corpus.append(make_sentence(rng, NEUTRAL, neutral=True))
            continue
        t = (POS_CONTEXT if label == 0 else NEG_CONTEXT)[rng.integers(5)]
        corpus.append(t.format(s=w, o=o, o2=o2))
    return corpus


def tokenize(s):
    return s.split()


def build_ppmi_embeddings(corpus, dim, window):
    vocab = sorted({t for s in corpus for t in tokenize(s)})
    idx = {w: i for i, w in enumerate(vocab)}
    v = len(vocab)
    counts = np.zeros((v, v), dtype=np.float64)
    for s in corpus:
        toks = tokenize(s)
        ids = [idx[t] for t in toks]
        for i, wi in enumerate(ids):
            lo, hi = max(0, i - window), min(len(ids), i + window + 1)
            for j in range(lo, hi):
                if j != i:
                    counts[wi, ids[j]] += 1.0
    total = counts.sum()
    row = counts.sum(axis=1, keepdims=True)
    col = counts.sum(axis=0, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        pmi = np.log((counts * total) / (row * col))
    ppmi = np.where(np.isfinite(pmi), np.maximum(pmi, 0.0), 0.0)
    u, s, _ = np.linalg.svd(ppmi, full_matrices=False)
    emb = u[:, :dim] * np.sqrt(s[:dim])
    norms = np.linalg.norm(emb, axis=1, keepdims=True)
    emb = emb / np.maximum(norms, 1e-12)
    return vocab, idx, emb


def random_embeddings(vocab, dim, seed):
    rng = np.random.default_rng(seed)
    emb = rng.normal(0.0, 1.0 / np.sqrt(dim), size=(len(vocab), dim))
    return emb


def encode(sentences, vocab, idx, emb):
    rows = []
    for s in sentences:
        ids = [idx[t] for t in tokenize(s) if t in idx]
        rows.append(emb[ids].mean(axis=0))
    return np.vstack(rows)


def softmax(z):
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def train_classifier(x, y, hidden, epochs, lr, l2, seed):
    n, d = x.shape
    rng = np.random.default_rng(seed)
    w1 = rng.normal(0.0, np.sqrt(2.0 / d), size=(d, hidden))
    b1 = np.zeros((1, hidden))
    w2 = rng.normal(0.0, np.sqrt(2.0 / hidden), size=(hidden, 2))
    b2 = np.zeros((1, 2))
    y1h = np.eye(2)[y]
    losses = []
    for _ in range(epochs):
        a1 = np.tanh(x @ w1 + b1)
        probs = softmax(a1 @ w2 + b2)
        loss = float(-np.mean(np.log(probs[np.arange(n), y] + 1e-12)))
        losses.append(loss)
        dz = (probs - y1h) / n
        dw2 = a1.T @ dz + l2 * w2
        db2 = dz.sum(axis=0, keepdims=True)
        da1 = dz @ w2.T
        dz1 = da1 * (1.0 - a1 ** 2)
        dw1 = x.T @ dz1 + l2 * w1
        db1 = dz1.sum(axis=0, keepdims=True)
        w1 -= lr * dw1
        b1 -= lr * db1
        w2 -= lr * dw2
        b2 -= lr * db2
    return {"w1": w1, "b1": b1, "w2": w2, "b2": b2}, losses


def predict(params, x):
    a1 = np.tanh(x @ params["w1"] + params["b1"])
    probs = softmax(a1 @ params["w2"] + params["b2"])
    return probs.argmax(axis=1), probs


def confusion(y, pred):
    cm = np.zeros((2, 2), dtype=int)
    for t, p in zip(y, pred):
        cm[t, p] += 1
    return cm


def pca_2d(emb):
    centered = emb - emb.mean(axis=0, keepdims=True)
    _, _, vh = np.linalg.svd(centered, full_matrices=False)
    return centered @ vh[:2].T


def main():
    train, test = build_dataset()
    rng = np.random.default_rng(SEED + 1)
    corpus = build_corpus(rng)

    vocab, idx, emb_ppmi = build_ppmi_embeddings(corpus, DIM, WINDOW)
    emb_rand = random_embeddings(vocab, DIM, SEED)

    x_train_text = [s for s, _ in train]
    y_train = np.array([y for _, y in train])
    x_test_text = [s for s, _ in test]
    y_test = np.array([y for _, y in test])

    results = {}
    all_pred_rows = []
    cms = {}
    for name, emb in (("random", emb_rand), ("ppmi_svd", emb_ppmi)):
        x_tr = encode(x_train_text, vocab, idx, emb)
        x_te = encode(x_test_text, vocab, idx, emb)
        params, losses = train_classifier(x_tr, y_train, HIDDEN, EPOCHS, LR, L2, SEED + 2)
        pred, probs = predict(params, x_te)
        acc = float((pred == y_test).mean())
        cm = confusion(y_test, pred)
        cms[name] = cm
        results[name] = {
            "accuracy": acc,
            "final_train_loss": losses[-1],
            "confusion_matrix": cm.tolist(),
            "params": int(sum(v.size for v in params.values())),
        }
        for s, t, p, pr in zip(x_test_text, y_test, pred, probs):
            all_pred_rows.append({
                "embedding": name,
                "sentence": s,
                "target": int(t),
                "prediction": int(p),
                "p_positive": round(float(pr[0]), 6),
            })

    # 最近邻检查：held-out 情感词在共现空间里靠近谁
    def neighbors(word, k=5):
        if word not in idx:
            return []
        v = emb_ppmi[idx[word]]
        sims = emb_ppmi @ v
        order = np.argsort(-sims)
        return [vocab[i] for i in order if vocab[i] != word][:k]

    nn = {w: neighbors(w) for w in POS_HELD[:2] + NEG_HELD[:2]}

    metrics = {
        "seed": SEED,
        "dim": DIM,
        "window": WINDOW,
        "epochs": EPOCHS,
        "learning_rate": LR,
        "hidden": HIDDEN,
        "vocab_size": len(vocab),
        "train_sentences": len(train),
        "test_sentences": len(test),
        "train_sentiment_words": {"positive": POS_TRAIN, "negative": NEG_TRAIN},
        "heldout_sentiment_words": {"positive": POS_HELD, "negative": NEG_HELD},
        "results": results,
        "heldout_neighbors_ppmi": nn,
        "note": "embeddings frozen; identical classifier init/seed for both conditions",
    }
    with open(os.path.join(OUT, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    with open(os.path.join(OUT, "confusion_matrix.csv"), "w", encoding="utf-8") as f:
        f.write("embedding,true_label,pred_negative,pred_positive\n")
        for name, cm in cms.items():
            for t in range(2):
                f.write(f"{name},{t},{cm[t, 0]},{cm[t, 1]}\n")

    with open(os.path.join(OUT, "predictions.csv"), "w", encoding="utf-8") as f:
        f.write("embedding,sentence,target,prediction,p_positive\n")
        for r in all_pred_rows:
            f.write(f"{r['embedding']},\"{r['sentence']}\",{r['target']},{r['prediction']},{r['p_positive']}\n")

    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.0))
    names = ["random", "ppmi_svd"]
    accs = [results[n]["accuracy"] for n in names]
    axes[0].bar(["random", "PPMI+SVD"], accs, color=["#7f8c8d", "#1f6f8b"])
    axes[0].axhline(0.5, color="#c0392b", linestyle="--", linewidth=1, label="chance")
    axes[0].set_ylim(0, 1.05)
    axes[0].set_ylabel("held-out accuracy")
    axes[0].legend(fontsize=8, loc="upper right")
    axes[0].set_title("Held-out sentiment words")
    for i, a in enumerate(accs):
        axes[0].text(i, a + 0.02, f"{a:.3f}", ha="center", fontsize=10)
    for ax, name in zip(axes[1:], names):
        cm = cms[name]
        im = ax.imshow(cm, cmap="Blues")
        ax.set_xticks([0, 1], ["neg", "pos"])
        ax.set_yticks([0, 1], ["neg", "pos"])
        ax.set_xlabel("predicted")
        ax.set_ylabel("true")
        ax.set_title(f"confusion: {name}")
        for i in range(2):
            for j in range(2):
                ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                        color="white" if cm[i, j] > cm.max() / 2 else "black")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "accuracy.png"), dpi=160)
    plt.close(fig)

    coords = pca_2d(emb_ppmi)
    fig, ax = plt.subplots(figsize=(6.4, 5.4))
    groups = [
        ("train positive", POS_TRAIN, "#c0392b"),
        ("train negative", NEG_TRAIN, "#2c3e50"),
        ("held-out positive", POS_HELD, "#e67e22"),
        ("held-out negative", NEG_HELD, "#16a085"),
        ("other", [w for w in vocab if w not in POS_TRAIN + NEG_TRAIN + POS_HELD + NEG_HELD], "#bdc3c7"),
    ]
    for label, words, color in groups:
        pts = [coords[idx[w]] for w in words if w in idx]
        if not pts:
            continue
        pts = np.array(pts)
        ax.scatter(pts[:, 0], pts[:, 1], s=70 if label != "other" else 28, c=color, label=label,
                   edgecolors="w", linewidths=0.6, alpha=0.9)
    for w in POS_HELD + NEG_HELD:
        if w in idx:
            p = coords[idx[w]]
            ax.annotate(w, p, fontsize=7, xytext=(4, 3), textcoords="offset points")
    ax.set_title("PPMI+SVD embeddings (PCA, 2D)")
    ax.legend(fontsize=8, loc="best")
    ax.set_xticks([])
    ax.set_yticks([])
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "embedding_pca.png"), dpi=160)
    plt.close(fig)

    print(json.dumps({
        "accuracy": {n: results[n]["accuracy"] for n in names},
        "confusion": {n: cms[n].tolist() for n in names},
        "vocab_size": len(vocab),
        "neighbors": nn,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
