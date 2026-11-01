# lab-04　跨度打分 + CKY 解码 vs 贪心解码（已知缺陷）

对应行动：`actions.md` 第 4 条。对应书中 §19.7（基于跨度的神经成分句法分析）。

## ⚠️ 已知缺陷：结果不可信

本 lab 存在严重问题，**结果不可信**：

1. 测试集 exact match = 0.0，说明模型在测试集上完全失败；但训练集 exact match 有 0.7965，说明不是代码 bug 而是严重的过拟合或数据分布问题。
2. 贪心合法树率 0.372 远低于书中引用的 95%（Gaddy et al., 2018），差距过大，怀疑是合成数据分布太窄或特征设计缺陷。
3. 由于 exact match 为 0.0，无法进一步计算 PARSEVAL 的 P/R/F1 和交叉括号。

该 lab 由前置 agent 生成，**尚未经过人工排查与修复**；后续 agent 需要检查：
- 数据生成是否有泄漏（train/test 同分布？）
- 感知机更新是否正确
- 特征是否足以泛化

## 怎么跑

```bash
cd labs/lab-04
python3 span_parser.py
```

依赖：`../cfgkit.py` + numpy。约 30 秒（8 epochs 结构化感知机 + 200 句测试）。

## 输入

- 数据：由 L1X 文法随机采样并二叉化得到的合成树库（train 1500 / test 250），金标准树自带。
- 模型：225 维离散特征 + 结构化感知机（structured perceptron），训练 8 epochs。

## 产物

| 文件 | 内容 |
|---|---|
| `out/dataset.csv` | train/test 句子数与长度统计 |
| `out/metrics.json` | 训练/测试 exact match、贪心合法树率 |
| `out/model.json` | 特征维度、标签集、超参数 |
| `out/test_pred.json` | 逐句预测结果（供 lab-05 计算 PARSEVAL） |
| `out/failures.txt` | 贪心解码拼不成树的示例（最多 5 条） |

## 关键输出（真实运行，但存在已知缺陷）

```json
{
  "train_sentences": 1500,
  "test_sentences": 250,
  "train_span_accuracy": 0.7965,
  "exact_match_cky": 0.0,
  "exact_match_greedy": 0.0,
  "greedy_valid_tree_rate": 0.372,
  "avg_spans_per_sentence": 17.79
}
```

## 结论（存疑，待修复）

当前结果**不可信**，不能用于验证或否定书中结论。唯一可用的信息是：
- 训练集 exact match 0.7965 说明感知机确实学到了训练数据的模式；
- 测试集 exact match 0.0 说明模型完全没有泛化能力；
- 贪心合法树率 0.372 说明在合成数据 + 手工特征上，贪心解码会大量失败。

## 反思

lab-04 的失败本身是一个重要教训——书中引用「95% 的预测括号结构能形成有效的树」是基于真实 PTB 数据与深度神经特征；在合成数据 + 手工特征上，这个比例会崩塌。这提醒我不能把论文中的数字当作跨任务常数引用。
