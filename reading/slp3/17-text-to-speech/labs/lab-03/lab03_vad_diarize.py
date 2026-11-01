#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""lab-03：两说话人日志（VAD → 片段级嵌入 → 聚类），复现 §17.5 的流水线

对应 book-notes §17.5「先切出连续语音片段，再提说话人嵌入向量，再对这些向量聚类」。

数据：脚本内合成 11.8 秒两说话人交替音频（同一元音序列，只改基频与声道长度，
     模拟「同内容、不同嗓音」），在两档信噪比下各跑一次（20 dB / 8 dB 白噪）。

流水线（严格按书里的三步）：
  1. VAD：25 ms 帧 / 10 ms 跳，能量门限（噪声底 + 比例余量）；
  2. 片段嵌入：0.5 s 窗 / 0.25 s 跳，对窗内浊音帧取 F0、谱质心、低频能量比、谱平坦度的中位数；
  3. 聚类：k-means（k=2，10 次重启取最小惯性），再把窗标签回填到帧。
  评估：帧准确率、浊音召回、段落切换点平均绝对误差（ms）。

只依赖 numpy + matplotlib + 标准库 wave。不联网。
"""

import json
import os
import wave

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

SR = 16000
WIN = int(0.025 * SR)
HOP = int(0.010 * SR)
SEG = int(0.50 * SR)
SEG_HOP = int(0.25 * SR)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

SPEAKERS = {"A": dict(f0=110.0, scale=1.00), "B": dict(f0=205.0, scale=1.15)}
VOWELS = [(730.0, 1090.0, 2440.0), (270.0, 2290.0, 3010.0), (300.0, 870.0, 2240.0)]
TURN_S, GAP_S = 1.0, 0.2
ORDER = ["A", "B", "A", "B", "A", "B", "A", "B", "A", "B"]


def resonator(x, f, bw):
    r = np.exp(-np.pi * bw / SR)
    th = 2 * np.pi * f / SR
    a1, a2 = 2 * r * np.cos(th), -r * r
    a0 = 1 - a1 - a2
    y = np.zeros_like(x)
    for n in range(len(x)):
        y[n] = a0 * x[n] + (a1 * y[n - 1] + a2 * y[n - 2] if n > 1 else 0.0)
    return y


def pulse_train(n, f0):
    x = np.zeros(n)
    k = 0.0
    while k < n:
        x[int(round(k))] = 1.0
        k += SR / f0
    y = np.zeros(n)
    for i in range(1, n):
        y[i] = 0.9 * y[i - 1] + 0.1 * x[i]
    return y * 25.0


def make_audio(noise_snr_db):
    chunks, truth, pos = [], [], 0
    for turn_i, spk in enumerate(ORDER):
        cfg = SPEAKERS[spk]
        n_turn = int(TURN_S * SR)
        seg = np.zeros(n_turn)
        per = n_turn // len(VOWELS)
        for vi, f in enumerate(VOWELS):
            s = vi * per
            e = n_turn if vi == len(VOWELS) - 1 else (vi + 1) * per
            src = pulse_train(e - s, cfg["f0"])[: e - s]
            y = src
            for fr, bw in zip(f, (60.0, 90.0, 120.0)):
                y = resonator(y, fr * cfg["scale"], bw)
            y = np.diff(y, prepend=0.0)
            seg[s:e] = y
        seg /= np.max(np.abs(seg)) + 1e-12
        chunks.append(seg * 0.7)
        truth.append((pos, pos + n_turn, spk))
        pos += n_turn
        if turn_i < len(ORDER) - 1:
            g = np.zeros(int(GAP_S * SR))
            chunks.append(g)
            truth.append((pos, pos + len(g), "-"))
            pos += len(g)
    wav = np.concatenate(chunks)
    rng = np.random.default_rng(3)
    p_speech = np.mean(wav[wav != 0] ** 2)
    p_noise = p_speech / (10 ** (noise_snr_db / 10))
    return wav + rng.normal(0, np.sqrt(p_noise), len(wav)), truth


def est_f0(f, lo=70.0, hi=350.0):
    f = f - f.mean()
    if np.sqrt(np.mean(f ** 2)) < 1e-5:
        return 0.0
    ac = np.correlate(f, f, mode="full")[len(f) - 1:]
    ac = ac / (ac[0] + 1e-12)
    a, b = int(SR / hi), int(SR / lo)
    lag = a + int(np.argmax(ac[a:b]))
    return SR / lag


def frame_feats(wav):
    n = 1 + (len(wav) - WIN) // HOP
    idx = np.arange(WIN)[None, :] + HOP * np.arange(n)[:, None]
    fr = wav[idx]
    rms_db = 20 * np.log10(np.sqrt(np.mean(fr ** 2, axis=1)) + 1e-10)
    spec = np.abs(np.fft.rfft(fr * np.hanning(WIN), axis=1))
    freqs = np.fft.rfftfreq(WIN, 1 / SR)
    power = spec ** 2 + 1e-12
    centroid = (power * freqs).sum(1) / power.sum(1)
    low = power[:, (freqs >= 100) & (freqs < 1000)].sum(1)
    high = power[:, (freqs >= 1000) & (freqs < 5000)].sum(1)
    low_ratio = low / (low + high + 1e-12)
    flat = np.exp(np.mean(np.log(power), 1)) / (np.mean(power, 1) + 1e-12)
    f0 = np.array([est_f0(f) for f in fr])
    return np.stack([rms_db, f0, centroid, low_ratio, flat], 1), n


def kmeans(x, k=2, restarts=10, seed=0):
    rng = np.random.default_rng(seed)
    best = None
    for _ in range(restarts):
        cb = x[rng.choice(len(x), size=k, replace=False)].copy()
        lab = np.zeros(len(x), dtype=int)
        for _ in range(80):
            d = ((x[:, None, :] - cb[None]) ** 2).sum(-1)
            lab = d.argmin(1)
            new = np.array([x[lab == j].mean(0) if (lab == j).any() else cb[j] for j in range(k)])
            if np.allclose(new, cb):
                break
            cb = new
        inertia = float(((x - cb[lab]) ** 2).sum())
        if best is None or inertia < best[0]:
            best = (inertia, lab.copy())
    return best[1]


def run(noise_snr_db, tag):
    wav, truth = make_audio(noise_snr_db)
    feats, nfr = frame_feats(wav)
    rms = feats[:, 0]

    floor = max(np.percentile(rms, 10), np.percentile(rms, 95) - 45)
    thr = floor + 0.40 * (np.percentile(rms, 95) - floor)
    voiced = rms > thr

    t = np.arange(nfr) * HOP / SR
    truth_lab = np.array([next((s for s, e, s_ in truth if s / SR <= tt < e / SR), "-") for tt in t])

    # ---- 片段级嵌入（0.5 s 窗 / 0.25 s 跳）
    starts = list(range(0, max(1, nfr - SEG // HOP) + 1, SEG_HOP // HOP))
    win_feat, win_span = [], []
    for s in starts:
        e = min(nfr, s + SEG // HOP)
        m = voiced[s:e]
        if m.sum() < 12:                       # 浊音太少，视为静音窗
            continue
        blk = feats[s:e][m]
        win_feat.append([np.median(blk[:, 1]), np.median(blk[:, 2]),
                         np.median(blk[:, 3]), np.median(blk[:, 4]), m.mean()])
        win_span.append((s, e))
    X = np.array(win_feat)
    Xs = (X - X.mean(0)) / (X.std(0) + 1e-9)
    lab_w = kmeans(Xs)

    # ---- 窗标签回填到帧（重叠窗取中心最近者）
    centers = np.array([(s + e) / 2 for s, e in win_span])
    wl = np.array(["?"] * nfr, dtype=object)
    for i in range(nfr):
        j = int(np.argmin(np.abs(centers - i)))
        wl[i] = lab_w[j]

    # 簇 → 说话人（按真值多数）
    mapping = {}
    for c in (0, 1):
        vals = truth_lab[(wl == c) & (truth_lab != "-")]
        mapping[c] = max(set(vals.tolist()), key=vals.tolist().count) if len(vals) else "-"
    pred = np.array([mapping[c] for c in wl])

    # 多数平滑，抑制边界抖动
    sm = pred.copy()
    h = 15
    for i in range(nfr):
        seg = pred[max(0, i - h): i + h + 1]
        vals, cnt = np.unique(seg[seg != "-"], return_counts=True)
        if len(vals):
            sm[i] = vals[cnt.argmax()]

    speech = truth_lab != "-"
    acc = float((sm[speech] == truth_lab[speech]).mean())
    recall = float((voiced & speech).sum() / speech.sum())
    fa = float((voiced & ~speech).sum() / max(1, (~speech).sum()))

    true_b = [(truth[i][1] + truth[i + 1][0]) / 2 / SR for i in range(len(truth) - 1)
              if truth[i][2] != "-" and truth[i + 1][2] != "-" and truth[i][2] != truth[i + 1][2]]
    pred_b = [i * HOP / SR for i in range(1, nfr) if sm[i] != sm[i - 1]]
    errs = [abs(min(pred_b, key=lambda p: abs(p - b)) - b) * 1000 for b in true_b] if pred_b else []
    bmae = float(np.mean(errs)) if errs else float("nan")

    stats = dict(noise_snr_db=noise_snr_db, n_frames=nfr, voiced_frames=int(voiced.sum()),
                 threshold_db=round(float(thr), 2), n_windows=len(win_span),
                 frame_accuracy=round(acc, 4), vad_recall=round(recall, 4),
                 vad_false_alarm=round(fa, 4), true_switches=len(true_b),
                 pred_switch_points=len(pred_b), boundary_mae_ms=round(bmae, 1),
                 boundary_errs_ms=[round(x) for x in errs])
    print(f"[{tag}] thr={thr:.1f}dB voiced={voiced.sum()}/{nfr} win={len(win_span)} "
          f"acc={acc:.3f} recall={recall:.3f} bMAE={bmae:.0f}ms errs={[round(x) for x in errs]}")

    rows = [(round(t[i], 3), round(float(rms[i]), 2), round(float(feats[i, 1]), 1),
             round(float(feats[i, 2]), 0), round(float(feats[i, 3]), 3), truth_lab[i],
             int(voiced[i]), str(sm[i])) for i in range(nfr)]
    return dict(tag=tag, wav=wav, t=t, f0=feats[:, 1], rows=rows, stats=stats,
                truth=truth_lab, pred=sm)


def write_wav(path, wav):
    data = np.int16(np.clip(wav / (np.max(np.abs(wav)) + 1e-9), -1, 1) * 32767)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(data.tobytes())


def main():
    res = [run(20.0, "snr20"), run(8.0, "snr8")]
    write_wav(os.path.join(OUT, "mix_snr20.wav"), res[0]["wav"])
    write_wav(os.path.join(OUT, "mix_snr8.wav"), res[1]["wav"])

    with open(os.path.join(OUT, "diarization_frames.csv"), "w", encoding="utf-8") as f:
        f.write("cond,t_s,rms_db,f0_hz,centroid_hz,low_ratio,truth,vad,pred\n")
        for r in res:
            for row in r["rows"]:
                f.write(r["tag"] + "," + ",".join(map(str, row)) + "\n")

    summary = dict(speakers=SPEAKERS, turn_order=ORDER, turn_s=TURN_S, gap_s=GAP_S,
                   conditions=[r["stats"] for r in res],
                   note="frame_accuracy 以真值语音帧为分母；VAD 漏检计为错误；窗长 0.5 s，跳 0.25 s")
    with open(os.path.join(OUT, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    fig, ax = plt.subplots(2, 1, figsize=(10, 5.6), sharex=True)
    for i, r in enumerate(res):
        col = np.where(r["pred"] == "B", "tab:red", np.where(r["pred"] == "A", "tab:blue", "0.85"))
        ax[i].scatter(r["t"], r["f0"], c=col, s=4)
        for b in [s for s, e, spk in [(0, 0, 0)] for s in []]:
            pass
        ax[i].set_ylabel("F0 (Hz)")
        ax[i].set_title(f"{r['tag']}: F0 track colored by predicted speaker, "
                        f"frame acc={r['stats']['frame_accuracy']:.3f}, "
                        f"boundary MAE={r['stats']['boundary_mae_ms']:.0f} ms")
    ax[1].set_xlabel("time (s)")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "frames.png"), dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    main()
