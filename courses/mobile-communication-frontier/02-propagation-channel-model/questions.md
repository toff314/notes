# 移动通信技术前沿 · 第2讲（电波传播与信道建模）· 疑问与自测

> **提取自测协议（怎么用这份自测）**：
> 1. **遮住** `notes.md`，只看下面的问题；
> 2. 合上一切材料，口头或笔头作答（答案须自己组织，不得复述原文）；
> 3. 答不出的进"我没掌握"，回看对应小节后再测一次；
> 4. 能讲给别人听 = 真懂（费曼标准）；讲不出的地方就是薄弱点。

## 自测（合上书回答）

1. 老师为什么说"难的是找到问题，不是解决问题"？在 AI 辅助下"换方法/换参数"式创新的价值发生了什么变化？→ 见 notes §1
2. 为什么说光通信、无线、铜线（数据中心互联）的边界在变模糊？老师举了哪些"需求不来自普通用户升级手机"的例子？→ 见 notes §1
3. 信道建模的"三阶段"各自给的是什么（均值？分布？与环境一一对应）？为什么算力够、有感知需求后必须走到第三阶段？→ 见 notes §2
4. 为什么"接收强度随距离增大而减小"这句话要打问号？老师给了哪两类"例外"？→ 见 notes §3
5. 城区与郊区的断点（1km / 100m）差异说明了什么？为什么城区在某些情况下信号峰值反而更高？→ 见 notes §3
6. SPM 用什么思路算大尺度覆盖？它的误差来源是什么？算力不够时老师建议怎么补？→ 见 notes §4
7. Okumura 的"峡谷/信道化效应"对基站选址有什么现实意义？为什么老师说 Hata 类模型的统计"大样本对、单次难说"？→ 见 notes §4
8. 为什么双线/多线模型"能算强弱却不适合多天线/宽带系统"？→ 见 notes §5
9. 曼哈顿模型如何描述"街道布局+室内外穿透"？它假定的"线性叠加、无快衰"合理吗？→ 见 notes §5
10. 为什么阴影衰落"每台手机各生成一套"是错的？"最终极"的生成方式是什么？→ 见 notes §6
11. 室外测量要在哪三个尺度上做？各自对应什么物理现象？→ 见 notes §6
12. 确定性仿真（射线追踪/FDTD）更准，为什么老师说"其他场景太复杂"还要用经验/统计模型？→ 见 notes §7
13. 老师为什么说"只要不跟真实网络连在一起，你的仿真就是假的"？DT 的两个用处是什么？→ 见 notes §7
14. NTN 的路径损耗由哪几部分组成？为什么"视距概率表"跟环境有关、城区与郊区应不同？→ 见 notes §8
15. 老师说"哲学就是不能只看一个点"——为什么"吸收特别强的频点"在抗干扰/感知场景反而有用？→ 见 notes §8
16. 为什么说低空城市是"最恶劣"的场景？视距 vs 非视距各带来什么好处与坏处（干扰/定位/空间自由度）？→ 见 notes §9
17. 无人机用毫米波做 payload、用低频做飞控，各是为什么？参考信号为什么要"按空域高度分配"？→ 见 notes §9
18. 天线阵列变大、频率变高后，为什么传统统计模型不够用？近场/远场用什么量划分？→ 见 notes §10
19. 什么是信道模型的"非平稳性"？GSCM 增强要求散射体怎么建模？"通感一致性（consistency）"指什么？→ 见 notes §10
20. WEI + AI 空口的"四步"是什么？为什么说它能把"黑盒变成知识库"？传统 CSI 会被替代吗？→ 见 notes §11
21. 老师自己的"图像信道"工作，用多大的精度代价换来了几个数量级的算力？适合什么场景？→ 见 notes §11
22. 为什么"场景适应性"是 AI 信道建模最难的关？"环境天天在变"与"训练过拟合"是什么关系？→ 见 notes §11

## 我没懂的

- ❓ 转写多处把 NVIDIA 的开源仿真工具写成「RT+C+physical+S」「S+」「S 几」，结合上下文（开源、含信道/物理层/链级、被综述用来做数字孪生）疑为 **NVIDIA Sionna**，待核。（转写 §? / notes §7）
- ❓ 转写中的「SPM」被反复提及（跨区域大、对流层绕射、地面双径、地球剖面），与标准里的 SPM/SF 模型族对应，但转写未给出全称，笔记按"SPM"沿用，待核。（notes §4）
- ❓ 「射线出来」「射线发射」与「镜像法」在转写中混用，PPT 第 210–220 页区分「射线跟踪（镜像法）」与「射线发射（SBR）」，转写边界不清，需看课件。（notes §7）
- ❓ 转写「SU MIMO」「叉 L MIMO」「一个 L MIMO」等疑为 **XL-MIMO（extremely large MIMO）**，待核。（notes §10）
- ❓ 转写「瑞丽距离」「瑞利距离」为同一概念（Rayleigh distance），转写记法不一，已统一为"瑞利距离"。（notes §10）
- ❓ 转写「GSCM」「几何随机」处是否即 **Geometry-Based Stochastic Channel Model**，以及"散射体按形状而非点/随机簇"的具体文献，待核。（notes §10）
- ❓ 转写「RIS」多次出现但老师称"最后是 RIS 部分"，而转写结尾停在 AI 信道建模，未见专门 RIS 章节——是时间不够省略，还是 RIS 分散在 A2G/MIMO 各节？需看是否有后续录音。（notes 全篇）
- ❓ 转写「英伟达的……做数字孪生」一节，DT 与 Sionna 的具体对应关系及综述出处待核。（notes §7）
- 【PPT】第 21–31 页 Okumura 的地形参数（地形波动高度、平均地面斜度、混合陆地-海上参数、h_ts/h_te/h_go）转写只笼统提到"修正因子"，具体因子未展开。
- 【PPT】第 101–131 页"室外传播环境模拟（补充）"（慢衰时间/空间相关模型、服务区模型、移动模型、天线方向性、干扰载波隔离、WINNER 五种部署场景 InH/UMi/UMa/RMa/SMa）转写只覆盖了慢衰相关与移动模型，WINNER 部署场景未涉及。
- 【PPT】第 133–302 页"室内无线传播及覆盖"（含 60GHz、毫米波、E-band 70/80GHz backhaul、室内 100GHz、V2V 信道、VANET 移动模型）——转写未按页展开，仅点到"室内覆盖痛点"与"V2V/无人机仿真不闭环"。
- 【PPT】第 303–330 页 NTN 各页的具体公式（PL=PLb+PLg+PLs+PLe、O2I 双对数正态、ITU-R 对流层闪烁三部分算法）转写只给结论未给公式。

## PPT 有、转写未覆盖（需自己看课件补）

- 【PPT】第 10–18 页：Longley-Rice（两种模式、主要参数、4 种变化模式、Urban Factor）与 Durkin（菲涅尔区）——转写仅"浏览模型群"。
- 【PPT】第 19–32 页：Okumura 的地形参数与 5 个因子（h_ts/h_te/h_go、地面起伏高度、独立山区地形参数、混合陆地-海上参数）——转写只提"修正因子"。
- 【PPT】第 33–40 页：Hata / COST-231 Hata 的具体公式——转写未给公式。
- 【PPT】第 52–58 页：Egli、Carey、Bertoni-Xia、TIREM——转写未涉及。
- 【PPT】第 101–131 页："室外传播环境模拟（补充）"（服务区模型、天线方向性、干扰载波隔离、WINNER 五种部署场景 InH/UMi/UMa/RMa/SMa）——转写只覆盖慢衰相关与移动模型。
- 【PPT】第 133–302 页："室内无线传播及覆盖"整章（室内信道参数、60GHz、毫米波、E-band backhaul、室内 100GHz、V2V、VANET 移动模型）——转写仅点到"室内覆盖痛点""V2V/无人机仿真不闭环"。
- 【PPT】第 303–330 页：NTN 各页公式/表格（PL=PLb+PLg+PLs+PLe、O2I 双对数正态、ITU-R 对流层闪烁算法）——转写只给结论。
- 【PPT】第 332–339 页：近场 MIMO 的瑞利距离公式、near-field beam split、distance-aware precoding、LDMA——转写只讲大意。
- 【PPT】第 353–361 页：WEI "无线环境信息处理步骤"逐页细节与"面向任务的 WEI 6G AI2 验证"——转写覆盖"四步"框架，细节未展开。

## 待查（需要外部资料）

- 3GPP TR 38.811（NTN 传播模型）——LOS 概率表、O2I 穿透、大气/闪烁损耗的标准化来源。
- 3GPP TR 38.901（含 WINNER 部署场景 InH/UMi/UMa/RMa/SMa，PPT 第 127–131 页引用 ITU-R M.2135）。
- NVIDIA Sionna / Sionna RT 官方文档与"用于数字孪生"的综述出处。
- 《A Survey of Air-to-Ground Propagation Channel Modeling for Unmanned Aerial Vehicles》（IEEE COMST, 2019, VOL.21 NO.3）——PPT 第 322 页 AG 信道综述。
- Mingyao Cui, Zidong Wu, ..., Linglong Dai, *Near-Field Communications for 6G*——PPT 第 332 页近场 MIMO 参考。
- Stefan Schwarz, Stefan Pratschner, *Multiple Antenna Systems in Mobile 6G*（IEEE Com. Mag., 2024）——PPT 第 341 页 6G 多天线参考。
- Jianhua Zhang, Yichen Cai, Li Yu, et al., *Four Steps Toward 6G AI-Enabled Air Interface: Wireless Environmental Information Sensing, Feature, Semantics...*——PPT 第 344 页 WEI/AI 空口参考（即笔记 §11 的"四步走"出处）。
- 3GPP SA1 文稿 S1-220094（2022.02，搜索关键词 "ViWi"）——PPT 第 329 页"非射频感知信道"出处。
- 60GHz 室内信道（Hirokazu Sawada et al., VTC 2010 Spring）、E-band（Hani Mehrpouyan et al., IEEE COMMAG 2014）、室内 100GHz（Thomas Kürner et al.）、V2V（David W. Matolak, IEEE Comm. Mag., 2008）、VANET 移动模型（Christoph Sommer, Falko Dressler, IEEE Comm. Mag., 2008）——PPT 第 254–299 页各"补充"页出处，本讲未展开。
