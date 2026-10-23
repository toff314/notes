# 《如何成为学习高手》消化索引（digest README）

> 本目录是《如何成为学习高手》（讲师：冷冷，24 讲/5 模块）的结构化消化产物，v2 重跑于 2026-10-23。
> **本目录绝对路径**：`/home/yuanwu/notes/geektime/如何成为学习高手/digest/`
> **课程原文**：留在 geektime 下载仓（`output/如何成为学习高手/`）不迁移，逐讲相对路径见 `lecture_summaries.json` 的 `source_file` 字段。

## 必读文件清单（按优先级）

1. `digest.md` — 课程一页纸（**人读唯一必读**）：课程地图、值不值得读、精华讲清单、略读清单。
2. `cards/` — 精华讲深读卡（选读）：3 金讲 + 3 银顶讲，每张四行（结论/证据/上下/批判）。
3. `content_triage.json` — 逐讲评分 + Adler 四问 + 数据审计（机读，写作前必查其 `data_audit` 与 `verification`）。
4. `course_review.json` — 课程评论文素材（机读）：四幕评价 + 整体得失。
5. `theme_articles/theme-001~002.json` — 主题深挖文素材（机读）：跨讲命题 + 数据闸门。

## 产出物总表

| 文件 | 内容 | 消费方式 |
|------|------|---------|
| `digest.md` | 课程一页纸（≤1500 字） | 人读（必读） |
| `cards/` | 精华讲深读卡 6 张（每张 ≤300 字） | 人读（选读） |
| `survey_notes.md` | Phase 1 通览笔记（Adler 两问 + 章节矩阵） | 人读（选读） |
| `concept_map.mermaid` | 课程概念图（可选产物） | 人读（选读） |
| `lecture_summaries.json` | Phase 1 逐讲摘要（含 source_file 路径） | 机读 |
| `content_triage.json` | Phase 2 逐讲分拣 + 六步质询 + 数据审计 | 机读 |
| `course_review.json` | Phase 4 课程评论文素材 | 机读 |
| `theme_articles/theme-001.json` | 主题文：记忆的底层逻辑（03/07/08/21） | 机读 |
| `theme_articles/theme-002.json` | 主题文：他律 vs 自律（12/13/14/16/17） | 机读 |

## 写作任务指引

### 写课程评论文
1. 读 `course_review.json` 的 `narrative_structure.acts`（四幕）与 `overall_assessment`。
2. 读 `content_triage.json` 的 `data_audit` 与金/银讲 `critical_notes`。

### 写主题深挖文
1. 选 `theme_articles/theme-001.json`（methodology）或 `theme-002.json`（opinion）。
2. 读其 `narrative_arc` 三幕与 `verification_gate`。
3. **`verification_gate.avoid_claims` 中的内容绝对禁止写进文章**。
4. 按 `source_lectures` 回原文核对引文：原文绝对路径 = geektime 下载根 + `lecture_summaries.json` 中对应讲的 `source_file`。

### 了解这门课（人读）
1. 读 `digest.md`（唯一必读；读完不需要打开原课程）。
2. 要深挖某讲再点 `cards/card-lecXX-*.md`（铜铁讲无卡，必要时回原文）。

## 金矿讲课导航（可逐字引用）

| 讲 | 标题 | 深读卡 |
|----|------|--------|
| 03 | 掌握考试思维：成为一个特别会考试的人 | `cards/card-lec03-kaoshisiwei.md` |
| 05 | 教你全面提升专注力，学习时不再走神 | `cards/card-lec05-momofa.md` |
| 07 | 我考北大中文系时，15 天背下 10 门专业课的连点成线法 | `cards/card-lec07-liandianchengxian.md` |
| 08 | 高效记忆的根本方法：主动思考和加工 & 组块化记忆 | `cards/card-lec08-zhudongjiagong.md` |
| 12 | 每个人都能学会：5 分钟克服拖延症的方法 | `cards/card-lec12-wufenzhong.md` |
| 13 | 3 个思路，让你成为一个真正自律的人 | `cards/card-lec13-talü.md` |

逐字引用原文时，路径拼接规则：`lecture_summaries.json` → 对应 `lecture_id` 的 `source_file` 字段（相对路径），拼接到 geektime 下载根下。

## 数据可信度警示

以下声明**禁止**作为事实引用（🚩 可疑 / ❓ 无法验证；⚠️ 引用须注明出处与争议）：

- ❓ 「15 天背下 10 门专业课」（第 07 讲标题，个人声明无佐证）
- ❓ 「考研英语提前 45 分钟交卷」（第 05 讲，个人孤证）
- ❓ 「高三月考 550 → 650 分」（第 04 讲，个人经历无法独立验证）
- ❓ 「每天工作 6 小时整最合适」（第 15 讲，个人经验数字无依据）
- ⚠️ 「5 分钟起步法 = 加拿大卡尔顿大学拖延心理学研究小组成果」（第 12 讲，名称系转述包装）
- ⚠️ 「替代拖延法」（第 12 讲，与 John Perry 结构化拖延法同源但未标注来源）
- ⚠️ 「爆米花实验：大桶比中桶多吃 53%」（第 16 讲，Wansink 实验室有撤稿争议，引用须注明）
- ⚠️ 「李笑来 GRE 案例：20000 词 = 40 万美元奖学金」（第 19 讲，转述数字无法独立验证）

## 元信息

- 消化评分：3.5/5（🥇3 🥈16 🥉5 ⛏️0）
- 数据审计：萃取声明 57 条 = ✅32 / ⚠️23 / ❓2 / 🚩0
- 人读预算：digest.md 1129 字 + cards 6 张共 1545 字 = 2674 字（上限 3300）
