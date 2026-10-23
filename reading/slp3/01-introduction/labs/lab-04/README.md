# Lab 04　代理指标与古德哈特：把 overlap 刷满，质量会涨吗？

**对应行动**：actions.md 第 4 条
**书中锚点**：§1.9.4 代理指标、古德哈特定律
**脚本**：`proxy_goodhart.py`　**产物**：`out/candidates.csv`、`out/summary.json`、`out/overlap_vs_adequacy.png`

## 输入的性质（先声明）

- 6 组中英句对、每组 4 个候选译文，是**为教学构造的样例**；
  `adequacy`（1–5）是人工设定的示意分，不是真实标注实验。
- `overlap_f1` 由脚本**真实计算**：候选与参考译文的 token 集合 F1（不看顺序、不看重复）。
- 选择过程也是真实的：每组取 overlap 最高的候选，再与"人工分最高的候选"对比。

## 运行

```bash
cd labs/lab-04
python3 proxy_goodhart.py
```

## 关键输出（真实运行）

```json
"mean_overlap_selected_adequacy": 3.0,
"mean_oracle_adequacy": 5.0,
"n_gamed_selected": 3,
"pearson_overlap_vs_adequacy": -0.5886
```

被选中的刷分候选之一：
`the the cat cat sat sat on on the the mat mat`（overlap 1.0，adequacy 1）。

## 结论（引用自己的产物）

1. 6 组里有 3 组，overlap 最高的候选是**词序被打乱的重复词串**；按指标选，
   平均 adequacy 只有 3.0，而按人工分选是 5.0。
2. 在这组构造数据上，overlap 与 adequacy 的相关系数是 **-0.59**：指标越高，质量反而越低。
   原因很直接：集合 F1 不看顺序和重复，把参考词全部倒出来就能拿满分。
3. 这不是说 BLEU/chrF 一无是处——它们用 n-gram 精度，会惩罚乱序；
   但只要指标可被优化，就存在"针对指标而不是针对目标"的解法。
   古德哈特定律说的是这个结构性风险，不是某一个指标的 bug。
4. 实践含义：代理指标适合**高频回归检查**，不能单独当发布门槛；
   关键决策仍要人评或 LLM 评判，并抽查指标与人工分的一致性。

## 反思

我原来觉得"指标涨了就是变好了"，最多担心一下过拟合。这个 lab 让我看到更难堪的一面：
只要我知道指标怎么算，就能构造出指标满分、人读不懂的输出。以后看到"我们的 BLEU 提升了 2 分"，
我会先问测试集、分词和候选选择方式，再决定要不要信。
