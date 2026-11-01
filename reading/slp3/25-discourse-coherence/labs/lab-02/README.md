# lab-02：中心理论 Cb/Cf/Cp 追踪

> **对应行动**：actions.md 第 2 条 —— 实现中心理论并追踪书中例句
> **运行**：`python3 lab02_centering.py`

## 目的

用 Python 实现中心理论（Grosz et al., 1995）的 Cb/Cf/Cp 追踪算法，对书中例句 (25.30) 进行走查，验证转移状态序列。

## 关键输出（真实运行）

```
U1: John went to his favorite music store.
  Cf = ['John']
  Cb = None
  Cp = John
  转移 = Start

U2: He bought a piano.
  Cf = ['John', 'piano']
  Cb = John
  Cp = John
  转移 = Smooth-Shift

U3: He was excited, finally he could own a piano.
  Cf = ['John', 'piano']
  Cb = John
  Cp = John
  转移 = Continue

连贯性评分（越高越连贯）: 3.00
```

## 产物

- `out/centering_trace.json`：三个话语的 Cf/Cb/Cp 与转移状态

## 结论

- U1 → U2：Smooth-Shift（Cb 出现但不同于前一话语的 Cb）
- U2 → U3：Continue（Cb = Cp 且延续）
- 书中例句的连贯性评分为 3.00（满分 4.0），属于较高连贯性

## 反思

实现中的关键简化：
1. **语法角色**：用规则模拟（人名/代词 → 主语，piano/store → 宾语），实际应用应使用 spaCy 的 dependency parsing
2. **代词共指**：将 He/he 统一映射为 John，实际应用应使用共指消解模型
3. **实体抽取**：只抽取了人名和乐器/地点名词，忽略了其他实体

中心理论的计算流程清晰，但对语法角色标注质量敏感。如果 spaCy 把 "He bought a piano" 中的 "He" 标为 nsubj、"piano" 标为 dobj，则 Cf = [He, piano]，与书中走查一致。
