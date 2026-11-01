# 第 16 章 · 行动清单（3 条）

> 纪律：每条都要有「可交付物 + 验收标准 + 日期」，否则不算行动。三条分别绑定 lab-01/02/03，产物落在 `labs/lab-0x/out/`。

1. **把 WER 做成能复算的工具**（绑定 lab-01-wer-tools）

- **做什么**：用 DP 实现词级最小编辑距离 + 回溯，输出 S/I/D 计数与对齐串；先用书中的 13 词例子复算 76.9%，再对自己写的 3 组中文句对跑一遍。
- **可交付物**：`labs/lab-01-wer-tools/wer.py`、`labs/lab-01-wer-tools/out/wer.csv`、`labs/lab-01-wer-tools/out/alignment.txt`。
- **验收标准**：① 书中例子复算值 = 76.92%（±0.05 内）；② CSV 至少 6 行，含 raw / normalized 两种参考口径；③ 规范化前后差值有文字解释。
- **日期**：2026-11-01 前完成。

2. **把 CTC 的「求和 vs 取最大」跑成反例**（绑定 lab-02-ctc-collapse）

- **做什么**：对 T=3、字母表 {a,b,ε} 穷举 27 条对齐，按折叠函数聚合出每个输出串的概率；用随机分布搜索「argmax 对齐所属输出 ≠ argmax 输出」的实例；再用前向 DP 复算同一概率。
- **可交付物**：`labs/lab-02-ctc-collapse/ctc.py`、`labs/lab-02-ctc-collapse/out/alignments.csv`、`labs/lab-02-ctc-collapse/out/summary.json`。
- **验收标准**：① 暴力枚举与前向 DP 的最大绝对差 < 1e-12；② 找到 ≥1 个 argmax 不一致实例并记录两侧概率；③ dinner/diner 折叠对照表存在。
- **日期**：2026-11-03 前完成。

3. **把 k-means 的粒度效应量出来**（绑定 lab-03-kmeans-units）

- **做什么**：合成 3 类元音共振峰 → 39 维倒谱特征 → k 从 3 扫到 32，记录纯度/ARI/惯性；再按 HuBERT 两阶段思路比较粗码本（k=8）与细码本（k=24）。
- **可交付物**：`labs/lab-03-kmeans-units/kmeans_units.py`、`labs/lab-03-kmeans-units/out/k_sweep.csv`、`labs/lab-03-kmeans-units/out/k_sweep_summary.json`。
- **验收标准**：① 每个 k 都有纯度与 ARI；② 5 组随机初始化下的纯度极差有数字；③ k=3 时 purity/ARI 同时最高，k>3 后 ARI 下降有数字记录。
- **日期**：2026-11-05 前完成。

---

## 错题归因（做自测后填；格式固定）

| 题号 | 错因类型 | 具体表现 | 补救动作 | 复测日期 |
|---|---|---|---|---|
| 例：4 | 概念混 | 把 45ms 算成 30ms，漏掉两端半帧 | 抄卡 4 通式 3 遍 + 重算 3 组不同 k | 2026-11-02 |
|  |  |  |  |  |
|  |  |  |  |  |

> 错因只填三类之一：**概念混** / **公式记错** / **条件漏**（漏了假设、前缀、归一化之类）。填不出类型说明还没定位到错在哪，不许写「粗心」。
