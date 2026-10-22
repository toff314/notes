# 从零构建可观测性 — 5 分钟速览

> 4 讲 / 约 9.5 小时 / 整体信噪比 3.6/5

## 如果你只记住一件事
**可观测性三界（日志/指标/追踪）不必三套孤岛：让每个环节都携带同一 trace ID，就能在 Grafana 里 log⇄metric⇄trace 任意互跳闭环排查；存储层规模问题交给"对象存储 + 下采样"解决。**

## 3 个核心框架
1. **Loki 轻量原理**：只索引时间戳+标签、不索引日志全文，靠"日志流选择器定位 → 流内过滤"实现低存储高速度（L01）
2. **直方图 vs Summary 选型**：要跨实例聚合或分布可知 → 直方图；分布未知且需绝对精确 → Summary；"分位数图为直线"= bucket 失配（L02）
3. **Thanos 下采样**：原始块→5 分钟块→1 小时块，空间换时间；30 天与 1 年查询成本恒定（同为 12 倍匹配），一年查询从 2G/80 秒降到 9MB/300ms（L03）

## 5 个可操作方法
1. 装 Loki：helm 装 Loki+Promtail+Grafana，Promtail 以 DaemonSet 挂载 `/var/log/pods` 采标准输出日志（L01）
2. 抓业务指标：写 ServiceMonitor（matchLabels + 端口名 + 10s + /metrics 路径），比 annotation 抓取更解耦（L01）
3. 业务指标伸缩：用 KEDA ScaleObject 写一条 PromQL（如 500 错误 QPS>10）即触发伸缩，别用配置复杂的 prometheus-adapter（L02）
4. 告警接飞书：PrometheusRule 写表达式+for+annotations，Alertmanager receiver 配 webhook 经 prometheus-alert 转发飞书机器人；group_wait/group_interval/repeat_interval 调长防告警疲劳（L02）
5. 三界打通：业务集成 OTel SDK（trace 发 Tempo、日志带 trace_id、指标带 #trace_id），Grafana 配 Loki derived field + Prometheus exemplar + Tempo traces-to-log 三处互跳（L04）

## 1 个反直觉观点
**下采样不是为了省存储，而是用更大的存储换更快的查询**——它额外生成 5 分钟块和 1 小时块，总存储量更大，但把一年维度的查询从分钟级解压降到 300 毫秒（L03）。

## 值不值得花时间？
**值（对有实操诉求的 DevOps/SRE）** — 全课无金矿级原创贡献，但 4 讲均为高质量整理与教程，日志/伸缩/告警/Thanos/OTel 打通都有可直接照做的配方；3-4 小时精读的 ROI 高于多数同类课。**不值（对只看理论的读者）** — 概念部分（三大支柱/黄金指标）是标准复述，且 ASR 转录阅读成本偏高。
