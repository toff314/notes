# lab-02　arc-standard vs arc-eager：弧什么时候建、交叉弧长什么样

## 目标

同一棵树，用两套转移系统各走一遍，记录**每条弧是在第几个动作建立的**。
这能回答一个文字读不出的问题：两种系统的差别不是「能否解析」，而是
「什么时候敢下结论」。

## 原文依据

- §20.2.4：arc-eager 有四个动作，RIGHTARC 会把缓冲区首词**压栈**（因此它还能
  继续当中心词），LEFTARC 弹栈顶，REDUCE 弹掉「已无未处理依存词」的栈顶。
- §20.2.3：书中强调同一结果可能有多条转移路径。
- §20.1.2：投射性——弧交叉的句子（如含 `which` 关系从句的句子）没有投射分析。

## 输入

- 三句短句（同 lab-01 的金标），用于逐步对比。
- 一句非投射句：`JetBlue canceled our flight this morning which was already late`
  （10 词），金标弧 10 条，其中关系从句 `flight→late` 跨过 `this morning`。

## 做法

两套系统共用一个「按格局查表」的神谕：

- standard：只在栈顶两个元素间建弧，建完即弹依存词。
- eager：栈顶与缓冲区首词之间建弧；RIGHTARC 把首词压栈（保留其当中心词的可能），
  栈顶完成即 REDUCE。缓冲区空时补一条收尾规则（把剩余栈元素按金标挂到栈下方）。

## 运行

```bash
cd lab-02 && python3 lab02_eager_vs_standard.py
```

## 实测输出

```
  Book the flight through Houston              n=5 steps_std=10 steps_eager=10 match_std=True match_eager=True
  Book me the morning flight                   n=5 steps_std=10 steps_eager=10 match_std=True match_eager=True
  I prefer the morning flight through Denver   n=7 steps_std=14 steps_eager=14 match_std=True match_eager=True
  弧 1->3（obj）: standard 第 9 步建，eager 第 4 步建，提前 5 步
  非投射句：10 词 / 10 弧，交叉对 1 个 -> projective=False
    交叉: 2->6 × 4->10
```

## 结论

- **总步数一样**（都是 2n），差别全在顺序：`Book→flight` 这条 obj 弧 eager 在第 4 个
  动作就敢挂（先挂上去，再让它继续长 the / through 的孩子），standard 要等到第 9 个动作
  （等 flight 的所有孩子都挂完才敢弹）。这就是「eager = 提前承诺」的字面含义。
- eager 提前决策换来的是**更大的错误传播面**：第 4 步挂错 `flight` 的头，后面 5 步全在
  错树上继续长；standard 的延迟决策让错误更局部，但栈操作更受限。
- 那句 10 词句确实非投射：`canceled→morning`（跨 `our flight`）与 `flight→late`
  （跨 `this morning`）交叉。任何 arc-standard/eager 解析器都**不可能**产出这棵树，
  不是准确率问题，是表达力问题——这正好接上 lab-04。

## 产物

- `out/delay.csv`：每条弧在两套系统里的建立步号与差值。
- `out/compare.csv`：每句的步数、是否精确还原。
- `out/crossing.json`：交叉弧对与 `projective` 布尔值。

## 坑

- eager 的 RIGHTARC 必须把词**压回栈**；写成「挂完即弃」就退化成 standard，
  步号会一模一样（我第一版就是这样，输出里两列全相等、没有任何时延差）。
- 缓冲区空后仍要收尾，否则最后一条 root 弧永远建不出来。
