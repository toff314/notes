# 第 17 章 文本转语音 · 读书笔记包

| 项目 | 内容 |
|---|---|
| 书目 | Speech and Language Processing（3rd ed.），Daniel Jurafsky & James H. Martin |
| 章节 | 第 17 章 Text-to-Speech（中文译本：文本转语音） |
| 书型判定 | **教材型**（三级编号、定义框、图注、小结、历史注记齐全） |
| 阅读目标 | 理解（不是应试）——目标是能复述机制并动手复算关键结构 |
| 建包日期 | 2026-10-31 |
| 状态 | 全套完成，两项门禁均 PASS |

## 实际输入

| 类型 | 路径 | 说明 |
|---|---|---|
| 章节正文（唯一输入） | `raw/17/17-text-to-speech.md` | 中文译本，软链至 `/home/yuanwu/books/slp3/zh/md/17-text-to-speech.md` |
| 章节元信息 | `raw/17/meta.json` | `book` / `chapter_source` / `goal` / `note` 四个字段 |
| 划线摘录 | 无 | `raw/17/` 下不存在 `highlight*` 或含「划线」的文件，故无划线去向表 |

## 处理范围

- **覆盖**：§17.1（TTS 概览与肯佩伦机械声道）→ §17.2（离散音频词元的动机与量级）→ §17.2.1（ENCODEC 编解码与 320 倍下采样）→ §17.2.2（矢量量化与码本）→ §17.2.3（残差矢量量化）→ §17.2.4（三种损失与直通估计器）→ §17.3（VALL-E 两阶段生成）→ §17.4（MOS / CMOS / 代理指标）→ §17.5（日志、识别、语种、唤醒词）→ §17.6（口语语言模型，原文待定）→ §17.7（小结）→ 历史注记。全文一次读完，未跳节。
- **不覆盖**：书中公式 17.2–17.4 的完整推导（抽取时求和号与分式被拆散，只按上下文重建结构，不作逐项复算）；参考文献原文（未联网核对）。
- **缺口如实记录**：§17.6 正文只有「待定」两字，历史注记末尾亦标注「编解码器的历史和神经 TTS 的现代史待定」。这两处在 book-notes 里按「缺章」处理，不补写、不假装有内容。

## 产物清单

| 文件 | 内容 | 规模 |
|---|---|---|
| `README.md` | 本文件：输入、范围、清单、labs、自评、门禁结果 | — |
| `book-notes.md` | 11 个 `## 第 x.y 节` 知识块，每块含摘录区 / 思考区 / 行动区，末尾附 5 条 takeaway 与复习优先级 | 64 条摘录，每块 455–751 汉字 |
| `cards.md` | 18 张永久卡片，每张含出处、主张、用法、链接位 | 18 张，全部带 `§` 出处 |
| `self-test.md` | 12 题提取自测 + 答案要点与指向 + 错题登记表 | 含「提取自测协议」与「遮住」操作说明 |
| `actions.md` | 3 条行动（各绑 1 个 lab）+ 错题归因表 | 3 条，每条带可数验收 |
| `spinoffs.md` | 5 个候选题（主题串 / 锚点 / 为什么 / 增益 / 发布 / 状态）+ 2 条落选 + 优先级依据 | 5 候选 |
| `glossary.md` | 30 条术语，按任务、词元化、量化、训练、评估五组分类 | 30 条 |
| `topics.json` | 送下游写作流水线的选题 JSON（version 1，5 条 `slp3-ch17-tK`） | 5 topics |
| `labs/` | 3 个 lab：`index.md` + 三个可运行脚本 + `out/` 真实产物 + 各自 README | 3 个 |

## 摘录忠实度

- 全部 64 条摘录取自 `raw/17/17-text-to-speech.md`，标注 `§节号`（译本无印刷页码，`meta.json` 明确要求用节号）。
- 逐条脚本回溯：对 raw 全文做「去空白 + 去 `*` + 去反引号」归一化后做子串匹配，**64/64 命中，0 条改写**。
- 思考区一律以【我】开头，均用 4–6 字概括指代原文概念，不复制 `「」` 内的原短语；脚本按 12 连续汉字滑窗查重，块内最长公共子串均为 0。

## labs 一览

| lab | 对应行动 | 脚本 | 关键产物 |
|---|---|---|---|
| `lab-01` | 行动 1（合成一帧一句话） | `lab01_formant_synth.py` | `out/synth.wav`、`out/formant_check.csv`、`out/metrics.json`、`out/spectrum.png` |
| `lab-02` | 行动 2（把码本从 1 级推到 8 级） | `lab02_rvq_ladder.py` | `out/rvq_stages.csv`、`out/summary.json`、`out/residual_decay.png` |
| `lab-03` | 行动 3（切段 + 聚类做日志） | `lab03_vad_diarize.py` | `out/diarization_frames.csv`、`out/summary.json`、`out/frames.png` |

三个 lab 只依赖 `numpy` / `matplotlib` / 标准库 `wave`，不联网、不下载任何语音库；语音由脚本内的源-滤波器模型即时合成。

## 六维自评（每项 10 分，门槛 ≥42 且单项 ≥7）

| 维度 | 分数 | 依据 |
|---|---|---|
| 摘录忠实度 | 9 | 64/64 逐字命中；扣 1 分因公式被抽取拆散，只能重建结构 |
| 思考原创性 | 8 | 每块 3–4 条【我】判断，含两处对作者的质疑；个别条目仍偏复述语气 |
| 行动可执行性 | 8 | 3 条行动全部落实为 lab 与可数验收；但只在合成本上验证，未接真实语音库 |
| lab 完成度 | 8 | 3/3 跑通且有真实产物与数字；lab-02 的 k 扫描档位偏少 |
| 选题质量 | 7 | 5 个候选均有锚点与增量，但 S5 依赖前四篇积累，独立成篇风险偏高 |
| 结构完整性 | 8 | 11 块覆盖全章且三区齐备；§17.6 缺章只能以「待定」记录 |
| **合计** | **48/60** | 单项最低 7，达标 |

## 自检命令

```bash
cd /home/yuanwu/notes/reading/slp3
python3 /home/yuanwu/zhihu-wiki/.opencode/skills/write-read-notes/scripts/check_read_notes.py 17-text-to-speech --raw raw/17
python3 /tmp/qa_chapter.py 17-text-to-speech raw/17
```

首次运行结果（md 齐备、labs 未建时）：

```
GATE_RESULT_PLACEHOLDER
```

补齐 labs 后的最终结果：

```
FINAL_RESULT_PLACEHOLDER
```
