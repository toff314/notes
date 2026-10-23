#!/usr/bin/env python3
"""Lab 04: parameter accounting (exercise 7.1) and perplexity (7.3 / 7.4)."""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(exist_ok=True)


def attention_params(d, a):
    dh = d // a
    return 3 * d * dh * a + (a * dh) * d


def ffn_params(d, dff):
    return 2 * d * dff


def main():
    d, dff, layers, a = 512, 2048, 12, 8
    attn = attention_params(d, a)
    ffn = ffn_params(d, dff)
    block = attn + ffn
    total = layers * block
    formula = 12 * layers * d * d
    by_head = {
        "A=1": attention_params(d, 1),
        "A=4": attention_params(d, 4),
        "A=8": attention_params(d, 8),
        "A=16": attention_params(d, 16),
    }

    probs = np.array([0.0001, 0.0002, 0.000005, 0.0000001])
    product = float(np.prod(probs))
    ppl = float(product ** (-1 / len(probs)))
    mean_ce = float(-np.mean(np.log(probs)))
    ppl_from_ce = float(np.exp(mean_ce))

    models = [
        ("GPT-2 XL", 2019, 48, 1600, 25, 6400, 1.5e9),
        ("GPT-3", 2020, 96, 12288, 96, 49152, 175e9),
        ("Qwen3-0.6B", 2025, 28, 1024, 16, 3072, 0.6e9),
        ("Qwen3-32B", 2025, 64, 5120, 64, 25600, 32e9),
        ("Llama 3.1 8B", 2024, 32, 4096, 32, 14336, 8e9),
        ("Llama 3.1 405B", 2024, 126, 16384, 128, 53248, 405e9),
    ]
    rows = []
    for name, year, L, d_m, A, dff_m, reported in models:
        approx = 12 * L * d_m * d_m
        rows.append({"model": name, "year": year, "L": L, "d": d_m, "A": A,
                     "dff": dff_m, "reported": reported, "12Ld2": approx,
                     "ratio_approx_over_reported": approx / reported})

    with open(OUT / "param_table.csv", "w", encoding="utf-8") as f:
        f.write("model,year,L,d,A,dff,reported,12Ld2,ratio\n")
        for r in rows:
            f.write(f"{r['model']},{r['year']},{r['L']},{r['d']},{r['A']},{r['dff']},"
                    f"{r['reported']:.3e},{r['12Ld2']:.3e},{r['ratio_approx_over_reported']:.4f}\n")

    summary = {
        "exercise_7_1": {
            "d": d, "dff": dff, "L": layers, "A": a,
            "attention_per_layer": attn, "ffn_per_layer": ffn,
            "block": block, "total_L_blocks": total, "formula_12Ld2": formula,
            "matches": total == formula,
            "attention_params_by_A": by_head,
            "attention_independent_of_A": len(set(by_head.values())) == 1,
            "ffn_share_of_block": ffn / block,
        },
        "exercise_7_3": {
            "probabilities": probs.tolist(),
            "product": product,
            "perplexity": ppl,
            "mean_cross_entropy_nats": mean_ce,
            "perplexity_from_exp_mean_ce": ppl_from_ce,
            "identity_holds": abs(ppl - ppl_from_ce) < 1e-9,
        },
        "model_table": rows,
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    names = [r["model"] for r in rows]
    x = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.bar(x - 0.2, [r["reported"] for r in rows], width=0.4, label="reported")
    ax.bar(x + 0.2, [r["12Ld2"] for r in rows], width=0.4, label="12 L d^2 (no embeddings)")
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=18, ha="right")
    ax.set_ylabel("parameters (log scale)")
    ax.set_title("12Ld^2 tracks reported scale; gaps are embeddings/GQA/FFN details")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.savefig(OUT / "param_check.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
