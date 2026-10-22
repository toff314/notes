# 课程通览：从零构建可观测性

## 基本信息
- 模块数：2
- 总讲数：4
- 总时长：约 9.5 小时（569 分钟）
- 讲师：极客时间直播课讲师（每周三/周日直播，"第九周"系列课程；背景为腾讯云环境 DevOps/SRE 实践者）
- 课程定位：面向 DevOps/SRE 的云原生可观测性实操课，覆盖日志（Loki）、指标（Prometheus/Thanos）、分布式追踪（OpenTelemetry/Tempo）三大支柱的选型、搭建、生产化与关联打通。

> ⚠️ **数据来源说明**：本课程各章节目录下的 `.md` 正文文件均为空壳（仅含一个标记注释），`.html` 亦为空模板；实际正文为同目录下视频字幕文件 `*_sub0.vtt`（ASR 语音识别转录）。本 digest 全部内容基于 4 份 VTT 转录（合计约 16.5 万字符）。转录为 ASR 结果，存在同音词错误（如 DevOps→"demo s/delos"、Prometheus→"promise"、Loki→"lucky"、OpenTelemetry→"open table/opening"、Tempo→"temple"、Thanos→"sandals/sennas/3S"、KEDA→"卡达/卡拉"），本笔记已按上下文还原。

## Adler 两问（检视阅读阶段必答）

- **Q1: 这门课整体讲了什么？**
  一门完整的云原生可观测性落地课。第 1 讲建立心智模型（可观测性起源与本质、监控/APM/可观测性三者演进、三大支柱、Google 四大黄金指标、SLI/SLO/SLA），并完成日志支柱（Loki + LogQL）与指标支柱入门（Prometheus 架构、黑盒/白盒监控、四种指标类型、ServiceMonitor、PromQL）。第 2 讲深化指标应用：直方图陷阱与摘要选型、基于业务指标的自定义 HPA（prometheus-adapter 与 KEDA 两条路径）、以及告警体系（PrometheusRule、AlertManager、告警疲劳治理、国内 IM 多渠道通知）。第 3 讲进入大规模生产：Prometheus 长期存储三大挑战与 Thanos 方案（架构、下采样、查询分片、多集群 global view），并铺垫分布式追踪历史与 OpenTelemetry 三合一原理。第 4 讲完成 OpenTelemetry 实战：SDK 集成三件套（trace/log/metric 全部携带 trace ID）、Grafana 三数据源（Loki/Prometheus/Tempo）通过 trace ID 互相跳转、自动注入方式对比、以及 EBPF 与 OTel 的关系辨析。

- **Q2: 作者想要解决什么问题？解决了多少？**
  - **已解决**：中小团队"从零到一"搭建可观测性全栈的选型与实操——日志、指标、追踪、告警、弹性伸缩五大块都给出了可直接照做的方案（helm 命令、CRD 写法、PromQL/LogQL 查询语句、Grafana 配置步骤）；大规模场景给出了 Thanos 多集群方案，含下采样量化分析与 global view 落地细节。
  - **部分解决**：告警疲劳与告警分层只给了参数建议和原则，未给完整生产配置模板；OTel 集成的渐进式成本（为什么要先日志再指标再 trace）只讨论了收益评估，未给出分阶段迁移路径。
  - **回避/未解决**：多云多集群调度与容灾明确预告在下一模块（不在本课程内）；EBPF 只做介绍级对比，未给生产级安全/网络实践；Thanos 的 receiver 模式、ruler 告警等只一句带过。

## 模块地图

| 模块 | 讲数 | 主题词 | 预期价值密度 |
|------|------|--------|-------------|
| 第一章：从零构建可观测性 | 2 | 概念/日志 Loki/监控 Prometheus/弹性伸缩/告警 | 高 |
| 第二章：OpenTelemetry 和可观测性大规模生产实践 | 2 | Thanos 大规模存储/多集群/OTel 三合一/EBPF | 高 |

## 章节标题矩阵

| 编号 | 标题 | 核心关键词 | 初判价值 | 初步印象 |
|------|------|-----------|---------|---------|
| 01 | 从零构建可观测性（一） | 三大支柱/黄金指标/SLI-SLO-SLA/Loki/LogQL/Prometheus/黑盒白盒监控 | ⭐⭐⭐ | 概念框架可查证，Loki 轻量原理与 LogQL 体系是亮点；但 2h48m 中安装演示与答疑占比大 |
| 02 | 从零构建可观测性（二） | 直方图bucket陷阱/直方图vs摘要/HPA原理/KEDA/告警疲劳/多渠道通知 | ⭐⭐⭐ | 实战洞察密度全课最高：分位数图变直线=桶配置问题、KEDA 一条 PromQL 替代 adapter 复杂配置 |
| 03 | 可观测性大规模生产实践 | Thanos/下采样/查询分片/多集群 global view/追踪历史/OTel 原理 | ⭐⭐⭐ | 全课最深：10亿级查询量化分析、下采样 12 倍关系洞察、多集群方案完整可复现 |
| 04 | Opentelemetry 概述与用法（源标题拼写如此） | OTel SDK/trace ID 三合一/Grafana 数据源打通/自动注入/EBPF | ⭐⭐⭐ | 三合一打通配置（derived field/exemplar/traces-to-logs）是全课最稀缺的可复现资产 |

## 整体印象
- 课程主线：从可观测性心智模型出发 → 逐个落地三大支柱（日志/指标/追踪）→ 业务化应用（弹性伸缩/告警）→ 大规模生产化（Thanos 多集群）→ 用 trace ID 把三界打通（OTel）。
- 最大亮点：Loki 轻量原理（不索引全文只索引时间戳+标签）、直方图 bucket 陷阱、KEDA 单条 PromQL、下采样 12 倍量化分析、Grafana 三数据源 trace ID 互跳配置——都是"看完就能复现"的硬核内容。
- 明显水份：每讲末尾大段 Q&A（约占总时长 15-20%）、安装演示中的等待与排错过程、L03 的分布式追踪历史通史（30 分钟纯背景）。
- 独特之处：以"trace ID 关联一切"作为全课收束主线，且给出了完整的三数据源 Grafana 配置；ASR 转录使阅读成本上升，但内容本身系统性很强。
- **形式/内容判断**：这门课是"教思维方式 + 堆砌实操知识"的混合体——概念部分（可观测性本质、冷热分层、去重思维）教思维方式，工具部分（LogQL/PromQL/CRD/Thanos 组件）是密集的事实与操作知识。核心价值在后者。
