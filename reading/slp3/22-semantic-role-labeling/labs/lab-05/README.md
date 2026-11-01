# Lab 05 · BIO 序列标注 + Viterbi 解码

## 行动来源
actions.md 第 5 条：实现 BIO 标注 + Viterbi 解码，实现一个简化的 BIO 序列标注器，对 5 个测试句子输出标签序列并计算 F1。

## 运行命令
```bash
python3 lab05_bio_viterbi.py
```

## 关键输出（真实运行）
```
=== BIO 标注 + Viterbi 解码 ===

句子: John broke the window with a stone
谓词: broke
金标: ['B-ARG0', 'O', 'B-ARG1', 'I-ARG1', 'B-ARGM-MNR', 'I-ARGM-MNR', 'I-ARGM-MNR']
预测: ['B-ARG0', 'O', 'B-ARG1', 'B-ARG1', 'B-ARGM', 'B-ARG1', 'B-ARG1']
F1: 0.5

句子: The window broke
谓词: broke
金标: ['B-ARG1', 'I-ARG1', 'O']
预测: ['B-ARG0', 'I-ARG0', 'O']
F1: 0

句子: Doris gave the book to Cary
谓词: gave
金标: ['B-ARG0', 'O', 'B-ARG1', 'I-ARG1', 'B-ARG2', 'I-ARG2']
预测: ['B-ARG0', 'O', 'B-ARG1', 'B-ARG1', 'B-ARGM', 'B-ARG1']
F1: 0.571

句子: Sales fell to 25 million
谓词: fell
金标: ['B-ARG1', 'O', 'B-ARG4', 'I-ARG4', 'I-ARG4']
预测: ['B-ARG0', 'O', 'B-ARGM', 'B-ARG2', 'B-ARG1']
F1: 0

句子: Big Fruit Co. increased the price of bananas
谓词: increased
金标: ['B-ARG0', 'I-ARG0', 'I-ARG0', 'O', 'B-ARG1', 'I-ARG1', 'I-ARG1', 'I-ARG1']
预测: ['B-ARG0', 'I-ARG0', 'B-ARG1', 'O', 'B-ARG1', 'B-ARG1', 'B-ARG1', 'B-ARG1']
F1: 0.6

=== 总体 ===
Precision: 0.292, Recall: 1.0, F1: 0.452
```

产物：`out/bio_viterbi_output.json`

## 结论
- 实现了一个基于规则的 BIO 标注器 + 简化 Viterbi 解码器，对 5 个测试句子的总体 F1 为 0.452。
- 主要错误：①无法区分 ARG0 和 ARG1（主动 vs 被动的主语语义不同）；②无法识别连续的 I-X 片段（预测为 B-X）；③无法区分 ARG2/ARG4 等目标角色。
- 这与书中观察一致：基于规则的方法在简单句上表现尚可，但遇到语态交替、目标角色等复杂情况就失效，需要监督学习。

## 反思
我原来以为 BIO 标注就是「打标签」，做完才发现边界检测（B vs I）和角色分类（ARG0 vs ARG1 vs ARG2）是两个独立的挑战。我的规则方法把「with a stone」标成了 ARGM（部分正确），但把「the window」的 I-ARG1 标成了 B-ARG1（边界错误），导致 F1 大幅下降。这让我理解为什么书中说「标准评估要求每个论元标签必须被指派到完全正确的词序列」——边界和标签必须同时正确。
