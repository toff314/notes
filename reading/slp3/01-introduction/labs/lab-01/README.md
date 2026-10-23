# Lab 01　bigram 下词预测：给定前缀，模型真的在看前缀吗？

**对应行动**：actions.md 第 1 条
**书中锚点**：§1.1 图 1.1、§1.2.2 香农游戏、§1.6.1 预训练
**脚本**：`bigram_next_word.py`　**产物**：`out/next_word.csv`、`out/summary.json`、`out/next_word.png`

## 输入

- 语料：`/home/yuanwu/books/slp3/zh/md/01-introduction.dual.md` 的英文 blockquote 行（本章英文原文）。
- 清洗：只保留 ASCII 字母占比 >55% 的行，转小写，去掉标点。
- 防泄漏：训练前剔除所有包含 `so long and thanks` 的句子（本章自己举过这句）。

## 运行

```bash
cd labs/lab-01
python3 bigram_next_word.py
```

## 关键输出（真实运行）

```text
tokens=13116 vocab=2381 lines=426
so long and thanks for -> [('example', 0.1471, 'bigram'), ('the', 0.0941, 'bigram'),
                            ('a', 0.0588, 'bigram'), ('each', 0.0353, 'bigram')]
the language -> [('models', 0.4494, 'bigram'), ('model', 0.2785, 'bigram'), ...]
```

`out/next_word.csv` 的完整前 12 名里没有 `all`。书中图 1.1 的 all（.44）/ the（.33）
在这份 1.3 万词的小语料上无法复现。

## 结论（引用自己的产物）

1. bigram 只看**最后一个词**。查询"so long and thanks for"时，模型实际的条件是 `for`，
   于是把本章说明文的常用搭配 `for example`（25 次，0.147）排在第一位，`all` 根本没进前 12。
2. `the language` 的分布则很尖锐：`models` 0.449、`model` 0.279，说明同一语料里
   "the language model(s)" 是高频模板。**语料体裁直接决定"合理续写"长什么样。**
3. `thanks` 在训练集里出现 0 次（OOV），但 bigram 不受影响，因为它的上下文只有 `for`。
   这既暴露了阶数假设的省事，也暴露了它丢信息。

## 反思

我原来以为"bigram 预测下一个词"至少会用到前面几个词，跑完才看清：它把
"so long and thanks for" 压成了一个 `for`。书里 all/the 的高概率不是 n-gram 的功劳，
而是大语料 + 长上下文。这个落差正好解释了为什么第 3 章要从 n-gram 走向神经网络语言模型。
