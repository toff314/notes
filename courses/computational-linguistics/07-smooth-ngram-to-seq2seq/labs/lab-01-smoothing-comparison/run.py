#!/usr/bin/env python3
"""Lab 01: 三种平滑方法的折扣率对比"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# 构造 Zipf 分布模拟真实词频
V = 1000  # 词表大小
N = 100000  # 总词数

# Zipf 分布：rank^-1
ranks = np.arange(1, V + 1)
zipf = 1.0 / ranks
zipf /= zipf.sum()
counts = (zipf * N).astype(int)
counts[0] = N - counts[1:].sum()  # 调整使总和为 N

# 原始概率
probs_orig = counts / N

def laplace(counts, N, V, delta=1.0):
    """Laplace/Lidstone 平滑"""
    return (counts + delta) / (N + delta * V)

def good_turing(counts, N):
    """简化版 Good-Turing 平滑（只用 N_c 统计）"""
    from collections import Counter
    freq_of_freq = Counter(counts.tolist())
    smoothed = np.zeros_like(counts, dtype=float)
    for i, c in enumerate(counts):
        if c == 0:
            # 零频词用 N_1/N 估计
            smoothed[i] = freq_of_freq.get(1, 0) / N / V
        else:
            # c* = (c+1) * N_{c+1} / N_c
            nc = freq_of_freq.get(c, 0)
            nc1 = freq_of_freq.get(c + 1, 0)
            if nc > 0 and nc1 > 0:
                c_star = (c + 1) * nc1 / nc
            else:
                c_star = c
            smoothed[i] = c_star / N
    # 归一化
    smoothed /= smoothed.sum()
    return smoothed

# 三种平滑
probs_laplace = laplace(counts, N, V, delta=1.0)
probs_lidstone = laplace(counts, N, V, delta=0.1)
probs_gt = good_turing(counts, N)

# 打印对比表
print("=" * 70)
print(f"{'方法':<12} {'最高频词':<12} {'中频词':<12} {'零频词':<12} {'总和'}")
print("-" * 70)

# 最高频词（rank 1）、中频词（rank 500）、零频词（假设有一个）
top_idx = 0
mid_idx = V // 2

# 找一个零频词（如果存在）
zero_idx = None
for i, c in enumerate(counts):
    if c == 0:
        zero_idx = i
        break
if zero_idx is None:
    # 构造一个零频词
    counts = np.append(counts, 0)
    probs_orig = np.append(probs_orig, 0.0)
    probs_laplace = laplace(counts, N, V, delta=1.0)
    probs_lidstone = laplace(counts, N, V, delta=0.1)
    probs_gt = good_turing(counts, N)
    zero_idx = len(counts) - 1

for name, probs in [("原始", probs_orig), ("Laplace", probs_laplace),
                     ("Lidstone", probs_lidstone), ("Good-Turing", probs_gt)]:
    print(f"{name:<12} {probs[top_idx]:<12.6f} {probs[mid_idx]:<12.6f} {probs[zero_idx]:<12.6f} {probs.sum():.4f}")

print("-" * 70)
print(f"N/V 临界点 = {N/V:.2f}")
print(f"原始最高频词计数 = {counts[top_idx]}, 平滑后概率变化 = {(probs_laplace[top_idx]-probs_orig[top_idx])/probs_orig[top_idx]*100:.1f}%")

# 绘图
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

methods = [("Laplace", probs_laplace, 'red'),
           ("Lidstone(δ=0.1)", probs_lidstone, 'blue'),
           ("Good-Turing", probs_gt, 'green')]

for ax, (name, probs, color) in zip(axes, methods):
    ax.scatter(probs_orig + 1e-10, probs + 1e-10, alpha=0.3, s=1, c=color)
    ax.plot([1e-10, 0.01], [1e-10, 0.01], 'k--', alpha=0.5, label='y=x')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Original Probability')
    ax.set_ylabel('Smoothed Probability')
    ax.set_title(name)
    ax.legend()

# 标出临界点
N_V = N / V
for ax in axes:
    ax.axvline(x=N_V/N, color='gray', linestyle=':', alpha=0.5, label=f'N/V={N_V:.0f}')

plt.tight_layout()
plt.savefig('smoothing_comparison.png', dpi=150)
print("\n图已保存: smoothing_comparison.png")
