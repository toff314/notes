# 第 6 讲 · 从 Skip-Gram 到 N-Gram

> 计算语言学基础（李蕾）第 6 讲听课笔记包。

## 一、本讲信息

| 项 | 内容 |
| --- | --- |
| 讲次 | 第 6 讲（连上第 5 讲之后，本章第 3 部分收尾 + 第 4 部分开头） |
| 主题 | Skip-Gram、负采样、GloVe、词向量评估与应用、N-gram 语言模型与数据稀疏 |
| 时长覆盖 | 转写稿 910 行 / 34,993 汉字 |
| 来源 | 飞书 wiki `HOQfwE5YfiYN4SkaqqrcmNn7nQh`（标题：自然语言基础6） |
| 音频分段 | 3 段（block 1 / 320 / 322 处的 `1` `2` `3` 标记） |

## 实际输入

- 转写文件：`raw/transcript.md`（飞书 wiki 导出，910 行 / 34,993 汉字）
- 课件文件：`raw/slides-1-skipgram-negativesampling.pptx`（P35–P65 用于本讲）、`raw/slides-2-word-vector-development.pptx`（P1–P43）、`raw/slides-3-ngram-language-model.pptx`（P1–P18）
- 元数据：`raw/meta.json`（页数、页码映射、未使用页范围）

## 二、三源对照（本讲未降级，G1 可判 PASS）

| # | 源 | 本地文件 | 覆盖范围 |
| --- | --- | --- | --- |
| 1 | 语音转写 | `raw/transcript.md` | 全讲 |
| 2 | PPT 03-2「词语义表示-向量方法」 | `raw/slides-1-skipgram-negativesampling.pptx`（65 页） | 本讲从 P35 讲到 P65 |
| 3 | PPT 03-3「词语义表示-词向量发展」 | `raw/slides-2-word-vector-development.pptx`（43 页） | 整份 P1–P43 |
| 4 | PPT 04-1「语言模型-N-gram」 | `raw/slides-3-ngram-language-model.pptx`（51 页） | 本讲从 P1 讲到 P18 |

三份 PPT 在同一堂连课内连续讲完，转写稿 L455 有切换提示（"刚才这个是 03-2，还有一个 03-3"）。04-1 的 P19–P51（Zipf 律、增加语料、各类平滑）本讲未涉及，留待第 7 讲。

## 三、产物清单（七件套 + 元数据）

| 文件 | 作用 |
| --- | --- |
| `notes.md` | 正文笔记，10 节，每节"一句话总结"开头，结论带【师】行号 /【PPT】页号双锚点 |
| `outline.md` | 主线 mermaid 图 + 分段地图（行号↔PPT 页）+ 三条支线 |
| `questions.md` | 课上真问过、真没答的问题，含老师自陈"我也不是很确定"处 |
| `corrections.md` | 19 条转写勘误，逐条标行号与依据；另列 2 处"课堂未定论" |
| `spinoffs.md` | 6 个衍生选题，四条判据逐项过筛，含索引表 |
| `my-notes.md` | 占位 + 三源交叉流程 + 待填槽位（未伪造课堂心得） |
| `topics.json` | 6 条选题，id 前缀 `computational-linguistics-lec06-tN` |
| `raw/meta.json` | 转写与 PPT 的页数、页码映射、未使用范围登记 |

## 四、阅读顺序建议

1. 先看 `outline.md` 的分段地图，建立"哪一节对应哪几页 PPT"的地图。
2. 读 `notes.md`，遇到数字想核对就翻 `raw/slides-*.pptx` 对应页。
3. `questions.md` 与 `my-notes.md` 的困惑清单合用，作为下次课前的问题集。
4. `spinoffs.md` 用于排后续写作计划。

## 五、已知缺口

- `notes.md` 中 GloVe 概率表的 `p(water|ice)`、`p(water|steam)` 两格转写含混，PPT 该页为图片，未强行补数，已标"转写含混"。
- 负采样采样池（词表 or 语料）课堂未定论，见 `corrections.md` 末节。
- 同学分享部分（L832–L905）非教师主讲，仅在 `notes.md` 附记中保留要点，未纳入选题判据。
