# lab-03　对数几率比信息狄利克雷先验（Monroe 2008）

对应行动：`actions.md` 第 3 条。对应书中 §23.5.1（式 23.7–23.11）。

## 怎么跑

```bash
cd labs/lab-03
python3 lab03_monroe_dirichlet.py
```

依赖：numpy + 标准库 math/csv。

## 输入

- 两个合成语料：正面评论 731 词、负面评论 725 词（各 50 句模板 + 200 个中性词 + 100 个高频中性词 movie）
- 极罕见词：flabbergasting（只在正面出现 1 次）
- 背景语料：合并两个语料，α0 = n_bg × 0.1，αw = f_bg × 0.1

## 产物

| 文件 | 内容 |
|---|---|
| `out/monroe_zscores.csv` | 所有词的 δ、z 分数、简单对数几率比 |

## 关键输出（真实运行）

```
Corpus sizes: pos=731, neg=725

Top 10 words by Monroe z-score (positive):
  amazing               z=+4.9637  simple=       inf
  wonderful             z=+4.6683  simple=       inf
  great                 z=+4.6683  simple=       inf
  excellent             z=+3.6635  simple=       inf
  love                  z=+3.6635  simple=       inf
  fantastic             z=+3.2688  simple=       inf
  perfect               z=+3.2688  simple=       inf
  superb                z=+2.8240  simple=       inf
  best                  z=+1.6226  simple=       inf
  flabbergasting        z=+0.7243  simple=       inf

Bottom 10 words by Monroe z-score (negative):
  this                  z=-0.3917  simple=   -0.1082
  a                     z=-0.4319  simple=   -0.1354
  atrocious             z=-1.6319  simple=       inf
  dreadful              z=-2.3135  simple=       inf
  horrible              z=-3.2876  simple=       inf
  worst                 z=-3.2876  simple=       inf
  hate                  z=-3.6847  simple=       inf
  awful                 z=-5.2758  simple=       inf
  terrible              z=-5.2758  simple=       inf
  bad                   z=-5.2758  simple=       inf

Rare word check:
  flabbergasting: z=0.7243, simple=inf
  movie: z=-0.0637, simple=-0.0096
```

## 结论

1. **简单对数几率比被极罕见词劫持**：flabbergasting 只在正面出现 1 次，simple 得分 = +inf，和 amazing/great 并列第一。这验证了书中「极罕见词在两个语料库中看起来出现情况差别很大」的警告。
2. **狄利克雷先验修正了极罕见词**：flabbergasting 的 z 分数降到 +0.72，排在第 10，不再霸榜。先验计数把它拉向背景语料的预期频率。
3. **高频中性词被正确压低**：movie 在两个语料都出现 100 次，z=-0.06 接近 0，说明 Monroe 方法不会把高频词的微小差异夸大。
4. **方向与书中一致**：正面词（amazing/wonderful/great）排前，负面词（bad/terrible/awful）排后，和图 23.12 的 Yelp 一星 vs 五星方向一致。

## 反思

我原以为「加先验」只是数学技巧，跑出来才看到直观效果：flabbergasting 从 +inf 降到 +0.72，从「和 amazing 并列第一」降到「第 10」。这验证了书中「把计数朝先验收缩」的直觉——它不是在「平滑」，而是在问「相较于背景语料预期的频率，差异有多大？」
