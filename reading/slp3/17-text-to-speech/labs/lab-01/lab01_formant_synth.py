#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""lab-01：源-滤波器（共振峰）合成 + 基频/共振峰回收校验

对应 book-notes §17.1（TTS 要生成波形）、§17.2.1（24 kHz → 75 Hz = 320 倍下采样）、
§17.4（自动代理指标不能替代 MOS）。

做法：
  1. 手工音素表（5 个元音 + 1 个摩擦音）→ 音段序列 → 24 kHz 波形；
  2. 激励 = 120 Hz 脉冲串 + 一阶低通（模拟声门谱倾斜）；
  3. 声道 = 三阶级联共振峰谐振器（Klatt 型）+ 一阶差分（唇辐射）；
  4. 回收：自相关估 F0、平滑对数谱 + 抛物线插值找 F1/F2；
  5. 代理指标：三档带宽版本的 log 谱距离。

只依赖 numpy + matplotlib + 标准库 wave。不联网。
"""

import json
import os
import wave

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

SR = 24000                      # 与 §17.2.1 的 24 kHz 一致
F0 = 120.0                      # 基频，Hz
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- 音素表
# 元音：(名称, F1, F2, F3, 时长 ms)；摩擦音用噪声段表示
VOWELS = {
    "a":  (730.0, 1090.0, 2440.0),
    "i":  (270.0, 2290.0, 3010.0),
    "u":  (300.0,  870.0, 2240.0),
    "e":  (500.0, 1500.0, 2500.0),
}
SEGMENTS = [
    ("sil", None, 80),
    ("a", "a", 300),
    ("i", "i", 260),
    ("u", "u", 280),
    ("e", "e", 240),
    ("s", None, 110),
    ("a", "a", 300),
    ("sil", None, 70),
]
BANDWIDTH = (60.0, 90.0, 120.0)  # F1/F2/F3 的 -3dB 带宽，Hz


def resonator(x, f, bw):
    """二阶谐振器：y[n] = a0*x[n] + a1*y[n-1] + a2*y[n-2]"""
    r = np.exp(-np.pi * bw / SR)
    theta = 2.0 * np.pi * f / SR
    a1 = 2.0 * r * np.cos(theta)
    a2 = -r * r
    a0 = 1.0 - a1 - a2
    y = np.zeros_like(x)
    for n in range(len(x)):
        y[n] = a0 * x[n] + (a1 * y[n - 1] + a2 * y[n - 2] if n > 1 else 0.0)
    return y


def glottal_source(n, f0=F0):
    """脉冲串 + 一阶低通（-6 dB/oct 谱倾斜）"""
    x = np.zeros(n)
    period = SR / f0
    k = 0.0
    while k < n:
        x[int(round(k))] += 1.0
        k += period
    y = np.zeros(n)
    alpha = 0.9
    for i in range(1, n):
        y[i] = alpha * y[i - 1] + (1 - alpha) * x[i]
    return y * 30.0


def synth(bw_scale=1.0):
    """按 SEGMENTS 拼接，返回 (波形, 每个音段的 (起, 止, 名称))"""
    rng = np.random.default_rng(7)
    chunks, spans, pos = [], [], 0
    for name, vowel, ms in SEGMENTS:
        n = int(SR * ms / 1000)
        if vowel is None:
            if name == "sil":
                seg = np.zeros(n)
            else:                       # 摩擦音：白噪经 4.5 kHz 宽带谐振
                seg = resonator(rng.standard_normal(n), 4500.0, 2500.0) * 0.35
        else:
            src = glottal_source(n)
            f1, f2, f3 = VOWELS[vowel]
            seg = src
            for f, b in zip((f1, f2, f3), BANDWIDTH):
                seg = resonator(seg, f, b * bw_scale)
            seg = np.diff(seg, prepend=0.0)          # 唇辐射一阶差分
        chunks.append(seg)
        spans.append((pos, pos + n, name))
        pos += n
    wav = np.concatenate(chunks)
    wav /= np.max(np.abs(wav)) + 1e-12
    fade = int(0.005 * SR)
    wav[:fade] *= np.linspace(0, 1, fade)
    wav[-fade:] *= np.linspace(1, 0, fade)
    return wav, spans


def write_wav(path, wav):
    data = np.int16(np.clip(wav, -1, 1) * 32767)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


def est_f0(x, lo=60.0, hi=400.0):
    """归一化自相关估基频"""
    x = x - np.mean(x)
    ac = np.correlate(x, x, mode="full")[len(x) - 1:]
    ac /= (ac[0] + 1e-12)
    lag_lo, lag_hi = int(SR / hi), int(SR / lo)
    lag = lag_lo + int(np.argmax(ac[lag_lo:lag_hi]))
    return SR / lag, ac


def spectrum_peaks(x, nfft=8192, smooth_hz=120.0, fmax=3400.0, npeaks=2):
    """平滑对数幅度谱上的前 npeaks 个峰（抛物线插值）"""
    w = np.hanning(len(x))
    mag = np.abs(np.fft.rfft(x * w, n=nfft))
    freqs = np.fft.rfftfreq(nfft, 1.0 / SR)
    db = 20 * np.log10(mag + 1e-12)
    df = freqs[1] - freqs[0]
    k = max(1, int(smooth_hz / df))
    kernel = np.ones(k) / k
    sm = np.convolve(db, kernel, mode="same")
    idx = np.where((freqs > 200) & (freqs < fmax))[0]
    peaks = []
    for i in idx[1:-1]:
        if sm[i] > sm[i - 1] and sm[i] >= sm[i + 1] and sm[i] > -60:
            peaks.append((sm[i], i))
    peaks.sort(reverse=True)
    picked = []
    for _, i in peaks:
        if all(abs(freqs[i] - freqs[j]) > 180.0 for j in picked):
            picked.append(i)
        if len(picked) >= npeaks:
            break
    picked.sort()
    out = []
    for i in picked:
        left, right = sm[i - 1], sm[i + 1]
        denom = (left - 2 * sm[i] + right)
        delta = 0.5 * (left - right) / denom if abs(denom) > 1e-9 else 0.0
        out.append(float(freqs[i] + delta * df))
    while len(out) < npeaks:
        out.append(float("nan"))
    return out, freqs, sm


def log_spec_dist(x, y):
    """两段波形平滑对数谱的平均绝对差（dB），作为自动代理指标"""
    n = min(len(x), len(y))
    _, f1, s1 = spectrum_peaks(x[:n], npeaks=1)
    _, f2, s2 = spectrum_peaks(y[:n], npeaks=1)
    band = (f1 > 100) & (f1 < 6000)
    return float(np.mean(np.abs(s1[band] - s2[band])))


def main():
    wav, spans = synth(1.0)
    write_wav(os.path.join(OUT, "synth.wav"), wav)
    dur = len(wav) / SR

    # ---- 1. 基频回收（取第一个元音中段 40 ms）
    a_start, a_end, _ = spans[1]
    mid = (a_start + a_end) // 2
    seg = wav[mid - int(0.02 * SR): mid + int(0.02 * SR)]
    f0_hat, _ = est_f0(seg)

    # ---- 2. 共振峰回收（每个元音的稳态中段 40 ms）
    rows = []
    for idx, (name, vowel, ms) in enumerate(SEGMENTS):
        if vowel is None:
            continue
        s, e, _ = spans[idx]
        c = (s + e) // 2
        win = wav[c - int(0.02 * SR): c + int(0.02 * SR)]
        peaks, _, _ = spectrum_peaks(win)
        tgt = VOWELS[vowel]
        rows.append(
            dict(
                phoneme=f"{vowel}#{idx}",
                target_F1=tgt[0], meas_F1=round(peaks[0], 1),
                err_F1_pct=round(100 * (peaks[0] - tgt[0]) / tgt[0], 2),
                target_F2=tgt[1], meas_F2=round(peaks[1], 1),
                err_F2_pct=round(100 * (peaks[1] - tgt[1]) / tgt[1], 2),
            )
        )

    with open(os.path.join(OUT, "formant_check.csv"), "w", encoding="utf-8") as f:
        f.write("phoneme,target_F1,meas_F1,err_F1_pct,target_F2,meas_F2,err_F2_pct\n")
        for r in rows:
            f.write("{phoneme},{target_F1},{meas_F1},{err_F1_pct},{target_F2},{meas_F2},{err_F2_pct}\n".format(**r))

    # ---- 3. 三档带宽 + 自动代理指标（§17.4：代理指标不能替代人评）
    variants = {}
    for scale, tag in ((0.5, "narrow"), (1.0, "base"), (2.0, "wide")):
        w, _ = synth(scale)
        variants[tag] = w
        write_wav(os.path.join(OUT, f"synth_{tag}.wav"), w)
    proxy = {tag: round(log_spec_dist(variants["base"], w), 2)
             for tag, w in variants.items()}

    # ---- 4. 24 kHz → 75 Hz 的 320 倍对照（§17.2.1）
    frames_theory = int(round(dur * 75))
    metrics = dict(
        sample_rate=SR,
        duration_s=round(dur, 3),
        f0_target=F0,
        f0_measured=round(f0_hat, 2),
        f0_err_pct=round(100 * (f0_hat - F0) / F0, 2),
        downsample_factor=SR // 75,
        frames_theory_75hz=frames_theory,
        samples_per_frame=round(dur * SR / frames_theory, 2),
        frame_ms=round(1000 / 75, 2),
        mean_abs_err_F1_pct=round(float(np.mean([abs(r["err_F1_pct"]) for r in rows])), 2),
        mean_abs_err_F2_pct=round(float(np.mean([abs(r["err_F2_pct"]) for r in rows])), 2),
        max_abs_err_pct=round(max(max(abs(r["err_F1_pct"]), abs(r["err_F2_pct"])) for r in rows), 2),
        proxy_spectral_dist_db=proxy,
    )
    with open(os.path.join(OUT, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    # ---- 5. 图：波形 + 谱与回收峰
    fig, ax = plt.subplots(2, 1, figsize=(10, 5.5))
    t = np.arange(len(wav)) / SR
    ax[0].plot(t, wav, lw=0.4)
    for s, e, nm in spans:
        ax[0].axvspan(s / SR, e / SR, color="0.9" if nm != "sil" else "0.7", alpha=0.4)
        ax[0].text((s + e) / 2 / SR, 1.02, nm, ha="center", fontsize=8)
    ax[0].set_ylim(-1.15, 1.2)
    ax[0].set_xlabel("time (s)")
    ax[0].set_ylabel("amplitude")
    ax[0].set_title("synthesized waveform (24 kHz, F0=120 Hz, 5 formant segments)")
    _, f, sm = spectrum_peaks(seg)
    ax[1].plot(f, sm, lw=0.8)
    ax[1].set_xlim(0, 4000)
    ax[1].set_xlabel("frequency (Hz)")
    ax[1].set_ylabel("smoothed |X| (dB)")
    ax[1].set_title(f"vowel /a/ spectrum, recovered F0={f0_hat:.1f} Hz, F1/F2={rows[0]['meas_F1']:.0f}/{rows[0]['meas_F2']:.0f} Hz")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "spectrum.png"), dpi=130)
    plt.close(fig)

    print(f"duration={dur:.3f}s  F0_hat={f0_hat:.2f}Hz  frames@75Hz={frames_theory}")
    for r in rows:
        print(f"  {r['phoneme']}: F1 {r['target_F1']:.0f}->{r['meas_F1']:.1f} ({r['err_F1_pct']:+.2f}%)  "
              f"F2 {r['target_F2']:.0f}->{r['meas_F2']:.1f} ({r['err_F2_pct']:+.2f}%)")
    print("proxy spectral dist (dB):", proxy)


if __name__ == "__main__":
    main()
