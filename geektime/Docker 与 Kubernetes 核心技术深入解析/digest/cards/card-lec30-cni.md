# 讲 30：容器网络接口 CNI（SNR 4.0 🥇）

**结论**：CNI exec 机制与跨节点网络两种模式（VXLAN/BGP），Calico 的全 1 MAC 虚拟网关是容器网络排障的关键心智模型。
**证据**：容器默认网关 169.254.1.1 无人配置，靠全 1 MAC 把流量吸到 veth 外侧由主机转发（✅）；BGP mesh 随节点数指数膨胀→Route Reflector 星状化（✅）；IPAM 三层结构 IPPool→IPAMBlock→IPHandle（✅）。
**上下**：承讲 05 的容器网络基础，启讲 36/39 的 kube-proxy 与真实网络拓扑。
**批判**：机制解释+选型经验均有独立洞见；Cilium 内核版本门槛等细节需按当前版本复核。
