# lab-04　归一化与词频：原始点积为什么偏爱高频词

对应行动：`actions.md` 第 4 条的后半。对应书中 §5.4（点积、向量长度、余弦）。

## 怎么跑

```bash
cd labs/lab-04
python3 lab04_normalization_and_bias.py
```

复用与 lab-03 相同的语料（本章英文原文，9,855 token，词表 555，窗口 ±5，PPMI + 秩 50 SVD），但**保留未归一化的向量**，以便比较点积与余弦。

## 产物

| 文件 | 内容 |
|---|---|
| `out/freq_norm.csv` | 每个词的频次、log10 频次、PPMI-SVD 向量范数 |
| `out/freq_norm.json` | 两条 Pearson 相关与高频/其余词的平均范数 |
| `out/dot_vs_cosine.csv` | 4 个目标词的点积 top-10 与余弦 top-10 并列 |
| `out/dot_vs_cosine.png` | 相似度分数随词频变化的散点（余弦 vs 点积） |
| `out/freq_norm.png` | log10 频次 vs 向量范数 |

## 关键输出（真实运行）

```
Pearson(log10 freq, ||v||_PPMI-SVD) = 0.247
Pearson(log10 freq, ||v||_raw count) = 0.722
  [word]    dot vs cosine top10 overlap = 50%
      dot:    each, apricot, c, occurs, context, row
      cosine: target, each, context, row, a, occurs
  [meaning] dot vs cosine top10 overlap = 60%
  [context] dot vs cosine top10 overlap = 60%
  [king]    dot vs cosine top10 overlap = 100%
```

## 结论

1. **「高频词向量更长」在原始计数上成立**：log 频次与原始计数向量范数的相关系数 0.722，是明确的正相关，与 §5.4 的说法一致。
2. **PPMI 已经做了相当程度的「去长度」**：同一批向量换成 PPMI-SVD 后，相关降到 0.247。也就是说，PPMI 这一步在压低高频组合，余弦再做一次方向归一化，两者作用叠加而不是重复。
3. **点积与余弦的差异只出现在「多义/泛用」词上**：`king` 的 top-10 完全一致（重叠 100%，因为它只在少数固定上下文出现，长度不构成偏差）；`word`、`meaning`、`context` 只重叠 50%–60%，点积版本更偏向出现次数多的邻居，余弦版本更偏向分布形状相似的邻居。
4. **所以归一化不是可选优化**：只要候选词频分布长尾，点积排序就会系统性偏向高频项。工程上要么用余弦，要么在训练时就做长度惩罚。

## 反思

我原以为「高频 → 向量长 → 点积大」会是一条非常强的规律（预期 r>0.9）。实测原始计数只有 0.72，而 PPMI-SVD 只有 0.25。查了 `freq_norm.json` 才明白：PPMI 对高频词的对数值做了压制，SVD 又只保留前 50 个主方向，两次变换把长度信息洗掉了大半。

这改变了我对「归一化」的理解：它不是一步操作，而是散布在流程里的三处——PPMI 的对数、SVD 的截断、最后的方向归一化。只做最后一步，前面两步的偏差仍会以「方向」的形式留在向量里。这也是为什么 §5.5.3 说 word2vec 与 PPMI 分解是同一件事：训练过程本身就在做类似的加权。
