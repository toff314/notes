# 行动执行闭环（labs/index.md）

> `actions.md` 的每条行动都在这里落成**可运行脚本 + 真实产物 + 结论 + 反思**。
> 所有数字来自本机实际运行（Python 3 / numpy 2.4.6 / matplotlib 3.10.9），可复跑；脚本只依赖标准库与 numpy/matplotlib。

| 行动 | 脚本 | 运行产物 | 一句话结论 | 反思入口 |
|---|---|---|---|---|
| 1. 从零实现 XOR 网络与梯度校验 | `lab-01/xor_mlp.py` | `lab-01/out/summary.json`、`gradient_check.json`、`loss_history.csv`、`loss_curve.png`、`decision_boundary.png` | 2-8-1 网络 4000 轮后准确率 1.0、损失 7.6e-4；有限差分相对误差 4.45e-10 | [lab-01/README.md](lab-01/README.html) |
| 2. 随机嵌入 vs 共现嵌入 | `lab-02/embedding_mlp.py` | `lab-02/out/metrics.json`、`predictions.csv`、`confusion_matrix.csv`、`accuracy.png`、`embedding_pca.png` | 同一分类器只换嵌入，held-out 准确率从 0.315 升到 0.995 | [lab-02/README.md](lab-02/README.html) |
| 3. 逐层梯度范数与梯度消失 | `lab-03/gradient_vanishing.py` | `lab-03/out/gradient_norms.csv`、`gradient_norms.png`、`decision_boundary.png`、`summary.json` | 10 层 sigmoid 首层梯度 4.23e-7、准确率 0.4875；ReLU/tanh 均 1.000 | [lab-03/README.md](lab-03/README.html) |

## 与 actions.md 的对应

1. **行动 1 → lab-01**：2-8-1 前向/反向手写、XOR 训练、损失曲线、决策边界、6 个参数的有限差分校验。验收项全部落在 `summary.json` 与 `gradient_check.json`。
2. **行动 2 → lab-02**：构造 240 条训练句 + 200 条 held-out 测试句，冻结随机/共现两种 16 维嵌入，同一 MLP 对照；产物含准确率、混淆矩阵、最近邻与 PCA 图。
3. **行动 3 → lab-03**：2-24×10-1 网络，分别用 sigmoid/tanh/ReLU 训练，逐层记录梯度范数与测试准确率，产物含 CSV 与对数坐标图。

## 复跑方式

```bash
cd labs
for d in lab-01 lab-02 lab-03; do (cd "$d" && python3 *.py); done
```

单跑某个实验时进入对应目录执行同名脚本即可；每个脚本都会覆盖自己的 `out/` 产物，结果由固定种子保证可复现。

## 输入与可复现性

- lab-01 的数据就是 XOR 四个点（硬编码），无外部输入。
- lab-02 的语料由脚本按固定模板生成（`build_dataset` / `build_corpus`），测试句严格使用训练中未出现的情感词，且不进入共现语料；这是"留出词"对照，不是随机划分。
- lab-03 的 two moons 由脚本用固定种子生成。
- 三张图都用 matplotlib 默认字体渲染英文标签；CSV/JSON 为 UTF-8，浮点数保留 6–10 位有效数字。

## 覆盖核对

- [x] 行动 1 → lab-01（脚本、JSON/CSV、两张 PNG、结论、反思）
- [x] 行动 2 → lab-02（脚本、JSON/CSV、两张 PNG、结论、反思）
- [x] 行动 3 → lab-03（脚本、JSON/CSV、两张 PNG、结论、反思）

> 本章没有"不可执行、只能降级为核查记录"的行动；三条都落成了代码与真实产物。
