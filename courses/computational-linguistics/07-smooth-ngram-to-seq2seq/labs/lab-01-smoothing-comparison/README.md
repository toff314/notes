# Lab 01 · 三种平滑方法的折扣率对比

> 验证：Laplace、Lidstone、Good-Turing 对同一词频分布的折扣效果差异。

## 运行

```bash
python3 run.py
```

## 输出

- 控制台打印：各方法对高频词、低频词、零频词的概率调整表
- `smoothing_comparison.png`：三种方法的"原始概率 vs 平滑后概率"散点图

## 原理

1. 构造 Zipf 分布模拟真实词频（V=1000，N=100000）
2. 分别用 Laplace（δ=1）、Lidstone（δ=0.1）、Good-Turing 平滑
3. 计算各方法对最高频词、中频词、零频词的概率调整幅度
4. 标出 N/V 临界点（加 1 平滑后概率不变的分界线）

## 关键观察

- Laplace 对高频词折扣最狠（可能掉 50%+）
- Lidstone δ 越小，折扣越温和
- Good-Turing 对零频词的分配与 N_1/N 相关
- 超过 N/V 的词在加 1 平滑后概率下降，低于 N/V 的上升
