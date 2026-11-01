#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""lab-03　梅尔刻度、三角滤波器组与对数梅尔特征

对应 actions.md 第 3 条；对应书中 §15.4.3（音高感知）与 §15.5.4（梅尔滤波器组）。
"""
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK JP", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

FS, FRAME, STRIDE, NFFT = 16000, 400, 160, 512
BIN = FS / NFFT
NCH = 80


def hz2mel(f):
    return 1127.0 * np.log(1.0 + np.asarray(f, float) / 700.0)


def mel2hz(m):
    return 700.0 * (np.exp(np.asarray(m, float) / 1127.0) - 1.0)


def resonator(x, f, bw=80.0):
    r = np.exp(-np.pi * bw / FS)
    a1 = 2 * r * np.cos(2 * np.pi * f / FS)
    y = np.zeros_like(x)
    for n in range(2, len(x)):
        y[n] = x[n] + a1 * y[n - 1] - r * r * y[n - 2]
    return y


def vowel(f0, formants, dur=0.4):
    n = int(dur * FS)
    src = np.zeros(n)
    src[:: int(round(FS / f0))] = 1.0
    y = src
    for f in formants:
        y = resonator(y, f)
    return y / (np.max(np.abs(y)) + 1e-12)


def frames(x):
    return np.array([x[i:i + FRAME] for i in range(0, len(x) - FRAME + 1, STRIDE)])


def logmel(x, fb):
    S = np.abs(np.fft.rfft(frames(x) * np.hamming(FRAME), NFFT)) ** 2
    return np.log(S @ fb.T + 1e-10)


def loglinear(x, nbins=40):
    S = np.abs(np.fft.rfft(frames(x) * np.hamming(FRAME), NFFT)) ** 2
    edges = np.linspace(0, len(S[0]), nbins + 1).astype(int)
    pooled = np.stack([S[:, edges[i]:edges[i + 1]].mean(1) for i in range(nbins)], 1)
    return np.log(pooled + 1e-10)


# ---------- 1. 梅尔刻度压缩比 ----------
rows = []
for f in (0, 100, 500, 1000, 2000, 4000, 7000, 8000):
    rows.append({"Hz": f, "mel": round(float(hz2mel(f)), 1)})
for lo in (0, 700, 7000):
    d = float(hz2mel(lo + 100) - hz2mel(lo))
    rows_d = {"Hz_range": f"{lo}-{lo+100}", "delta_mel": round(d, 1)}
    print(f"每 100 Hz 的梅尔增量 {lo}-{lo+100} Hz: {d:.1f} mel")
with open(os.path.join(OUT, "mel_scale.csv"), "w", encoding="utf-8") as f:
    f.write("Hz,mel\n")
    for r in rows:
        f.write(f"{r['Hz']},{r['mel']}\n")

# ---------- 2. 三角滤波器组 ----------
mel_pts = np.linspace(hz2mel(0), hz2mel(FS / 2), NCH + 2)
hz_pts = mel2hz(mel_pts)
fb = np.zeros((NCH, NFFT // 2 + 1))
for m in range(1, NCH + 1):
    lo, ce, hi = hz_pts[m - 1], hz_pts[m], hz_pts[m + 1]
    for k in range(NFFT // 2 + 1):
        f = k * BIN
        if lo < f <= ce:
            fb[m - 1, k] = (f - lo) / (ce - lo)
        elif ce < f < hi:
            fb[m - 1, k] = (hi - f) / (hi - ce)
bin_counts = (fb > 0).sum(1)
print(f"滤波器数 {NCH}；第 1 个占 {bin_counts[0]} 个 FFT bin，最后一个占 {bin_counts[-1]} 个")
print(f"最低中心 {hz_pts[1]:.1f} Hz，最高中心 {hz_pts[-2]:.1f} Hz")

plt.figure(figsize=(9, 3.4))
for m in range(NCH):
    plt.plot(np.arange(NFFT // 2 + 1) * BIN, fb[m], lw=.8)
plt.xlim(0, 8000); plt.xlabel("频率 / Hz"); plt.ylabel("权重")
plt.title(f"{NCH} 通道梅尔三角滤波器组（0–8000 Hz，16 kHz 采样）")
plt.grid(alpha=.3); plt.tight_layout()
plt.savefig(os.path.join(OUT, "filterbank.png"), dpi=130)
plt.close()

# ---------- 3. 三个元音的 log-mel 可分性 ----------
# [iy] 540/2581/3020、[ae] 930/1860/3020 取书中数值；[uh] 书中只给 F1≈800 与"F2 最低"，
# 这里把 F2 设为 1150 作为合成参数（不是测量值）。
VOWELS = {"iy": (540, 2581, 3020), "ae": (930, 1860, 3020), "uh": (800, 1150, 2500)}
rng = np.random.default_rng(7)
F0S = (100, 120, 140)

proto = {}
for name, fmts in VOWELS.items():
    proto[name] = logmel(vowel(120, fmts), fb).mean(0)


def classify(feat, refs):
    x = feat - feat.mean()
    best, bs = None, -9
    for k, v in refs.items():
        v = v - v.mean()
        s = float(x @ v / (np.linalg.norm(x) * np.linalg.norm(v) + 1e-12))
        if s > bs:
            best, bs = k, s
    return best, bs


def make_set(featurizer):
    data = {}
    for name, fmts in VOWELS.items():
        arr = []
        for f0 in F0S:
            for trial in range(5):
                jit = [f * (1 + rng.normal(0, 0.01)) for f in fmts]
                arr.append(featurizer(vowel(f0, jit)).mean(0))
        data[name] = np.array(arr)
    return data


def margin(data):
    """同类最大余弦距离 与 异类最小余弦距离 之比的对数（越大越好分）"""
    def cd(a, b):
        a = a - a.mean(); b = b - b.mean()
        return 1 - float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))
    within, between = [], []
    for k, v in data.items():
        for i in range(len(v)):
            for j in range(i + 1, len(v)):
                within.append(cd(v[i], v[j]))
    ks = list(data)
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            for a in data[ks[i]]:
                for b in data[ks[j]]:
                    between.append(cd(a, b))
    return max(within), min(between), min(between) / (max(within) + 1e-12)


def add_noise(x, snr, rng):
    p = np.mean(x ** 2)
    return x + rng.normal(0, np.sqrt(p / 10 ** (snr / 10)), len(x))


sweep = []
for snr in (20, 10, 0, -5):
    row = {"snr_dB": snr}
    for fname, feat in (("logmel80", lambda y: logmel(y, fb)),
                        ("lin80", lambda y: loglinear(y, 80)),
                        ("lin40", lambda y: loglinear(y, 40))):
        protos, ok, tot = {}, 0, 0
        for name, fmts in VOWELS.items():
            protos[name] = feat(vowel(120, fmts)).mean(0)
        for name, fmts in VOWELS.items():
            for f0 in F0S:
                for trial in range(5):
                    jit = [f * (1 + rng.normal(0, 0.01)) for f in fmts]
                    pred, _ = classify(feat(add_noise(vowel(f0, jit), snr, rng)).mean(0), protos)
                    ok += pred == name
                    tot += 1
        row[fname] = round(ok / tot, 3)
    sweep.append(row)
    print(row)

w_all, b_all, ratio_all = margin(make_set(lambda y: logmel(y, fb)))
w_lin80, b_lin80, ratio_lin80 = margin(make_set(lambda y: loglinear(y, 80)))
w_lin, b_lin, ratio_lin = margin(make_set(lambda y: loglinear(y, 40)))
print(f"log-mel 80: 同类最大距离 {w_all:.3f} / 异类最小距离 {b_all:.3f} → 比值 {ratio_all:.2f}")
print(f"线性 80 桶: 同类最大距离 {w_lin80:.3f} / 异类最小距离 {b_lin80:.3f} → 比值 {ratio_lin80:.2f}")
print(f"线性 40 桶: 同类最大距离 {w_lin:.3f} / 异类最小距离 {b_lin:.3f} → 比值 {ratio_lin:.2f}")

with open(os.path.join(OUT, "snr_sweep.csv"), "w", encoding="utf-8") as f:
    f.write("snr_dB,logmel80_acc,lin80_acc,lin40_acc\n")
    for r in sweep:
        f.write(f"{r['snr_dB']},{r['logmel80']},{r['lin80']},{r['lin40']}\n")

summary = {
    "n_channels": NCH, "bin_hz": BIN,
    "mel_100Hz_step": {f"{lo}-{lo+100}": round(float(hz2mel(lo + 100) - hz2mel(lo)), 1)
                       for lo in (0, 700, 7000)},
    "bins_per_filter_first_last": [int(bin_counts[0]), int(bin_counts[-1])],
    "center_range_Hz": [round(float(hz_pts[1]), 1), round(float(hz_pts[-2]), 1)],
    "snr_sweep": sweep,
    "margin_logmel": round(ratio_all, 2),
    "margin_lin80": round(ratio_lin80, 2),
    "margin_lin40": round(ratio_lin, 2),
}
with open(os.path.join(OUT, "summary.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
