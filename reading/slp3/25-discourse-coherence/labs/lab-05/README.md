# lab-05：RST vs PDTB 对比

> **对应行动**：actions.md 第 5 条 —— 对比 RST 与 PDTB
> **运行**：`python3 lab05_rst_vs_pdtb.py`

## 目的

对同一段文本，分别用 RST（§25.1.1）和 PDTB（§25.1.2）两种范式进行标注，从结构形式、标注单位、关系来源、关系类型、对称性、标注成本、典型应用七个维度对比。

## 输入

5 句英文文本：
> Jane took the train from Paris to Istanbul. She had to attend a conference. The conference was about advances in natural language processing. Jane presented her work on discourse coherence. Many researchers attended the session.

## 关键输出（真实运行）

```
── RST 标注（3 个关系）──
  [Reason] NUC: Jane took the train from Paris to Istanbul....
           SAT: She had to attend a conference....
  [Elaboration] NUC: She had to attend a conference....
           SAT: The conference was about advances in natural langu...
  [Elaboration] NUC: Jane presented her work on discourse coherence....
           SAT: Many researchers attended the session....

── PDTB 标注（3 个关系）──
  [because] (隐式) Contingency.Cause.Reason
    Arg1: Jane took the train from Paris to Istanbul....
    Arg2: She had to attend a conference....
  [in particular] (隐式) Expansion.Restatement.Specification
    Arg1: She had to attend a conference....
    Arg2: The conference was about advances in natural langu...
  [and] (显式) Expansion.Conjunction
    Arg1: Jane presented her work on discourse coherence....
    Arg2: Many researchers attended the session....

── 对比 ──
维度           RST                                 PDTB
结构形式         层级树（覆盖全篇）                           扁平关系对（仅相邻片段）
标注单位         EDU（基本篇章单元）                         Arg1 / Arg2（连接词两侧的文本片段）
关系来源         标注者直接判断语义关系                         从篇章连接词列表出发
关系类型         78 种关系，归 16 大类                        4 顶层类别，16 类型，23 子类型
对称性          核心-卫星不对称                              Arg1/Arg2 理论上对称
标注成本         高（需构建完整树）                           较低（只需标注片段对）
典型应用         自动文摘、篇章分析                            连接词消歧、浅层篇章分析
```

## 产物

- `out/rst_vs_pdtb.json`：RST 标注、PDTB 标注、七维对比

## 结论

RST 和 PDTB 是两种互补的篇章关系模型：
- **RST** 适合需要全局结构的任务（如自动文摘），但标注成本高
- **PDTB** 适合局部关系识别（如连接词消歧），标注量大但单条成本低
- 两者关系类型有映射（如 RST 的 Reason ≈ PDTB 的 Contingency.Cause.Reason），但不完全一一对应

## 反思

1. **结构差异**：RST 的树结构能表达篇章的层级组织，PDTB 的扁平对则更灵活
2. **标注哲学**：RST 从语义关系出发，PDTB 从词汇连接词出发，这导致 PDTB 对显式连接词依赖更强
3. **实际应用**：许多现代系统（如 §25.4 的 LCD 模型）不再依赖手工标注的 RST/PDTB，而是用自监督学习连贯表示，但 RST/PDTB 仍是评估和理解篇章结构的重要基准
