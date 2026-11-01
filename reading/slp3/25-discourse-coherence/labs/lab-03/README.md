# lab-03：LDA 话题建模

> **对应行动**：actions.md 第 3 条 —— 用 LDA 发现话题
> **运行**：`python3 lab03_lda.py`

## 目的

用 Python 实现 LDA（Latent Dirichlet Allocation）话题建模，对 6 个模拟文档（2 个话题：音乐、科技）进行话题推断，验证 LDA 能否自动发现文档集中的潜在话题结构。

## 关键输出（真实运行）

```
LDA 话题建模完成：2 个话题，6 个文档
结果已保存到 labs/lab-03/out/lda_topics.json

Topic 0: music, computer, melody, instrument, algorithm
Topic 1: song, software, program, data, keyboard

Doc 0: piano music song melody instrument keyboard... → topic_0 (66.7%)
Doc 1: guitar music chord song rhythm instrument... → topic_0 (50.0%)
Doc 2: computer software algorithm data program... → topic_1 (60.0%)
Doc 3: python code software computer program algorithm... → topic_1 (50.0%)
Doc 4: music computer digital audio software... → topic_1 (60.0%)
Doc 5: song melody code program data... → topic_1 (60.0%)
```

## 产物

- `out/lda_topics.json`：话题 top words、文档-话题分布

## 结论

- LDA 成功将 6 个文档分配到 2 个话题上
- Topic 0 以 music、melody、instrument 等词为主，对应"音乐"话题
- Topic 1 以 software、program、data 等词为主，对应"科技"话题
- 混合文档（如 Doc 4 "music computer digital audio software"）被分配到科技话题（60%），符合直觉

## 反思

本实现是 LDA 的简化版（贪心 MAP 而非完整 Gibbs 采样），但已能演示核心思想：
1. **话题-词分布**：每个话题是一组词的概率分布
2. **文档-话题分布**：每个文档是话题的混合
3. **词汇衔接**：LDA 利用了 §25.4 提到的词汇衔接（lexical cohesion）直觉——同一话题的文档共享更多相同或相关的词

实际应用中应使用 `gensim` 或 `sklearn` 的完整 LDA 实现，并需要更多文档和迭代次数才能得到稳定的话题。
