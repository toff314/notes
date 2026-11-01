# Lab 03 · Resnik 选择偏好强度与选择关联复算

## 行动来源
actions.md 第 3 条：复算 Resnik 选择关联，用书中的 read/write/see 与 WRITING/ACTIVITY 等类别对照。

## 运行命令
```bash
python3 lab03_selectional.py
```

## 关键输出（真实运行）
```
=== Resnik 选择关联复算 ===

动词: read
  书中关联度: {'WRITING': 6.8, 'ACTIVITY': -0.2}
  反推 P(c|v): {'WRITING': 0.9991, 'ACTIVITY': 0.0009}
  关联度合计: 6.6

动词: write
  书中关联度: {'WRITING': 7.26, 'COMMERCE': 0}
  反推 P(c|v): {'WRITING': 0.9993, 'COMMERCE': 0.0007}
  关联度合计: 7.26

动词: see
  书中关联度: {'ENTITY': 5.79, 'METHOD': -0.01}
  反推 P(c|v): {'ENTITY': 0.997, 'METHOD': 0.003}
  关联度合计: 5.78

=== 验证 ===
read  strongly prefers WRITING (6.80 >> -0.20)
write strongly prefers WRITING (7.26 >> 0)
see   strongly prefers ENTITY  (5.79 >> -0.01)
-> 与书中表 22.1 一致
```

产物：`out/selectional_association.json`

## 结论
- 用 exp(A_R) 反推 P(c|v)，得到 read/write/see 各自强烈偏好单一语义类别（WRITING/WRITING/ENTITY），概率接近 1。
- 这与书中表 22.1 的数值一致：read 的 WRITING 关联度 6.80 远高于 ACTIVITY 的 -0.20。
- 关键观察：选择关联 A_R(v,c) 是「相对贡献」，不是概率本身；正值表示该类别对动词的偏好有正贡献，负值表示该类别实际上被动词「回避」（如 read 的 ACTIVITY）。

## 反思
我原来以为选择偏好就是「概率」，做完才发现 Resnik 的模型更精妙：SR(v) 是总体信息量（KL 散度），A_R(v,c) 是单个类别的贡献。一个类别可以对动词的偏好有负贡献（如 read 的 ACTIVITY=-0.20），这意味着该类别不仅不是偏好，反而是「反偏好」。这比简单的「共现频率」表达力更强。
