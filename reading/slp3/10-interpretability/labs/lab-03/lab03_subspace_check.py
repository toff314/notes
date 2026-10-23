#!/usr/bin/env python3
"""lab-03 补充诊断：SAE 是否恢复了真特征所在的子空间？

单特征余弦低可能有两种原因：(a) 编码器没学到；(b) 学到了同一子空间但基被旋转。
这里对 λ=0.5 的模型逐样本比较「4 个真特征张成的子空间」与
「激活最大的 4 个字典原子张成的子空间」的重叠度（1=完全一致）。
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import lab03_sae as L

OUT = Path(__file__).resolve().parent / "out"
LAMBDA = 0.5


def main() -> None:
    A, F, S = L.make_data()
    n_train = int(0.8 * L.N)
    We, be, Wd, bd = L.train_sae(A[:n_train], LAMBDA)

    Ate = A[n_train:]
    Ste = S[n_train:]
    Z = np.maximum(Ate @ Wd + be, 0.0)
    overlaps = []
    for i in range(len(Ate)):
        true_idx = np.where(Ste[i] > 0)[0]
        dict_idx = np.argsort(-Z[i])[: L.K]
        Q1 = np.linalg.qr(F[true_idx].T)[0]
        Q2 = np.linalg.qr(Wd[:, dict_idx])[0]
        overlaps.append(float(np.linalg.norm(Q1.T @ Q2, "fro") ** 2 / L.K))

    Dn = Wd / (np.linalg.norm(Wd, axis=0, keepdims=True) + 1e-8)
    best = (Dn.T @ F.T).max(axis=0)
    report = {
        "lambda": LAMBDA,
        "steps": L.STEPS,
        "n_test": int(len(Ate)),
        "mean_subspace_overlap": round(float(np.mean(overlaps)), 4),
        "median_subspace_overlap": round(float(np.median(overlaps)), 4),
        "p10_subspace_overlap": round(float(np.percentile(overlaps, 10)), 4),
        "mean_best_feature_cosine": round(float(best.mean()), 4),
        "max_best_feature_cosine": round(float(best.max()), 4),
        "frac_feature_cosine_gt_0.8": round(float((best > 0.8).mean()), 3),
    }
    (OUT / "subspace_check.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
