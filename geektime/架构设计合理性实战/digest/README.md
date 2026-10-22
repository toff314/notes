# 《架构设计合理性实战》消化索引（digest README）

> 本目录是《架构设计合理性实战》（讲师：华仔，架构实战营模块3）的结构化消化产物，生成于 2026-08-31。
> **本目录绝对路径**：`/home/yuanwu/geektime/output/架构设计合理性实战/digest/`
> **课程原文绝对路径**：`/home/yuanwu/geektime/output/架构设计合理性实战/如何保证设计出合理的架构？/<讲>/
> ⚠️ 正文说明：各讲 .md 文件为 47 字节占位符，实际正文为同名 `_sub0.vtt` 字幕转录（已转 `_transcript.txt`）。

## 写作前必读（按优先级）

1. **`course_review.json`** — 课程判决、三幕逐幕评价（定位/方法论/实战）。任何写作任务先读它定位基调。
2. **`content_triage.json`** — 逐讲评分、四层分拣、9 条量化声明的数据审计。引用任何课程数据前必查 verification 状态。
3. **`theme_articles/theme-001.json`** — 可直接成文的主题深挖素材包（架构选型方法论）。

## 产出物总表

| 文件 | 内容 | 消费方式 |
|------|------|---------|
| `course_review.json` | 课程评论文素材（三幕评价+数据可信度审计） | 机读 |
| `theme_articles/theme-001.json` | 主题深挖文素材（架构选型：优先级排序评估法） | 机读 |
| `study_guide.md` | 完整学习指南（5 主题重组 + Mermaid 概念图 + 3 条阅读路线） | 人读 |
| `study_guide_slim.md` | 5 分钟速览 | 人读 |
| `survey_notes.md` | 通览笔记（Adler 两问 + 章节标题矩阵） | 人读 |
| `lecture_summaries.json` | 逐讲摘要（6 讲扫描数据） | 机读 |
| `content_triage.json` | 逐讲分拣 + 数据审计（gold 1 / silver 5） | 机读 |

## 写作任务指引

### 写课程评论文
1. 读 `course_review.json` 的 acts / overall_assessment / writing_direction
2. 读 `content_triage.json` 的 data_audit（9 条声明：✅1 ⚠️1 ❓6 🚩1）

### 写主题深挖文
1. 读 `theme_articles/theme-001.json` 的 narrative_arc / verification_gate
2. **verification_gate.avoid_claims 中的内容绝对禁止写进文章**（存储难度 100 倍、短信转化率、6 个月/2-3 年、15-16 台、性能量级无基线）
3. 按 source_lectures（03/05/06）对应路径读讲课原文核对引文：
   - `如何保证设计出合理的架构？/3. 架构设计中期应该怎么做？/…_transcript.txt`
   - `如何保证设计出合理的架构？/5. 消息队列备选架构设计实战/…_transcript.txt`
   - `如何保证设计出合理的架构？/6. 消息队列备选架构选择和细化实战/…_transcript.txt`

### 写学习指南文
1. 读 `study_guide.md`（可直接作为文章骨架）
2. 读 `content_triage.json` 的 entries 获取逐讲分级

## 金矿讲课导航（可逐字引用）

| 讲 | 标题 | 原文绝对路径 |
|----|------|---------|
| 06 | 消息队列备选架构选择和细化实战 | `/home/yuanwu/geektime/output/架构设计合理性实战/如何保证设计出合理的架构？/6. 消息队列备选架构选择和细化实战/6. 消息队列备选架构选择和细化实战_transcript.txt` |

## 数据可信度警示

以下声明**禁止**作为事实引用（🚩 可疑 / ❓ 无法验证）：

- 存储系统难度"业务功能 1 vs 存储 100"（第6讲，🚩 夸张比喻无出处）
- 短信转化率 1-2%、实际访问量 5000 多（第1讲，❓ 讲师经验）
- 澳X通项目 3 个月开发/6 个月监管上线（第2讲，❓ 个人案例）
- 自研存储 0→1 要 6 个月、成熟 2-3 年（第6讲，❓ 经验判断）
- 自研服务器 15-16 台（第6讲，❓ 个人案例）
- Kafka 4-5 万 vs MySQL 3-4 万 vs 自研 2-4 千性能量级（第6讲，⚠️ 量级常识无基线，引用须标注）

## 元信息

- 消化评分：3.56/5（🥇1 🥈5 🥉0 ⛏️0）
- 处理文章数：6（正文为 vtt 转录，.md 为占位符）
- 主题深挖文：1 篇（金矿 1 → 决策表 0-1 篇；金矿+银矿 6 ≥ 5，SNR 3.56 ≥ 2.5 不减半）
