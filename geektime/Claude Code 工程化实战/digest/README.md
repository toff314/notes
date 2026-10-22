# 《Claude Code 工程化实战》消化索引（digest README）

> 本目录是《Claude Code 工程化实战》（讲师：黄佳）的结构化消化产物，生成于 2026-08-31。
> **本目录绝对路径**：`/home/yuanwu/geektime/output/Claude Code 工程化实战/digest/`
> **课程原文绝对路径**：`/home/yuanwu/geektime/output/Claude Code 工程化实战/<模块>/<讲>/`

## 写作前必读（按优先级）

1. **`course_review.json`** — 课程判决、四幕逐幕评价。任何写作任务先读它定位基调：高价值但需批判性消费的教程课，金矿藏在水份之下。
2. **`content_triage.json`** — 逐讲评分、四层分拣、数据审计。引用任何课程数据前必查：✅ 可引 / ⚠️ 标注语境 / ❓ / 🚩 禁用。
3. **`theme_articles/theme-001.json`** — 可直接成文的主题深挖素材包（多 Agent 选型）。

## 产出物总表

| 文件 | 内容 | 消费方式 |
|------|------|---------|
| `course_review.json` | 课程评论文素材（四幕结构） | 机读 |
| `theme_articles/theme-001.json` | 主题深挖文素材（多 Agent 选型，跨 5 讲） | 机读 |
| `study_guide.md` / `study_guide_slim.md` | 学习指南 / 5 分钟速览 | 人读 |
| `survey_notes.md` | 通览笔记（Adler 两问） | 人读 |
| `lecture_summaries.json` | 逐讲摘要（34 讲，含扫描数据） | 机读 |
| `content_triage.json` | 逐讲分拣+数据审计（金2/银17/铜10/铁5） | 机读 |

## 写作任务指引

### 写课程评论文
1. 读 `course_review.json` 的 acts / overall_assessment
2. 读 `content_triage.json` 的 data_audit（47 条声明：✅33 ⚠️10 ❓2 🚩2）
3. 叙事方向已给出：反差开场 → 四幕评价 → 数据边界诚实交代

### 写主题深挖文
1. 读 `theme_articles/theme-001.json` 的 narrative_arc / verification_gate
2. **verification_gate.avoid_claims 中的内容绝对禁止写进文章**（决策树阈值 50K tokens、Agent Teams 无量化成本）
3. 按其 source_lectures（04/03/07/08/hot-05）对应路径读讲课原文核对引文

### 写学习指南文
1. 读 `study_guide.md`（可直接作为文章骨架，含 Mermaid 概念图）
2. 读 `content_triage.json` 的 entries 获取逐讲分级

## 金矿讲课导航（可逐字引用）

| 讲 | 标题 | 原文绝对路径 |
|----|------|---------|
| hot-03 | 真相大白：源码泄露事故带来的架构验证与工程启示 | `/home/yuanwu/geektime/output/Claude Code 工程化实战/热点加餐（随技术趋势动态更新）/真相大白：源码泄露事故带来的架构验证与工程启示/真相大白：源码泄露事故带来的架构验证与工程启示.md` |
| 04 | 量体裁衣：从 Sub-Agents 到 Multi-Agent 的工程指南 | `/home/yuanwu/geektime/output/Claude Code 工程化实战/子代理（Sub-Agents）/04｜量体裁衣：从 Sub-Agents 到 Multi-Agent 的工程指南/04｜量体裁衣：从 Sub-Agents 到 Multi-Agent 的工程指南.md` |

## 数据可信度警示

以下声明**禁止**作为事实引用（🚩 可疑 / ❓ 无法验证）：

- token 利用率提升 98%（11 讲释题，🚩 无出处夸大，正文自认"大概估算"）
- 功能代码:安全代码≈1:3（hot-03，🚩 讲师经验估算）
- 27+ 平台 / 52,000+ Skills / Top Skills 安装量 180,000（14 讲，❓ 课程出版时点生态数据）
- Claude Code 81K stars / OpenCode 119K stars 月活 65 万+ / 10 亿美元年化收入（hot-02，❓ 无法独立验证）
- Claw-Code 2 小时 50K stars / Sigrid Jin 250 亿 token（hot-03，❓ 网络转述）
- 信噪比 50 行法则（06 讲，❓ 讲师经验值）
- 升级决策树阈值"工具<5、上下文<50K tokens"（04 讲，❓ 讲师经验值）

## 元信息

- 消化评分：2.92/5（🥇2 🥈17 🥉10 ⛏️5）
- 主题深挖文：1 篇（金矿 2 按决策表 0-1 篇取上限；金+银=19≥5 达标；overall SNR 2.92≥2.5 不减半）
- 数据审计：47 条声明 = ✅33（70%）/ ⚠️10（21%）/ ❓2（4%）/ 🚩2（4%）
