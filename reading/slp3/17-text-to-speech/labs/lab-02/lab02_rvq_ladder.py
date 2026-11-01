#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""lab-02：矢量量化 → 残差矢量量化（RVQ）逐级残差衰减

对应 book-notes §17.2.2（k-means / 码本 / k 的选择）、§17.2.3（8 级残差、码字相加）、
§17.2.4（码本初始化影响首级残差）、§17.2（词元率与注意力平方开销）。

数据：不下载语音库。用固定随机种子生成具有簇结构的 256 维帧特征（D=256 与 §17.2.1 一致），
     模拟 ENCODEC 编码器输出的嵌入分布：6 个隐成分的稀疏混合 + 时间平滑漂移 + 噪声。

跑四件事：
  1. 单级 VQ：k 从 16 扫到 256，看重构 SNR 与「从未被用到的码字」比例；
  2. RVQ：8 级、每级 k=64，逐级记录残差 MSE / 累计 SNR / 第一级解释的信息占比；
  3. 码本初始化对照：随机取样 vs k-means++，比较空簇数与首级 MSE；
  4. 词元率账：16 kHz 采样点 / 75×8=600 词元每秒 / 75 帧每秒 的序列长度与注意力平方开销。

只依赖 numpy + matplotlib。
"""

import json
import os

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)
RNG = np.random.default_rng(20261031)

D = 256          # 嵌入维度
N = 4000         # 帧数（约 53 秒 @75 Hz）
N_COMP = 6       # 粗成分个数
N_FINE = 24      # 细成分个数


def make_embeddings(n=N, d=D, seed=0):
    """簇结构的帧嵌入：粗成分（音段内容）+ 细成分（音色/细节）+ 小噪声

    模仿真实语音嵌入的层级结构：少量大能量的粗成分决定「说的是什么」，
    大量小能量的细成分承载音色与协同发音，二者都可被量化，残差才有得学。
    """
    rng = np.random.default_rng(seed)
    # 粗成分：能量大、数量少
    coarse = rng.standard_normal((N_COMP, d)) * 1.0
    probs = np.array([0.35, 0.25, 0.15, 0.12, 0.08, 0.05])
    idx = rng.choice(N_COMP, size=n, p=probs)
    c_coef = np.zeros((n, N_COMP))
    c_coef[np.arange(n), idx] = 1.0
    for t in range(1, n):
        c_coef[t] = 0.75 * c_coef[t] + 0.25 * c_coef[t - 1]
    x = c_coef @ coarse

    # 细成分：能量小、数量多、逐帧独立
    fine = rng.standard_normal((N_FINE, d)) * 0.32
    f_coef = (rng.random((n, N_FINE)) < 0.12) * rng.random((n, N_FINE))
    x = x + f_coef @ fine

    x += 0.10 * rng.standard_normal((n, d))           # 不可量化的帧内噪声
    x += 0.08 * np.sin(np.arange(n)[:, None] / 50.0)  # 缓慢漂移
    return x


def kmeans(x, k, iters=25, init="random", seed=0):
    """最简 k-means；返回 (码本, 标签, 空簇数)"""
    rng = np.random.default_rng(seed)
    if init == "kmeans++":
        cb = [x[rng.integers(len(x))]]
        d2 = ((x - cb[0]) ** 2).sum(1)
        for _ in range(1, k):
            p = d2 / (d2.sum() + 1e-12)
            cb.append(x[rng.choice(len(x), p=p)])
            d2 = np.minimum(d2, ((x - cb[-1]) ** 2).sum(1))
        cb = np.array(cb)
    else:
        cb = x[rng.choice(len(x), size=k, replace=False)].copy()
    for _ in range(iters):
        d = ((x[:, None, :] - cb[None, :, :]) ** 2).sum(-1) if k <= 32 else \
            (x ** 2).sum(1)[:, None] - 2 * x @ cb.T + (cb ** 2).sum(1)[None, :]
        lab = d.argmin(1)
        for j in range(k):
            m = lab == j
            if m.any():
                cb[j] = x[m].mean(0)
    lab = (((x ** 2).sum(1)[:, None] - 2 * x @ cb.T + (cb ** 2).sum(1)[None, :])).argmin(1)
    used = len(np.unique(lab))
    return cb, lab, k - used


def snr_db(x, xhat):
    mse = float(np.mean((x - xhat) ** 2))
    return 10 * np.log10(float(np.mean(x ** 2)) / (mse + 1e-12)), mse


def main():
    x = make_embeddings()
    base_mse = float(np.mean((x - x.mean(0)) ** 2))     # 全用均值重建的基线
    print(f"data: {x.shape}, var={np.mean(x**2):.4f}, baseline_mse={base_mse:.4f}")

    # ---- 1. 单级 VQ：k 扫描
    scan = []
    for k in (16, 32, 64, 128, 256):
        cb, lab, empty = kmeans(x, k, iters=12)
        snr, mse = snr_db(x, cb[lab])
        scan.append(dict(k=k, mse=round(mse, 4), snr_db=round(snr, 2),
                         unused_ratio=round(empty / k, 3), iters=12))
        print(f"  VQ k={k:3d}: mse={mse:.4f} snr={snr:6.2f} dB unused={empty/k:.1%}")

    # ---- 2. RVQ：8 级 × k=64
    STAGES, K = 8, 64
    resid = x.copy()
    cum = np.zeros_like(x)
    stages = []
    for s in range(1, STAGES + 1):
        cb, lab, empty = kmeans(resid, K, iters=12)
        q = cb[lab]
        resid = resid - q
        cum = cum + q
        snr, mse_cum = snr_db(x, cum)
        stage_mse = float(np.mean(resid ** 2))
        stages.append(dict(stage=s, residual_mse=round(stage_mse, 5),
                           cum_mse=round(mse_cum, 5), cum_snr_db=round(snr, 2),
                           unused_ratio=round(empty / K, 3)))
        print(f"  RVQ stage {s}: resid_mse={stage_mse:.5f} cum_snr={snr:6.2f} dB")

    info_share = 1.0 - stages[0]["cum_mse"] / base_mse
    drop_ratio = [round(stages[i - 1]["residual_mse"] / stages[i]["residual_mse"], 2)
                  for i in range(1, len(stages))]

    # ---- 3. 初始化对照（固定 k=64，单级）
    init_rows = []
    for init in ("random", "kmeans++"):
        cb, lab, empty = kmeans(x, 64, iters=12, init=init, seed=11)
        snr, mse = snr_db(x, cb[lab])
        init_rows.append(dict(init=init, empty_clusters=empty,
                              mse=round(mse, 4), snr_db=round(snr, 2)))
    print("  init:", init_rows)

    # ---- 4. 词元率账（§17.2）
    rates = dict(samples_16k=16000, frames_75hz=75, tokens_8x75=600)
    ratio_vs_frames = rates["tokens_8x75"] / rates["frames_75hz"]
    attn = {name: (r / rates["tokens_8x75"]) ** 2 for name, r in rates.items()}
    rate_block = dict(rates=rates,
                      seq_len_ratio_to_tokens={k: round(v / 600, 2) for k, v in rates.items()},
                      attn_cost_ratio_squared={k: round(v, 2) for k, v in attn.items()},
                      rmq_stage1_attn_saving=round(1 - 1 / ratio_vs_frames ** 2, 4))

    summary = dict(
        n_frames=N, dim=D, n_components=N_COMP,
        baseline_mse=round(base_mse, 4),
        vq_scan=scan,
        rvq=dict(stages=stages, info_share_stage1=round(info_share, 4),
                 residual_drop_ratio=drop_ratio,
                 final_snr_db=stages[-1]["cum_snr_db"]),
        init_compare=init_rows,
        token_rate=rate_block,
    )
    with open(os.path.join(OUT, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    with open(os.path.join(OUT, "rvq_stages.csv"), "w", encoding="utf-8") as f:
        f.write("stage,residual_mse,cum_mse,cum_snr_db,unused_ratio\n")
        for r in stages:
            f.write(f"{r['stage']},{r['residual_mse']},{r['cum_mse']},{r['cum_snr_db']},{r['unused_ratio']}\n")

    with open(os.path.join(OUT, "vq_k_scan.csv"), "w", encoding="utf-8") as f:
        f.write("k,mse,snr_db,unused_ratio\n")
        for r in scan:
            f.write(f"{r['k']},{r['mse']},{r['snr_db']},{r['unused_ratio']}\n")

    # ---- 图：残差衰减 + k 扫描
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    st = [r["stage"] for r in stages]
    ax[0].plot(st, [r["residual_mse"] for r in stages], "o-", label="residual MSE after stage s")
    ax[0].plot(st, [r["cum_mse"] for r in stages], "s--", label="reconstruction MSE (cumulative)")
    ax[0].set_yscale("log")
    ax[0].set_xlabel("RVQ stage")
    ax[0].set_ylabel("MSE (log)")
    ax[0].set_title("residual decays, reconstruction saturates")
    ax[0].legend(fontsize=8)
    ax[0].grid(alpha=0.3)

    ks = [r["k"] for r in scan]
    ax[1].plot(ks, [r["snr_db"] for r in scan], "o-", label="SNR (dB)")
    ax2 = ax[1].twinx()
    ax2.plot(ks, [r["unused_ratio"] for r in scan], "rx--", label="unused codeword ratio")
    ax2.set_ylabel("unused codeword ratio", color="r")
    ax[1].set_xscale("log", base=2)
    ax[1].set_xlabel("codebook size k")
    ax[1].set_ylabel("SNR (dB)")
    ax[1].set_title("one-stage VQ: bigger k, diminishing SNR")
    ax[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "residual_decay.png"), dpi=130)
    plt.close(fig)

    print(f"info_share_stage1={info_share:.3%}  final_snr={stages[-1]['cum_snr_db']} dB")
    print("rate block:", json.dumps(rate_block, ensure_ascii=False))


if __name__ == "__main__":
    main()
