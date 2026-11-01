# 《Speech and Language Processing》第 3 版 · 第 22 章 · 行动清单（5 条）

> 从各节行动区提炼的本章级 A2；每条 = 动词 + 对象 + 时间/验收。
> 教材型含错题归因条目。每条行动由 `labs/` 下对应脚本执行，结果见 `labs/index.md`。

## 学习行动（教材型）

1. **归纳语态交替与题元网格**：对 break、give、open 三个动词，各写出全部可能的题元网格和语态交替形式，在 2026-11-02 前完成，与书中 (22.3)–(22.8) 对照（验收：每个动词至少 3 种实现方式，且标注每种实现的句法位置，落盘为 `labs/lab-01/out/alternations.json`）。——来自 §22.2
2. **解析 PropBank 框架文件并自动标注**：用程序解析 agree.01、fall.01、increase.01 三个框架文件，自动标注 6 个测试句子，2026-11-03 前完成（验收：每个句子的 Arg0/Arg1/Arg2/ArgM 标注与书中示例一致，输出 `labs/lab-02/out/propbank_annotations.json`）。——来自 §22.4
3. **复算 Resnik 选择关联**：复算选择偏好强度 SR(v) 和选择关联 A_R(v,c)，用书中的 read/write/see 与 WRITING/ACTIVITY 等类别对照，2026-11-04 前完成（验收：数值与书中表 22.1 一致，误差 <0.01，落盘 `labs/lab-03/out/selectional_association.csv`）。——来自 §22.7.2
4. **实现 SRL 特征抽取器**：实现 Gildea & Jurafsky 2000 的特征模板，对书中图 22.5 的句子（The San Francisco Examiner issued a special edition yesterday）抽取特征向量，2026-11-05 前完成（验收：输出与书中 §22.6.1 所列特征一致的特征表，落盘 `labs/lab-04/out/feature_vector.json`）。——来自 §22.6.1
5. **实现 BIO 标注 + Viterbi 解码**：实现一个简化的 BIO 序列标注器，对 5 个测试句子输出标签序列并计算 F1，2026-11-06 前完成（验收：输出标签序列和 F1 值，与基线 BIO 对照，落盘 `labs/lab-05/out/bio_viterbi_output.json`）。——来自 §22.6.2、§22.6.3

## 错题归因（教材型，来自 self-test）

| 错题 | 类型 | 归因 | 补救动作 | 截止 |
|---|---|---|---|---|
| break 的语态交替（漏「工具作主语」） | 知识性 | 对「居间工具 vs 使能工具」区分不清 | 回 §22.3，用 lab-01 重新归纳 | 2026-11-02 |
| change position on a scale 框架元素（漏「取值范围」） | 技巧性 | 只记核心角色，忽略边缘角色 | 对照图 22.3 补全 | 2026-11-03 |
| Resnik 选择关联计算（P(c\|v) 和 P(c) 搞反） | 知识性 | 条件概率方向不清 | 回 §22.7.2，配合 lab-03 数值复算 | 2026-11-04 |
