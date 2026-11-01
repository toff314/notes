#!/usr/bin/env python3
"""Lab 02: 梯度消失/爆炸的数值模拟"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# 模拟不同梯度值在时间步上的连乘
T = 100  # 时间步
gradients = [0.9, 0.99, 1.0, 1.01, 1.1]
colors = ['red', 'orange', 'green', 'blue', 'purple']

# 计算连乘
results = {}
for g in gradients:
    results[g] = [g**t for t in range(T)]

# 打印关键数值
print("=" * 60)
print("梯度连乘模拟：g^t")
print("-" * 60)
print(f"{'时间步':<8}", end="")
for g in gradients:
    print(f"{g:<12}", end="")
print()
print("-" * 60)

for t in [0, 10, 25, 50, 75, 100]:
    if t < T:
        print(f"{t:<8}", end="")
        for g in gradients:
            val = results[g][t]
            if val < 0.001:
                print(f"{val:<12.2e}", end="")
            elif val > 1000:
                print(f"{val:<12.2e}", end="")
            else:
                print(f"{val:<12.4f}", end="")
        print()

print("-" * 60)
print(f"0.9^50 = {0.9**50:.6f} (几乎消失)")
print(f"1.1^50 = {1.1**50:.2f} (已经爆炸)")

# 绘图
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# 左图：正常尺度
for g, color in zip(gradients, colors):
    ax1.plot(range(T), results[g], label=f'g={g}', color=color, linewidth=2)
ax1.set_xlabel('Time Step (t)')
ax1.set_ylabel('Gradient Value')
ax1.set_title('Gradient: Linear Scale')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.axhline(y=1.0, color='black', linestyle='--', alpha=0.5)

# 右图：对数尺度
for g, color in zip(gradients, colors):
    ax2.semilogy(range(T), results[g], label=f'g={g}', color=color, linewidth=2)
ax2.set_xlabel('Time Step (t)')
ax2.set_ylabel('Gradient Value (log)')
ax2.set_title('Gradient: Log Scale')
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.axhline(y=1.0, color='black', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig('gradient_vanish_explode.png', dpi=150)
print("\n图已保存: gradient_vanish_explode.png")

# 附加：模拟 RNN 中的梯度流
print("\n" + "=" * 60)
print("RNN 梯度流模拟：带 tanh 激活")
print("-" * 60)

# 模拟一个简单 RNN 的梯度流
# h_t = tanh(W_h * h_{t-1} + W_x * x_t)
# 梯度 = W_h^T * diag(tanh'(h_t)) * ...

np.random.seed(42)
hidden_dim = 10
W_h = np.random.randn(hidden_dim, hidden_dim) * 0.1  # 小权重

# 计算 Jacobian 的特征值
eigenvalues = np.linalg.eigvals(W_h)
spectral_radius = max(abs(eigenvalues))
print(f"W_h 谱半径 = {spectral_radius:.4f}")

# 模拟 100 步的梯度连乘
gradients_rnn = []
grad = np.eye(hidden_dim)
for t in range(100):
    # 随机一个 tanh 导数（0~1 之间）
    tanh_grad = np.diag(np.random.rand(hidden_dim) * 0.5 + 0.5)
    grad = grad @ W_h.T @ tanh_grad
    grad_norm = np.linalg.norm(grad)
    gradients_rnn.append(grad_norm)

print(f"100 步后梯度范数 = {gradients_rnn[-1]:.6f}")
print(f"前 10 步梯度范数: {[f'{g:.4f}' for g in gradients_rnn[:10]]}")

# 绘制 RNN 梯度流
fig, ax = plt.subplots(figsize=(8, 5))
ax.semilogy(range(100), gradients_rnn, 'b-', linewidth=2)
ax.set_xlabel('Time Step')
ax.set_ylabel('Gradient Norm (log)')
ax.set_title('RNN Gradient Flow (with tanh)')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('rnn_gradient_flow.png', dpi=150)
print("图已保存: rnn_gradient_flow.png")
