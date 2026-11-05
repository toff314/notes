# 讲 26：调度器 kube-scheduler（SNR 4.1 🥇）

**结论**：两阶段调度（Predicate/Priority）背后的资源与隔离哲学——超售、Taint 门禁、PriorityClass 抢占，以及"应用炸弹"级联故障模式。
**证据**：request（调度锁定）≠limit（cgroup 配额），差值即超售；Taint 三效应（NoSchedule/PreferNoSchedule/NoExecute）；无 PID 限额的 Pod 耗尽节点→NotReady→驱逐→换节点再炸的循环（✅ 机制可验证）。
**上下**：承讲 03 的 cgroups 资源模型，启讲 33 的 QoS 推导与驱逐优先级。
**批判**：机制+运营经验最丰富的一讲；"8000 Pod/2 分钟"压测数据为内部实验（❓），且默认配置参数需按版本核对。
