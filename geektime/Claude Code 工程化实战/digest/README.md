# 《Claude Code 工程化实战》消化索引（digest v2）

> 课程：极客时间《Claude Code 工程化实战》，讲师黄佳，34 讲 / 约 9.9 小时。
> 本目录：`/home/yuanwu/notes/geektime/Claude Code 工程化实战/digest/`
> 课程原文：`/home/yuanwu/geektime/output/Claude Code 工程化实战/<模块>/<讲>/`

## 一、写作前必读（按优先级）

1. **`digest.md`** — 课程一页纸，唯一必读。10 分钟建立全局判断。
2. **`course_review.json`** — 课程判决、四幕评价、写作方向。写评论文先读它定基调。
3. **`content_triage.json`** — 逐讲评分、四层分拣、47 条数据审计。引用任何数字前必查可信度标签。
4. **`theme_articles/theme-001.json`** — 多 Agent 选型的主题深挖素材包，含 `verification_gate.avoid_claims`。
5. **`cards/`** — 6 张金/银讲深读卡，写具体章节时按需点开。

## 二、产出物总表

| 文件 | 用途 | 人读/机读 |
|---|---|---|
| `digest.md` | 课程一页纸（≤1500 字） | 人读·必读 |
| `cards/card-lec-hot03-source-leak.md` | 源码泄露十点实证 | 人读·选读 |
| `cards/card-lec04-multi-agent.md` | 多 Agent 决策框架 | 人读·选读 |
| `cards/card-lec16-stop-hook.md` | Stop Hook 质量门控 | 人读·选读 |
| `cards/card-lec20-rules.md` | 指令规则 vs 权限规则 | 人读·选读 |
| `cards/card-lec11-progressive-disclosure.md` | Skill 三层披露架构 | 人读·选读 |
| `cards/card-lec-hot05-workflow.md` | 控制流位置判据 | 人读·选读 |
| `survey_notes.md` | 通览笔记 + Adler 两问 | 人读·可选 |
| `lecture_summaries.json` | 34 讲逐讲摘要 | 机读 |
| `content_triage.json` | 逐讲评分 / 分拣 / 数据审计 | 机读 |
| `course_review.json` | 课程评论文素材（四幕） | 机读 |
| `theme_articles/theme-001.json` | 主题深挖文素材（跨 5 讲） | 机读 |
| `concept_map.mermaid` | 课程模块与概念依赖图源文件 | 机读/可渲染 |

> `study_guide*.md/.html`、`survey_notes.html`、`README.html` 是 v1 遗留的扩展阅读，**不属于 v2 必读集**；与 v2 冲突时以本表为准。

## 三、写作任务指引

### 写课程评论文
1. 读 `course_review.json` 的 `narrative_structure.acts` 与 `overall_assessment`。
2. 读 `content_triage.json` 的 `data_audit`：47 条 = ✅33 / ⚠️10 / ❓2 / 🚩2。
3. 叙事线：反差开场（工具课为何敢谈工程化）→ 四幕评价 → 诚实交代数据边界。

### 写主题深挖文
1. 读 `theme_articles/theme-001.json` 的 `narrative_arc` / `verification_gate`。
2. **`avoid_claims` 中的内容绝对禁止写成事实**：50K tokens 阈值、Agent Teams 无量化成本。
3. 按 `source_lectures`（04/03/07/08/hot-05）回原文核对引文。

### 了解课程 / 深挖某讲
先读 `digest.md`；需要细节时点 `cards/`；再不够按下方路径回原文。

## 四、金矿讲课导航（可逐字引用）

| 讲 | 标题 | 原文绝对路径 |
|---|---|---|
| hot-03 | 真相大白：源码泄露事故带来的架构验证与工程启示 | `/home/yuanwu/geektime/output/Claude Code 工程化实战/热点加餐（随技术趋势动态更新）/真相大白：源码泄露事故带来的架构验证与工程启示/真相大白：源码泄露事故带来的架构验证与工程启示.md` |
| 04 | 量体裁衣：从 Sub-Agents 到 Multi-Agent 的工程指南 | `/home/yuanwu/geektime/output/Claude Code 工程化实战/子代理（Sub-Agents）/04｜量体裁衣：从 Sub-Agents 到 Multi-Agent 的工程指南/04｜量体裁衣：从 Sub-Agents 到 Multi-Agent 的工程指南.md` |

高价值银矿原文：16（Hooks 高级）、20（Rules）、11（渐进式披露）、hot-05（Workflow）、09（SKILL.md）、18（Tools）、19（Headless）、22（Agent SDK），路径同构：`<模块>/<讲目录>/<讲目录>.md`。

## 五、数据可信度警示（写作禁用）

以下内容**不得作为事实**引用：

- 🚩 token 利用率提升 98%（11 讲释题，正文自认"大概估算"）
- 🚩 功能代码 : 安全代码 ≈ 1:3（hot-03，讲师经验估算）
- ❓ 27+ 平台 / 52,000+ Skills / Top Skills 安装量 180,000（14 讲，出版时点生态数据）
- ❓ Claude Code 81K stars / OpenCode 119K stars / 月活 65 万+ / 10 亿美元年化（hot-02，无法独立验证）
- ❓ Claw-Code 2 小时 50K stars / Sigrid Jin 250 亿 token（hot-03，网络转述）
- ❓ 信噪比 50 行法则（06 讲，讲师经验值）
- ❓ 升级决策树"工具 < 5、上下文 < 50K tokens"（04 讲，讲师经验值）

**可引但需标注语境**：90.2% 性能提升、15 倍 token 成本（Anthropic 官方博客 ✅）；40% token 节省（LangChain 图表转述 ⚠️）；源码泄露的 512K 行 / 1,900 文件 / 41K fork（事件分析转述 ⚠️）。

## 六、元信息

- 消化版本：v2（digest + cards + JSON 简报）
- 消化日期：2026-10-26
- 评分：SNR 2.92/5（🥇2 🥈17 🥉10 ⛏️5）
- 主题深挖文：1 篇（金矿 2 → 按决策表取 0-1 篇上限；金+银 19 ≥ 5；overall SNR 2.92 ≥ 2.5 不减半）
- 数据审计：47 条 = ✅33（70%）/ ⚠️10（21%）/ ❓2（4%）/ 🚩2（4%）
- 本次开渠成品（课程评论文）：`/home/yuanwu/zhihu-wiki/web-system/data/local/articles/20261026/294/article.md`
