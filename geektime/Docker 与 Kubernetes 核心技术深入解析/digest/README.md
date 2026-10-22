# 《Docker 与 Kubernetes 核心技术深入解析》消化索引（digest README）

> 本目录是《Docker 与 Kubernetes 核心技术深入解析》的结构化消化产物，生成于 2026-08-31。
> **本目录绝对路径**：`/home/yuanwu/geektime/output/Docker 与 Kubernetes 核心技术深入解析/digest/`
> **课程原文绝对路径**：`/home/yuanwu/geektime/output/Docker 与 Kubernetes 核心技术深入解析/<模块>/<讲>/`（每讲含 `<讲名>.digest.json` 结构化讲稿、`.md` 大纲、`.txt` 原始讲稿）

## 写作前必读（按优先级）

1. **`course_review.json`** — 课程判决、四幕评价（容器地基/etcd/API Server/调度与数据面）、数据可信度汇总。任何写作任务先读它定位基调。
2. **`content_triage.json`** — 39 讲逐讲评分、金银铜铁分拣、Adler 四问、萃取内容与验证状态、数据审计。引用任何课程数据前必查。
3. **`theme_articles/`** — 两篇可直接成文的主题深挖素材包（etcd 高可用、Pod 优雅终止）。

## 产出物总表

| 文件 | 内容 | 消费方式 |
|------|------|---------|
| `course_review.json` | 课程评论文素材（四幕结构+ROI 评估） | 机读 |
| `theme_articles/theme-001.json` | 主题文①：etcd 高可用与 Raft 生产落地（跨 L13/L14/L16/L17） | 机读 |
| `theme_articles/theme-002.json` | 主题文②：Pod 优雅终止与 SIGTERM 信号穿透链（跨 L06/L28/L33） | 机读 |
| `study_guide.md` | 完整学习指南（6 主题重组+1 张 Mermaid 图+3 条阅读路线） | 人读 |
| `study_guide_slim.md` | 5 分钟速览（1 件事/3 框架/5 方法/1 反直觉） | 人读 |
| `survey_notes.md` | 课程通览（Adler 两问+模块地图+39 讲标题矩阵） | 人读 |
| `lecture_summaries.json` | 39 讲逐讲摘要（关键术语/初判/风险信号/量化声明快照） | 机读 |
| `content_triage.json` | 39 讲分拣+SNR 评分卡+数据审计（金 6/银 23/铜 10，SNR 3.42） | 机读 |

## 写作任务指引

### 写课程评论文
1. 读 `course_review.json` 的 narrative_structure.acts / overall_assessment
2. 读 `content_triage.json` 的 data_audit（量化声明审计结论在 summary 中）
3. 注意：40% 误驱逐、140ms→40ms、4% 营收等内部数据须标注"据讲师称"

### 写主题深挖文
1. 列出 `theme_articles/` 全部文件，按主题选一篇
2. 读其 narrative_arc（三幕） / verification_gate
3. **verification_gate.avoid_claims 中的内容绝对禁止写进文章**
4. 按其 source_lectures 对应路径读讲课 digest.json 核对引文：
   - 主题①：`第三章：Kubernetes 控制平面组件：etcd/2. Raft 协议/`、`/3. etcd 如何实现 Raft 协议/`、`/5. 高可用集群管理/`、`/6. etcd 常见问题及解决办法/`
   - 主题②：`第一章：Docker 核心技术/6. Dockerfile 的最佳实践/`、`第五章：Kubernetes 控制平面组件：调度器和控制器/3. kubelet 组件/`、`第六章：生命周期管理和服务发现/1. 深入理解 Pod 的生命周期/`

### 写学习指南文
1. 读 `study_guide.md`（可直接作为文章骨架）
2. 读 `content_triage.json` 的 entries 获取逐讲分级与萃取内容

## 金矿讲课导航（可逐字引用）

| 讲 | 标题 | 原文 digest.json 绝对路径 |
|----|------|---------|
| 16 | 高可用集群管理 | `/home/yuanwu/geektime/output/Docker 与 Kubernetes 核心技术深入解析/第三章：Kubernetes 控制平面组件：etcd/5. 高可用集群管理/5. 高可用集群管理.digest.json` |
| 17 | etcd 常见问题及解决办法 | `/home/yuanwu/geektime/output/Docker 与 Kubernetes 核心技术深入解析/第三章：Kubernetes 控制平面组件：etcd/6. etcd 常见问题及解决办法/6. etcd 常见问题及解决办法.digest.json` |
| 26 | 调度器 kube-scheduler | `/home/yuanwu/geektime/output/Docker 与 Kubernetes 核心技术深入解析/第五章：Kubernetes 控制平面组件：调度器和控制器/1. 调度器 kube-scheduler/1. 调度器 kube-scheduler.digest.json` |
| 30 | 容器网络接口 CNI | `/home/yuanwu/geektime/output/Docker 与 Kubernetes 核心技术深入解析/第五章：Kubernetes 控制平面组件：调度器和控制器/5. 容器网络接口 CNI/5. 容器网络接口 CNI.digest.json` |
| 33 | 深入理解 Pod 的生命周期 | `/home/yuanwu/geektime/output/Docker 与 Kubernetes 核心技术深入解析/第六章：生命周期管理和服务发现/1. 深入理解 Pod 的生命周期/1. 深入理解 Pod 的生命周期.digest.json` |
| 39 | 案例分享：Ingress 和 Service 网络拓扑 | `/home/yuanwu/geektime/output/Docker 与 Kubernetes 核心技术深入解析/第六章：生命周期管理和服务发现/7. 案例分享：通过 Ingress 和 Service 完成一个网络拓扑/7. 案例分享：通过 Ingress 和 Service 完成一个网络拓扑.digest.json` |

> 注：金矿讲中"可逐字引用"仅限 `content_triage.json` 中 `verification.status=✅` 的萃取内容与机制类表述；❓/🚩 数据见下方警示。

## 数据可信度警示

以下声明**禁止**作为事实引用（🚩 可疑 / ❓ 无法验证），如需使用须标注"据讲师称"：

- 容器性能与主机相差不超过 1%（L02，❓ 无测试出处）
- 虚拟机一台最多几十个实例、容器可跑几千个（L02，❓ 量级估计）
- 心跳周期=网络 RTT 的 0.5-1.5 倍、选举超时=RTT 的 10 倍（L16，❓ 工程经验值）
- 40% 节点被误驱逐、1 万 pod 一次 list 超 100MB（L16/L17，❓ 讲师内部环境故障案例）
- 外部 Webhook 授权场景不足 10%（L21，❓ 讲师估计）
- 100 个节点并发创建 8000 Pod 调度约 2 分钟（L26，❓ 内部压测）
- OverlayFS 比 Device Mapper 提升约 20%（L31，❓ 内部测试）
- 团队将 TolerationSeconds 扩至 900 秒（L33，❓ 内部实践）
- 单集群 23000 个 Pod（L35，❓ 讲师所见）
- 硬件负载均衡器十几万美金/套、公司用几千对（L39，❓ 内部数据）
- 跨大陆响应 140ms→40ms、每 100ms 影响 4% 营收（L39，❓ 内部项目/预测）

部分验证（⚠️，引用需注明差异）：etcd 1000 写/2000 读每秒（官方 benchmark 语境）；EndpointSlice 切片 500/1000（官方默认 100）；node-port-range 3 万-3 万 2（官方 30000-32767）；"30 分钟快照+10 秒增量"为讲师团队生产配置（机制可验证）。

## 元信息

- 消化评分：3.42/5（🥇6 🥈23 🥉10 ⛏️0）
- 数据审计：25 条量化声明 → ✅8（32%）⚠️4（16%）❓13（52%）🚩0；无编造数据迹象
- 主题深挖文：2 篇（金矿 6 → 决策表 2-3 篇，金+银=29≥5，SNR 3.42≥2.5）
