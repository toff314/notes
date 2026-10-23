# lab-02　从零实现 SGNS：梯度校验与类比实验

对应行动：`actions.md` 第 3 条。对应书中 §5.5.1（分类器）、§5.5.2（损失/梯度/SGD）、§5.7（平行四边形模型及其失败模式）。

## 怎么跑

```bash
cd labs/lab-02
python3 lab02_sgns_from_scratch.py                 # 默认 dim=40, window=±2, k=5, 12 epochs, 3 seeds
python3 lab02_sgns_from_scratch.py --epochs 20 --dim 50
```

纯 numpy 实现，无深度学习框架；CPU 约 80 秒（3 个随机种子）。

## 实现与书中公式的对应

| 书中 | 实现 |
|---|---|
| P(+|w,c)=σ(c·w)（5.15） | `sigmoid(cpos @ w)` |
| L=−[log σ(c_pos·w)+Σ log σ(−c_neg·w)]（5.21） | `loss_and_grads()` 第一行 |
| ∂L/∂c_pos=[σ(c_pos·w)−1]w（5.22） | `g_cpos` |
| ∂L/∂c_neg=[σ(c_neg·w)]w（5.23） | `g_cnegs` |
| ∂L/∂w=[σ(c_pos·w)−1]c_pos+Σ[σ(c_neg·w)]c_neg（5.24） | `g_w` |
| 负采样 P_α(w)∝count(w)^0.75 | `noise = freq ** 0.75` 归一化后 `rng.choice` |
| W+C 作为词向量 | `final_vectors()` |

语料是按模板生成的 1,580 句（8,924 token）：王室的性别/年龄轴、国家首都、形容词的三级形态，外加 200 句虚词填充。

## 产物

| 文件 | 内容 |
|---|---|
| `out/loss.csv` | 每个 epoch 的平均损失（best seed） |
| `out/vectors.csv` | 73 个词 × 40 维单位向量 |
| `out/neighbors.csv` | 8 个目标词的 6 个近邻 |
| `out/analogies.json` | 20 题逐题结果、top5、成功/失败分类、梯度校验误差 |
| `out/analogy_accuracy.csv` | 3 个种子的命中率与极差 |
| `out/vector_arithmetic.png` | 王室/性别词的二维投影与 man→king、woman→queen 箭头 |

## 关键输出（真实运行）

```
corpus: 1580 sentences, 8924 tokens, vocab=73
gradient check: max relative error = 3.172e-09
seed=0 analogy acc=0.750 (hit=15, returned_input=5, miss=0)
seed=1 analogy acc=0.750 (hit=15, returned_input=5, miss=0)
seed=2 analogy acc=0.700 (hit=14, returned_input=6, miss=0)
analogy acc mean=0.733 range=0.050
loss: 2.031984 -> 1.602222 (epoch 1 -> 12)
```

命中示例：

```
king:queen::man:woman -> woman [hit]
king:queen::prince:princess -> princess [hit]
paris:france::rome:italy -> italy [hit]
```

失败示例（5 题全部落在形容词三级形态上，且全部属于「返回输入词」）：

```
big:bigger::small:smaller -> warm（raw top1 = small）[returned_input]
cold:colder::warm:warmer  -> bigger（raw top1 = colder）[returned_input]
bigger:biggest::smaller:smallest -> tallest（raw top1 = biggest）[returned_input]
```

## 结论

1. **梯度推导正确**：有限差分与解析梯度的最大相对误差 3.2e-9，远小于 1e-5。这同时验证了我在笔记里对式 5.22–5.24 的重建（原书抽取文本里这些式子排版错乱）。
2. **平行四边形模型在合成语料上成立**：15/20 命中，王室与首都两类 10 题全中。说明「关系 = 向量差」在上下文结构一致时确实可学。
3. **失败集中在三级形态**：`big/bigger/biggest` 共享同一批上下文（`has`、`degree`、`one/two/three`），导致 a 与 b 自身互为近邻，检索第一步就返回输入词——正是 §5.7 说的「必须显式排除 3 个输入词及其形态变体」。
4. **结果随种子波动**：三个种子命中率 0.70–0.75（极差 0.05），与 §5.9「随机初始化 + 随机负采样导致不可复现」一致。20 题样本太小，0.05 的波动不足以谈优劣。

## 反思

我原先以为类比失败是因为「训练不够、维度太低」。把失败样本逐个打印后才发现：5 题的 raw top1 全是输入词之一（small / cold / bigger / biggest），其中 3 题的正确词连 top5 都没进。也就是说，问题不是向量没学好，而是评测流程少了「排除输入词」这一步——书中把它写成一句提醒，我在实现时才体会到它是必须的工程步骤。

另一个发现是损失下降到 1.60 左右就不再降。起初以为实现有 bug，算了一下噪声下限才明白：k=5 个随机负样本里必然混入真实上下文词，损失不可能趋近 0。这也说明「损失曲线好看」不等于「向量好用」，最终还是要看近邻与类比。
