# 《Claude Code 企业级全链路开发实战》消化索引（digest README）

> 本目录是《Claude Code 企业级全链路开发实战》（讲师：Robert）的结构化消化产物，生成于 2025-08-25。
> **本目录绝对路径**：`/home/yuanwu/geektime/output/Claude Code 企业级全链路开发实战/digest/`
> **课程原文绝对路径**：`/home/yuanwu/geektime/output/Claude Code 企业级全链路开发实战/<模块>/<讲>/`

## 写作前必读（按优先级）

1. **`course_review.json`** — 课程判决、逐幕评价、who_should_read/skip。任何写作任务先读它定位基调。
2. **`content_triage.json`** — 逐讲评分、四层分拣（金/银/铜/铁）、数据审计。引用任何课程数据前必查。
3. **`theme_articles/`** — 三篇可直接成文的主题深挖素材包（SDD 方法论全景 / 角色重构 / 陌生技术探路法）。

## 产出物总表

| 文件 | 内容 | 消费方式 |
|------|------|---------|
| `course_review.json` | 课程评论文素材（三幕评价 + 整体判决） | 机读 |
| `theme_articles/theme-001.json` | SDD 规范驱动开发方法论全景 | 机读 |
| `theme_articles/theme-002.json` | 角色重构：从写代码到做决策 | 机读 |
| `theme_articles/theme-003.json` | 陌生技术探路法 | 机读 |
| `study_guide.md` | 完整学习指南（按主题重组 + Mermaid 图） | 人读 |
| `study_guide_slim.md` | 5 分钟速览 | 人读 |
| `survey_notes.md` | 通览笔记（Adler 两问 + 模块地图） | 人读 |
| `lecture_summaries.json` | 逐讲摘要（37 讲机器数据） | 机读 |
| `content_triage.json` | 逐讲分拣 + 数据审计 | 机读 |

## 写作任务指引

### 写课程评论文
1. 读 `course_review.json` 的 `narrative_structure.acts` 和 `overall_assessment`
2. 读 `content_triage.json` 的 `data_audit`，核对引用的数据可信度

### 写主题深挖文
1. 列出 `theme_articles/` 全部文件，按主题选一篇
2. 读其 `narrative_arc`（三幕）/ `verification_gate` / `controversy_hooks`
3. **`verification_gate.avoid_claims` 中的内容绝对禁止写进文章**
4. 按其 `source_lectures` 对应路径读讲课原文核对引文

### 写学习指南文
1. 读 `study_guide.md`（可直接作为文章骨架）
2. 读 `content_triage.json` 的 `entries` 获取逐讲分级

## 金矿讲课导航（可逐字引用）

| 讲 | 标题 | 原文绝对路径 |
|----|------|---------|
| 02 | 规范驱动开发（SDD） | `/home/yuanwu/geektime/output/Claude Code 企业级全链路开发实战/认知篇/02｜规范驱动开发（SDD）：让 AI 永远在轨道上/02｜规范驱动开发（SDD）：让 AI 永远在轨道上.md` |
| 14 | 把经验变成 Skill | `/home/yuanwu/geektime/output/Claude Code 企业级全链路开发实战/核心功能交付：基础篇/14｜把经验变成 Skill：让 Claude Code 自动按流程走/14｜把经验变成 Skill：让 Claude Code 自动按流程走.md` |
| 27 | AI 写代码保证质量靠体系 | `/home/yuanwu/geektime/output/Claude Code 企业级全链路开发实战/测试与部署篇/27｜AI 写代码，保证质量不靠运气，靠体系/27｜AI 写代码，保证质量不靠运气，靠体系.md` |
| 31 | SDD/Spec-Kit/老项目改造 | `/home/yuanwu/geektime/output/Claude Code 企业级全链路开发实战/高阶与复盘/31｜进阶：SDD、Spec-Kit、Spec Coding 与老项目改造/31｜进阶：SDD、Spec-Kit、Spec Coding 与老项目改造.md` |
| 32 | 局限与起点 | `/home/yuanwu/geektime/output/Claude Code 企业级全链路开发实战/高阶与复盘/32｜局限与起点：让 Hify 成为你真正的项目经验/32｜局限与起点：让 Hify 成为你真正的项目经验.md` |

## 数据可信度警示

以下声明**禁止**作为事实引用（❓ 无法验证 / ⚠️ 部分验证）：

- 双模型 review 抓出 12 个问题、4 个高危（第 27 讲，❓ 讲师个人实践，无独立来源）
- Claude 订阅约 $40/月（第 32 讲语境，❓ 个人陈述，无法精确定位）
- Hify 峰值 QPS 3-5（第 03 讲，❓ 基于假设的内部估算，无实测）
- LLM 单次响应延迟 3-30 秒（第 03 讲，⚠️ 行业经验值，非精确数据）

> 本课无 🚩 编造数据。可放心引用的 ✅ 数据：源码泄漏 51.2 万行/1900 文件、阿里禁用 Claude Code、text-embedding-3-small 价格约前代 1/5。

## 元信息

- 消化评分：2.98/5（🥇金矿 5 · 🥈银矿 17 · 🥉铜矿 13 · ⛏️铁矿 2）
- 总讲数：37
- 讲师：Robert
- 课程定位：用 Claude Code 从零造简版 Dify（Hify），教"用 AI 做工程"的方法论
