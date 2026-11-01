# lab-04　简化版 SentProp 标签传播

对应行动：`actions.md` 第 4 条。对应书中 §23.4.2（SentProp 算法）。

## 怎么跑

```bash
cd labs/lab-04
python3 lab04_sentprop.py
```

依赖：numpy + scipy（stats.spearmanr）。

## 输入

- 50 词小图：25 正向词（pos0–pos24）+ 25 负向词（neg0–neg24）
- 向量：100 维，前 20 维是情感维度（正向 +1.5，负向 −1.5）
- k-NN 图：k=5，边权 = max(cos, 0.01)
- 3 组种子词：每组 3 正向 + 3 负向，来自不同位置

## 产物

| 文件 | 内容 |
|---|---|
| `out/sentprop_ranks.csv` | 50 词在 3 组种子下的排名及标准差 |

## 关键输出（真实运行）

```
Seed set 1: pos=['pos0', 'pos1', 'pos2'], neg=['neg0', 'neg1', 'neg2']
  Top 5: ['pos0', 'pos1', 'pos2', 'pos3', 'pos4']
  Bottom 5: ['neg20', 'neg21', 'neg22', 'neg23', 'neg24']

Seed set 2: pos=['pos5', 'pos6', 'pos7'], neg=['neg5', 'neg6', 'neg7']
  Top 5: ['pos0', 'pos1', 'pos2', 'pos3', 'pos4']
  Bottom 5: ['neg20', 'neg21', 'neg22', 'neg23', 'neg24']

Seed set 3: pos=['pos10', 'pos11', 'pos12'], neg=['neg10', 'neg11', 'neg12']
  Top 5: ['pos0', 'pos1', 'pos2', 'pos3', 'pos4']
  Bottom 5: ['neg20', 'neg21', 'neg22', 'neg23', 'neg24']

Spearman rank correlations between seed sets:
  set1 vs set2: ρ=1.0000, p=0.000000
  set1 vs set3: ρ=1.0000, p=0.000000
  set2 vs set3: ρ=1.0000, p=0.000000

Most unstable words (std of ranks across seed sets):
  pos0: std=0.00
  pos1: std=0.00
  pos2: std=0.00
  pos3: std=0.00
  pos4: std=0.00
```

## 结论

1. **3 组种子下排名完全一致（ρ=1.00）**：因为合成向量的情感维度信号很强（±1.5），且 50 词的结构非常规整（25 正 + 25 负，无多义词、无边缘词）。这不是「SentProp 稳」的证据，而是「合成数据太干净」的证据。
2. **排名和构造一致**：pos 词全部排在 top-25，neg 词全部排在 bottom-25，说明算法实现正确。
3. **排名标准差全为 0**：再次说明合成数据没有「不稳定词」。在真实语料中，多义词和边缘词会导致非零标准差，这正是书中「自举抽样给置信度」的动机。
4. **简化版 vs 完整版**：本 lab 用带重启的随机游走（reset_prob=0.2）近似书中「从种子集出发的随机游走」，省略了自举抽样置信度计算（因为合成数据无波动）。

## 反思

我原预期 3 组种子会有轻微排名差异（ρ 在 0.9 左右），实际 ρ=1.00。反思后发现：我的合成向量情感维度信号太强（±1.5 vs 噪声 0.3），导致所有正向词紧密抱团，换种子不影响大局。这说明 SentProp 的稳定性依赖语料结构——在情感维度清晰的语料上极稳，在多义词多的语料上才可能不稳。要观察种子敏感性，需要构造有边缘词的更真实语料。本实验达到验收标准（ρ≥0.80），但**只能作为「算法实现正确」的验证，不能作为「SentProp 对种子词稳健」的证据**。
