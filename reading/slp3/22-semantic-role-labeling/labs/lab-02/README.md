# Lab 02 · PropBank 框架文件解析与角色标注

## 行动来源
actions.md 第 2 条：解析 PropBank 框架文件并自动标注，解析 agree.01、fall.01、increase.01 三个框架文件，自动标注 6 个测试句子。

## 运行命令
```bash
python3 lab02_propbank.py
```

## 关键输出（真实运行）
```
=== 解析的框架文件 ===
agree.01: 3 个角色 -> ['Arg0', 'Arg1', 'Arg2']
fall.01: 4 个角色 -> ['Arg1', 'Arg2', 'Arg3', 'Arg4']
increase.01: 5 个角色 -> ['Arg0', 'Arg1', 'Arg2', 'Arg3', 'Arg4']

=== 自动标注 7 个句子 ===

[agree.01] [Arg0 The group] agreed [Arg1 it wouldn't make an offer].
  Arg0: The group
  Arg1: it wouldn't make an offer

[agree.01] [ArgM-TMP Usually] [Arg0 John] agrees [Arg2 with Mary] [Arg1 on everything].
  ArgM-TMP: Usually
  Arg0: John
  Arg2: with Mary
  Arg1: on everything

[fall.01] [Arg1 Sales] fell [Arg4 to $25 million] [Arg3 from $27 million].
  Arg1: Sales
  Arg4: to $25 million
  Arg3: from $27 million

[fall.01] [Arg1 The average junk bond] fell [Arg2 by 4.2%].
  Arg1: The average junk bond
  Arg2: by 4.2%

[increase.01] [Arg0 Big Fruit Co.] increased [Arg1 the price of bananas].
  Arg0: Big Fruit Co.
  Arg1: the price of bananas

[increase.01] [Arg1 The price of bananas] was increased again [Arg0 by Big Fruit Co.].
  Arg1: The price of bananas
  Arg0: by Big Fruit Co.

[increase.01] [Arg1 The price of bananas] increased [Arg2 5%].
  Arg1: The price of bananas
  Arg2: 5%
```

产物：`out/propbank_annotations.json`

## 结论
- agree.01 有 3 个核心角色（Arg0/Arg1/Arg2），fall.01 有 4 个（无 Arg0，因为 fall 的主语是原型受事），increase.01 有 5 个。
- 自动标注的 7 个句子全部与书中 (22.11)–(22.16) 的示例一致，包括 ArgM-TMP 修饰语的识别。
- 关键观察：同一个事件结构（increase）在主动句、被动句、无施事句中，Arg0/Arg1 的句法位置完全不同，但语义角色保持不变——这正是 PropBank 标注的意义。

## 反思
我原来以为 PropBank 的 Arg0/Arg1 是固定的「施事/受事」，做完才发现 fall.01 根本没有 Arg0。这让我意识到：PropBank 的编号是「相对于动词义项」的，不是全局语义标签。这种设计牺牲了跨动词泛化，但换来了标注的一致性和可操作性。
