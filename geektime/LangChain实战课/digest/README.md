# 《LangChain实战课》消化索引（digest README）

> 本目录是《LangChain实战课》（讲师：黄佳）的结构化消化产物，生成于 2026-08-14。
> **本目录绝对路径**：`/home/yuanwu/geektime/output/LangChain实战课/digest/`
> **课程原文绝对路径**：`/home/yuanwu/geektime/output/LangChain实战课/<模块>/<讲>/`

## 写作前必读（按优先级）

1. **`course_review.json`** — 课程判决、三幕评价。任何写作任务先读它定位基调。
2. **`content_triage.json`** — 逐讲评分、四层分拣、数据审计。引用任何课程数据前必查。
3. **`theme_articles/`**（若存在）— 可直接成文的主题深挖素材包。

## 产出物总表

| 文件 | 内容 | 消费方式 |
|------|------|---------|
| `course_review.json` | 课程评论文素材（三幕结构） | 机读 |
| `theme_articles/theme-001.json` | 主题深挖文素材（CoT→ReAct 认知链） | 机读 |
| `study_guide.md` / `study_guide_slim.md` | 学习指南 / 5分钟速览 | 人读 |
| `survey_notes.md` | 通览笔记 | 人读 |
| `concept_map.mermaid` | 核心概念关系图 | 人读 |
| `lecture_summaries.json` | 逐讲摘要（Phase 1） | 机读 |
| `content_triage.json` | 逐讲分拣+数据审计（Phase 2） | 机读 |

## 写作任务指引

### 写课程评论文
1. 读 `course_review.json` 的 acts / overall_assessment
2. 读 `content_triage.json` 的 data_audit（64% 可验证 / 0 编造）

### 写主题深挖文
1. 列出 `theme_articles/` 全部文件，按主题选一篇
2. 读其 narrative_arc / verification_gate
3. **verification_gate.avoid_claims 中的内容绝对禁止写进文章**（如 $80.16 玫瑰价格）
4. 按其 source_lectures 对应路径读讲课原文核对引文

### 写学习指南文
1. 读 `study_guide.md`（可直接作为文章骨架）
2. 读 `content_triage.json` 的 entries 获取逐讲分级

## 金矿讲课导航（可逐字引用）

| 讲 | 标题 | 原文路径 |
|----|------|---------|
| 11 | 代理（上）：ReAct框架，推理与行动的协同 | `/home/yuanwu/geektime/output/LangChain实战课/基础篇/11｜代理（上）：ReAct框架，推理与行动的协同/11｜代理（上）：ReAct框架，推理与行动的协同.md` |

## 数据可信度警示

以下声明**禁止**作为事实引用（🚩 可疑 / ❓ 无法验证 / ⚠️ 时效性失效）：

- 美国一打玫瑰平均价 $80.16、夏威夷 $108.33、宾夕法尼亚 $66.15（第11/12讲，❓ 搜索引擎返回片段，无原始出处）
- Auto-GPT Star 数半年飙升 150K（第19讲，⚠️ 时效性快照）
- tree-of-thoughts repo 3.3K stars（第05讲，⚠️ 时效性快照）
- 大模型训练一次费用几百万美元（第06讲，⚠️ 估计值）
- CoT 在 GSM8K "达到当时最先进"（第05讲，⚠️ 无具体数字）

## 元信息

- 消化评分：2.7/5（🥇1 🥈10 🥉13 ⛏️5）
- 讲师：黄佳（新加坡科研局研究员）
- 总讲数：29
