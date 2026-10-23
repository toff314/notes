# 行动执行闭环（labs/index.md）

> `actions.md` 的每条行动都在这里落成**可运行脚本 + 真实产物 + 结论 + 反思**。
> 所有数字来自本机实际运行（Python 3 / numpy 2.4.6 / matplotlib 3.10.9），可复跑。

| 行动 | 脚本 | 运行产物 | 一句话结论 | 反思入口 |
|---|---|---|---|---|
| 1. bigram 下词排序 | `lab-01/bigram_next_word.py` | `lab-01/out/next_word.csv`、`summary.json`、`next_word.png` | 1.3 万词语料上，"...thanks for" 实际只条件于 `for`，`example` 居首，书中 `all` 不在前 12 | [lab-01/README.md](lab-01/README.html) |
| 2. 困惑度与平滑 | `lab-02/perplexity.py` | `lab-02/out/perplexity.json`、`perplexity.csv`、`perplexity.png` | 无平滑全为 ∞；bigram 加一 1292.76，反而差于 unigram 加一 552.02 | [lab-02/README.md](lab-02/README.html) |
| 3. 香农游戏纠正分布 | `lab-03/shannon_game.py` | `lab-03/out/corrections.csv`、`rates.csv`、`summary.json`、`rates.png` | 整体纠正率 67.2%；第二字母最难（84%），功能词比实词好猜 | [lab-03/README.md](lab-03/README.html) |
| 4. 代理指标与古德哈特 | `lab-04/proxy_goodhart.py` | `lab-04/out/candidates.csv`、`summary.json`、`overlap_vs_adequacy.png` | 6 组中 3 组选中刷分候选；按 overlap 选平均 adequacy 3.0，人工最优 5.0 | [lab-04/README.md](lab-04/README.html) |

## 复跑方式

```bash
cd labs
for d in lab-01 lab-02 lab-03 lab-04; do (cd "$d" && python3 *.py); done
```

## 输入与可复现性

- 四个 lab 都读取 `/home/yuanwu/books/slp3/zh/md/01-introduction.dual.md` 的英文原文；
  lab-01/02/03 在训练前剔除会被查询/测试的句子，避免"自己考自己"。
- lab-04 的句对与 adequacy 是构造的教学样例（README 已声明），overlap 与选择过程为真实计算。
- 产物中的图使用 Noto Sans CJK 字体渲染中文标签；CSV/JSON 为 UTF-8。

## 覆盖核对

- [x] 行动 1 → lab-01（脚本、CSV、PNG、结论、反思）
- [x] 行动 2 → lab-02（脚本、JSON/CSV、PNG、结论、反思）
- [x] 行动 3 → lab-03（脚本、CSV、PNG、结论、反思）
- [x] 行动 4 → lab-04（脚本、CSV、PNG、结论、反思）

> 本章没有"不可执行、只能降级为核查记录"的行动；四条都落成了代码与产物。
