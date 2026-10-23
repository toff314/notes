# labs 索引：行动执行闭环

> `actions.md` 是「要做什么」，本目录是「真的做了」。每个 lab 一个子目录，编号与 `actions.md` 对齐。
> 运行环境：Python 3.12，标准库 + numpy 2.4.6 + matplotlib 3.10.9；三个脚本均于 **2026-10-21** 重新运行，退出码 0。

## 覆盖表

| 行动 | 主题 | Lab | 脚本 | 主要产物 | 状态 |
|---|---|---|---|---|---|
| actions.md #1 | Bradley–Terry 奖励模型 + 捷径反转测试 | `lab-01/` | `bradley_terry_rm.py` | `metrics.json`、`loss_curve.png`、`weight_recovery.png` | ✅ 已运行 |
| actions.md #2 | DPO 的 β：损失、隐式奖励、KL 轨迹 | `lab-02/` | `dpo_beta.py` | `metrics.json`、`beta_curve.png`、`kl_optimum.png`、`kl_trajectory.png` | ✅ 已运行 |
| actions.md #3 | best-of-N 的噪声上限 | `lab-03/` | `best_of_n.py` | `metrics.json`、`best_of_n.csv`、`best_of_n.png` | ✅ 已运行 |

## lab-01：用成对偏好训练奖励模型

- **对应行动**：`actions.md` #1；对应原文 §8.3.2、§8.3.3、§8.4。
- **运行**：
  ```bash
  cd labs/lab-01 && python3 bradley_terry_rm.py
  ```
- **产物**：`out/metrics.json`、`out/loss_history.csv`、`out/loss_curve.png`、`out/weight_recovery.png`。
- **结论**：干净特征下学到权重与真实权重余弦相似度 0.9984，测试准确率 0.765（Bayes 上限约 0.775）；注入长度捷径后训练准确率 0.9995、反转相关性测试掉到 0.007。奖励模型学的是「与赢共现的特征」，不是「质量」。
- **反思**：反转后准确率不是 0.5 而是 0.007，因为常量长度差把整批 margin 平移；pairwise accuracy 会混淆「常量偏移」与「排序错误」。详见 `lab-01/README.md`。

## lab-02：DPO 的 β 双重角色

- **对应行动**：`actions.md` #2；对应原文 §8.4 式 8.7、§8.4.2。
- **运行**：
  ```bash
  cd labs/lab-02 && python3 dpo_beta.py
  ```
- **产物**：`out/metrics.json`、`out/beta_curve.csv`、`out/beta_curve.png`、`out/beta_optimum.csv`、`out/kl_optimum.png`、`out/kl_trajectory.png`。
- **结论**：固定 margin 时有效梯度峰值在 β≈3.23；闭式最优下 β 越大越贴近参考策略（KL 0.474→0.00115），但最优点的 DPO 损失恒为 0.3133；单个可分对上 β=0.01 与 0.1 的 KL 终点同为 0.78734，β 改的是速度不是端点。
- **反思**：β 不是 KL 硬预算，它同时缩放隐式奖励与 sigmoid 温度；只比较 loss 曲线会看不出 β 的分布效应。详见 `lab-02/README.md`。

## lab-03：best-of-N 的收益与噪声

- **对应行动**：`actions.md` #3；对应原文 §8.3.3、§8.4。
- **运行**：
  ```bash
  cd labs/lab-03 && python3 best_of_n.py
  ```
- **产物**：`out/metrics.json`、`out/best_of_n.csv`、`out/best_of_n.png`。
- **结论**：σ=0 时 N 越大严格越好；σ=0.5 时 N=2→128，期望真实质量 0.507→2.332，但 P(选中真最优) 0.853→0.460，奖励高估 0.125→0.570；σ=2、N=128 时高估达 4.657。
- **反思**：best-of-N 是「用算力换质量 + 用选择偏差换奖励高估」的交易，上线前应先测奖励噪声，而不是先调大 N。详见 `lab-03/README.md`。

## 复现说明

1. 三个脚本都只写自己的 `out/`，不修改笔记文件；重复运行会覆盖同名产物。
2. 随机性：lab-01 `SEED=8`、lab-03 `SEED=11`；lab-02 为确定性解析/数值计算。
3. 若需从零验证，可先删除各 `out/` 再运行；本文档中的数字均来自 2026-10-21 的实际运行结果。
