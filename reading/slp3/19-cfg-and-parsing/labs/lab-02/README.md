# lab-02　结构歧义枚举与计数（Groucho 例句 + PP 增长）

对应行动：`actions.md` 第 2 条。对应书中 §19.5（附着歧义、并列歧义）、§19.6.3（分析器与回溯指针）。

## 怎么跑

```bash
cd labs/lab-02
python3 enumerate.py
```

依赖：纯标准库（共用工具在 `../cfgkit.py`）。<1 秒。

## 输入

- 文法：L1 文法（同 lab-01）+ 变体 L1X（多开一条 `NP → NP PP`），用来对照「文法自由度决定歧义数」。
- 例句：`i shot an elephant in my pajamas`（§19.5 Groucho 例句）+ 逐步追加 PP 的句族。

## 产物

| 文件 | 内容 |
|---|---|
| `out/elephant_parses.txt` | 主句全部 3 种分析，按 PP 宿主产出式分类 |
| `out/attachment.csv` | n_pp → 分析数（L1 / L1X）、Catalan 数、k!、枚举耗时 |
| `out/summary.json` | 主句统计与增长表 |

## 关键输出（真实运行）

主句分析（3 种）：

```
VP->Verb-NP-PP         (S (NP i) (VP (Verb shot) (NP (Det an) (Nominal elephant)) (PP (Preposition in) (NP (Det my) (Nominal pajamas)))))
Nominal->Nominal-PP    (S (NP i) (VP (Verb shot) (NP (Det an) (Nominal (Nominal elephant) (PP (Preposition in) (NP (Det my) (Nominal pajamas)))))))
VP->VP-PP              (S (NP i) (VP (VP (Verb shot) (NP (Det an) (Nominal elephant))) (PP (Preposition in) (NP (Det my) (Nominal pajamas)))))
```

PP 增长表（L1 vs L1X）：

| n_pp | n_words | parses_L1 | parses_L1X | catalan_k | factorial_k | n_enumerated_L1X | t_enum(s) |
|---|---|---|---|---|---|---|---|
| 0 | 4 | 1 | 1 | 1 | 1 | 1 | 0.0000 |
| 1 | 7 | 3 | 4 | 1 | 1 | 4 | 0.0000 |
| 2 | 9 | 8 | 17 | 2 | 2 | 17 | 0.0001 |
| 3 | 11 | 15 | 63 | 5 | 6 | 63 | 0.0008 |
| 4 | 14 | 24 | 226 | 14 | 24 | 226 | 0.0036 |

## 结论

1. **Groucho 例句有 3 种合法分析**：PP in my pajamas 的宿主产出式分别为 VP->Verb-NP-PP（我穿睡衣开枪）、Nominal->Nominal-PP（大象穿睡衣）、VP->VP-PP（右附加）。这与 §19.5 图 19.9 的两棵幽默解读 + 一棵「正常」解读对应。
2. **分析数随 PP 个数 Catalan 型增长**：L1 文法下 0→4 个 PP 时分析数 1→3→8→15→24，接近 k+1 阶 Catalan 数；L1X 文法下 1→4→17→63→226，更接近纯 Catalan 数（1,1,2,5,14）。k! 是更松的上界。
3. **文法自由度决定歧义数**：L1X 只比 L1 多一条 `NP → NP PP`，但 4 个 PP 时分析数从 24 跳到 226（近 10 倍）。这说明「给文法多开一条附着口子」会指数级放大歧义——§19.3 说的 4,500 条 VP 规则的宾州树库，在真实句子上歧义爆炸得更厉害。
4. **枚举与计数的耗时差**：4 个 PP 时枚举 226 棵树只要 0.0036 秒，但 DP 计数只要 0.0003 秒（10 倍差）。这预示了 lab-03 的结论——CKY 填表（不枚举）才是多项式时间的，枚举本身是指数输出。

## 反思

我原以为「分析数随 PP 个数指数增长」是夸张说法，实测才发现 L1X 在 4 个 PP 时已经有 226 种分析——这还只是玩具文法。真实宾州树库的扁平文法（§19.3 说的 4,500 条 VP 规则）在真实句子上会爆炸得更厉害。

另一个发现是 Catalan 数出现在这里不是巧合：PP 附着问题等价于「k 个元素的括号化方案数」，这正是 Catalan 数的组合定义。L1 文法的增长略低于 Catalan，是因为某些附着方式被文法规则排除了（如 Nominal→Nominal Noun 不允许 PP 插在中间）。
