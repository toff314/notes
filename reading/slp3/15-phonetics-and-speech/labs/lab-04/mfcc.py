#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""lab-04　倒谱、MFCC 与差分特征：源与滤波器能不能分开

对应 actions.md 第 4 条；对应书中 §15.6（MFCC、倒谱、Δ/ΔΔ）。
"""
import json
import os

import numpy as np
from scipy.fftpack import dct
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK JP", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

FS, FRAME, STRIDE, NFFT, NCH = 16000, 400, 160, 512, 40
AE = (930, 1860, 3020)     # 书中 [ae] 的 F1/F2/F3


def resonator(x, f, bw=80.0):
    r = np.exp(-np.pi * bw / FS)
    a1 = 2 * r * np.cos(2 * np.pi * f / FS)
    y = np.zeros_like(x)
    for n in range(2, len(x)):
        y[n] = x[n] + a1 * y[n - 1] - r * r * y[n - 2]
    return y


def vowel(f0, formants, dur=0.5):
    n = int(dur * FS)
    src = np.zeros(n)
    src[:: int(round(FS / f0))] = 1.0
    y = src
    for f in formants:
        y = resonator(y, f)
    return y / (np.max(np.abs(y)) + 1e-12)


def frames(x):
    return np.array([x[i:i + FRAME] for i in range(0, len(x) - FRAME + 1, STRIDE)])


def hz2mel(f):
    return 1127.0 * np.log(1.0 + np.asarray(f, float) / 700.0)


def mel2hz(m):
    return 700.0 * (np.exp(np.asarray(m, float) / 1127.0) - 1.0)


def filterbank(nch=NCH):
    pts = mel2hz(np.linspace(hz2mel(0), hz2mel(FS / 2), nch + 2))
    fb = np.zeros((nch, NFFT // 2 + 1))
    for m in range(1, nch + 1):
        lo, ce, hi = pts[m - 1], pts[m], pts[m + 1]
        for k in range(NFFT // 2 + 1):
            f = k * FS / NFFT
            if lo < f <= ce:
                fb[m - 1, k] = (f - lo) / (ce - lo)
            elif ce < f < hi:
                fb[m - 1, k] = (hi - f) / (hi - ce)
    return fb


FB = filterbank()


def logmel(x, nch=NCH):
    S = np.abs(np.fft.rfft(frames(x) * np.hamming(FRAME), NFFT)) ** 2
    return np.log(S @ FB.T + 1e-10)


def mfcc(x, n=13):
    L = logmel(x)
    return dct(L, type=2, axis=1, norm="ortho")[:, :n]


def deltas(c, N=2):
    pad = np.pad(c, ((N, N), (0, 0)), mode="edge")
    num = sum(k * (pad[N + k:len(c) + N + k] - pad[N - k:len(c) + N - k]) for k in range(1, N + 1))
    return num / (2 * sum(k * k for k in range(1, N + 1)))


# ---------- 1. 倒谱估 F0 ----------
f0_rows = []
for f0 in (100, 120, 150, 200):
    x = vowel(f0, AE)
    seg = frames(x)[25] * np.hamming(FRAME)
    logmag = np.log(np.abs(np.fft.rfft(seg, NFFT)) + 1e-10)
    ceps = np.fft.irfft(logmag, NFFT)
    lo, hi = int(FS / 400), int(FS / 60)          # 2.5–16.7 ms 的倒谱搜索区
    q = lo + int(np.argmax(ceps[lo:hi]))
    est = FS / q
    f0_rows.append({"true_F0": f0, "quefrency_sample": q, "quefrency_ms": round(q / FS * 1000, 2),
                    "est_F0": round(est, 1), "err_Hz": round(est - f0, 1)})
    print(f"F0={f0:3d} Hz → 倒谱峰在 {q} 样本（{q/FS*1000:.2f} ms），估计 {est:.1f} Hz")

with open(os.path.join(OUT, "cepstrum_f0.csv"), "w", encoding="utf-8") as f:
    f.write("true_F0,quefrency_sample,quefrency_ms,est_F0,err_Hz\n")
    for r in f0_rows:
        f.write(",".join(str(v) for v in r.values()) + "\n")

# ---------- 2. 源-滤波分离测试 ----------
c_a, c_b = mfcc(vowel(100, AE)), mfcc(vowel(150, AE))
a, b = c_a.mean(0), c_b.mean(0)
low = float(np.linalg.norm(a[1:13] - b[1:13]))
high = float(np.linalg.norm(a[13:] - b[13:]))
la, lb = logmel(vowel(100, AE)).mean(0), logmel(vowel(150, AE)).mean(0)
lm = float(np.linalg.norm(la - lb))
print(f"同一 [ae]、F0 从 100 换到 150 Hz：c1–c12 距离 {low:.3f}，log-mel 距离 {lm:.3f}")

# 不同元音（滤波器变了）作为对照
c_c = mfcc(vowel(100, (540, 2581, 3020))).mean(0)
low2 = float(np.linalg.norm(a[1:13] - c_c[1:13]))
lm2 = float(np.linalg.norm(la - logmel(vowel(100, (540, 2581, 3020))).mean(0)))
print(f"同一 F0、[ae] 换成 [iy]：c1–c12 距离 {low2:.3f}，log-mel 距离 {lm2:.3f}")
print(f"比值（换元音/换音高）：倒谱 {low2/(low+1e-12):.1f}×，log-mel {lm2/(lm+1e-12):.1f}×")

with open(os.path.join(OUT, "source_filter.csv"), "w", encoding="utf-8") as f:
    f.write("条件,c1_c12距离,logmel距离\n")
    f.write(f"F0 100→150 Hz（同一滤波器）,{low:.3f},{lm:.3f}\n")
    f.write(f"ae→iy（同一 F0）,{low2:.3f},{lm2:.3f}\n")

# ---------- 3. 39 维与 Δ/ΔΔ ----------
iiy = vowel(120, (540, 2581, 3020), dur=0.25)
iae = vowel(120, AE, dur=0.35)
x = np.concatenate([iiy[:int(0.2 * FS)], iae[:int(0.2 * FS)]])
C = mfcc(x)
D = deltas(C)
A = deltas(D)
feat = np.hstack([C, D, A])
print(f"MFCC 形状 {C.shape}，Δ {D.shape}，ΔΔ {A.shape}，拼接 {feat.shape}")

fig, ax = plt.subplots(3, 1, figsize=(8, 6), sharex=True)
ax[0].imshow(C.T, aspect="auto", origin="lower", cmap="viridis")
ax[0].set_ylabel("倒谱阶数")
ax[1].plot(C[:, 1], label="c1"); ax[1].plot(C[:, 2], label="c2"); ax[1].legend(loc="upper right"); ax[1].set_ylabel("系数值")
ax[2].plot(D[:, 1], label="Δc1"); ax[2].plot(D[:, 2], label="Δc2"); ax[2].legend(loc="upper right"); ax[2].set_ylabel("Δ 值")
ax[2].set_xlabel("帧序号（10 ms/帧）")
ax[0].set_title("合成 [iy]→[ae] 过渡：MFCC 热图与 c1/c2 及其差分")
plt.tight_layout(); plt.savefig(os.path.join(OUT, "mfcc_delta.png"), dpi=130); plt.close()

transition = int(np.argmax(np.abs(D[:, 1])))
print(f"|Δc1| 最大的帧 = {transition}（约 {transition*10} ms），C 的第 1 维跨度 {C[:,1].min():.2f}→{C[:,1].max():.2f}")

summary = {
    "n_mfcc": 13, "dim_39": int(feat.shape[1]),
    "f0_estimation": f0_rows,
    "dist_same_filter_diff_f0": {"cepstrum_c1_12": round(low, 3), "logmel": round(lm, 3)},
    "dist_diff_vowel_same_f0": {"cepstrum_c1_12": round(low2, 3), "logmel": round(lm2, 3)},
    "ratio_cepstrum": round(low2 / (low + 1e-12), 1),
    "ratio_logmel": round(lm2 / (lm + 1e-12), 1),
    "transition_frame": int(transition),
}
with open(os.path.join(OUT, "summary.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
