# lab-01　共现矩阵 → PPMI → 截断 SVD

对应行动：`actions.md` 第 1、2 条。对应书中 §5.3（词-上下文矩阵）、§5.4（余弦）、§5.5.3（PPMI 与计数派）。

## 怎么跑

```bash
cd labs/lab-01
python3 lab01_cooccurrence_ppmi_svd.py            # 默认窗口 ±4，秩 20
python3 lab01_cooccurrence_ppmi_svd.py --window 1 --rank 10
```

依赖：numpy、matplotlib（脚本已固定 Agg 后端，无显示环境也能出图）。

## 输入

自建 28 句英文小语料（food 与 computer 两个语义场），词表 31 个（min_count=2）。语料写死在脚本 `CORPUS` 里，可复现且不依赖外部下载。

## 产物

| 文件 | 内容 |
|---|---|
| `out/cooccurrence.csv` | 31×31 原始共现计数 |
| `out/ppmi.csv` | PPMI 加权矩阵（列和 +1 平滑） |
| `out/singular_values.csv` | 奇异值及其解释方差比 |
| `out/word_vectors.csv` | 归一化后的 20 维词向量（可直接算余弦） |
| `out/neighbors.csv` | 5 个目标词 × 5 个余弦近邻 |
| `out/window_sweep_cherry.json` | cherry 行在 ±1 与 ±4 下的非零维对照 |
| `out/book_cosine_check.csv` | 复算书中 §5.4 的两个余弦 |
| `out/vectors_2d.png` | PPMI-SVD 前两维散点（红色 = food 词） |

## 关键输出（真实运行）

```
vocab=31  cooccurrence_nnz=372/961
PPMI nonzero ratio=0.338; rank=20
neighbors:
  cherry -> pie(0.430), a(0.412), in(0.393), are(0.377), is(0.339)
  strawberry -> jam(0.552), are(0.376), sugar(0.371), and(0.360), dessert(0.291)
  digital -> information(0.638), stores(0.331), are(0.307), data(0.287), computer(0.284)
  information -> digital(0.638), device(0.554), on(0.446), data(0.363), to(0.317)
  sugar -> pie(0.398), strawberry(0.371), sweet(0.312), cherry(0.295), cream(0.293)
book cosine check:
  cos(cherry,information)=0.017754 book=0.018 diff=0.000246
  cos(digital,information)=0.996321 book=0.996 diff=0.000321
cos(cherry,strawberry)=0.2261  cos(digital,information)=0.6385
```

## 结论

1. **书中数值可复算**：用 §5.3 图 5.3 的三维计数重算，两个余弦与书中 .018 / .996 的误差都在 0.0004 以内。这说明我对「余弦 = 归一化点积」的理解与书中计算口径一致（§5.4）。
2. **同域词确实靠近**：`digital` 与 `information` 互为第一名（0.638），`strawberry` 的第一名是 `jam`（0.552），`sugar` 的前两名是 `pie` 与 `strawberry`。food 与 computer 两个簇在 `vectors_2d.png` 中分开。
3. **小语料的代价**：`cherry` 的近邻里混进了 `a`、`in`、`are`、`is`。PPMI 只压低了「高频 × 高频」的组合，但本语料的虚词几乎出现在每一句里，仍会挤进前排。这正好说明 §5.9 说的语料规模问题：1 万词以下谈近邻质量意义有限。
4. **窗口改变共现指纹**：cherry 在 ±1 下只与 9 个词共现（`and` 4 次、`pie` 2 次），±4 下扩到 17 个词，新增 `apple`、`strawberry`、`fruit`、`garden`。窗口越大，向量越「主题化」，与 §5.7 的描述一致。

## 反思

我原以为只要做了 PPMI，虚词问题就会自动消失；实际跑出来 cherry 的前五仍有四个功能词。原因是 PPMI 抑制的是「超出独立假设的偶然共现」，而虚词的高频本身是真实的、稳定的共现。要得到干净近邻，还需要停用词处理或更好的加权（如 §5.3 提到的 tf-idf、§5.5.3 的 PPMI 变体），这一步书中没有展开，我是在自己的输出里才看清的。

另一个意外是 SVD 之后 `cherry` 与 `strawberry` 的余弦只有 0.226（连前五都没进），远低于 `digital`–`information` 的 0.638。检查后发现语料里两者的句式差异较大（一个多在「pie/dessert」，一个多在「jam/sugar」），说明「同域」不等于「同上下文指纹」——这也解释了为什么书中要用 Wikipedia 级别的语料。
