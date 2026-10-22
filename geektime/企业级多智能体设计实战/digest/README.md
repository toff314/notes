# 《企业级多智能体设计实战》消化索引（digest README）

> 本目录是《企业级多智能体设计实战》（讲师：晓寒）的结构化消化产物，生成于 2026-08-14。
> **本目录绝对路径**：`/home/yuanwu/geektime/output/企业级多智能体设计实战/digest/`
> **课程原文绝对路径**：`/home/yuanwu/geektime/output/企业级多智能体设计实战/<模块>/<讲>/`

## 写作前必读（按优先级）

1. **`course_review.json`** — 课程判决、逐幕评价。任何写作任务先读它定位基调。
2. **`content_triage.json`** — 逐讲评分、四层分拣、数据审计。引用任何课程数据前必查。
3. **`theme_articles/`**（若存在）— 可直接成文的主题深挖素材包（共 3 篇）。

## 产出物总表

| 文件 | 内容 | 消费方式 |
|------|------|---------|
| `course_review.json` | 课程评论文素材（四幕评价） | 机读 |
| `theme_articles/theme-001.json` | 主题深挖：从 Orchestrator 到数字员工团队 | 机读 |
| `theme_articles/theme-002.json` | 主题深挖：Prompt 管不了 Agent 安全 | 机读 |
| `theme_articles/theme-003.json` | 主题深挖：AI 项目失败的第一原因是选题 | 机读 |
| `study_guide.md` / `study_guide_slim.md` | 学习指南 / 速览 | 人读 |
| `survey_notes.md` | 通览笔记 | 人读 |
| `lecture_summaries.json` | 逐讲摘要 | 机读 |
| `content_triage.json` | 逐讲分拣+数据审计 | 机读 |
| `concept_map.mermaid` | 概念关系图 | 人读（渲染） |

## 写作任务指引

### 写课程评论文
1. 读 `course_review.json` 的 acts / overall_assessment
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
| 23 | Orchestrator范式 | `/home/yuanwu/geektime/output/企业级多智能体设计实战/模块四：协作与设计模式，掌握5大架构设计模式/23｜Orchestrator范式：任务层的主 Agent + 子 Agent/23｜Orchestrator范式：任务层的主 Agent + 子 Agent.md` |
| 26 | 任务链与信息传递 | `/home/yuanwu/geektime/output/企业级多智能体设计实战/模块四：协作与设计模式，掌握5大架构设计模式/26｜任务链与信息传递：数字员工的协作协议/26｜任务链与信息传递：数字员工的协作协议.md` |
| 27 | Human as 甲方 | `/home/yuanwu/geektime/output/企业级多智能体设计实战/模块四：协作与设计模式，掌握5大架构设计模式/27｜Human as 甲方：如何设计 Agent 团队的人类介入点/27｜Human as 甲方：如何设计 Agent 团队的人类介入点.md` |
| 28 | 数字员工的自我进化 | `/home/yuanwu/geektime/output/企业级多智能体设计实战/模块四：协作与设计模式，掌握5大架构设计模式/28｜数字员工的自我进化：让 Agent 团队越用越好/28｜数字员工的自我进化：让 Agent 团队越用越好.md` |
| 34 | 需求边界 | `/home/yuanwu/geektime/output/企业级多智能体设计实战/生产交付篇：全生命周期工程化/34｜需求边界：如何使用 AI 适用性评估表识别高 ROI 场景？/34｜需求边界：如何使用 AI 适用性评估表识别高 ROI 场景？.md` |
| 36 | 评测体系 | `/home/yuanwu/geektime/output/企业级多智能体设计实战/生产交付篇：全生命周期工程化/36｜评测体系：让AI质量可量化/36｜评测体系：让AI质量可量化.md` |

## 数据可信度警示

以下声明**禁止**作为事实引用（🚩 可疑 / ❓ 无法验证）：

- 629 次安全测试劫持成功率 80%（第 32 讲，🚩 精确数值无来源且被反复引用）
- Galileo+PwC 独立验收 70% vs 10%（第 23 讲，⚠️ 无原始报告）
- Google DeepMind 误差放大 17.2 倍（第 23 讲，❓ 无出处）
- MAST inter-agent 误对齐 37%（第 26 讲，❓ 无出处）
- 约 15% 云端 Skill 藏木马（第 32 讲，❓ 无出处）
- Agent 死循环 264 小时烧 $70,000+（第 30 讲，❓ 轶事）
- Anthropic 1协调者+3-5专家提升 90%+（第 25 讲，❓ 无出处）

## 元信息

- 消化评分：3.0/5（🥇6 🥈15 🥉16 ⛏️7）
- 数据审计：37 个量化声明中 14 个可验证（38%）、7 个部分验证（19%）、15 个无法验证（40%）、1 个可疑（3%）
