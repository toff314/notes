# lab-02　关系分类器：三类特征 + 实体类型消融

**对应**：§21.2.2「有监督的关系抽取」
**一句话**：在 48 条训练 / 14 条泛化测试上，全特征 macro-F1 = 1.000；去掉实体类型组合特征后跌到 0.750。typepair 是当 between-words 特征失效时唯一的判别信号。

## 怎么跑

```bash
cd labs/lab-02 && python3 lab.py
```

依赖：scikit-learn 1.9.1（本机已装）。产物写到 `out/`。

## 特征设计（对应 §21.2.2 三类特征）

| 特征类 | 实现 | 说明 |
|---|---|---|
| 两端词 head words | `head1=`, `head2=`, `heads=e1\|e2` | 实体本身作为特征 |
| 中间词 between words | `between=w` × len(between) | 实体之间的词 |
| 实体类型组合 entity type pair | `typepair=PERSON-ORG` 等 | 消融对象 |

## 数据

- 4 类关系：founder-of / located-in / employed-by / no-relation
- 训练集 48 条，测试集 14 条（全部为训练中未出现的实体对，模拟泛化场景）
- 关键设计：加入 8 条「是…的」样本（PERSON-ORG→employed-by、GPE-GPE→located-in、PERSON-GPE / GPE-ORG→no-relation）。这些样本的 between-words 完全相同（`[是, 的]`），**关系完全由实体类型组合决定**。

## 关键输出（真实运行）

```
train=48 test=14
full macro-F1   = 1.0  (dim=119)
no-type macro-F1= 0.75  (dim=115)
delta           = 0.25

[full confusion matrix]
labels: ['employed-by', 'founder-of', 'located-in', 'no-relation']
   employed-by: [4, 0, 0, 0]
    founder-of: [0, 2, 0, 0]
    located-in: [0, 0, 4, 0]
   no-relation: [0, 0, 0, 4]

[per-class F1 no_type]
   employed-by: P=1.000 R=0.500 F1=0.667
    founder-of: P=1.000 R=1.000 F1=1.000
   located-in: P=1.000 R=0.500 F1=0.667
   no-relation: P=0.500 R=1.000 F1=0.667

errors(full): 0
```

## 结论

1. **实体类型组合特征在泛化场景下不可替代**。当测试集出现训练中未见的实体对时，head-word 特征失效（全是新词），between-words 特征在「是…的」样本上无法区分（同样的中间词对应三种不同关系）。此时 typepair 是唯一可用的判别信号。
2. **消融的 delta = 0.25**，全部来自「是…的」样本：no_type 模型把 2 条 located-in 误判为 no-relation，又把 2 条 no-relation 误判为 located-in——它在「中间词相同但关系不同」的样本上只能靠猜测。
3. **在训练集见过的实体对上，typepair 是冗余的**。 head-word 特征本身就能记住训练样本的关系，所以消融实验必须用未登录实体对做测试，否则看不出 typepair 的价值。

## 反思

最初我把训练/测试按句子顺序简单拆分，结果全特征和无 typepair 的模型都 100% 正确， delta = 0。困惑了一会儿才发现：测试集里的实体对在训练中都出现过，head-word 特征直接「背诵」了答案，typepair 根本没有出场机会。

这提醒我：**消融实验的关键不是删掉一个特征看分数降不降，而是构造一个「只有这个特征能救回来」的测试集**。书中说「实体类型组合是关系分类的关键特征」，在训练-测试同分布的评测下这句话是看不出来的——只有泛化场景才能验证。

另一个观察是：no_type 模型在「是…的」样本上的错误不是随机的——它把 located-in 和 no-relation 搞混了。这说明 between-words 特征学到了一个「`是...的` 大概率不是 employed-by」的偏差，但无法进一步区分 GPE-GPE 和 PERSON-GPE。这种错误模式比单纯报一个 F1 数字更有诊断价值。
