# labs · 行动执行闭环

> 环境：Python 3 + numpy 2.4.6 + matplotlib 3.10.9（仅标准库 + 这两个包）。
> 两个 lab 覆盖 `actions.md` 的 4 条行动；每条都留下可复现脚本、真实产物、结论与反思。

## 总览

| 行动 | 脚本 | 运行产物 | 结论一句话 |
|---|---|---|---|
| 1. 从零实现二分类逻辑回归 | `lab-01/logreg_binary.py` | `lab-01/out/weights.json`、`loss_curve.png`、`decision_boundary.png`、`training_log.csv` | 22 条样本上收敛到 w=[1.5131,−1.8113]、b=0.1646，损失 0.2550，准确率 0.909 |
| 2. 复现 §4.6.3 单步并做数值校验 | `lab-01/logreg_binary.py` | `lab-01/out/gradient_step.json` | 一步后 w=[0.15,0.10]、b=0.05；解析与数值梯度相对误差 ~1e-11 |
| 3. softmax 多分类 + 指标 + 超参扫描 | `lab-02/logreg_multiclass.py` | `lab-02/out/metrics.json`、`confusion_matrix.png`、`lr_comparison.*`、`reg_comparison.*` | 测试准确率 0.767，宏 F1 0.760、微 F1 0.767；α=0.1 时准确率最高 0.833 |
| 4. 配对自助检验 | `lab-02/logreg_multiclass.py` | `lab-02/out/bootstrap.json`、`bootstrap_hist.png` | δ=0.0667、b=2000、p=0.085，按 0.01 阈值不显著 |

## 运行方式

```bash
cd labs/lab-01 && python3 logreg_binary.py
cd ../lab-02 && python3 logreg_multiclass.py
```

两个脚本都使用 `matplotlib.use("Agg")`，无图形界面也能产出 PNG。

---

## 行动 1：从零实现二分类逻辑回归

- **脚本**：`lab-01/logreg_binary.py`（sigmoid / 交叉熵 / 解析梯度 / 批量 GD）
- **产物**：`out/weights.json`（权重、偏置、逐条概率）、`out/loss_curve.png`、`out/decision_boundary.png`、`out/training_log.csv`
- **结论**：正词权重 +1.5131、负词权重 −1.8113，符号与量级都符合 §4.3.1 的示例方向；损失从 ln2=0.693 单调降到 0.2550；训练准确率 0.909，两条歧义样本保留了误差。
- **反思**：教材公式直接照抄会在 z 很负时溢出，必须按符号分支实现稳定 sigmoid；另外“损失单调下降”不是因为数据干净，而是凸性 + 合适学习率的共同结果。

## 行动 2：复现 §4.6.3 单步并做数值校验

- **脚本**：`lab-01/logreg_binary.py` 中的 `numerical_gradient_check()`
- **产物**：`out/gradient_step.json`
- **结论**：初始 w=b=0、x=[3,2]、y=1 时，解析梯度为 (−1.5,−1.0,−0.5)，乘 η=0.1 取反得 w=[0.15,0.10]、b=0.05，与书中完全一致；中心差分数值梯度与解析梯度的相对误差约 1e-11。
- **反思**：手算时最容易漏掉“梯度要乘 x_j”，数值校验把这种错误立刻暴露出来；它也让我确认书中 OCR 错位的公式 4.26 实际含义就是 (ŷ−y)x_j。

## 行动 3：softmax 多分类 + 指标 + 超参扫描

- **脚本**：`lab-02/logreg_multiclass.py`
- **产物**：`out/metrics.json`、`out/confusion_matrix.png`、`out/lr_comparison.png`、`out/lr_comparison.csv`、`out/reg_comparison.png`、`out/reg_comparison.csv`
- **结论**：测试准确率 0.767，宏平均 P/R/F1 = 0.788/0.767/0.760，微平均 = 0.767/0.767/0.767；正类 20/20 全对，错误集中在中性类；lr=1.0 时损失反弹到 0.7777；L2 从 0 到 1.0 使 ‖W‖₂ 从 2.391 降到 0.440，最佳准确率出现在 α=0.1。
- **反思**：宏/微平均只差 0.007，说明这份数据类别均衡；一旦类别比例失衡，两者的分歧会被放大。学习率扫描也验证了“凸函数不等于随便选步长都收敛”。

## 行动 4：配对自助检验

- **脚本**：`lab-02/logreg_multiclass.py` 中的 `paired_bootstrap()`
- **产物**：`out/bootstrap.json`、`out/bootstrap_hist.png`
- **结论**：L2 模型（acc 0.833）对无正则模型（acc 0.767），δ=0.0667；b=2000 次有放回重采样中，按书中的 2δ 判据得到 p=0.085 > 0.01，不能拒绝“两者一样好”。
- **反思**：6.7 个百分点的差距在 60 条测试样本上并不稳固；书里的 2δ 规则比“δ>0”保守得多，报告结果时应该同时给出效应量与 p 值，而不是只报“更高”。

---

## 未纳入 labs 的行动

`actions.md` 中的“错题归因”属于学习记录，不需要代码，已在 self-test 的例题重做表中跟踪。
