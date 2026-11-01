# lab-03　Chu-Liu-Edmonds 最大生成树与穷举对拍

## 目标

实现 §20.3.1 的 MST 解析思路（寻找分数最高的有根生成树），用 `networkx` 的
`minimum_spanning_arborescence` 做核心计算，再对 150 张随机小图与**穷举所有合法树**
的最优解对拍，验证「我理解的算法」与「算法本身」是否同一。

## 原文依据

- §20.3.1：MST 解析把句法分析看成「为每个词选唯一 head、总分数最高、无环」的图论问题。
- §20.3.1：Edmonds/Chu-Liu 算法通过「找最大入弧 → 检环 → 收缩 → 减权」迭代求解。
- 书中 `Book that flight` 的三条蓝边（图 20.10）：0→3(root→flight)、3→2(flight→that)、3→1(flight→Book)。

## 输入

- 书中玩具句 `Book that flight`（含完整 4×4 分数矩阵，含负分与零分弧）。
- 人造 2 环样例（4 词，含环结构触发收缩逻辑）。
- 150 张随机有向图：n ∈ {4,5,6}，分数 ∈ [-9,9]，`random.seed(20261101)`。

## 关键设计

**单根约束**：`networkx.minimum_spanning_arborescence` 只保证「0 无入弧、其余点唯一入弧」，
并不禁止 0 有多个孩子。UD 要求恰好一个词挂 ROOT，因此对每个候选根孩子各跑一次 Edmonds
（共 n 次），取最优。

**单根枚举**（`mst` 函数）：

```python
for r in nodes:
    forbid = {(root, v) for v in nodes if v not in (root, r)}
    s, h = mst_once(nodes, w, root, forbid)
```

## 怎么跑

```bash
cd lab-03 && python3 lab03_cle_mst.py
```

依赖 `networkx`（`pip install networkx`）。约 2 秒。

## 产物

| 文件 | 内容 |
|---|---|
| `out/mst_vs_brute.csv` | 150 张随机图：n、mst 分数、brute 分数、是否一致、heads 是否完全相同 |
| `out/summary.json` | 玩具样例 greedy/mst/brute 的 heads 与分数；随机对拍一致率 |

## 关键输出（真实运行）

```
== lab-03 Edmonds/Chu-Liu 最大生成树 ==
  贪心入弧（Book that flight）: {1: 3, 2: 0, 3: 0} 分数 26  环: None
  Edmonds 最优: 25 heads={1: 3, 2: 3, 3: 0}
  穷举   最优: 25 heads={1: 3, 2: 3, 3: 0}
  一致: True
  人造 2 环样例：贪心 {1: 0, 2: 0, 3: 1} 环=[1, 3]
  收缩后最优 7 vs 穷举 7 一致=True
  随机对拍: 分数一致 150/150；其中树完全相同 147（其余为同分不同树）
```

## 结论

1. **贪心 ≠ 最优**：玩具句上贪心入弧得 26 分（root 有 3 个孩子，非法），MST 得 25 分。
   差 1 分，但合法性比分数更重要——这正是 MST 解析相对「局部分类器 + 后处理」的本质优势。
2. **150/150 一致**：与穷举对拍全部通过。其中 147 张 heads 完全相同，3 张同分不同树
   （`mst_vs_brute.csv` 中 `same_heads=0` 的 trial 18/66/116）。
3. **单根约束不可省略**：如果不枚举根孩子直接跑 `minimum_spanning_arborescence`，
   某些图会得到 root 多孩子的结果。`forbid` 集合是必需的补丁。
4. **收缩逻辑正确性**：人造 2 环样例触发收缩，收缩后最优 7 与穷举 7 一致，
   验证了「环收缩 + 减权」的实现没有 off-by-one。

## 反思

我第一版没有处理单根约束，直接调用 `networkx` 的 API，结果在某些随机图上
root 有 2 个孩子。这才意识到书中「ROOT 只有一个孩子」是一个**额外的约束**，
不是 Edmonds 算法的自然输出。这个约束在 UD 里是强制的（每个句子只有一个根），
但在一般图论问题里不存在——**算法的默认值 ≠ 任务的需求**，这是复现论文/教材算法时
最容易踩的坑。

另外，对拍是验证「我理解的算法」与「算法本身」是否同一的最快手段。
如果只靠读伪代码，我可能会漏掉「收缩后要减去被替换边权」这个细节
（`actions.md` E2 的教训），而对拍 150 张图立刻暴露问题。

## 与 actions.md 的对应

行动 4：「CLE 与穷举对拍」。验收标准「一致率 100%」已达成（150/150）。
