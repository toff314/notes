#!/usr/bin/env python3
"""Lab 03: 用正则做 GPT-2 式预词元化，并核查中英西句子的切分差异。

对应 actions.md 行动 3；对应《Speech and Language Processing》§2.6.9。
标准库 re 不支持 \\p{L}，这里用 [^\\W\\d_] 近似 Unicode 字母，并保留原模式的骨架。
只依赖标准库 + numpy + matplotlib。
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
OUT.mkdir(parents=True, exist_ok=True)

PATTERN = re.compile(
    r"’s|’t|’re|’ve|’m|’ll|’d|"
    r" ?[^\W\d_]+|"
    r" ?\d+|"
    r" ?[^\s\w]+|"
    r"\s+(?!\S)|\s+"
)

SENTENCES = [
    "We’re 350 dogs! Um, lunch?",
    "词元化是 NLP 的第一步。",
    "El niño comió nuez y jengibre.",
    "doesn't charge $10.40 — https://www.stanford.edu #nlproc",
]


def main() -> None:
    rows = []
    detail = []
    for sent in SENTENCES:
        pieces = PATTERN.findall(sent)
        visible = [p.replace(" ", "␣") for p in pieces]
        words = sent.split()
        rows.append(
            {
                "sentence": sent,
                "chars_no_space": len(sent.replace(" ", "")),
                "space_words": len(words),
                "tokens": len(pieces),
                "tokens_per_word": round(len(pieces) / len(words), 3),
                "naive_whitespace_tokens": len(words),
            }
        )
        detail.append({"sentence": sent, "tokens": visible})

    with (OUT / "pretokenization.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (OUT / "pretokenization.json").write_text(
        json.dumps(detail, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    labels = ["EN book", "ZH", "ES", "mixed"]
    token_counts = [r["tokens"] for r in rows]
    whitespace_counts = [r["naive_whitespace_tokens"] for r in rows]
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(x - 0.2, token_counts, 0.4, label="regex pretokenizer", color="#2b6cb0")
    ax.bar(x + 0.2, whitespace_counts, 0.4, label="whitespace split", color="#dd6b20")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("number of tokens")
    ax.set_title("Pretokenization: regex vs whitespace")
    ax.legend()
    for i, v in enumerate(token_counts):
        ax.text(i - 0.2, v + 0.2, str(v), ha="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "token_counts.png", dpi=160)
    plt.close(fig)

    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
