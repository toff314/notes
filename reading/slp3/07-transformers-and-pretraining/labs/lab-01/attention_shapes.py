#!/usr/bin/env python3
"""Lab 01: scaled dot-product attention + causal mask + multi-head concat."""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(exist_ok=True)
RNG = np.random.default_rng(7)


def softmax(x, axis=-1):
    m = np.max(x, axis=axis, keepdims=True)
    e = np.exp(x - m)
    return e / np.sum(e, axis=axis, keepdims=True)


def causal_mask(n):
    return np.triu(np.ones((n, n), dtype=bool), k=1)


def multihead_attention(X, heads, Wo, mask=True):
    """heads: list of (Wq, Wk, Wv); Wo: [A*dh, d]."""
    n, d = X.shape
    outs, all_weights = [], []
    for Wq, Wk, Wv in heads:
        dh = Wq.shape[1]
        Q, K, V = X @ Wq, X @ Wk, X @ Wv
        scores = Q @ K.T / np.sqrt(dh)
        if mask:
            scores = np.where(causal_mask(n), -np.inf, scores)
        weights = softmax(scores, axis=-1)
        outs.append(weights @ V)
        all_weights.append(weights)
    concat = np.concatenate(outs, axis=-1)
    return {
        "weights": all_weights,
        "concat": concat,
        "out": concat @ Wo,
    }


def make_heads(d, dh, n_heads):
    return [
        (
            RNG.normal(scale=0.4, size=(d, dh)),
            RNG.normal(scale=0.4, size=(d, dh)),
            RNG.normal(scale=0.4, size=(d, dh)),
        )
        for _ in range(n_heads)
    ]


def main():
    n, d, n_heads = 6, 8, 2
    dh = d // n_heads
    X = RNG.normal(size=(n, d))
    heads = make_heads(d, dh, n_heads)
    Wo = RNG.normal(scale=0.4, size=(n_heads * dh, d))

    res = multihead_attention(X, heads, Wo, mask=True)
    weights = res["weights"][0]

    # Causality: changing future tokens must not change earlier outputs.
    X2 = X.copy()
    X2[3:] += 2.5
    res2 = multihead_attention(X2, heads, Wo, mask=True)
    causal_diff = float(np.max(np.abs(res["out"][:3] - res2["out"][:3])))

    # Without the mask the same perturbation leaks into earlier positions.
    res_nomask = multihead_attention(X, heads, Wo, mask=False)
    res2_nomask = multihead_attention(X2, heads, Wo, mask=False)
    leak_diff = float(np.max(np.abs(res_nomask["out"][:3] - res2_nomask["out"][:3])))

    # Parameter count, biases ignored (exercise 7.1).
    attn_params = 3 * d * dh * n_heads + (n_heads * dh) * d
    attn_params_a1 = 3 * d * d + d * d
    ffn_params = 2 * d * (4 * d)
    per_block = attn_params + ffn_params

    checks = {
        "shapes": {
            "concat": list(res["concat"].shape),
            "out": list(res["out"].shape),
            "per_head_weights": [list(w.shape) for w in res["weights"]],
        },
        "row_sum_max_error": float(np.max(np.abs(weights.sum(axis=-1) - 1.0))),
        "masked_upper_max_weight": float(np.max(np.abs(np.triu(weights, k=1)))),
        "causal_perturbation_max_diff": causal_diff,
        "unmasked_perturbation_leak": leak_diff,
        "head_dim_equals_d_over_A": dh == d // n_heads,
        "attention_params_A2": attn_params,
        "attention_params_A1": attn_params_a1,
        "attention_params_independent_of_A": attn_params == attn_params_a1,
        "ffn_params_no_bias": ffn_params,
        "per_block_params_no_bias": per_block,
        "formula_12d2": 12 * d * d,
    }
    checks["all_pass"] = bool(
        checks["row_sum_max_error"] < 1e-12
        and checks["masked_upper_max_weight"] == 0.0
        and causal_diff < 1e-12
        and leak_diff > 1e-6
        and checks["attention_params_independent_of_A"]
        and per_block == 12 * d * d
    )
    (OUT / "checks.json").write_text(json.dumps(checks, indent=2, ensure_ascii=False), encoding="utf-8")
    np.savetxt(OUT / "attention_weights.csv", weights, delimiter=",", fmt="%.6f")

    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8))
    for ax, mat, title in (
        (axes[0], res_nomask["weights"][0], "no mask"),
        (axes[1], weights, "causal mask (upper = 0)"),
    ):
        im = ax.imshow(mat, cmap="Blues", vmin=0, vmax=1)
        ax.set_title(title)
        ax.set_xlabel("key position j")
        ax.set_ylabel("query position i")
        ax.set_xticks(range(n))
        ax.set_yticks(range(n))
    fig.colorbar(im, ax=axes, fraction=0.046, pad=0.04)
    fig.suptitle("Scaled dot-product attention weights (one head)")
    fig.savefig(OUT / "attention_heatmap.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    print(json.dumps(checks, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
