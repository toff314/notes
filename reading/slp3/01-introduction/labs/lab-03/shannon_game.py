#!/usr/bin/env python3
"""Lab 03: 复现香农游戏（字母级），统计"哪里更难猜"。

猜词者是一个字母三元模型（context = 前两个字符，含空格），每次只猜一个字母，
猜错就被告知正确字母（与 §1.2.2 的规则一致）。目标文本取自 §1.2.2 的英文样例，
训练语料中剔除该样例，避免泄漏。

输出：out/corrections.csv、out/rates.csv、out/summary.json、out/rates.png
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

DEFAULT_SOURCE = Path("/home/yuanwu/books/slp3/zh/md/01-introduction.dual.md")
TARGET = (
    "the room was not very light a small oblong reading lamp on the desk "
    "shed glow on polished wood but less on the shabby red carpet"
)
ALPHABET = "abcdefghijklmnopqrstuvwxyz "
LEAK_MARKERS = ("the room was not very light", "shabby red carpet")
FUNCTION_WORDS = {
    "a", "an", "the", "and", "or", "but", "if", "of", "to", "in", "on", "at",
    "for", "with", "by", "from", "as", "is", "was", "were", "are", "be", "been",
    "it", "this", "that", "these", "those", "not", "very", "so", "than", "then",
    "he", "she", "they", "we", "you", "i", "his", "her", "their", "our", "its",
}


def load_chars(path: Path) -> str:
    lines: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.startswith("> "):
            continue
        text = raw[2:].strip()
        if not text or "释义" in text or text.startswith("`"):
            continue
        letters = sum(ch.isascii() and ch.isalpha() for ch in text)
        if len(text) > 15 and letters / len(text) > 0.55:
            lines.append(text)
    lines = [ln for ln in lines if not any(m in ln.lower() for m in LEAK_MARKERS)]
    text = re.sub(r"[^a-z ]+", " ", " ".join(lines).lower())
    return re.sub(r"\s+", " ", text).strip()


def context_of(prefix: str) -> str:
    return (prefix[-2:] if len(prefix) >= 2 else " " * (2 - len(prefix)) + prefix)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    ap.add_argument("--out", type=Path, default=Path(__file__).parent / "out")
    args = ap.parse_args()

    train = " " + load_chars(args.source) + " "
    trigram: dict[str, Counter] = defaultdict(Counter)
    for i in range(2, len(train)):
        trigram[train[i - 2:i]][train[i]] += 1
    args.out.mkdir(parents=True, exist_ok=True)

    words = TARGET.split()
    word_of = {}
    pos_of = {}
    for wi, w in enumerate(words):
        for pi, _ in enumerate(w):
            word_of[len(" ".join(words[:wi])) + pi] = (w, wi, pi)

    rows = []
    prefix = ""
    for idx, ch in enumerate(TARGET):
        ctx = context_of(prefix)
        counts = trigram.get(ctx, Counter())
        total = sum(counts.values())
        # 加一平滑，保证每个字母都有非零概率
        best = max(ALPHABET, key=lambda c: counts.get(c, 0) + 1)
        best_p = (counts.get(best, 0) + 1) / (total + len(ALPHABET))
        correct_p = (counts.get(ch, 0) + 1) / (total + len(ALPHABET))
        word, _, pos = word_of.get(idx, ("", 0, 0))
        if ch == " ":
            bucket, cls = "space", "boundary"
        else:
            bucket = "first" if pos == 0 else ("second" if pos == 1 else "later")
            cls = "function" if word in FUNCTION_WORDS else "content"
        rows.append(
            {
                "index": idx,
                "char": ch,
                "context": ctx,
                "guess": best,
                "correct": int(best == ch),
                "guess_prob": round(best_p, 6),
                "true_prob": round(correct_p, 6),
                "surprisal_bits": round(-math.log2(correct_p), 4),
                "word": word,
                "position": pos,
                "position_bucket": bucket,
                "word_class": cls,
            }
        )
        prefix += ch

    with (args.out / "corrections.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    agg = defaultdict(lambda: {"n": 0, "errors": 0, "surprisal": 0.0})
    for r in rows:
        for key in (f"pos:{r['position_bucket']}", f"class:{r['word_class']}"):
            a = agg[key]
            a["n"] += 1
            a["errors"] += 1 - r["correct"]
            a["surprisal"] += r["surprisal_bits"]

    with (args.out / "rates.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["bucket", "n_chars", "corrections", "correction_rate", "mean_surprisal_bits"])
        for key in sorted(agg):
            a = agg[key]
            w.writerow([key, a["n"], a["errors"], f"{a['errors'] / a['n']:.4f}",
                        f"{a['surprisal'] / a['n']:.4f}"])

    summary = {
        "target": TARGET,
        "train_chars": len(train),
        "chars": len(TARGET),
        "overall_correction_rate": round(sum(1 - r["correct"] for r in rows) / len(rows), 4),
        "buckets": {
            key: {
                "n": a["n"],
                "correction_rate": round(a["errors"] / a["n"], 4),
                "mean_surprisal_bits": round(a["surprisal"] / a["n"], 4),
            }
            for key, a in sorted(agg.items())
        },
    }
    (args.out / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    plt.rcParams["font.sans-serif"] = ["Noto Sans CJK JP", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for ax, prefix_key, title in zip(
        axes,
        ["pos:", "class:"],
        ["按词内位置：首字母 vs 后续字母", "按词类：功能词 vs 实词"],
    ):
        if prefix_key == "pos:":
            keys = ["pos:first", "pos:second", "pos:later"]
            labels = ["首字母", "第二字母", "后续字母"]
        else:
            keys = ["class:function", "class:content"]
            labels = ["功能词", "实词"]
        values = [agg[k]["errors"] / agg[k]["n"] for k in keys]
        bars = ax.bar(labels, values, color="#2c7fb8")
        for b, k in zip(bars, keys):
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.01,
                    f"{values[keys.index(k)]:.2f}\nn={agg[k]['n']}", ha="center", fontsize=8)
        ax.set_ylim(0, 1)
        ax.set_ylabel("纠正率（猜错比例）")
        ax.set_title(title)
    fig.suptitle("字母三元模型玩香农游戏：哪些位置更需要被纠正")
    fig.tight_layout()
    fig.savefig(args.out / "rates.png", dpi=160)

    print(f"train chars={len(train)} target chars={len(TARGET)}")
    print(f"overall correction rate={summary['overall_correction_rate']}")
    for key, a in summary["buckets"].items():
        print(f"  {key}: n={a['n']} rate={a['correction_rate']} bits={a['mean_surprisal_bits']}")


if __name__ == "__main__":
    main()
