#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""lab-05　从波形量出韵律：F0 轨迹、强度与"升调/降调"判定

对应 actions.md 第 5 条；对应书中 §15.3（突显、重音、调型）与 §15.4.3（音高、响度）。
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

FS = 16000
FL, HOP = int(0.040 * FS), int(0.010 * FS)


def syllable(dur, f0_func, amp=1.0):
    """用相位累积合成一个带 F0 轮廓的浊音段"""
    n = int(dur * FS)
    t = np.arange(n) / FS
    f0 = f0_func(t / max(dur, 1e-9))
    phase = 2 * np.pi * np.cumsum(f0) / FS
    x = sum(np.sin(k * phase) / k for k in range(1, 6))
    env = np.hanning(n) ** 0.5
    return amp * x * env


def utterance(kind, f0_start=130.0, jitter=0.0, rng=None):
    """两个音节：第一个重读（长、响），第二个轻读；调型由 kind 决定"""
    if kind == "fall":
        f2 = lambda u: f0_start + (f0_start - 25 - f0_start) * u
    else:
        f2 = lambda u: f0_start - 10 + (f0_start + 35 - (f0_start - 10)) * u
    s1 = syllable(0.18, lambda u: f0_start + 6 * np.sin(np.pi * u))
    s2 = syllable(0.12, f2, amp=0.55)
    gap = np.zeros(int(0.02 * FS))
    x = np.concatenate([s1, gap, s2])
    if jitter:
        x = x + rng.normal(0, jitter * np.std(x), len(x))
    return x


def f0_track(x):
    f0s, inten = [], []
    for i in range(0, len(x) - FL, HOP):
        seg = x[i:i + FL] * np.hamming(FL)
        rms = np.sqrt(np.mean(seg ** 2) + 1e-12)
        inten.append(20 * np.log10(rms + 1e-12))
        seg = seg - seg.mean()
        ac = np.correlate(seg, seg, "full")[FL - 1:]
        lo, hi = int(FS / 400), int(FS / 60)
        lag = lo + int(np.argmax(ac[lo:hi]))
        f0s.append(FS / lag)
    return np.array(f0s), np.array(inten)


def final_slope(f0, ms=250):
    k = max(3, int(ms / 10))
    y = f0[-k:]
    t = np.arange(len(y)) * 0.01
    return float(np.polyfit(t, y, 1)[0]), float(y.max() - y.min())


rng = np.random.default_rng(3)
rows, curves = [], {}
for kind in ("fall", "rise"):
    x = utterance(kind)
    f0, inten = f0_track(x)
    slope, span = final_slope(f0)
    curves[kind] = (f0, inten)
    rows.append({"kind": kind, "f0_mean": round(float(f0.mean()), 1),
                 "f0_max": round(float(f0.max()), 1), "f0_min": round(float(f0.min()), 1),
                 "final_slope_Hz_per_s": round(slope, 1), "final_span_Hz": round(span, 1),
                 "intensity_range_dB": round(float(inten.max() - inten.min()), 1)})
    print(f"{kind}: 末段斜率 {slope:+.1f} Hz/s，末段跨度 {span:.1f} Hz，强度动态 {inten.max()-inten.min():.1f} dB")

# 判定器：末 250 ms 斜率 > +40 Hz/s 判为疑问
correct = 0
trials = 0
det = []
for kind in ("fall", "rise"):
    for _ in range(10):
        x = utterance(kind, f0_start=rng.uniform(110, 150), jitter=0.02, rng=rng)
        f0, _ = f0_track(x)
        slope, _ = final_slope(f0)
        pred = "rise" if slope > 40 else "fall"
        det.append({"true": kind, "slope": round(slope, 1), "pred": pred})
        correct += pred == kind
        trials += 1
print(f"调型判定准确率（含噪声与基频随机化）：{correct}/{trials} = {correct/trials:.2f}")

# 音高 vs 响度：整体缩放 0.5
x = utterance("fall")
x2 = 0.5 * x
f1, i1 = f0_track(x)
f2, i2 = f0_track(x2)
d_db = float(i1.mean() - i2.mean())
d_hz = float(np.abs(f1 - f2).max())
print(f"振幅减半：平均强度差 {d_db:.2f} dB，F0 最大差 {d_hz:.3f} Hz")
print(f"理论值 20·log10(2) = {20*np.log10(2):.2f} dB")

fig, ax = plt.subplots(2, 1, figsize=(8, 5), sharex=True)
for kind, (f0, inten) in curves.items():
    t = np.arange(len(f0)) * 0.01
    ax[0].plot(t, f0, label=f"{kind}（末段 {rows[0 if kind=='fall' else 1]['final_slope_Hz_per_s']:+.0f} Hz/s）")
    ax[1].plot(t, inten, label=kind)
ax[0].set_ylabel("F0 / Hz"); ax[0].legend(); ax[0].grid(alpha=.3)
ax[1].set_ylabel("强度 / dB"); ax[1].set_xlabel("时间 / s"); ax[1].legend(); ax[1].grid(alpha=.3)
ax[0].set_title("同一声段、两种调型的 F0 与强度轨迹")
plt.tight_layout(); plt.savefig(os.path.join(OUT, "prosody_tracks.png"), dpi=130); plt.close()

with open(os.path.join(OUT, "f0_intensity.csv"), "w", encoding="utf-8") as f:
    f.write("kind,frame,time_s,f0_Hz,intensity_dB\n")
    for kind, (f0, inten) in curves.items():
        for i, (a, b) in enumerate(zip(f0, inten)):
            f.write(f"{kind},{i},{i*0.01:.2f},{a:.1f},{b:.2f}\n")

summary = {"contours": rows, "classifier_acc": round(correct / trials, 3),
           "scale_half": {"intensity_drop_dB": round(d_db, 2), "max_f0_diff_Hz": round(d_hz, 3),
                          "theory_dB": round(float(20 * np.log10(2)), 2)},
           "detections": det}
with open(os.path.join(OUT, "summary.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
