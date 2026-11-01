# lab-02　语义轴方法（Semantic Axis）

对应行动：`actions.md` 第 2 条。对应书中 §23.4.1（语义轴方法，式 23.3）。

## 怎么跑

```bash
cd labs/lab-02
python3 lab02_semantic_axis.py
```

依赖：numpy。

## 输入

- 5 个正向种子词：`good, great, amazing, love, excellent`
- 5 个负向种子词：`bad, terrible, awful, hate, horrible`
- 20 个候选词：明确正向（wonderful/fantastic/delightful/superb/marvelous/terrific）、明确负向（horrible/dreadful/atrocious/appalling）、弱正向（mediocre/adequate/acceptable/satisfactory/fine）、多义词（critical/volatile/sharp/bright/light）、中性词（neutral/ordinary/standard/common/usual）
- 向量：100 维合成向量，前 20 维是情感维度（正向词 +1.5，负向词 −1.5），其余维是主题+噪声。

## 产物

| 文件 | 内容 |
|---|---|
| `out/axis_scores.csv` | 25 个候选词的语义轴得分与方向 |

## 关键输出（真实运行）

```
V_axis[:5] = [0.2195 0.2217 0.2253 0.2421 0.2079]

Top 20 candidates by semantic axis score:
  fantastic        score=+0.9147  → pos
  marvelous        score=+0.9129  → pos
  wonderful        score=+0.9056  → pos
  terrific         score=+0.9000  → pos
  delightful       score=+0.8890  → pos
  superb           score=+0.8819  → pos
  light            score=+0.4902  → pos
  sharp            score=+0.4600  → pos
  bright           score=+0.4044  → pos
  mediocre         score=+0.3419  → pos
  ...
  volatile         score=-0.4299  → neg
  critical         score=-0.4948  → neg

Potentially ambiguous words:
  light            score=+0.4902  → pos
  sharp            score=+0.4600  → pos
  bright           score=+0.4044  → pos
  volatile         score=-0.4299  → neg
  critical         score=-0.4948  → neg

Direction check: 18/25 scored as positive
```

## 结论

1. **语义轴方向正确**：6 个明确正向词全部排在 top-6，得分 >0.88；4 个明确负向词（horrible/dreadful/atrocious/appalling）排在 bottom-4，得分 <−0.75。方向与构造一致。
2. **弱正向词排在中游**：mediocre/adequate/acceptable/satisfactory/fine 得分在 0.13–0.34 之间，低于强正向但高于中性词。这说明语义轴能捕捉强度差异。
3. **多义词方向不稳定**：light/sharp/bright 被判为正向（因为构造时给了 +0.5 情感维度），但 volatile/critical 被判为负向。这印证了「固定词表忽略语境」的问题——同一个词在不同语境下极性不同。
4. **18/25 正向**：因为候选词里正向词更多（构造偏差），不是算法问题。

## 反思

我原以为语义轴方法对多义词会给出「中性」得分（因为多义词在情感维度上信号弱），实际发现它还是会给一个明确方向（正或负），因为质心差 Vaxis 会把任何轻微的信号放大。这说明语义轴方法对多义词不是「安全」的——它会自信地给一个可能错误的方向。
