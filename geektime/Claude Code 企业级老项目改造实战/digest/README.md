# 《Claude Code 企业级老项目改造实战》消化索引（digest README）

> 本目录是《Claude Code 企业级老项目改造实战》（讲师：Robert）的结构化消化产物，生成于 2026-08-31。
> **本目录绝对路径**：`/home/yuanwu/geektime/output/Claude Code 企业级老项目改造实战/digest/`
> **课程原文绝对路径**：`/home/yuanwu/geektime/output/Claude Code 企业级老项目改造实战/<模块>/<讲>/`

## 写作前必读（按优先级）

1. **`course_review.json`** — 课程判决、三幕逐幕评价（方法论地基 / 实战闭环 / 方法论迁移）。任何写作任务先读它定位基调。
2. **`content_triage.json`** — 37 讲逐讲评分、四层分拣、Adler 四问、数据审计。引用任何课程数据前必查 verification 状态。
3. **`theme_articles/`**（3 篇）— 可直接成文的主题深挖素材包（含 verification_gate 数据闸门）。

## 产出物总表

| 文件 | 内容 | 消费方式 |
|------|------|---------|
| `course_review.json` | 课程评论文素材（三幕结构+数据可信度+ROI） | 机读 |
| `theme_articles/theme-001.json` | 主题文：Characterization Test 安全网（跨 05/14/15/19） | 机读 |
| `theme_articles/theme-002.json` | 主题文：人是最后的兜底员翻车复盘（跨 17/20/22） | 机读 |
| `theme_articles/theme-003.json` | 主题文：两段式翻译需求方法论（跨 17/18/25） | 机读 |
| `study_guide.md` | 完整学习指南（5 主题重组+Mermaid 概念图） | 人读 |
| `study_guide_slim.md` | 5 分钟速览（一核心/三框架/五方法/一反直觉） | 人读 |
| `survey_notes.md` | 课程通览（模块地图+章节矩阵+Adler 两问） | 人读 |
| `lecture_summaries.json` | 37 讲逐讲摘要（首尾 200 字+标题+风险信号） | 机读 |
| `content_triage.json` | 37 讲逐讲分拣+数据审计（Phase 2 核心产物） | 机读 |

## 写作任务指引

### 写课程评论文
1. 读 `course_review.json` 的 narrative_structure.acts / overall_assessment / writing_direction
2. 读 `content_triage.json` 的 data_audit 获取数据可信度结论
3. 可选标题灵感已内置：`title_idea` 字段

### 写主题深挖文
1. 列出 `theme_articles/` 全部文件，按主题选一篇
2. 读其 narrative_arc（三幕结构）/ verification_gate / search_keywords
3. **verification_gate.avoid_claims 中的内容绝对禁止写进文章**
4. 按其 source_lectures 对应路径读讲课原文核对引文

### 写学习指南文
1. 读 `study_guide.md`（可直接作为文章骨架）
2. 读 `content_triage.json` 的 entries 获取逐讲分级与金句

## 金矿讲课导航（可逐字引用）

| 讲 | 标题 | 原文绝对路径 |
|----|------|---------|
| 15 | 补出一套兜底测试：让 AI 用 Characterization Test 锁住行为 | `/home/yuanwu/geektime/output/Claude Code 企业级老项目改造实战/运行和测试：编译、测试、建立护栏/15｜补出一套兜底测试：让 AI 用 Characterization Test 锁住行为/15｜补出一套兜底测试：让 AI 用 Characterization Test 锁住行为.md` |
| 17 | 从一句话需求到需求文档：让 AI 帮你拆需求 | `/home/yuanwu/geektime/output/Claude Code 企业级老项目改造实战/需求改造：给 Spring AI Alibaba Admin 加新功能/17｜从一句话需求到需求文档：让 AI 帮你拆需求/17｜从一句话需求到需求文档：让 AI 帮你拆需求.md` |
| 20 | 执行改造（下）：前端开发和接口对接 | `/home/yuanwu/geektime/output/Claude Code 企业级老项目改造实战/需求改造：给 Spring AI Alibaba Admin 加新功能/20｜执行改造（下）：前端开发和接口对接/20｜执行改造（下）：前端开发和接口对接.md` |
| 22 | 核心五问：这门课的思路是如何解决问题的？ | `/home/yuanwu/geektime/output/Claude Code 企业级老项目改造实战/阶段总结复盘/22｜核心五问：这门课的思路是如何解决问题的？/22｜核心五问：这门课的思路是如何解决问题的？.md` |
| 25 | 两次翻译：把"基于 Hermes Agent 的自动化测试"拆成技术方案 | `/home/yuanwu/geektime/output/Claude Code 企业级老项目改造实战/二次开发：基于 Hermes Agent 做自动化测试/25｜两次翻译：把“基于 Hermes Agent 的自动化测试”拆成技术方案/25｜两次翻译：把“基于 Hermes Agent 的自动化测试”拆成技术方案.md` |

## 数据可信度警示

以下声明**禁止**作为事实引用（🚩 可疑 / ❓ 无法验证）：

- **🚩 可疑（无出处且过于精确）**：
  - "Dumb Zone：context 使用率超 40% 输出质量下降"（05 讲，FIU 研究无原始链接）
  - "跑了流程效果还是不好，99% 的原因是该停的地方没停"（22 讲，绝对化无数据）
- **❓ 无法验证（讲师经验型估计）**：
  - "70% 时间理解、30% 动手"（01 讲）
  - "AI 主导做 80% / 对半 50% / 人主导 20%"（02 讲）
  - "AI 强维度 85+ 分、中 60 分、弱 30 分以下"（17 讲）
  - "三步拆需求 20 分钟、比手写省 2 小时"（17 讲）
  - "AI 覆盖 70%、人补 30%"（17/22 讲）
  - "Anthropic 52 人实验：AI 组理解测试低 17%"（05 讲）
  - "Thoughtworks CodeConcise：COBOL 逆向时间减 66%"（05 讲）
  - "CodeMap 降低 LLM 依赖 79%"（05 讲，论文存在但数值未核实）
  - "30 分钟 CI 换上千次自动检查"（15 讲）
  - "自研成本比工具函数大好几倍 / 0.2x"（25 讲）
  - "代码层 80% 能搬、业务层完全重写"（28 讲）
- **⚠️ 部分验证（来源真实，数值需回原始报告核实）**：
  - "Sonar 调查：42% 代码 AI 生成 / 96% 不信任 / 48% 每次 review"（05 讲）
  - "Veracode 2025：45% AI 生成代码引入安全漏洞"（05 讲）
  - "Anthropic $100M Partner Network + Code Modernization Starter Kit"（05 讲）
  - "Cleveroad 三个失败模式"（05 讲）

## 元信息

- 消化评分：**2.82/5**（🥇5 🥈10 🥉17 ⛏️5）
- 金矿占比 13.5%（符合 10-15% 目标），金矿+银矿 15 讲 → 主题深挖文 3 篇（决策表：金矿 5-7 → 2-3 篇；总体 SNR 2.82 ≥ 2.5 不减半）
- 量化声明可信度：全课 18 条声明中仅 1 条完全可验证（6%），11 条无法独立验证（61%）
