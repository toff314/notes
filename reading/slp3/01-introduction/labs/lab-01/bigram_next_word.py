#!/usr/bin/env python3
"""Lab 01: 用本章英文原文训练 bigram，复现"给定前缀猜下一个词"。

数据源：SLP3 第 1 章双语对照文件中的英文段落（blockquote 行）。
为避免测试句泄漏，训练前剔除包含 "so long and thanks" 的句子。
输出：out/next_word.csv、out/summary.json、out/next_word.png
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

DEFAULT_SOURCE = Path("/home/yuanwu/books/slp3/zh/md/01-introduction.dual.md")
HOLDOUT = "so long and thanks"
PREFIXES = ["so long and thanks for", "the language", "in the"]


def load_english_lines(path: Path) -> list[str]:
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
    return lines


def normalize(lines: list[str]) -> list[str]:
    text = " ".join(lines).lower()
    text = re.sub(r"[^a-z' ]+", " ", text)
    return text.split()


def build_counts(tokens: list[str]):
    unigram = Counter(tokens)
    bigram = Counter(zip(tokens, tokens[1:]))
    return unigram, bigram


def rank_next_words(prefix: str, unigram, bigram, total: int, vocab: list[str]):
    """返回 [(rank, word, count_bigram, p_bigram, p_unigram_backoff, source)]。"""
    prev = prefix.split()[-1]
    rows = []
    for word in vocab:
        c_next = bigram.get((prev, word), 0)
        c_prev = unigram.get(prev, 0)
        p_bigram = (c_next / c_prev) if c_prev else None
        p_backoff = (unigram.get(word, 0) + 1) / (total + len(vocab))
        rows.append((word, c_next, p_bigram, p_backoff))
    rows.sort(key=lambda r: (-(r[2] or 0.0), -r[3], r[0]))

    out = []
    for i, (word, c_next, p_bigram, p_backoff) in enumerate(rows, 1):
        source = "bigram" if p_bigram else "unigram-backoff"
        out.append((i, word, c_next, p_bigram, p_backoff, source))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    ap.add_argument("--out", type=Path, default=Path(__file__).parent / "out")
    args = ap.parse_args()

    lines = load_english_lines(args.source)
    kept = [ln for ln in lines if HOLDOUT not in ln.lower()]
    tokens = normalize(kept)
    unigram, bigram = build_counts(tokens)
    vocab = sorted(unigram)
    total = len(tokens)
    args.out.mkdir(parents=True, exist_ok=True)

    csv_path = args.out / "next_word.csv"
    summary = {
        "source": str(args.source),
        "english_lines": len(lines),
        "lines_after_holdout": len(kept),
        "train_tokens": total,
        "vocab_size": len(vocab),
        "holdout_rule": f"剔除包含 {HOLDOUT!r} 的句子",
        "queries": {},
    }
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["prefix", "rank", "word", "bigram_count", "p_bigram", "p_unigram_backoff", "source"]
        )
        for prefix in PREFIXES:
            prev = prefix.split()[-1]
            seen = sum(bigram.get((prev, w), 0) for w in vocab)
            summary["queries"][prefix] = {
                "conditioning": "只使用最后一个词（bigram 的马尔可夫假设）",
                "prev": prev,
                "prev_count": unigram.get(prev, 0),
                "next_token_occurrences": seen,
                "book_expectation": ["all", "the"] if prefix.startswith("so long") else [],
            }
            rows = rank_next_words(prefix, unigram, bigram, total, vocab)
            for rank, word, c_next, p_bigram, p_backoff, source in rows[:12]:
                writer.writerow(
                    [
                        prefix,
                        rank,
                        word,
                        c_next,
                        "" if p_bigram is None else f"{p_bigram:.6f}",
                        f"{p_backoff:.6f}",
                        source,
                    ]
                )

    (args.out / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    plt.rcParams["font.sans-serif"] = ["Noto Sans CJK JP", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    for ax, prefix, title in zip(
        axes,
        ["so long and thanks for", "the language"],
        ["1.3 万词语料：for→example 居首（书中 all 未入前 12）", "语料内有观测：the language→models"],
    ):
        rows = rank_next_words(prefix, unigram, bigram, total, vocab)[:8]
        labels = [r[1] for r in rows]
        values = [(r[3] if r[3] else r[4]) for r in rows]
        colors = ["#c0392b" if r[5] == "unigram-backoff" else "#2c7fb8" for r in rows]
        ax.barh(labels[::-1], values[::-1], color=colors[::-1])
        ax.set_title(f'前缀："...{prefix.split()[-1]}"')
        ax.set_xlabel("P(next | prev)")
        ax.text(0.02, 0.02, title, transform=ax.transAxes, fontsize=8, color="#555")
    fig.suptitle("Bigram 下一个词概率（只条件于最后一个词）")
    fig.tight_layout()
    fig.savefig(args.out / "next_word.png", dpi=160)
    print(f"tokens={total} vocab={len(vocab)} lines={len(lines)}")
    for prefix in PREFIXES:
        top = rank_next_words(prefix, unigram, bigram, total, vocab)[:5]
        print(prefix, "->", [(w, round(p or 0, 4), src) for _, w, _, p, _, src in top])
    print("wrote", csv_path)


if __name__ == "__main__":
    main()
