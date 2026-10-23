#!/usr/bin/env python3
"""lab-02: logit lens vs J-lens（玩具残差流）

构造一个已知算法的 4 层玩具模型：
  h0  词嵌入之和
  h1  = h0 + L1(h0)        L1 检测「fourth + planet」，写入 mars
  h2  = R2 @ h1 + L2(...)  L2 检测「mars + color」，写入 red；此处换基
  h3  = R2^{-1} @ h2       回到输出基
  logits = U @ h3

logit lens 直接用 U 乘各层向量；J-lens 先用数值雅可比把该层映射到 h3。
换基之后 logit lens 应当失效，而 J-lens 仍能读出中间概念。
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

RNG = np.random.default_rng(7)
OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(exist_ok=True)

D = 32
TOKENS = ["<pad>", "the", "fourth", "planet", "is", "mars", "red",
          "large", "small", "color", "and", "its", "of"]
T2I = {t: i for i, t in enumerate(TOKENS)}

PROMPTS = {
    "A_planet": {"tokens": ["the", "fourth", "planet", "is"], "answer": "mars"},
    "B_color": {"tokens": ["the", "fourth", "planet", "is", "mars", "and", "its", "color", "is"],
                "answer": "red"},
}

ALPHA = 10.0
BETA = 10.0
GATE = 0.5


def ortho_basis(n: int, d: int) -> np.ndarray:
    q, _ = np.linalg.qr(RNG.normal(size=(d, n)))
    return q.T  # n × d，行相互正交


V = ortho_basis(len(TOKENS), D)
DIR = {t: V[i] for i, t in enumerate(TOKENS)}
R2, _ = np.linalg.qr(RNG.normal(size=(D, D)))
R2_inv = R2.T


def emb(tokens: list[str]) -> np.ndarray:
    h = np.zeros(D)
    for t in tokens:
        h += DIR[t] + RNG.normal(scale=0.01, size=D)
    return h


def and_gate(a: float, b: float) -> float:
    """两个概念同时出现时才通过：投影相乘后减去阈值。"""
    return max(max(a, 0.0) * max(b, 0.0) - GATE, 0.0)


def layer1(h: np.ndarray) -> np.ndarray:
    gate = and_gate(np.dot(DIR["fourth"], h), np.dot(DIR["planet"], h))
    return ALPHA * gate * DIR["mars"]


def layer2(h: np.ndarray) -> np.ndarray:
    gate = and_gate(np.dot(R2 @ DIR["mars"], h), np.dot(R2 @ DIR["color"], h))
    return BETA * gate * (R2 @ DIR["red"])


def forward(h0: np.ndarray) -> tuple[list[np.ndarray], np.ndarray]:
    h1 = h0 + layer1(h0)
    h2 = R2 @ h1 + layer2(R2 @ h1)
    h3 = R2_inv @ h2
    return [h0, h1, h2, h3], h3


def to_final(h: np.ndarray, layer: int) -> np.ndarray:
    """从第 layer 层的状态继续前向，返回最终 h3（J-lens 需要）。"""
    if layer == 0:
        h = h + layer1(h)
        layer = 1
    if layer == 1:
        h = R2 @ h
        h = h + layer2(h)
    if layer <= 2:
        h = R2_inv @ h
    return h


def logits(h: np.ndarray) -> np.ndarray:
    return V @ h


def jacobian(h: np.ndarray, layer: int, eps: float = 1e-5) -> np.ndarray:
    J = np.zeros((D, D))
    for i in range(D):
        e = np.zeros(D)
        e[i] = eps
        hp = to_final(h + e, layer)
        hm = to_final(h - e, layer)
        J[:, i] = (hp - hm) / (2 * eps)
    return J


def rank_of(scores: np.ndarray, token: str) -> int:
    order = np.argsort(scores)[::-1]
    return int(np.where(order == T2I[token])[0][0]) + 1


def topk(scores: np.ndarray, k: int = 5) -> list[str]:
    order = np.argsort(scores)[::-1][:k]
    return [TOKENS[i] for i in order]


def main() -> None:
    rows = []
    summary = {}
    for name, spec in PROMPTS.items():
        h0 = emb(spec["tokens"])
        states, h3 = forward(h0)
        answer = spec["answer"]
        for li, h in enumerate(states):
            for lens, scores in (
                ("logit", logits(h)),
                ("j_lens", logits(jacobian(h, li) @ h)),
            ):
                rows.append({
                    "prompt": name,
                    "layer": li,
                    "lens": lens,
                    "top1": topk(scores, 1)[0],
                    "rank_correct": rank_of(scores, answer),
                    "top5": "|".join(topk(scores, 5)),
                })
        summary[name] = {
            "answer": answer,
            "final_top1": topk(logits(h3), 1)[0],
            "logit_rank_by_layer": [],
            "jlens_rank_by_layer": [],
        }
        for li in range(len(states)):
            hrs = [r for r in rows if r["prompt"] == name and r["layer"] == li]
            summary[name]["logit_rank_by_layer"].append(
                [r for r in hrs if r["lens"] == "logit"][0]["rank_correct"])
            summary[name]["jlens_rank_by_layer"].append(
                [r for r in hrs if r["lens"] == "j_lens"][0]["rank_correct"])

    fields = ["prompt", "layer", "lens", "top1", "rank_correct", "top5"]
    with open(OUT / "lens_rank.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    with open(OUT / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "Noto Sans CJK JP", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.0), sharey=True)
    for ax, (name, s) in zip(axes, summary.items()):
        ax.plot(range(4), s["logit_rank_by_layer"], marker="o", label="logit lens", color="#1f77b4")
        ax.plot(range(4), s["jlens_rank_by_layer"], marker="s", label="J-lens", color="#d62728")
        ax.axvspan(1.5, 2.5, color="#ffcc99", alpha=0.35, label="换基层")
        ax.set_xticks(range(4))
        ax.set_xlabel("层（0=嵌入，1=推理一步，2=换基，3=输出）")
        ax.set_title(f"{name}（答案：{s['answer']}）")
        ax.grid(alpha=0.25)
        ax.legend(fontsize=8)
    axes[0].set_ylabel("正确答案的排名（1=最好）")
    axes[0].set_ylim(0.5, len(TOKENS) + 0.5)
    fig.tight_layout()
    fig.savefig(OUT / "lens_rank.png", dpi=150)

    for r in rows:
        print(f"{r['prompt']} L{r['layer']} {r['lens']:6s} top1={r['top1']:7s} "
              f"rank={r['rank_correct']:2d} top5={r['top5']}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
