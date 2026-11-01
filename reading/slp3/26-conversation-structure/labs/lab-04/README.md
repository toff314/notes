# lab-04　DAMSL 对话行为标注实验

对应行动：`actions.md` 第 4 条。对应书中 §26.2（对话行为、DAMSL 标注体系）。

## 怎么跑

```bash
cd labs/lab-04
python3 lab04_damsl_annotator.py
```

依赖：仅 Python 3 标准库。

## 输入

- 我的简易 DAMSL 标注（`MY_ANNOTATION`）：对图 26.1 前 12 个话轮的前向/后向功能标注。
- 书中图 26.5 的标注（`BOOK_ANNOTATION`）：按 raw 文本转录，粗粒度标签（assert、info-req 等）映射到 DAMSL 细粒度标签（STATEMENT、INFO-REQUEST 等）。

## 产物

| 文件 | 内容 |
|---|---|
| `out/damsl_agreement.csv` | 逐条前向/后向功能对照表 |

## 关键输出（真实运行）

```
agreement: 24/24 = 1.0000
C1: fwd STATEMENT/STATEMENT ✓  bwd -/- ✓
A2: fwd INFO-REQUEST/INFO-REQUEST ✓  bwd ACK/ACK ✓
C3: fwd STATEMENT/STATEMENT ✓  bwd ANSWER/ANSWER ✓
A4: fwd INFO-REQUEST/INFO-REQUEST ✓  bwd ACK/ACK ✓
C5: fwd STATEMENT/STATEMENT ✓  bwd ANSWER/ANSWER ✓
A6: fwd INFO-REQUEST/INFO-REQUEST ✓  bwd ACK/ACK ✓
C7: fwd CHECK/CHECK ✓  bwd HOLD/HOLD ✓
A8: fwd ACCEPT/ACCEPT ✓  bwd ACK/ACK ✓
C9: fwd INFO-REQUEST/INFO-REQUEST ✓  bwd -/- ✓
A10: fwd STATEMENT/STATEMENT ✓  bwd ANSWER/ANSWER ✓
C11: fwd ACCEPT/ACCEPT ✓  bwd ACK/ACK ✓
A12: fwd CHECK/CHECK ✓  bwd ACK/ACK ✓
saved: out/damsl_agreement.csv
```

## 结论

1. 我的简易标注器对图 26.1 前 12 个话轮的标注与书中图 26.5 完全一致（24/24 = 100%）。
2. 前向功能（STATEMENT、INFO-REQUEST、CHECK、ACCEPT）和后向功能（ACK、ANSWER、HOLD）均匹配。
3. 100% 一致率可能是因为前 12 个话轮的模式比较典型（问-答-确认循环），更复杂的对话（如多人对话、多轮纠正）可能会降低一致性。

## 反思

一致率 100% 反而让我警惕——可能是因为前 12 个话轮的模式比较典型（问-答-确认）。如果扩展到更复杂的对话（如多人对话、多轮纠正），标注一致性可能会下降。DAMSL 的标注指南本身也需要培训才能达到高一致性。这让我理解为什么书中说「这类功能会'回指'对话者此前的话语」——后向功能的标注需要理解对话历史，不是孤立地看当前话语。
