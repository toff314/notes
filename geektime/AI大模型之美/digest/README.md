# 《AI大模型之美》消化索引（digest README）

> 本目录是《AI大模型之美》（讲师：徐文浩）的结构化消化产物，生成于 2026-08-14。
> **本目录绝对路径**：`/home/yuanwu/geektime/output/AI大模型之美/digest/`
> **课程原文绝对路径**：`/home/yuanwu/geektime/output/AI大模型之美/<模块>/<讲>/`

## 写作前必读（按优先级）

1. **`course_review.json`** — 课程判决、逐幕评价、ROI 评估。任何写作任务先读它定位基调。
2. **`content_triage.json`** — 逐讲评分、四层分拣、数据审计。引用任何课程数据前必查。
3. **`theme_articles/`**（若存在）— 可直接成文的主题深挖素材包。

## 产出物总表

| 文件 | 内容 | 消费方式 |
|------|------|---------|
| `course_review.json` | 课程评论文素材（三幕+加餐结构，含 data_credibility_flags） | 机读 |
| `theme_articles/theme-001.json` | 主题深挖文素材：第二大脑/RAG 模式 | 机读 |
| `study_guide.md` / `study_guide_slim.md` | 学习指南 / 5 分钟速览 | 人读 |
| `survey_notes.md` | 通览笔记 | 人读 |
| `lecture_summaries.json` | 逐讲摘要 | 机读 |
| `content_triage.json` | 逐讲分拣 + 数据审计 | 机读 |
| `concept_map.mermaid` | 概念关系图 | 人读 |

## 写作任务指引

### 写课程评论文
1. 读 `course_review.json` 的 acts / overall_assessment / writing_direction
2. 读 `content_triage.json` 的 data_audit

### 写主题深挖文
1. 列出 `theme_articles/` 全部文件，按主题选一篇
2. 读其 narrative_arc / verification_gate
3. **verification_gate.avoid_claims 中的内容绝对禁止写进文章**
4. 按其 source_lectures 对应路径读讲课原文核对引文

### 写学习指南文
1. 读 `study_guide.md`（可直接作为文章骨架）
2. 读 `content_triage.json` 的 entries 获取逐讲分级

## 金矿讲课导航（可逐字引用）

| 讲 | 标题 | 原文路径 |
|----|------|---------|
| 10 | AI连接外部资料库，让Llama Index带你阅读一本书 | `/home/yuanwu/geektime/output/AI大模型之美/实战提高篇（一）：利用NLP技术完成高级任务/10｜AI连接外部资料库，让Llama Index带你阅读一本书/10｜AI连接外部资料库，让Llama Index带你阅读一本书.md` |
| 13 | 让AI帮你写测试，体验多步提示语 | `/home/yuanwu/geektime/output/AI大模型之美/实战提高篇（一）：利用NLP技术完成高级任务/13 ｜让AI帮你写测试，体验多步提示语/13 ｜让AI帮你写测试，体验多步提示语.md` |

## 数据可信度警示

以下声明**禁止**作为事实引用（❓ 无法验证 / ⚠️ 部分验证）：

- GPT-3 训练语料中中文占比不到 1%（第10讲，❓ 无精确出处）
- 「text-davinci-003 比 gpt-3.5-turbo 贵十倍」（第10讲，⚠️ 近似数且模型已废弃）
- 零样本情感分析 96% 准确率（第2讲，⚠️ 单数据集单次运行，且差评召回率仅73%）
- Midjourney「十几人团队、1亿美元年收入、无融资」（第27讲，⚠️ 未经官方确认）

## 元信息

- 消化评分：2.79/5（🥇2 🥈11 🥉16 ⛏️5）
