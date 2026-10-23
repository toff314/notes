# lab-02 · logit lens vs J-lens（玩具残差流）

## 目的

对应 `actions.md` 学习行动 2，比较两种「读中间层」的方法：

1. **logit lens**：把任意一层的向量直接乘最终层的解嵌入矩阵 `U`，再做 softmax，看它「像什么词」（§10.3）。
2. **J-lens**：用最终层对中间层的雅可比 `J` 把该层向量搬到输出基，再乘 `U`，补偿「中间层与最终层不在同一嵌入空间」的问题（§10.3）。
3. **关键对照**：在残差流中途插入一个正交换基矩阵 `R2`，观察 logit lens 是否失效、J-lens 是否仍能读出。

## 输入

不依赖外部模型，脚本内构造一个 4 层玩具残差流（固定种子 `7`）：

| 项 | 值 |
|---|---|
| 维度 D | 32 |
| 词表 | 13 个词元（`<pad>`、`the`、`fourth`、`planet`、`is`、`mars`、`red` 等） |
| 提示 A | `the fourth planet is` → 答案 `mars` |
| 提示 B | `the fourth planet is mars and its color is` → 答案 `red` |
| 计算 | `h1 = h0 + L1(h0)`；`h2 = R2 @ h1 + L2(R2 @ h1)`；`h3 = R2^{-1} @ h2`；`logits = U @ h3` |
| 换基 | `R2` 为随机正交矩阵，只在 layer 2 起作用 |

`L1` 检测「fourth + planet」写入 `mars`；`L2` 检测「mars + color」写入 `red`。这是一个**分段线性、无偏置**的玩具网络。

## 运行

```bash
cd /home/yuanwu/notes/reading/slp3/10-interpretability/labs/lab-02
python3 lab02_lens.py
```

实测约 **1 秒**。依赖：标准库 + numpy + matplotlib。

## 产物

| 文件 | 内容 |
|---|---|
| `out/lens_rank.csv` | 2 个提示 × 4 层 × 2 种 lens；列含 `top1`、`rank_correct`、`top5` |
| `out/lens_rank.png` | 两个提示的「正确答案排名」随层变化，阴影标出换基层 |
| `out/summary.json` | 逐层排名汇总与最终 top-1 |

## 关键输出

正确答案排名（1 = 最好）：

| 提示 | lens | L0 | L1 | L2（换基） | L3 |
|---|---|---:|---:|---:|---:|
| A_planet（mars） | logit lens | 7 | 1 | **10** | 1 |
| A_planet（mars） | J-lens | 1 | 1 | **1** | 1 |
| B_color（red） | logit lens | 10 | 10 | **13** | 1 |
| B_color（red） | J-lens | 1 | 1 | **1** | 1 |

换基层 top-1：

```text
A_planet L2 logit  top1=<pad>    rank=10
A_planet L2 j_lens top1=mars     rank=1
B_color  L2 logit  top1=planet   rank=13
B_color  L2 j_lens top1=red      rank=1
```

## 结论

1. **换基会让 logit lens 失效**：在 layer 2，`U` 仍按输出基解释向量，但 `h2` 已被 `R2` 旋转；结果 A 提示的 top-1 是 `<pad>`（答案排名 10），B 提示的 top-1 是 `planet`（排名 13）。
2. **J-lens 能补偿换基**：同一层上 J-lens 的答案排名仍为 1，说明雅可比把「中间层的微小变化如何传到输出」纳入了读出。
3. **「读不出」有两种原因**：B_color 在 layer 1 的 logit lens 也失败（排名 10），但这不是换基，而是 `red` 还没被 layer 2 写入。判断失效原因时，必须区分「空间不对」与「信息还没算出来」。
4. **实验演示的是机制，不是规模**：玩具模型只有 13 个词、4 层、两个提示，不能据此推断真实 LLM 的内部工作方式。

## 局限

- **分段线性 + 无偏置导致 J-lens 偏乐观**：模型在局部是线性的，J-lens 的一阶项在小范围内恰好等于剩余网络的前向，因此它在 layer 0/1 也能「看到」未来步骤。真实 Transformer 有 layernorm、偏置与非线性，J-lens 只是局部近似，不会这么干净。
- 换基只有一个正交矩阵 `R2`，没有模拟缩放、平移或逐层不同的基；真实模型的「不同空间」更复杂。
- 没有实现 J-lens 论文中的「在许多上下文上取平均」，也没有做逐 token 的 top-k 可视化，只看了答案排名。
- `top5` 里混有 `<pad>` 与功能词，说明玩具词表的解嵌入没有经过真实训练，概率质量分布不可直接类比真实模型。
- 没有与真实开源模型的 logit lens 实现对照；脚本是自包含的教学实现。

## 反思

我原来把 J-lens 理解成「更贵的 logit lens」，好像两者只是成本差异。这个 lab 让我看到差别在**读法**：logit lens 假设所有层共享输出基，J-lens 先问「这一层动一下，最终输出会怎么动」，再把中间向量搬过去。也正因为如此，J-lens 的结果不能直接当作「模型此刻在想什么」——它是对剩余网络的一个局部线性近似，模型越非线性，这个近似越不可靠。
