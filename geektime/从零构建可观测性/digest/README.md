# 《从零构建可观测性》消化索引（digest README）

> 本目录是《从零构建可观测性》（极客时间直播课，DevOps/SRE 方向）的结构化消化产物，生成于 2026-08-31。
> **本目录绝对路径**：`/home/yuanwu/geektime/output/从零构建可观测性/digest/`
> **课程原文绝对路径**：`/home/yuanwu/geektime/output/从零构建可观测性/<模块>/<讲>/`
>
> ⚠️ **正文来源警示**：本课程各讲目录下的 `.md`/`.html` 均为空壳，实际正文在同目录 `*_sub0.vtt` 视频字幕（ASR 转录，含同音词错误，如 promise=Prometheus、temple=Tempo、lucky=Loki）。引用原文时请以转录为准并按上下文还原术语。

## 写作前必读（按优先级）

1. **`course_review.json`** — 课程判决、四幕评价（心智模型+日志指标 / 伸缩告警 / Thanos 大规模 / OTel 打通）。任何写作任务先读它定位基调。
2. **`content_triage.json`** — 逐讲评分、四层分拣、26 条量化声明的数据审计。引用课程任何数据前必查 verification 状态。
3. **`study_guide.md`** — 按主题重组的学习地图（7 主题 + Mermaid 概念图 + 阅读路线），可直接作为文章骨架。

## 产出物总表

| 文件 | 内容 | 消费方式 |
|------|------|---------|
| `course_review.json` | 课程评论文素材（四幕结构+ROI 评估+写作方向） | 机读 |
| `theme_articles/` | 主题深挖文素材（本课程 0 篇：金矿 0 + 银矿 4 < 5，按决策表不产生） | 机读 |
| `study_guide.md` | 完整学习指南（7 主题重组 + Mermaid 概念图 + 阅读路线） | 人读 |
| `study_guide_slim.md` | 5 分钟速览 | 人读 |
| `concept_map.mermaid` | 概念关系图（Mermaid 源文件） | 人读 |
| `survey_notes.md` | 课程通览（Adler 两问 + 章节标题矩阵 + 整体印象） | 人读 |
| `lecture_summaries.json` | 逐讲扫描摘要（首尾 200 字、小标题、关键词、风险信号、量化声明快照） | 机读 |
| `content_triage.json` | 逐讲分拣 + Adler 四问 + 5 维评分 + 数据审计 | 机读 |

## 写作任务指引

### 写课程评论文
1. 读 `course_review.json` 的 acts / overall_assessment / writing_direction
2. 读 `content_triage.json` 的 data_audit 与各 entry 的 critical_notes
3. 三幕改四幕叙事：概念入门 → 伸缩与告警 → Thanos 大规模 → OTel 三界打通

### 写主题深挖文
本课程无主题深挖文（金矿 0 篇、金矿+银矿 4 < 5）。如需自行扩展，可从 `content_triage.json` 的 silver 萃取项合成命题（如"用 trace ID 打通日志/指标/追踪三界"，跨 L01/L03/L04），务必遵守各 extraction 的 verification 状态。

### 写学习指南文
1. 读 `study_guide.md`（7 主题可直接作为文章骨架）
2. 读 `content_triage.json` 的 entries 获取逐讲分级与萃取内容

## 金矿讲课导航（可逐字引用）

本课程无金矿讲次（SNR ≥ 4.0）。以下为最接近金矿、引用价值最高的讲次：

| 讲 | 标题 | 原文路径 |
|----|------|---------|
| 03 | 可观测性大规模生产实践（SNR 3.9，下采样量化+多集群 global view） | `<digest 上级>/第二章：OpenTelemetry 和可观测性大规模生产实践/1. 可观测性大规模生产实践/1. 可观测性大规模生产实践.vtt` |
| 02 | 从零构建可观测性（二）（SNR 3.6，直方图陷阱+KEDA+告警治理） | `<digest 上级>/第一章：从零构建可观测性/2. 从零构建可观测性（二）/2. 从零构建可观测性（二）.vtt` |

## 数据可信度警示

以下声明**禁止**作为事实引用（🚩 可疑 / ❓ 无法验证）：

- "Loki 官方支持每天 TB/PB 级日志量"（第 1 讲，❓ 转述 Grafana 大会，无具体出处）
- "SLA 赔偿基本都是代金券"（第 1 讲，❓ 讲师观点）
- "block 压缩约 12 倍"（第 3 讲，❓ 转述'官方数据'，无出处）
- "block 解压约 10-43 纳秒/样本"（第 3 讲，❓ 转述，数值未证实）
- "Grafana dashboard 市场约 7000+ 个"（第 4 讲，❓ 动态数字未验证）
- "BCC 项目约 516 个贡献者"（第 4 讲，❓ 无法独立验证）

⚠️ 部分验证需注明差异后引用：

- "可观测性 1960 年 Kalman 提出"（第 1 讲，⚠️ 概念源于控制理论，表述为简化转述）
- "kube-prometheus-stack TSDB retention 默认 10 天"（第 3 讲，⚠️ 随版本变化）
- "下采样后 30 天/1 年查询约 300ms、9MB"（第 3 讲，⚠️ 基于假设的推算）
- "Datadog 2019 年发布"（第 3 讲，⚠️ 指具体产品线，公司整体早于该年）

✅ 可放心引用：四大黄金指标、SLI/SLO/SLA、Loki 轻量原理、LogQL/PromQL 语法、直方图 vs Summary 对比、KEDA ScaleObject 机制、HPA 15 秒查询、分布式追踪历史年份（X-Trace/Dapper/Zipkin/SkyWalking/Jaeger/OTel/Tempo/SigNoz）、OTel 自动注入 5 语言、30 天 17 万样本算术推导。

## 元信息

- 消化评分：3.6/5（🥇0 🥈4 🥉0 ⛏️0）
- 数据审计：26 条量化声明 = ✅15 / ⚠️5 / ❓6 / 🚩0
- 主题深挖文：0 篇（金矿+银矿=4 < 5，按决策表不产生）
