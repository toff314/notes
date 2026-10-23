# lab-02：嵌入 + MLP 文本分类（随机 vs 共现嵌入）

**对应**：§6.4（分类器）、§6.5（嵌入、池化、表示学习）。
**行动**：`actions.md` 第 2 条。

## 运行

```bash
cd labs/lab-02
python3 embedding_mlp.py
```

只依赖标准库 + numpy + matplotlib；随机种子固定为 `SEED=11`。

## 数据怎么构造（重要）

- 73 个词的词表：14 个评价对象（movie/film/…）、8 个中性形容词、20 个情感词、少量功能词。
- **训练句 240 条**：只用 12 个情感词（good/great/… 与 bad/terrible/…），模板中性（"the {对象} was {情感词}" 等）。
- **测试句 200 条**：只用 8 个**训练中从未出现**的情感词（charming/enjoyable/lovely/impressive 与 clumsy/dismal/tedious/painful）。
- **无标注语料 900 条**：覆盖全部 20 个情感词，情感词只出现在带极性的子句里（正面配 love/recommend，负面配 hate/avoid），用于构造共现嵌入；测试句不参与。
- 两种嵌入都**冻结**，分类器结构、初始化、训练轮数完全相同；差异只来自输入表示。

这是一次受控对照，不是真实语料实验：模板语料刻意放大了"分布相似 → 极性相似"的信号，结论应理解为机制演示，而非效果排名。

## 方法

1. 共现嵌入：窗口 3 的对称共现计数 → PPMI → SVD 取前 16 维 → 行归一化。
2. 随机嵌入：`N(0, 1/√16)`，同样 16 维，固定种子。
3. 分类器：对句内词向量做平均池化 → 24 维 tanh 隐藏层 → 2 类 softmax；全批量梯度下降 400 轮，学习率 0.15，L2=1e-4。

## 真实运行结果

| 嵌入 | held-out 准确率 | 训练末损失 | 混淆矩阵（行=真实，列=预测 neg/pos） |
|---|---|---|---|
| 随机 | 0.315 | 0.4777 | [[22, 67], [70, 41]] |
| PPMI+SVD | 0.995 | 0.0289 | [[89, 0], [1, 110]] |

最近邻（共现空间）：

- `charming` → brilliant, lovely, great, superb, excellent
- `enjoyable` → good, excellent, impressive, superb, lovely
- `clumsy` → dismal, boring, awful, bad, dull
- `dismal` → clumsy, boring, bad, tedious, dull

产物：`out/metrics.json`、`out/predictions.csv`、`out/confusion_matrix.csv`、`out/accuracy.png`、`out/embedding_pca.png`。

## 结论

1. 同一分类器、同一随机种子，只换嵌入，held-out 准确率从 0.315 到 0.995（`out/metrics.json`）。差距几乎全部来自"没见过的词能否落在正确的语义区域"。
2. 最近邻里，四个 held-out 词的邻居全部是同极性词，说明共现统计确实把极性编码进了向量；`out/embedding_pca.png` 中 held-out 正负词分居两侧。
3. 随机嵌入低于 0.5 并不反常：held-out 词的向量与训练词无关，分类器学到的线性边界对它们是随机的；200 条测试句上的方差足以让它落到 0.3 附近。

## 反思

我原来以为"随机嵌入 + 可训练分类器"至少能到 0.8，因为分类器总能在训练词上找到分界面。实测 0.315 让我意识到：**分类器只能切它见过的表示空间**，测试词不在这个空间里有意义的位置，切得再好也没用。这也解释了为什么书里反复强调"表示学习"而不是"更强的分类头"。

另一个教训是数据设计。第一版语料里正负情感词出现在完全相同的模板中，PPMI 学到的只是"它们在句法位置上一样"，极性邻居全混在一起，准确率只有随机水平（约 0.5）。把极性上下文（love/hate）加进无标注语料后，共现才真正携带情感。分布假说不是自动成立的，**共现的上下文必须与目标任务相关**。

## 文件

- `embedding_mlp.py`：数据构造、PPMI/SVD、分类器、出图
- `out/`：指标、预测、混淆矩阵、两张图
- `README.md`：本文件
