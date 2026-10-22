# 《大模型安全实战课》消化索引（digest README）

> 本目录是《大模型安全实战课》（讲师：赵帅，前极氪汽车资深算法专家）的结构化消化产物，生成于 2026-08-31。
> **本目录绝对路径**：`/home/yuanwu/geektime/output/大模型安全实战课/digest/`
> **课程原文绝对路径**：`/home/yuanwu/geektime/output/大模型安全实战课/<模块>/<讲>/`

## 写作前必读（按优先级）

1. **`course_review.json`** — 课程判决、四幕逐幕评价。任何写作任务先读它定位基调（金矿 1 讲，银矿 14 讲，整体 2.83/5）。
2. **`content_triage.json`** — 逐讲评分、四层分拣、数据审计（21 条量化声明：12 ✅ / 3 ⚠️ / 4 ❓ / 2 🚩）。引用任何课程数据前必查。
3. **`theme_articles/theme-001.json`** — 可直接成文的主题深挖素材包（"对齐+评估闭环"命题）。

## 产出物总表

| 文件 | 内容 | 消费方式 |
|------|------|---------|
| `course_review.json` | 课程评论文素材（四幕评价+ROI+写作方向） | 机读 |
| `theme_articles/theme-001.json` | 主题深挖文素材（1 篇：行为对齐与安全评估闭环） | 机读 |
| `study_guide.md` | 完整学习指南（六主题重组+Mermaid 概念图+路线 A/B/C） | 人读 |
| `study_guide_slim.md` | 5 分钟速览（3 框架+5 方法+1 反直觉观点） | 人读 |
| `survey_notes.md` | 通览笔记（Adler 两问+模块地图+标题矩阵） | 人读 |
| `lecture_summaries.json` | 逐讲摘要（38 讲首尾词+小标题+关键词+风险信号） | 机读 |
| `content_triage.json` | 逐讲分拣+数据审计（评分卡+Adler 四问+萃取+验证状态） | 机读 |

## 写作任务指引

### 写课程评论文
1. 读 `course_review.json` 的 acts / overall_assessment / writing_direction
2. 读 `content_triage.json` 的 data_audit 与 gold/silver 讲 critical_notes
3. 建议标题方向：《大模型安全课值不值得学？我评完38讲后只推荐这15讲》

### 写主题深挖文
1. 列出 `theme_articles/` 全部文件（当前 1 篇：theme-001）
2. 读其 narrative_arc / verification_gate / quality_rubric_hints
3. **verification_gate.avoid_claims 中的内容绝对禁止写进文章**
4. 按其 source_lectures（17/29/01/26）对应路径读讲课原文核对引文

### 写学习指南文
1. 读 `study_guide.md`（可直接作为文章骨架）
2. 读 `content_triage.json` 的 entries 获取逐讲分级与原文金句

## 金矿讲课导航（可逐字引用）

| 讲 | 标题 | 原文绝对路径 |
|----|------|---------|
| 17 | 对齐技术：RLHF、RLAIF与Constitutional AI与行为控制 | `/home/yuanwu/geektime/output/大模型安全实战课/防御篇/17｜对齐技术：RLHF、RLAIF与Constitutional AI与行为控制/17｜对齐技术：RLHF、RLAIF与Constitutional AI与行为控制.md` |

银矿导航（次优先引用）：04/06/07/12/13/16/18/20/22/25/26/27/29/31（路径见 `lecture_summaries.json` 的 `source_file` 字段，均在 `/home/yuanwu/geektime/output/大模型安全实战课/<模块>/<讲>/` 下）。

## 数据可信度警示

以下声明**禁止**作为事实引用（🚩 可疑 / ❓ 无法验证）：

- "某 AI 助手回答种族问题导致品牌掉粉十万"（第03讲，🚩 无出处，疑似编造）
- "斯坦福 GrootLM 提出水印方法"（第26讲，🚩 无出处，疑似虚构/张冠李戴）
- "90% 以上的诱导式攻击在身份切换策略处被切断"（第06讲，❓ 讲师内部演练，无独立来源）
- "花了两周才找出毒样本"（第07讲，❓ 讲师个人经历）
- "医疗平台用 RLAIF 让主模型变谨慎"（第17讲，❓ 讲师转述）
- "采集阶段伪造坐标可规避 90% 以上风险暴露"（第18讲，❓ 讲师经验值）
- "端侧模型 200 毫秒内完成推理"（第27讲，⚠️ 经验值，非正式基准）
- "模糊中立派 vs 正面肯定派"实测分类（第17讲，⚠️ 可复测但非正式评测，模型版本会更新）

写作引用规则：只引用 `content_triage.json` 中 `verification.status == "✅"` 的数据；⚠️ 需注明差异；❓/🚩 一律不直接引用。

## 元信息

- 消化评分：2.83/5（🥇1 🥈14 🥉19 ⛏️4，共 38 讲）
- 数据审计：21 条量化声明，12 ✅ / 3 ⚠️ / 4 ❓ / 2 🚩（57% 可验证）
- 主题深挖文：1 篇（金矿 1 讲 → 决策表 1-2 档；金矿+银矿 15 ≥ 5，整体 SNR 2.83 ≥ 2.5，未触发减半）
