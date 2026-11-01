# lab-01：RST 关系手工标注

> **对应行动**：actions.md 第 1 条 —— 手工标注 RST 关系
> **运行**：`python3 lab01_rst_annotation.py`

## 目的

对 5 段文本（含书中例句）标注 Reason、Elaboration、Evidence、Attribution、List 五种 RST 关系，与书中 §25.1.1 定义逐条对照。

## 关键输出（真实运行）

```
RST 关系标注完成：5/5 正确，准确率 100.0%
结果已保存到 labs/lab-01/out/rst_annotations.json
  ✓ t1: Reason (正确: Reason)
  ✓ t2: Elaboration (正确: Elaboration)
  ✓ t3: Evidence (正确: Evidence)
  ✓ t4: Attribution (正确: Attribution)
  ✓ t5: List (正确: List)
```

## 产物

- `out/rst_annotations.json`：5 条标注记录，含预测、正确答案、是否一致

## 结论

5 种 RST 关系全部标注正确。书中例句的特征明显：
- Reason：卫星给出核心的原因（「她必须去参加一个会议」）
- Elaboration：卫星给出核心的附加信息（「她住在大片 Kansas 草原的中央」）
- Evidence：卫星说服读者接受核心（「他的车停在外面」）
- Attribution：卫星给出转述话语的归属（「分析师估计」）
- List：多核心并列（「Billy Bones 是大副；Long John，他是舵手长」）

## 反思

Evidence 和 Elaboration 的定义只差「目的在说服读者」这一从句，实际标注时容易混淆。书中的例句通过「车停在外面」这个具体证据 vs 「住在大片草原」这个背景细节，给出了可操作的区分标准。
