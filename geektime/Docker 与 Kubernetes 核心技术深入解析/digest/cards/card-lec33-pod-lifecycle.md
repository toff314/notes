# 讲 33：深入理解 Pod 的生命周期（SNR 4.2 🥇）

**结论**：全课信息密度最高一讲——状态机、QoS 推导、三类探针默认值哲学、优雅终止三动作链，以及 bash 吞 SIGTERM 的亲历踩坑。
**证据**：QoS 由 request/limit 关系自动推导（Guaranteed=相等）；Liveness 未探测前默认 Live、Readiness 未到初始延迟默认 NotReady；SIGTERM 被 bash 吃掉导致优雅中止失效、发布变慢（✅ 符合 Linux 信号机制）；默认 TolerationSeconds=300s、terminationGracePeriod=30s（✅）。
**上下**：承讲 26 的资源模型，启讲 39 的高可用总集成。
**批判**：可操作极强；"团队扩至 900 秒"为内部实践（❓），默认值以官方文档为准。
