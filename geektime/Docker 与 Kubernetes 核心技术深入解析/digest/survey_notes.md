# 课程通览：Docker 与 Kubernetes 核心技术深入解析

## 基本信息
- 模块数：6
- 总讲数：39
- 总时长：约 21 小时 38 分钟（1298 分钟）
- 讲师：唐炳昌（曾任职 IBM、eBay 等，负责云计算/Kubernetes 平台建设，讲师背景自述于 L07/L21/L39 等）
- 课程定位：以"为什么这样设计"为导向的容器与 Kubernetes 控制平面原理课，逐组件拆解 Docker 核心技术、etcd（Raft）、API Server、调度器、控制器、kubelet、CRI/CNI/CSI、服务发现与 Ingress，穿插大量讲师生产环境踩坑与真实故障案例。

## Adler 两问（检视阅读阶段必答）
- **Q1: 这门课整体讲了什么？**
  课程沿"容器 → 编排 → 控制平面逐组件 → 数据面"主线推进：第一章讲 Docker 的三大底层技术（Namespace 隔离、cgroups 资源控制、OverlayFS 分层文件系统）与容器网络/Dockerfile 实践；第二章讲 Kubernetes 的 Borg 渊源、声明式系统设计原则与对象模型（TypeMeta/Metadata/Spec/Status）；第三~五章逐个深入控制平面组件——etcd（Raft 协议与生产运维）、API Server（认证/授权/准入/限流四道门与 apimachinery 机制）、调度器与控制器（超售/Taint/亲和性、Informer 框架、kubelet 与 CRI/CNI/CSI 三大接口）；第六章回到数据面，讲 Pod 生命周期、服务发现（负载均衡技术全景）、Service/kube-proxy/DNS/Ingress，最后以一个跨地域多活的真实项目案例收尾。
- **Q2: 作者想要解决什么问题？解决了多少？**
  已解决：① 讲清了"Kubernetes 为什么这样设计"——声明式系统、最终一致性、控制器模式、标准接口（CRI/CNI/CSI/OCI）的动机链条完整；② 提供了大量可验证的机制级解释（Raft 选主与日志复制、iptables 概率命中 DNAT、IPVS dummy 设备、pause Sandbox 容器、乐观锁 revision 等）；③ 贡献了稀缺的生产踩坑经验（etcd list 穿透堵死 gRPC、API Server 假健康导致 40% 节点被误驱逐、无指数退避的认证重试风暴、bash 吞掉 SIGTERM 破坏优雅终止、Service 环境变量撑爆容器启动命令行等）。
  未解决/回避：① 视频课形态导致部分讲稿转录有术语错漏（如 "Set OS"=setns、"C Group"=cgroups），需对照原文理解；② 集群安装、手写 Operator 等实操内容以 GitHub 仓库教程形式外置，课内未完整演示；③ 部分量化声明（如"每提升 100ms 影响 4% 营收"）为内部数据，无法独立验证。

## 模块地图
| 模块 | 讲数 | 主题词 | 预期价值密度 |
|------|------|--------|-------------|
| 第一章：Docker 核心技术 | 6 | 容器三大技术/网络/Dockerfile | 中高 |
| 第二章：Kubernetes 架构原则和对象设计 | 5 | Borg/声明式/对象模型 | 中高 |
| 第三章：Kubernetes 控制平面组件：etcd | 6 | Raft/高可用/生产故障 | 高 |
| 第四章：Kubernetes 控制平面组件：API Server | 8 | 认证/授权/准入/限流 | 中高 |
| 第五章：Kubernetes 控制平面组件：调度器和控制器 | 7 | 调度/控制器/kubelet/CRI/CNI/CSI | 高 |
| 第六章：生命周期管理和服务发现 | 7 | Pod 生命周期/服务发现/Ingress | 高 |

## 章节标题矩阵
| 编号 | 标题 | 核心关键词 | 初判价值 | 初步印象 |
|------|------|-----------|---------|---------|
| 01 | 从系统架构谈起 | 单体→SOA→微服务、ESB、Istio 合并 | ⭐⭐ | 架构演进常识+Istio 合并案例有洞见 |
| 02 | 理解 Docker | 起源、容器vs虚拟机、基础命令 | ⭐⭐ | 教程级对比，性能数据无出处 |
| 03 | Docker 的核心技术（一） | Namespace/cgroups/CFS/vruntime | ⭐⭐⭐ | 原理深入+CPU 实验可验证 |
| 04 | Docker 的核心技术（二） | OverlayFS/写时复制/OCI/containerd | ⭐⭐⭐ | 分层文件系统机制清晰，架构演进有洞见 |
| 05 | 容器网络 | 四种模式/veth/Overlay/Underlay/VXLAN | ⭐⭐ | 手工配置实验教学价值高 |
| 06 | Dockerfile 的最佳实践 | 构建上下文/缓存/多段/tini | ⭐⭐⭐ | 大量真实踩坑（缓存、VOLUME、信号） |
| 07 | Kubernetes 架构基础（一） | Borg/Cell/Job/混布/命令式vs声明式 | ⭐⭐⭐ | Borg 数据可溯源，遥控器类比精妙 |
| 08 | Kubernetes 架构基础（二） | 标准API/etcd watch/三个A/Informer | ⭐⭐⭐ | 架构链路完整，信息密度高 |
| 09 | 了解 kubectl（一） | kubectl/kubeconfig/IaaS-PaaS-SaaS/设计原则 | ⭐⭐⭐ | 声明式设计原则（线性复杂度等）有洞见 |
| 10 | 深入理解 Kubernetes（二） | TypeMeta/Metadata/Spec/Status/Finalizer/乐观锁 | ⭐⭐ | 对象属性讲解，机制清楚但偏复述 |
| 11 | 核心对象概览 | Node/Namespace/Pod/探针/StatefulSet/CRD | ⭐⭐ | 对象遍历，官方文档覆盖度高 |
| 12 | etcd 概要 | KV/Watch/Lease/CAS | ⭐⭐ | 入门介绍，性能数据待查 |
| 13 | Raft 协议 | 选主/日志复制/网络分区/Learner | ⭐⭐⭐ | 原理清晰，偶数节点反直觉点成立 |
| 14 | etcd 如何实现 Raft | WAL/revision/MVCC/1.5MB | ⭐⭐⭐ | 工程实现细节扎实 |
| 15 | 构建高可用 etcd 集群 | mTLS/snapshot/restore/quota | ⭐⭐ | 实验课，磁盘满→alarm 坑真实 |
| 16 | 高可用集群管理 | operator/堆叠vs外部/故障案例/备份方案 | ⭐⭐⭐ | 生产故障案例+量化经验值，稀缺 |
| 17 | etcd 常见问题及解决办法 | 备份增强/落盘加密/FMA 故障注入 | ⭐⭐⭐ | 假健康误驱逐案例极有价值 |
| 18 | API Server 概念 | API网关/四层自我保护 | ⭐⭐ | 概念引入，为后续铺垫 |
| 19 | API Server 认证机制 | X509/静态token/SA JWT | ⭐⭐ | demo 型讲解，机制清楚 |
| 20 | 基于 Webhook 的认证集成 | TokenReview/指数退避/重试风暴 | ⭐⭐⭐ | 重试风暴事故复盘是独立洞见 |
| 21 | API Server 授权机制 | RBAC/多租户/事故教训 | ⭐⭐⭐ | 事故教训+update→patch 权限坑真实 |
| 22 | API Server 准入控制 | 变形/校验/ResourceQuota/Webhook | ⭐⭐ | 教程级+机制解释 |
| 23 | API Server 限流方法 | 令牌桶/MaxInFlight/APF/Shuffle | ⭐⭐⭐ | APF 机制讲解清楚 |
| 24 | 高可用 API Server | 冗余+LB/WatchCache/多租户 | ⭐⭐ | 方案串讲，NamespaceCreator 模式可操作 |
| 25 | API Server 运作机制 apimachinery | GKV/conversion/code generator/sub-resource | ⭐⭐ | 源码走读，概念解释有价值 |
| 26 | 调度器 kube-scheduler | 超售/Taint/亲和/PriorityClass/应用炸弹 | ⭐⭐⭐ | 机制+运营经验最丰富的一讲 |
| 27 | 控制器 Controller Manager | Informer/队列/滚动升级/GC | ⭐⭐⭐ | 控制器模式讲解透彻 |
| 28 | kubelet 组件 | SyncLoop/PLEG/Sandbox/pause | ⭐⭐⭐ | 1容器2进程的 pause 解释是亮点 |
| 29 | 容器运行时接口 CRI | gRPC/运行时分层/OCI/切换 | ⭐⭐ | 历史+实操，选型理由清晰 |
| 30 | 容器网络接口 CNI | VXLAN/BGP/Calico/IPAM/RR | ⭐⭐⭐ | 机制+生产选型，169.254.1.1 反直觉 |
| 31 | 容器存储接口 CSI | 演进/emptyDir/hostPath/PV-PVC/LVM | ⭐⭐ | 原理+生产实践，静动态供给对比 |
| 32 | Rook 的工作原理 | Operator/provisioner/Unix socket | ⭐⭐ | 项目走读，演示为主 |
| 33 | 深入理解 Pod 生命周期 | 状态机/QoS/污点驱逐/优雅终止 | ⭐⭐⭐ | 高密度+信号坑踩坑，金矿 |
| 34 | 服务发现 | LB 技术全景/NAT/DR/隧道/DNS TTL | ⭐⭐⭐ | 理论梳理系统，"改包头"总结精炼 |
| 35 | Service 对象 | Endpoint/EndpointSlice/类型/Topology | ⭐⭐ | 机制解释清楚，中间表类比好 |
| 36 | kube-proxy 组件 | iptables 概率链/IPVS/dummy | ⭐⭐⭐ | 规则解读实操性强，选型结论明确 |
| 37 | DNS 原理和实践 | CoreDNS/FQDN/ndots/enableServiceLinks | ⭐⭐⭐ | enableServiceLinks 踩坑独特 |
| 38 | Ingress 对象 | L4vsL7/Controller/TLS/class | ⭐⭐ | 概念+演示，简单vs灵活权衡讨论 |
| 39 | 案例分享：Ingress+Service 拓扑 | ECMP/DSR/99-1权重/边缘加速 | ⭐⭐⭐ | 真实项目，方案可迁移，量化数据不可验 |

## 整体印象
- 课程主线：容器底层技术 → Kubernetes 设计哲学 → 控制平面逐组件原理 → 数据面与服务发现，最后以真实项目收尾，逻辑闭环完整。
- 最大亮点：① 生产故障案例密度高（etcd list 穿透、假健康误驱逐、认证重试风暴、SIGTERM 被吞、Service 环境变量撑爆命令行），且每个案例都有根因→修复的完整链条；② 机制级反直觉解释多（CPU Share 不是上限、quota/period=核数、虚 IP 靠规则不靠设备、pause 底座、全 1 MAC 虚拟网关、iptables 33%/50%/100% 概率链）。
- 明显水份：① 部分讲以命令演示/实验为主（L02 基础命令、L15 集群构建、L32 Rook demo），信息密度偏低；② 源码走读类内容（L25 apimachinery）对非研发读者性价比低；③ 部分量化数据无出处（性能 1%、20% 提升、营收 4% 等）。
- 独特之处：讲师有 eBay/腾讯等大规模集群运营背景，故障案例多为亲历（L17 春节误删集群、L20 Keystone 重试风暴、L39 跨境边缘加速项目），这是同类课程少有的"可验证的生产叙事"。
- **形式/内容判断**：这门课主要在"教思维方式"——反复强调设计动机与权衡（为何声明式、为何超售、为何用 LB 而非 DNS 切流、为何 pause 做底座），事实知识是载体而非目的；但也包含相当比例的官方文档复述与命令演示。
