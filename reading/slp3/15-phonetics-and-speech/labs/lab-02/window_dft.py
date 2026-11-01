#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""lab-02　分帧、加窗与 DFT：矩形窗的泄漏到底有多大

对应 actions.md 第 2 条；对应书中 §15.4.6–§15.5.3（源-滤波器、加窗、DFT）。
离线可跑：只用 numpy / matplotlib。
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
DUR = 0.5
FRAME = 400          # 25 ms
STRIDE = 160         # 10 ms
NFFT = 512
BIN = FS / NFFT


def resonator(x, f, bw=80.0, fs=FS):
    r = np.exp(-np.pi * bw / fs)
    a1 = 2 * r * np.cos(2 * np.pi * f / fs)
    a2 = -r * r
    y = np.zeros_like(x)
    for n in range(2, len(x)):
        y[n] = x[n] + a1 * y[n - 1] + a2 * y[n - 2]
    return y


def vowel(f0, formants, dur=DUR, fs=FS):
    """脉冲串（声门源）→ 三个共振峰级联（声道滤波器）"""
    n = int(dur * fs)
    src = np.zeros(n)
    src[:: int(round(fs / f0))] = 1.0
    y = src
    for f in formants:
        y = resonator(y, f)
    return y / (np.max(np.abs(y)) + 1e-12)


def frames(x, frame=FRAME, stride=STRIDE):
    return np.array([x[i:i + frame] for i in range(0, len(x) - frame + 1, stride)])


def db(v):
    return 20 * np.log10(v / (v.max() + 1e-20) + 1e-12)


# 书中给出的共振峰：[iy] F1=540 F2=2581；[ae] F1=930 F2=1860 F3=3020（§15.4.4–15.4.5）
VOWELS = {"iy": (540, 2581, 3020), "ae": (930, 1860, 3020)}
WINDOWS = (("rect", np.ones(FRAME)), ("hamming", np.hamming(FRAME)))

metrics = []
rowstxt = []

x = vowel(120, VOWELS["ae"])
fr = frames(x)
metrics += [
    ("信号采样点数", len(x), "点"),
    ("帧长", FRAME, "样本 / 25.0 ms"),
    ("帧移", STRIDE, "样本 / 10.0 ms"),
    ("帧数", len(fr), "1+floor((8000-400)/160)"),
]

# ---------- 纯音：整周期 vs 非整周期 ----------
t = np.arange(FRAME) / FS
tone_rows = []
for f0_tone in (240.0, 250.0):
    tone = np.sin(2 * np.pi * f0_tone * t)
    row = {"tone_Hz": f0_tone, "cycles_in_frame": f0_tone * FRAME / FS}
    for name, win in WINDOWS:
        S = np.abs(np.fft.rfft(tone * win, NFFT))
        P = S ** 2
        Sdb = db(S)
        k = int(np.argmax(S))
        main = np.zeros(len(S), bool)
        main[max(0, k - 2):k + 3] = True          # 主瓣取 ±2 bin
        leak = 1 - P[main].sum() / P.sum()
        half = np.where(Sdb >= -3.0)[0]
        # 扇贝损失：与"频率正好落在 bin 中心"时的理想峰值相比
        row[f"{name}_扇贝损失_dB"] = round(float(20 * np.log10(2 * S.max() / win.sum())), 2)
        row[f"{name}_3dB主瓣宽_Hz"] = round(float((half.max() - half.min() + 1) * BIN), 2)
        row[f"{name}_主瓣外能量占比"] = round(float(leak), 4)
        row[f"{name}_最坏旁瓣_dB"] = round(float(Sdb[~main].max()), 2)
        if f0_tone == 250.0:
            plt.plot(np.arange(len(S)) * BIN, Sdb, label=name, lw=.9)
    tone_rows.append(row)
    for name, _ in WINDOWS:
        metrics.append((f"{f0_tone:.0f} Hz 纯音 · {name} 窗", row[f"{name}_最坏旁瓣_dB"], "dB 最坏旁瓣"))
        metrics.append((f"{f0_tone:.0f} Hz 纯音 · {name} 窗", row[f"{name}_主瓣外能量占比"], "主瓣外能量占比"))

plt.xlim(0, 1200); plt.ylim(-90, 5)
plt.xlabel("频率 / Hz"); plt.ylabel("相对幅值 / dB")
plt.title("250 Hz 纯音（帧内 6.25 个周期）：矩形窗 vs 汉明窗")
plt.legend(); plt.grid(alpha=.3); plt.tight_layout()
plt.savefig(os.path.join(OUT, "window_leakage.png"), dpi=130)
plt.close()

# ---------- 元音帧：谐波与谷的对比 ----------
contrast = {}
for vname, fmts in VOWELS.items():
    xv = vowel(120, fmts)
    seg = frames(xv)[20]
    bins = np.arange(NFFT // 2 + 1) * BIN
    peak_mask = np.zeros(len(bins), bool)
    valley_mask = np.zeros(len(bins), bool)
    for h in range(120, 3600, 120):
        peak_mask |= np.abs(bins - h) <= 40
        valley_mask |= np.abs(bins - (h + 60)) <= 30
    for name, win in WINDOWS:
        Sdb = db(np.abs(np.fft.rfft(seg * win, NFFT)))
        contrast[(vname, name)] = float(Sdb[peak_mask].max() - Sdb[valley_mask].max())
        metrics.append((f"[{vname}] {name} 窗 谐波-谷对比", round(contrast[(vname, name)], 2), "dB"))
        if vname == "ae":
            plt.plot(bins, Sdb, lw=.9, label=name)
    if vname == "ae":
        plt.xlim(0, 4000); plt.ylim(-80, 5)
        plt.xlabel("频率 / Hz"); plt.ylabel("相对幅值 / dB")
        plt.title("元音 [ae] 单帧频谱（F0=120 Hz，F1=930，F2=1860，F3=3020）")
        plt.legend(); plt.grid(alpha=.3); plt.tight_layout()
        plt.savefig(os.path.join(OUT, "vowel_ae_spectrum.png"), dpi=130)
        plt.close()

with open(os.path.join(OUT, "windowing_metrics.csv"), "w", encoding="utf-8") as f:
    f.write("指标,数值,单位\n")
    for a, b, c in metrics:
        f.write(f"{a},{b},{c}\n")

summary = {
    "fs": FS, "frame_ms": FRAME / FS * 1000, "stride_ms": STRIDE / FS * 1000,
    "n_frames": int(len(fr)), "nfft": NFFT, "bin_hz": BIN,
    "tones": tone_rows,
    "harmonic_contrast_dB": {f"{k[0]}-{k[1]}": round(v, 2) for k, v in contrast.items()},
}
with open(os.path.join(OUT, "summary.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

for a, b, c in metrics:
    print(f"{a}: {b} {c}")
print("tone rows:")
for r in tone_rows:
    print(" ", r)
