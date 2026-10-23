# Labs · 行动执行闭环

> `actions.md` 是「要做什么」，这里是「已经跑了什么、看到什么、改了什么想法」。
> 环境：Python 3 + numpy 2.4.6 + matplotlib 3.10.9；全部脚本可直接复跑。

## 行动 ↔ Lab 覆盖

| 行动（actions.md） | Lab | 脚本 | 运行产物 | 状态 |
|---|---|---|---|---|
| 1. 实现并跑通 BPE（训练 40 次合并） | [lab-01](lab-01/README.html) | `bpe_lab.py` | `out/metrics.json`、`out/vocab.csv`、`out/compression_curve.png` | ✅ 已跑 |
| 2. 实现 Levenshtein DP + 回溯对齐 | [lab-02](lab-02/README.html) | `edit_distance_lab.py` | `out/distances.json`、`out/dp_matrix_intention_execution.csv`、`out/edit_distance_matrix.png` | ✅ 已跑 |
| 3. 正则审计中英混合预词元化 | [lab-03](lab-03/README.html) | `pretokenize_lab.py` | `out/pretokenization.json`、`out/token_counts.png` | ✅ 已跑 |

## lab-01 · BPE

- **运行**：`cd lab-01 && python3 bpe_lab.py`
- **结论**：40 次合并把 291 个字符压到 210 个词元（−27.84%），英文高频词根先被合并，中文逐字未动。
- **证据**：`out/compression_curve.png` 显示前 10 次合并下降最陡；`out/segments.csv` 里 `tokenization` 等词已成为单 token。
- **反思**：频率是全局竞争的，中英语料混合时中文排不进前 40 次合并；这复现了 §2.4.3 的多语言偏斜问题。

## lab-02 · 最小编辑距离

- **运行**：`cd lab-02 && python3 edit_distance_lab.py`
- **结论**：`intention → execution` 在替换代价 2 下距离 8，DP 表与书中图 2.20 逐格一致；替换代价 1 下距离 5。
- **证据**：`out/dp_matrix_intention_execution.csv` 末行为 `9,8,9,10,11,12,11,10,9,8`；`out/alignments.csv` 给出 `d s s = i s = = = =`。
- **反思**：代价表会改变拼写错误的相对排序，不能把教材默认值当任务默认值。

## lab-03 · 预词元化

- **运行**：`cd lab-03 && python3 pretokenize_lab.py`
- **结论**：书中例句切出 `We | ’re | ␣350 | …` 共 9 个词元；中文近似模式下整段未切；混合句因 URL 被切到 18 个词元。
- **证据**：`out/pretokenization.json` 保留每个词元（空格显示为 ␣）；`out/token_counts.png` 对比正则与空白切分。
- **反思**：`\p{L}` 与 `[^\W\d_]` 在中文上的行为不同，预词元化必须先核对切分表，再谈 BPE 参数。
