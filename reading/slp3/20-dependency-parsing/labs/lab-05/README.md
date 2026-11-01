# lab-05　UAS / LAS / LS / EM：复算 §20.4 的六个弧

## 目标

用书中 `Book me the flight through Houston` 的金标树与系统树，复算四个评测指标：
UAS（无标签附着分数）、LAS（有标签附着分数）、LS（标签分数）、EM（完全匹配率）。
验证「UAS 只比 head、LAS 比 head+label、LS 只比 label」的定义理解正确。

## 原文依据

- §20.4：依存解析评测的四个指标定义。
- 书中例句：金标 6 弧（含 root），系统树有 2 处错误——`the` 的 head 错挂到 `Book`，
  `flight` 的标签错标为 `nmod`。

## 输入

| 词 | 金标 (head, label) | 系统 (head, label) | 错误类型 |
|---|---|---|---|
| Book | (0, root) | (0, root) | — |
| me | (1, iobj) | (1, iobj) | — |
| the | (4, det) | (1, det) | **head 错** |
| flight | (1, obj) | (1, nmod) | **label 错** |
| through | (4, nmod) | (4, nmod) | — |
| Houston | (5, pobj) | (5, pobj) | — |

## 怎么跑

```bash
cd lab-05 && python3 lab05_uas_las.py
```

纯标准库，秒级。

## 产物

| 文件 | 内容 |
|---|---|
| `out/metrics.csv` | UAS/LAS/LS/EM 四行：correct/total/score |
| `out/per_word.csv` | 逐词比对：gold_head/sys_head/gold_label/sys_label + 三个 hit 位 |
| `out/label_confusion.csv` | 标签混淆矩阵（按 dep_index 对齐后） |
| `out/summary.json` | 四个指标的小数形式 |

## 关键输出（真实运行）

```
== lab-05 UAS / LAS / LS ==
  句子: Book me the flight through Houston（词数 6）
  UAS: 5/6 = 0.8333
  LAS: 4/6 = 0.6667
  LS: 4/6 = 0.6667
  EM: 0/1 = 0.0000
  UAS-LAS 差 = 0.1667（差 1 条弧：标签错而头对）
  逐词 UAS 命中: Book=1, me=1, flight=1, the=0, through=1, Houston=1
```

`metrics.csv` 内容：

```
metric,correct,total,score
UAS,5,6,0.8333
LAS,4,6,0.6667
LS,4,6,0.6667
EM,0,1,0.0000
```

## 结论

1. **UAS=5/6**：唯一 miss 是 `the`（head 错挂到 Book 而非 flight）。
   验证 UAS 只比 `head` 字段，与 label 无关。
2. **LAS=4/6**：在 UAS 的 5 个 hit 中，`flight` 的 label 错（obj→nmod），
   所以 LAS 比 UAS 少 1。验证 LAS = UAS ∩ label_correct。
3. **LS=4/6**：`the` 的 label 是 det（对），`flight` 的 label 是 nmod（错），
   其余 4 个 label 全对。验证 LS 只比 label，与 head 无关。
4. **EM=0/1**：只要有一条弧不同，整句 EM 就是 0。这是四个指标中最严格的。

## 反思

我第一版算 UAS 时把「方向反了」的弧也算对——比如把 `the→flight` 当成
`flight→the` 的同一关系。这混淆了「两个词之间有弧」与「中心词正确」。
改正后 UAS 从 6/6 降到 5/6，与书中一致。

另一个容易忽略的细节：LS（label score）在 `the` 上是 1（label 对了），
尽管 head 错了。这说明 **LS 与 UAS 是互补的视角**：
UAS 看结构对不对，LS 看标签对不对，LAS 要求两者同时满足。
实际报告中通常只给 UAS 和 LAS，因为 LS 单独使用场景较少。

UAS−LAS=0.1667 这个差值本身也有信息：它等于「head 对但 label 错」的弧占比。
如果系统 UAS 高而 LAS 低，说明标签分类器是瓶颈；反之则可能是 head 选择问题。

## 与 actions.md 的对应

行动 5：「复算 LAS/UAS」。验收标准「LAS=2/3、UAS=5/6、EM=0」已达成。
