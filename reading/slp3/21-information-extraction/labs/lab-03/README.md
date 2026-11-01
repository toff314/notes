# lab-03　RlogF 公式重建与自举语义漂移

**对应**：§21.2.3「自举（bootstrapping）」
**一句话**：中文版式(21.10)丢了分母与对数，按 Riloff & Jones (1999) 重建后，RlogF 能在一轮内选出高精度模式（P=1.0）；但一旦实体词典被自动扩展，第二轮 precision 跌到 0.0——语义漂移不可避免。

## 怎么跑

```bash
cd labs/lab-03 && python3 lab.py
```

零依赖（matplotlib 可选，缺了只跳过画图）。产物写到 `out/`。

## Part 1：RlogF 公式重建

中文版式(21.10)在 Markdown 里只剩：

```
Conf RlogF(p) = |hits(p)|
```

按 Riloff & Jones (1999) 重建为：

```
RlogF(p) = |hits(p)| / ( |finds(p)| * log(|finds(p)|) )
```

其中 `hits(p)` 是模式 p 命中且属于目标关系的次数，`finds(p)` 是 p 的总命中次数。

**重建前后的排名差异**（用 5 个合成模式演示）：

| pattern | hits | finds | log(finds) | 错误公式得分 | 正确 RlogF |
|---|---|---|---|---|---|
| P1_等 | 5 | 6 | 1.7918 | 5.00 | 0.4651 |
| P2_包括 | 3 | 4 | 1.3863 | 3.00 | 0.5410 |
| P3_是一种 | 2 | 3 | 1.0986 | 2.00 | 0.6068 |
| P4_例如 | 1 | 10 | 2.3026 | 1.00 | 0.0434 |
| P5_称为 | 1 | 2 | 0.6931 | 1.00 | 0.7213 |

- 错误公式（只有 hits）排名：P1 > P2 > P3 > P4 = P5
- 正确 RlogF 排名：P5(0.721) > P3(0.607) > P2(0.541) > P1(0.465) > P4(0.043)

关键差异：P4「例如」在错误公式下得 1 分，在正确公式下只有 0.043——因为它 finds=10 但只命中 1 次，log-finds 分母大幅惩罚了这种「高触发、低命中」的模式。P5「称为」虽然 hits 只有 1，但 finds=2，分母小，所以得分最高。**RlogF 的本质是「命中率除以触发频率的修正」，不是单纯的命中率。**

## Part 2：三轮自举实验

### 设置

- 种子：3 个已知上下位对（紫菜-红藻、国航-航空公司、Python-编程语言）
- 语料：16 句「干净」样本 + 20 句「脏」样本（干扰/漂移源）
- 模式：X等Y / X包括Y / X是Y的一种（只在词典内匹配，模拟 NER 约束）
- Round 1 后模拟「NER 自动扩展」：把脏样本中的 17 个新实体加入词典（无人工校验）

### 关键输出（真实运行）

```
Round 1:
  Top patterns: ['X是Y的一种', 'X等Y']
  Pattern scores:
    X是Y的一种       RlogF=  1.4427  (hits=2, finds=2)
    X等Y          RlogF=  0.1803  (hits=3, finds=8)
    X包括Y         RlogF=  0.0000  (hits=0, finds=2)
  New pairs: [('MySQL', '数据库'), ('PostgreSQL', '数据库'), ('Rust', '编程语言'), ('东航', '航空公司'), ('石花菜', '红藻')]
  Precision: 1.0  (5/5)
  Cumulative pairs: 8

Round 2:
  Top patterns: ['X是Y的一种', 'X等Y']
  Pattern scores:
    X是Y的一种       RlogF=  1.4427  (hits=2, finds=2)
    X等Y          RlogF=  0.1176  (hits=8, finds=22)
    X包括Y         RlogF=  0.0000  (hits=0, finds=2)
  New pairs: [('MySQL', '命令'), ('MySQL', '开源软件'), ('PostgreSQL', '关系型数据库'), ('Python', '脚本'), ('Rust', '系统语言'), ('国航', '企业'), ('数据库', '问题'), ('石花菜', '藻类'), ('紫菜', '食材'), ('红藻', '水生植物'), ('红藻', '海洋生物'), ('编程语言', '工具'), ('航空公司', '行业')]
  Precision: 0.0  (0/13)
  Cumulative pairs: 21

Round 3:
  Top patterns: ['X是Y的一种', 'X等Y']
  Pattern scores:
    X是Y的一种       RlogF=  1.4427  (hits=2, finds=2)
    X等Y          RlogF=  0.3235  (hits=22, finds=22)
    X包括Y         RlogF=  0.0000  (hits=0, finds=2)
  New pairs: []
  Precision: 0.0  (0/0)
  Cumulative pairs: 21
```

Drift 曲线：

| Round | New | TP | Precision | Cumulative |
|---|---|---|---|---|
| 1 | 5 | 5 | 1.0000 | 8 |
| 2 | 13 | 0 | 0.0000 | 21 |
| 3 | 0 | 0 | — | 21 |

首次 precision < 0.6：**Round 2**。最终累计 precision：8/21 = 0.381。

## 结论

1. **RlogF 在严格词典下工作正常**。Round 1 选出「X是Y的一种」（RlogF=1.44，2/2 全中）和「X等Y」（RlogF=0.18，3/8），扩展的 5 个新对全部正确（P=1.0）。
2. **语义漂移的来源是实体词典的自动扩展，不是模式本身**。Round 2 把脏实体加入词典后，同样的「X等Y」模式开始匹配到「MySQL-命令」「Python-脚本」「国航-企业」等错误对——模式没变，匹配范围变了。
3. **RlogF 无法阻止漂移，甚至可能加剧**。注意 Round 3 中「X等Y」的 RlogF 从 0.1176 上升到 0.3235——因为 Round 2 的错误对也被加入了 known_pairs，hits 从 8 增加到 22，RlogF 被「洗白」了。如果语料更大，这个模式会继续扩展更多错误对。
4. **「X是Y的一种」始终保持 RlogF=1.4427（2/2）**，因为它只匹配了 2 句干净样本，没有匹配到脏样本。这说明高 RlogF 不等于高 recall——它只反映了「在当前已知对上的命中率」，对未知噪声没有免疫力。

## 反思

我最初以为 RlogF 的 log-finds 分母能自动过滤噪声模式。实验显示它确实惩罚了「高触发低命中」的模式（如 Part 1 的 P4），但在自举的迭代场景中，**噪声对一旦被加入 known，就会反哺模式的 hits，让 RlogF 上升**。这是自举漂移的一个结构性问题：评价指标和被扩展的数据耦合在一起。

另一个发现是：在中文里，「等」作为列举标记和动词的歧义是漂移的重要来源。脏样本中「Python 等脚本跑完再说」的「等」是动词，但由于「Python」和「脚本」都在词典里，模式照样匹配。这提示我：实体类型约束（如要求两端类型一致）可能比 RlogF 更能阻止这类漂移——lab-01 已经验证了类型约束的有效性。
