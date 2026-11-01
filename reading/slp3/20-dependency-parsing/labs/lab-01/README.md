# lab-01　arc-standard 转移系统与训练神谕

## 目标

不看论文伪代码，只按书里的三动作定义把 arc-standard 写出来，再用「训练神谕」
从金标树回放出一条合法的动作序列，验证**回放结果等于金标**。

## 原文依据

- §20.2：栈、输入缓冲区、依存关系集合、神谕（oracle）四个部件。
- §20.2.1：用神谕把树库转成分类器训练样本。
- 书中 LEFTARC / RIGHTARC 的约定是：**LEFTARC 让栈顶 S1 当中心词、第二个词 S2
  当依存词，并弹掉 S2**；RIGHTARC 相反，弹掉栈顶 S1。

## 输入

四句手写金标（弧用 `head→dep` 表示，节点 0 是 ROOT）：

| 句 | 词数 | 弧数 | 弧 |
|----|------|------|-----|
| Book me the morning flight | 5 | 5 | 0→1 root, 1→2 iobj, 1→5 obj, 5→3 det, 5→4 compound |
| Book the flight through Houston | 5 | 5 | 0→1 root, 1→3 obj, 3→2 det, 3→4 nmod, 4→5 pobj |
| I prefer the morning flight through Denver | 7 | 7 | 0→2 root, 2→1 nsubj, 2→5 obj, 5→3 det, 5→4 compound, 5→6 nmod, 6→7 pobj |
| United canceled the morning flights to Houston | 7 | 7 | 0→2 root, 2→1 nsubj, 2→5 obj, 5→3 det, 5→4 compound, 5→6 nmod, 6→7 pobj |

## 神谕规则（三条前提缺一不可）

1. 若 `(S1, S2)` 在金标里且 `S2 != ROOT` 且 S2 的所有依存词都已挂好 → `LEFTARC`。
2. 否则若 `(S2, S1)` 在金标里且 S1 的所有依存词都已挂好 → `RIGHTARC`。
3. 否则 `SHIFT`；缓冲区空了仍不满足 1/2 就停下并报错。

第 1 条少写「S2 的依存词都已挂好」，就会把还能长孩子的词提前弹掉——
这是我第一版在第 6 步就弹飞 `flight` 的原因。

## 运行

```bash
cd lab-01 && python3 lab01_arc_standard_oracle.py
```

## 实测输出

```
  Book me the morning flight                     n=5 arcs= 5 actions=10 recovered= 5 exact=True
  Book the flight through Houston                n=5 arcs= 5 actions=10 recovered= 5 exact=True
  I prefer the morning flight through Denver     n=7 arcs= 7 actions=14 recovered= 7 exact=True
  United canceled the morning flights to Houston n=7 arcs= 7 actions=14 recovered= 7 exact=True
  exact match: 4/4  total actions: 48
  actions == 2n for all sentences: True
```

## 结论

- 4 句全部精确还原；每句动作数恰为 `2n`（n 次 SHIFT + n 次建弧），
  这就是「线性时间」的字面含义：动作数是词数的 2 倍，不是平方。
- 同一条弧在不同句子里的**相对步号不同**（`Book me…` 里 obj 在第 9 个动作，
  另一句在第 5 个），说明神谕是「按格局决策」而不是「按位置执行」。

## 产物

- `out/transitions.csv`：每步的栈、缓冲区、动作、新建弧。
- `out/parse_results.csv`：每句的还原弧与金标比对。
- `out/summary.json`：`exact=4/4`、`total_actions=48`。

## 坑

- 约定方向。照 Nivre 论文伪代码写 LEFTARC（弹栈顶）会得到镜像的栈内容，
  虽然最终树相同，但「第几步建哪条弧」全错，lab-02 的时延对比也就没有意义。
- ROOT 不能当依存词：`S2 == ROOT` 时必须禁 LEFTARC，否则根会被挂到别人下面。
