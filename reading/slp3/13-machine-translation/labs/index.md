# 第 13 章 labs 索引

三个 lab 各对应 `../actions.md` 里的一条行动，全部只依赖 Python 3 与 numpy（lab-02 另需 matplotlib 出图），产物在各自 `out/` 下，都是真实运行结果。

| lab | 一句话 | 对应节 | 脚本 | 产物 |
|---|---|---|---|---|
| lab-01 | 从零实现 IBM Model 1 的 EM，看均匀对齐假设能学出什么、会漏什么 | §历史注记、§13.2.2 | `lab-01/ibm1_em.py`（163 行） | `t_table.csv`、`loglik.csv`、`alignments.json`、`t_heatmap.png` |
| lab-02 | 手算 chrF2 与 BLEU-4，把书中 .86/.62 复现到小数点后两位 | §13.6.2 | `lab-02/chrf_bleu.py`（194 行） | `summary.txt`、`chrf_terms.csv`、`chrf_k_sweep.csv`、`bleu_compare.csv`、`bleu_chrf.png` |
| lab-03 | 复现图 13.7 的贪心失败，并量化长度归一化的排名翻转率 | §13.4、§13.4.1 | `lab-03/beam_search.py`（170 行） | `results.json`、`beam_trace.csv`、`beam.png` |

## 三个 lab 互相咬合的地方

- lab-01 的 `alignments.json` 里 **P(0.7917) 高、R(0.5375) 低**，说明 IBM-1 倾向「少连不多连」。同一个偏向在 lab-03 里以另一种形式出现：贪心解码也是「早下注、少分支」。
- lab-02 的 `chrF2_hand_n12 = .8644 / .6198` 与 `chrF2_n6 = .6552 / .4162` 是同一句的两个口径，差 0.21 / 0.20。这组差值本身就是「指标是约定」的最好证据。
- lab-03 的翻转率 `.1135`（GNMT）vs `.2280`（平均归一化）说明：长度惩罚越狠，越容易把原本正确的最高分候选翻掉。这解释了为什么工业系统用 `(5+|y|)^α/6^α` 而不是简单除以长度。

## 一键复现

```bash
cd /home/yuanwu/notes/reading/slp3/13-machine-translation/labs
python3 lab-01/ibm1_em.py
python3 lab-02/chrf_bleu.py
python3 lab-03/beam_search.py
```

`out/` 会被覆盖重写。三个脚本都没有网络依赖，lab-03 用 `default_rng(0)`，结果确定可复现。
