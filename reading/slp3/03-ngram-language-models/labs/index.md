# labs · 行动执行闭环（第 3 章）

> `actions.md` 的每条行动在这里都有一个可运行脚本、真实产物、结论与反思。
> 所有脚本仅依赖标准库 + numpy/matplotlib，语料由 `shared_corpus.py` 固定种子生成，可重复。

## 行动 ↔ lab 对照

| # | actions.md 行动 | lab | 脚本 | 主要产物 | 结论（引用自己的产物） | 反思 |
|---|---|---|---|---|---|---|
| 1 | 训练 1–4 元模型，产出困惑度表与两张图 | `lab-01` | `ngram_perplexity.py` | `metrics.csv`（12 行）、`ppl_by_n.png`、`ppl_vs_train_size.png`、`samples_generated.txt` | 2-gram 最低（6.68），3/4-gram 回升到 9.92/13.26；训练量 25%→100% 时 3-gram 降 45.3% | 高阶优势依赖语料规模与平滑强度，不是单调结论 |
| 2 | 四种平滑同测试集对比并画柱状图 | `lab-02` | `smoothing_compare.py` | `metrics.csv`、`smoothing_ppl.png`、`dev_vs_test.png`、`lambdas.json`、`backoff_examples.json` | MLE=inf；add-k(0.01)=8.86 最优；插值=7.28，再低 17.8%；λ=(0.1,0.7,0.2) | 平滑并非越轻越好，k=0.001 反而回升；插值最稳 |
| 3 | 重算书中例子并断言 | `lab-03` | `verify_book_numbers.py` | `checks.json`、`bigram_iamsam.csv`、`exercise37.png` | 20/20 通过；颜色 B 反转测试从 1.89 升到 6.60 | 错误集中在计数口径（`<s>`、`</s>`、V 怎么数） |

## 复现方式

```bash
cd labs/lab-01 && python3 ngram_perplexity.py
cd ../lab-02 && python3 smoothing_compare.py
cd ../lab-03 && python3 verify_book_numbers.py
```

`lab-01` 与 `lab-02` 共享 `labs/shared_corpus.py`（320 句模板语料 + 8 句手写句，去重后 248 句，seed=7，70/15/15 切分），因此两个 lab 的困惑度数字可以直接对照。

## 章节内小行动的落实

- §3.1.2 手算 bigram：由 `lab-03/out/bigram_iamsam.csv` 覆盖（6 个概率）。
- §3.2 训练/测试交集检查：`shared_corpus.build_corpus` 先 shuffle 再切分，并用集合断言确认 train/dev/test 两两无重叠。
- §3.3 困惑度比值：`lab-01/out/metrics.csv` 的 2-gram/3-gram 行可直接相除。
- §3.3.1 反转测试集：`lab-03/out/checks.json` 中 `colour LM B perplexity (swapped test)`。
- §3.4 采样：`lab-01/out/samples_generated.txt`（每阶 5 句）。
- §3.5 训练规模对比：`lab-01/out/ppl_vs_train_size.png` 与 CSV 的 `train_frac` 列。
- §3.6 k 值扫描：`lab-02/out/metrics.csv` 的四个 add-k 行。
- §3.6.3 插值权重：`lab-02/out/lambdas.json`（和 = 1.00）。
- §3.6.4 回退手算：`lab-02/out/backoff_examples.json`。
- §3.7 熵换算：`lab-03/out/checks.json` 的 `horse entropy (bits)`、`uniform 8-way entropy (bits)` 与 `2 bits in nats`。

## 未做成脚本的部分（核查记录）

- 「语料是否带 datasheet」属于外部资料核查，本章不涉及具体数据集，故未建 lab；处理方式是在 README 的「实际输入」中如实登记语料来源（合成语料，无版权问题）。
