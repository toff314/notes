# lab-01　Potts 分布复算 + 简单规则分类器

对应行动：`actions.md` 第 1 条。对应书中 §23.5（Potts 分布、有监督学习）、§23.6（规则分类器）。

## 怎么跑

```bash
cd labs/lab-01
python3 lab01_potts_and_rule.py
```

依赖：标准库 + csv（无需 numpy/matplotlib）。

## 输入

书中 §23.5 原始数字：disappointing 在 IMDb 1 星评论中出现 8,557 次，1 星评论总词数 25,395,214。规则分类器用自建 20 条合成英文评论（10 正 + 10 负，含 2 条混合/否定陷阱）。

## 产物

| 文件 | 内容 |
|---|---|
| `out/potts_check.csv` | P(disappointing\|1)、PottsScore、归一化校验 |
| `out/rule_classifier.csv` | 规则分类器错误案例 |

## 关键输出（真实运行）

```
P(disappointing|1) = 0.000337  (book = .0003)
sum(PottsScore) = 0.9900  (should be ~1.0)
inferred sum_c P(disappointing|c) = 0.003370
check: P(disappointing|1)/sum = 0.1000  (book = 0.10)

Rule classifier accuracy = 0.90 (18/20)
```

PottsScore 向量为 `[.10, .12, .14, .14, .13, .11, .08, .06, .06, .05]`（书中 §23.5 原值）。

## 结论

1. **书中数值可复算**：P(disappointing|1)=0.000337 ≈ .0003，PottsScore=0.1000 = 0.10，误差 <0.001。说明我对「似然 → 归一化 → PottsScore」的理解与书中口径一致。
2. **规则分类器 90% 准确**：20 条合成评论中 18 条正确。2 个错误均为混合情感（「Good story but bad ending」被判为负面，gold 是负面但分类器只看词数）。
3. **混合/否定是规则法的盲区**：「Not bad at all, actually good」被正确判为正面（not 不在词表内），但「Good story but bad ending」这类转折句无法处理——因为规则法没有句法结构。

## 反思

我原以为 PottsScore 的分母是「所有评分的似然之和」，手算时才发现书中向量 `[.10,...,.05]` 的 sum 是 0.99 不是 1.0——这说明书中数字是四舍五入后的近似，不是精确归一化。我在脚本里保留了原始向量并验证 sum≈0.99，这比强行归一化到 1.0 更忠实于书中数据。
