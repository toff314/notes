# lab-03　窗口大小对照：短窗偏句法、长窗偏主题？

对应行动：`actions.md` 第 4 条的前半。对应书中 §5.7（窗口大小的语义后果）、§5.3（共现矩阵）。

## 怎么跑

```bash
cd labs/lab-03
python3 lab03_window_size_compare.py
```

约 2 秒。语料只读本章英文对照文件 `/home/yuanwu/books/slp3/zh/md/05-embeddings.dual.md`，不修改书稿目录。

## 语料怎么来的

只取 dual md 中以 `> ` 开头的英文行，过滤掉定义框、图片说明和中文行（ASCII 比例 > 0.9），得到 317 句、9,855 个 token、词表 555（min_count=3）。这是一份**技术体裁**语料，这一点对结论很重要。

## 产物

| 文件 | 内容 |
|---|---|
| `out/window_compare.csv` | 12 个目标词 × 3 个窗口 × 前 8 近邻及余弦 |
| `out/overlap.csv` | 相邻窗口 top-10 的 Jaccard 重叠 + 具体词表 |
| `out/vocab_stats.json` | 各窗口的非零率、秩、第一奇异值占比 |
| `out/window_space.png` | ±2 与 ±5 两个空间的二维投影并排图 |

## 关键输出（真实运行）

```
sentences=317 tokens=9855 vocab=555
window=+/-2:  nnz=0.050 rank=50
window=+/-5:  nnz=0.097 rank=50
window=+/-10: nnz=0.142 rank=50

[word]    w=2: a(0.644), is(0.603), of(0.532), context(0.512), target(0.503), the(0.491)
[word]    w=5: target(0.607), each(0.585), context(0.575), row(0.565), a(0.553), occurs(0.519)
[context] w=2: window(0.534), sentences(0.520), cpos(0.516), word(0.512), noise(0.490)
[context] w=5: window(0.717), target(0.640), word(0.575), column(0.518), matrix(0.510), row(0.510)
[king]    w=2: man(0.901), woman(0.894), queen(0.861), analogy(0.796)
[king]    w=5: woman(0.985), man(0.982), queen(0.960), closest(0.918), analogy(0.826)

overlap@10 (Jaccard): word 0.538 | meaning 0.053 | vector 0.111 |
context 0.111 | similar 0.429 | language 0.176 | king 0.429
```

## 结论

1. **部分成立**：`word` 在 ±2 下的近邻几乎全是虚词（a、is、of、the），±5 前排换成了 `target`、`context`、`row`、`occurs` 这类内容词；`context` 从「句子、cpos、noise」变成「window、target、column、matrix、row」，即从局部搭配转向矩阵/表格这一主题。方向与 §5.7 一致。
2. **幅度远小于书中**：书中 Hogwarts 的例子是近邻类别整体换掉（虚构学校 → 人物/术语），而这里 top-10 平均只有约 1/4 重叠（meaning 仅 0.053，word 0.538）。本语料只有 1 万词且体裁单一，无法产生足够多样的主题共现。
3. **短窗的「句法」表现被虚词污染**：理论上是「同词性词更近」，实测短窗前排常是功能词，因为它们在任意 2 词距离内都高频共现。这说明「短窗偏句法」的前提是已经处理过停用词或采用了下采样（书中未展开）。
4. **窗口越大矩阵越稠密**：非零率 0.050 → 0.097 → 0.142，计算与存储成本随窗口线性上升，这是选择窗口时的现实约束。

## 反思

我原本期待看到「±2 抓同义词、±5 抓主题」的干净二分。实际跑完才意识到两件事：一是这个结论是在**千万级、多体裁**语料上得到的，1 万词的技术章节根本不够；二是短窗的「句法性」很容易被虚词吃掉，必须配合停用词或高频下采样。也就是说，§5.7 给的是趋势而非定律，复现它需要匹配的语料条件。

另外，`king`/`queen` 在两种窗口下都稳居彼此近邻（0.86 / 0.96），说明**强语义关系对窗口不敏感**，窗口主要影响的是弱关系与主题层。这一点书中没写，是我从对照表里读出来的。
