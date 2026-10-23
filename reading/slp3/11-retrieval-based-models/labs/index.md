# Labs · 行动执行闭环

> `actions.md` 是「我要做什么」，本目录是「我真的做了，并看到结果」。
> 四条行动各对应一个 lab，全部用标准库 + numpy 2.4.6 + matplotlib 3.10.9 实跑。

| Lab | 对应行动 | 脚本 | 主要产物 | 一句话结论 |
|---|---|---|---|---|
| lab-01 | 行动 1：稀疏 vs 稠密检索 | `lab-01/sparse_vs_dense.py` | `out/metrics.csv`、`out/metrics.png`、`out/gap_analysis.png` | 玩具规模上 BM25（MRR 0.842）仍强于共现向量（0.739） |
| lab-02 | 行动 3：玩具 RAG 评估 | `lab-02/toy_rag_eval.py` | `out/metrics.csv`、`out/rag_compare.png` | 开卷命中率 0.60→0.85，但 3 次失败全是「引用了错来源」 |
| lab-03 | 行动 2：复现 AP / 11 点插值 | `lab-03/pr_metrics.py` | `out/summary.json`、`out/pr_curve.png`、`out/interpolated_curve.png` | AP=0.5972，与书 0.6 一致；插值表逐点误差 ≤0.01 |
| lab-04 | 行动 4：BM25 参数网格 | `lab-04/bm25_sweep.py` | `out/grid_mrr.csv`、`out/mrr_heatmap.png`、`out/b_curve.png` | b=0 时长文档抢走 56% 第一名；k1=0 时 b 失效 |

## 逐条对应（G10）

### 行动 1 → lab-01

- **验证的问题**：在中文玩具语料上，字面匹配与共现向量检索谁更稳？稠密的收益需要什么前提？
- **运行**：`cd lab-01 && python3 sparse_vs_dense.py`
- **关键输出**：tfidf MRR 0.850 / bm25 0.842 / dense 0.739；标题查询 Recall@1 = 1.00 / 1.00 / 0.79。
- **结论**：稠密侧输在表示质量而非方法本身；书里没说破的前提是预训练规模与监督数据。
- **反思**：我曾把「语义向量」当成升级按钮，实验说明它只是换了匹配方式，没换信息量。

### 行动 2 → lab-03

- **验证的问题**：书上的 AP 与 11 点插值表能不能从定义一步步算出来？
- **运行**：`cd lab-03 && python3 pr_metrics.py`
- **关键输出**：AP = 0.5972（书 0.6）；`max_abs_diff_vs_book_table = 0.010`。
- **结论**：定义无隐藏步骤；插值确实偏乐观（召回 0.5 处实测 0.36–0.545，插值 0.625）。
- **反思**：用书上的表格当单元测试，比通读定义更能暴露理解偏差。

### 行动 3 → lab-02

- **验证的问题**：开卷一定比闭卷好吗？只看答案对错会漏掉什么？
- **运行**：`cd lab-02 && python3 toy_rag_eval.py`
- **关键输出**：闭卷 acc 0.60/F1 0.777；开卷 acc 0.85/引用率 1.00/引用正确率 0.85；给对段落 acc 1.00。
- **结论**：RAG 把「无据的自信」换成「有据的自信」；引用正确率是必须单独报的第三指标。
- **反思**：失败从「没引用」变成「引错源」，这是更隐蔽的失效模式。

### 行动 4 → lab-04

- **验证的问题**：k1 与 b 各自的作用能否在可观测指标上分开？
- **运行**：`cd lab-04 && python3 bm25_sweep.py`
- **关键输出**：b=0 长文档胜率 0.56、MRR 0.563；b≥0.75 胜率 0、MRR 0.793；k1=0 整行不变。
- **结论**：两个参数不正交；k1=0 时 b 没有作用对象，扫参前须确认维度有效。
- **反思**：b 的效果是断崖不是斜坡，曲线平缓可能只是测试集没覆盖敏感区间。

## 环境与复现

```bash
python3 -c "import numpy, matplotlib; print(numpy.__version__, matplotlib.__version__)"
# 2.4.6 3.10.9
for d in lab-01 lab-02 lab-03 lab-04; do (cd $d && python3 *.py); done
```

所有脚本只读本地文件；lab-01 的背景语料路径不可用时自动回退到玩具语料，并在 `scores.json` 记录实际来源。图表用 Noto Sans CJK 字体（系统缺失时中文会显示为方框，数值不受影响）。
