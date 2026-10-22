# 《AI原生开发工作流实战》消化索引（digest README）

> 本目录是《AI原生开发工作流实战》（讲师：Tony Bai）的结构化消化产物，生成于 2026-08-14。
> **本目录绝对路径**：`/home/yuanwu/geektime/output/AI原生开发工作流实战/digest/`
> **课程原文绝对路径**：`/home/yuanwu/geektime/output/AI原生开发工作流实战/<模块>/<讲>/`

## 写作前必读（按优先级）

1. **`course_review.json`** — 课程判决、逐幕评价。任何写作任务先读它定位基调。
2. **`content_triage.json`** — 逐讲评分、四层分拣、数据审计。引用任何课程数据前必查。
3. **`theme_articles/`** — 可直接成文的主题深挖素材包（共 2 篇）。

## 产出物总表

| 文件 | 内容 | 消费方式 |
|------|------|---------|
| `course_review.json` | 课程评论文素材（三幕结构+整体评估） | 机读 |
| `theme_articles/theme-001.json` | 主题深挖：规范驱动开发（SDD）第一性原理 | 机读 |
| `theme_articles/theme-002.json` | 主题深挖：AI 能力封装四象限选型 | 机读 |
| `study_guide.md` | 完整学习指南（按主题重组） | 人读 |
| `study_guide_slim.md` | 5 分钟速览 | 人读 |
| `survey_notes.md` | 课程通览笔记 | 人读 |
| `lecture_summaries.json` | 逐讲摘要（Phase 1 中间产物） | 机读 |
| `content_triage.json` | 逐讲分拣 + 数据审计（Phase 2 产物） | 机读 |
| `concept_map.mermaid` | 课程核心概念关系图 | 机读（Mermaid） |

## 写作任务指引

### 写课程评论文
1. 读 `course_review.json` 的 `narrative_structure.acts` / `overall_assessment`
2. 读 `content_triage.json` 的 `data_audit`（13 个量化声明，仅 15% 可验证）

### 写主题深挖文
1. 列出 `theme_articles/` 全部文件，按主题选一篇
2. 读其 `narrative_arc` / `verification_gate`
3. **`verification_gate.avoid_claims` 中的内容绝对禁止写进文章**
4. 按其 `source_lectures` 对应路径读讲课原文核对引文

### 写学习指南文
1. 读 `study_guide.md`（可直接作为文章骨架）
2. 读 `content_triage.json` 的 `entries` 获取逐讲分级

## 金矿讲课导航（可逐字引用）

| 讲 | 标题 | 原文路径 |
|----|------|---------|
| 02 | 核心引擎：AI原生开发第一性原理——规范驱动开发 | `/home/yuanwu/geektime/output/AI原生开发工作流实战/概念篇：建立AI原生世界观/02｜核心引擎：AI原生开发第一性原理——规范驱动开发/02｜核心引擎：AI原生开发第一性原理——规范驱动开发.md` |
| 13 | 智能涌现的基石：精通Agent Skills | `/home/yuanwu/geektime/output/AI原生开发工作流实战/进阶篇：将AI锻造成你的专属能力/13｜智能涌现的基石：精通Agent Skills，为AI植入专家能力/13｜智能涌现的基石：精通Agent Skills，为AI植入专家能力.md` |
| 19 | 编码与测试：AI驱动的TDD与框架能力的协同作战 | `/home/yuanwu/geektime/output/AI原生开发工作流实战/实战篇：在真实项目中重塑工程实践/19｜编码与测试：AI驱动的TDD与框架能力的协同作战/19｜编码与测试：AI驱动的TDD与框架能力的协同作战.md` |
| 速递2 | 告别"方言"：Agent Skills 行业标准与高阶心法 | `/home/yuanwu/geektime/output/AI原生开发工作流实战/前沿技术速递/前沿技术速递｜告别“方言”：全面解析 Agent Skills 行业标准与高阶编写心法/前沿技术速递｜告别“方言”：全面解析 Agent Skills 行业标准与高阶编写心法.md` |

## 数据可信度警示

以下声明**禁止**作为事实引用（🚩 可疑 / ❓ 无法验证）：

- "你的知识体系已经领先于业界 90% 的开发者"（结束语，🚩 营销性夸大）
- "维护与重构占软件工程师超过 70% 的工作时间"（第22讲，❓ 无出处）
- "传统模式 70-80% 时间花在编码与实现"（第01讲，❓ 无出处）
- "传统模式 80% 时间花在将需求翻译成代码"（开篇词，❓ 无出处）
- 各类演示输出（184 任务、23 测试用例、31.2MB 镜像、cost 0.1857 USD）为环境特定数据，不可当普遍结论（⚠️）

## 元信息

- 消化评分：3.2/5（🥇4 🥈20 🥉2 ⛏️2）
- 总讲数：28
- 主题文：2 篇（金矿数 4 → 1-2 篇区间）
