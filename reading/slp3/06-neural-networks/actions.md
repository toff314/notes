# 《Speech and Language Processing》第 6 章 · 行动清单（3 条）

> 从各节行动区提炼的可执行项；每条 = 动词 + 对象 + 时间/验收。
> 三条均已提前跑通（真实产物见 `labs/index.md`）；下列日期保留为重跑与复习截止。

## 学习行动（教材型）

1. **10 月 23 日前**跑 `labs/lab-01/xor_mlp.py`，从零实现 2-8-1 网络的向前与反向，在 XOR 上训练并做有限差分校验。
   验收：`out/summary.json` 的 accuracy=1.0、final_loss<0.001；`out/gradient_check.json` 中初始化的最大相对误差 <1e-6；`out/decision_boundary.png` 能把四象限按 0/1 分开。

2. **10 月 26 日前**跑 `labs/lab-02/embedding_mlp.py`，用同一分类器比较随机嵌入与 PPMI+SVD 共现嵌入，测试集只含训练中没出现过的情感词。
   验收：`out/metrics.json` 同时记录两种嵌入的准确率与混淆矩阵；相对差至少 30 个百分点；`out/embedding_pca.png` 中 held-out 正负词分居两侧。

3. **10 月 29 日前**跑 `labs/lab-03/gradient_vanishing.py`，在 10 层网络上逐层测量 sigmoid/tanh/ReLU 的梯度范数。
   验收：`out/gradient_norms.csv` 含 3×10 行；sigmoid 首层梯度 <1e-6 且测试准确率 ≤0.5，tanh/ReLU 准确率 ≥0.95；`out/gradient_norms.png` 能看到 sigmoid 的单调衰减。

## 错题归因（自测后填写）

> 每次做完 `self-test.md`，把错题按三类归档，禁止只抄正确答案。
> 归因结果直接决定下一条行动，而不是笼统地"再看一遍"。

- **知识性**（定义记错、公式条件漏）：回到对应 § 重读，并在 48 小时内用自己的话重写该卡片的 A 面。当前待办：§6.6.4 的 sigmoid 导数（10 月 30 日前）。
- **理解性**（读懂了题但抓错关键词）：把题干关键词圈出来，补一条"这题在问什么"的旁注，再找一道同型题验证。当前待办：XOR 的隐藏表示合并（10 月 24 日前）。
- **技巧性**（会但超时/算错）：限时 15 分钟重做同型题 2 道，记录用时与错误位置。当前待办：有限差分探针选择（11 月 1 日前）。
