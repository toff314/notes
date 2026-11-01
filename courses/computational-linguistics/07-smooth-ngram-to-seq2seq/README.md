# 第 7 讲 · 从 N-gram 平滑到 Seq2Seq

> 计算语言学基础（李蕾）第 7 讲听课笔记包。

## 一、本讲信息

| 项 | 内容 |
| --- | --- |
| 讲次 | 第 7 讲（紧接第 6 讲，04-1 P22 起） |
| 主题 | N-gram 平滑技术（折扣/回退/差值）、语言模型评估（PPL）、神经语言模型（FNN/RNN/LSTM/GRU）、Seq2Seq 与序列标注 |
| 时长覆盖 | 转写稿 3 段 / 40,710 汉字 |
| 来源 | 飞书 wiki `KaWcwjI2TiPtS5kFeHBc7msDn4d`（2026-11-01 课堂录音转写） |
| 音频分段 | 3 段（block 1 / 188 / 485 处的 `1` `2` `3` 标记） |

## 实际输入

- 转写文件：`raw/transcript-seg1.md`（13,337 字符）、`raw/transcript-seg2.md`（14,357 字符）、`raw/transcript-seg3.md`（13,016 字符）
- 课件文件：`raw/slides-1-ngram-smoothing.pptx`（04-1 P22-P51，30 页）、`raw/slides-2-neural-lm-seq2seq.pptx`（04-2 P1-P110，110 页）
- 元数据：`raw/meta.json`（页数、页码映射、未使用页范围）

## 二、三源对照（本讲未降级，G1 可判 PASS）

| # | 源 | 本地文件 | 覆盖范围 |
| --- | --- | --- | --- |
| 1 | 语音转写 | `raw/transcript-seg1.md` ~ `raw/transcript-seg3.md` | 全讲 3 节 |
| 2 | PPT 04-1「语言模型-N-gram」 | `raw/slides-1-ngram-smoothing.pptx`（51 页） | 本讲从 P22 讲到 P51（平滑 + 评估） |
| 3 | PPT 04-2「语言模型-神经语言模型」 | `raw/slides-2-neural-lm-seq2seq.pptx`（110 页） | 整份 P1-P110（FNN/RNN/LSTM/GRU/Seq2Seq） |

04-1 的 P1-P21（N-gram 基础、Zipf 律）已在第 6 讲讲过，本讲从 P22「平滑技术」开始。04-2 全部 110 页在本讲讲完。

## 三、讲节与 PPT 页映射

| 节 | 转写段落 | PPT 页 | 内容 |
| --- | --- | --- | --- |
| 第 1 节 | seg1 | 04-1 P22-P41 | 平滑技术：折扣（Laplace/Lidstone/Good-Turing/KN）、回退、差值 |
| 第 1 节 | seg1 | 04-1 P42-P51 | 语言模型评估：外部/内部评估、PPL、熵、分支因子 |
| 第 2 节 | seg2 | 04-2 P1-P62 | 神经语言模型：FNN（Bengio 2003）、RNN（Mikolov 2010）、LSTM、GRU |
| 第 3 节 | seg3 | 04-2 P63-P110 | Seq2Seq、序列标注（BiLSTM-CRF）、自编码器、注意力机制开头 |

## 四、文件清单

| 文件 | 说明 |
| --- | --- |
| `notes.md` | 主笔记（讲师思路 + 概念卡片 + 互动 + 例子） |
| `outline.md` | 思路大纲（mermaid 主线图 + 分层展开） |
| `questions.md` | 课堂问答与未解问题 |
| `corrections.md` | 转写勘误（PPT 原文核对） |
| `spinoffs.md` | 衍生选题（5 条，含发布状态索引） |
| `topics.json` | 选题结构化数据（版本 1，供问渠同步） |
| `labs/` | 实验（5 个） |
| `raw/` | 原始材料（转写 3 份 + PPT 2 份 + meta） |

## 五、一句话主线

> N-gram 的稀疏问题催生平滑（折扣/回退/差值），平滑的局限催生神经语言模型（FNN→RNN→LSTM→GRU），神经语言模型的序列能力催生 Seq2Seq，Seq2Seq 的瓶颈催生注意力——语言模型的每一步进化都在解决前一步的"天花板"。
