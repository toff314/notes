#!/usr/bin/env python3
"""Lab 01: 从零实现 BPE（训练 + 编码 + 压缩率统计）。

对应 actions.md 行动 1、2；对应《Speech and Language Processing》§2.4。
只依赖标准库 + numpy + matplotlib。
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
OUT.mkdir(parents=True, exist_ok=True)

CORPUS = """low lower lowest new newer newest wide wider widest
the tokenizer tokenizes tokenization tokens tokenizing
自然语言处理研究词、词元与子词。
字节对编码从单个字符出发，反复合并最频繁的相邻词元。
正则表达式用于预词元化，编辑距离用于比较字符串。
语料库包含不同语言、体裁与说话人。
词类型与词例是两种计数方式。
使用 Unicode 码点表示字符，再用 UTF-8 编码写入文件。
最小编辑距离用动态规划计算，并回溯得到对齐。
合并只发生在词内部，不跨越空白与标点。
词元化处理文本，词元化生成词元。
词元化是自然语言处理的第一步。
"""

TEST_SENTENCES = [
    "lowest newer tokenization",
    "词元化是自然语言处理的第一步",
    "unseen word: tokenizer",
]

# 预词元化：英文按连续字母、数字成块，汉字逐字，标点单独成块。
PRETOKEN = re.compile(r"[A-Za-z]+|[0-9]+|[\u4e00-\u9fff]|[^\sA-Za-z0-9\u4e00-\u9fff]")


def pretokenize(text: str) -> list[str]:
    return PRETOKEN.findall(text)


def build_counts(lines: list[str]) -> Counter[tuple[str, ...]]:
    counts: Counter[tuple[str, ...]] = Counter()
    for line in lines:
        for piece in pretokenize(line):
            counts[tuple(piece)] += 1
    return counts


def count_pairs(words: Counter[tuple[str, ...]]) -> Counter[tuple[str, str]]:
    pairs: Counter[tuple[str, str]] = Counter()
    for symbols, freq in words.items():
        for left, right in zip(symbols, symbols[1:]):
            pairs[(left, right)] += freq
    return pairs


def merge_word(symbols: tuple[str, ...], pair: tuple[str, str]) -> tuple[str, ...]:
    merged: list[str] = []
    i = 0
    while i < len(symbols):
        if i + 1 < len(symbols) and (symbols[i], symbols[i + 1]) == pair:
            merged.append(pair[0] + pair[1])
            i += 2
        else:
            merged.append(symbols[i])
            i += 1
    return tuple(merged)


def train_bpe(lines: list[str], num_merges: int) -> tuple[list[tuple[str, str]], Counter[tuple[str, ...]], list[dict]]:
    words = build_counts(lines)
    merges: list[tuple[str, str]] = []
    history: list[dict] = []
    total_chars = sum(len("".join(w)) * f for w, f in words.items())
    for step in range(1, num_merges + 1):
        pairs = count_pairs(words)
        if not pairs:
            break
        pair, freq = max(pairs.items(), key=lambda kv: (kv[1], kv[0]))
        merged_words: Counter[tuple[str, ...]] = Counter()
        for w, f in words.items():
            merged_words[merge_word(w, pair)] += f
        words = merged_words
        merges.append(pair)
        total_tokens = sum(len(w) * f for w, f in words.items())
        history.append(
            {
                "step": step,
                "merge": pair[0] + "+" + pair[1],
                "pair_freq": freq,
                "vocab_size": len({s for w in words for s in w}),
                "total_tokens": total_tokens,
                "chars_per_token": round(total_chars / total_tokens, 4),
            }
        )
    return merges, words, history


def encode(piece: str, merges: list[tuple[str, str]]) -> list[str]:
    symbols = list(piece)
    for pair in merges:
        symbols = list(merge_word(tuple(symbols), pair))
    return symbols


def main() -> None:
    lines = [ln for ln in CORPUS.splitlines() if ln.strip()]
    merges, trained_words, history = train_bpe(lines, num_merges=40)

    with (OUT / "merge_history.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(history[0]))
        writer.writeheader()
        writer.writerows(history)

    with (OUT / "vocab.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["rank", "token", "source"])
        alphabet = sorted({ch for line in lines for ch in line if not ch.isspace()})
        for i, ch in enumerate(alphabet, 1):
            writer.writerow([i, ch, "char"])
        for i, (a, b) in enumerate(merges, len(alphabet) + 1):
            writer.writerow([i, a + b, "merge"])

    rows = []
    total_chars = 0
    total_tokens = 0
    for word, freq in sorted(trained_words.items(), key=lambda kv: (-kv[1], kv[0])):
        text = "".join(word)
        pieces = encode(text, merges)
        total_chars += len(text) * freq
        total_tokens += len(pieces) * freq
        rows.append(
            {
                "word": text,
                "freq": freq,
                "n_tokens": len(pieces),
                "tokens": " | ".join(pieces),
            }
        )
    with (OUT / "segments.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["word", "freq", "n_tokens", "tokens"])
        writer.writeheader()
        writer.writerows(rows)

    test_rows = []
    for sent in TEST_SENTENCES:
        pieces = []
        for p in pretokenize(sent):
            pieces.extend(encode(p, merges))
        test_rows.append(
            {
                "sentence": sent,
                "chars": len(sent.replace(" ", "")),
                "tokens": len(pieces),
                "segmentation": " | ".join(pieces),
            }
        )
    with (OUT / "test_segments.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["sentence", "chars", "tokens", "segmentation"])
        writer.writeheader()
        writer.writerows(test_rows)

    steps = np.array([h["step"] for h in history])
    tokens = np.array([h["total_tokens"] for h in history])
    cpt = np.array([h["chars_per_token"] for h in history])
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot(steps, tokens, color="#2b6cb0", lw=2)
    axes[0].set_title("BPE training: total tokens vs merges")
    axes[0].set_xlabel("merge step")
    axes[0].set_ylabel("tokens on training corpus")
    axes[0].grid(alpha=0.3)
    axes[1].plot(steps, cpt, color="#c05621", lw=2)
    axes[1].set_title("Compression: characters per token")
    axes[1].set_xlabel("merge step")
    axes[1].set_ylabel("chars / token")
    axes[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "compression_curve.png", dpi=160)
    plt.close(fig)

    metrics = {
        "corpus_lines": len(lines),
        "pretokenized_types": len(trained_words),
        "alphabet_size": len({ch for line in lines for ch in line if not ch.isspace()}),
        "num_merges": len(merges),
        "first_10_merges": ["+".join(m) for m in merges[:10]],
        "tokens_initial_chars": total_chars,
        "tokens_after": history[-1]["total_tokens"],
        "token_reduction_pct": round(100 * (1 - history[-1]["total_tokens"] / (total_chars)), 2),
        "chars_per_token_after": round(total_chars / history[-1]["total_tokens"], 3),
        "train_chars": total_chars,
        "test": test_rows,
    }
    (OUT / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
