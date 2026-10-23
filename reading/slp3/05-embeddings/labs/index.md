# labs · 行动执行闭环（lab-01 ~ lab-05）

> `actions.md` 是「我要做什么」，这里是「我真的做了，并看到了什么」。
> 全部脚本只依赖标准库 + numpy 2.4.6 + matplotlib 3.10.9，已在 /home/yuanwu 本机实际运行，产物为真实输出。

## 行动 → lab 对照（5/5 覆盖）

| # | actions.md 行动 | lab | 脚本 | 关键产物 | 结论一句话 |
|---|---|---|---|---|---|
| 1 | 复算书中余弦 | lab-01 | `lab01_cooccurrence_ppmi_svd.py` | `lab-01/out/book_cosine_check.csv` | 复算 0.017754 / 0.996321，与书中 .018 / .996 误差 <0.0004 |
| 2 | 建 PPMI+SVD 词向量与近邻图 | lab-01 | 同上 | `neighbors.csv`、`vectors_2d.png`、`ppmi.csv` | 两个语义场分开，但小语料下虚词挤进前排 |
| 3 | 从零实现 SGNS、梯度校验、20 题类比 | lab-02 | `lab02_sgns_from_scratch.py` | `analogies.json`、`loss.csv`、`vector_arithmetic.png` | 梯度误差 3.2e-9；类比 15/20；5 题失败全因返回输入词 |
| 4 | 窗口 ±2/±5 对照 + 点积/余弦对照 | lab-03、lab-04 | `lab03_window_size_compare.py`、`lab04_normalization_and_bias.py` | `window_compare.csv`、`dot_vs_cosine.csv`、两张 png | 长窗确实更主题化，但幅度远小于书中；点积与余弦仅对泛用词分歧明显 |
| 5 | 偏见审计 + 可复现性 | lab-05 | `lab05_bias_audit.py` | `bias_audit.csv`、`bias_permutation.csv`、`bias_effect.png` | 本语料不能复现书中结论（p=0.81 / 0.62，样本量为 3） |

## 复现命令

```bash
cd labs/lab-01 && python3 lab01_cooccurrence_ppmi_svd.py
cd ../lab-02 && python3 lab02_sgns_from_scratch.py
cd ../lab-03 && python3 lab03_window_size_compare.py
cd ../lab-04 && python3 lab04_normalization_and_bias.py
cd ../lab-05 && python3 lab05_bias_audit.py
```

运行环境与耗时（实测）：lab-01 约 1 秒；lab-02 约 80 秒（3 seeds × 12 epochs）；lab-03 约 2 秒；lab-04 约 3 秒；lab-05 约 5 秒。

## 每条行动的结论与反思

### 行动 1（lab-01）：书中余弦可复算
- **结论**：cos(cherry, information)=0.017754、cos(digital, information)=0.996321，与书中 .018 / .996 一致；说明「余弦 = 归一化点积」的实现与教材口径相同。
- **反思**：手算时我漏了三维展开中的一项，脚本跑完才对齐；数值复算是检验「是否真懂公式」最便宜的方式。

### 行动 2（lab-01）：PPMI+SVD 的近邻
- **结论**：`digital` 与 `information` 互为第一（0.638）；`strawberry` 第一是 `jam`（0.552）；food/computer 两簇在二维图中分开。但 `cherry` 的近邻混入 a/in/are/is。
- **反思**：PPMI 不能自动解决虚词问题；停用词处理与高频下采样是必要步骤，书中未展开。

### 行动 3（lab-02）：SGNS 与类比
- **结论**：数值梯度校验 3.2e-9；王室 5 题 + 首都 5 题全中，形容词三级形态 5 题全败；失败均为「raw top1 是输入词」。
- **反思**：类比评测必须显式排除 a、b、a* 及其形态变体，否则会把实现缺陷误判为「向量没学好」。

### 行动 4（lab-03 + lab-04）：窗口与归一化
- **结论**：长窗把 `word` 的虚词近邻换成内容词，`context` 从局部搭配转向矩阵主题；top-10 平均 Jaccard 约 0.27。点积与余弦在 `king` 上完全一致（100%），在 `word/meaning/context` 上只有 50%–60%；原始计数向量长度与 log 频次相关 0.722，PPMI-SVD 后降到 0.247。
- **反思**：窗口效应的强度依赖语料规模与体裁；归一化散布在 PPMI、SVD、方向归一化三处，只做最后一步不够。

### 行动 5（lab-05）：偏见审计
- **结论**：性别—属性平均余弦差 +0.016 / −0.042，置换检验 p = 0.813 / 0.619；7 个性别词有 4 个零频，人文属性词只剩 1 个。结论是「本语料不可复现」，不是「无偏见」。
- **反思**：不做置换检验就会把一个噪声差值当成发现；审计结论必须同时报样本量。

## 已知局限

- 语料规模小（lab-01 为 28 句自建语料；lab-03~05 为 9,855 token 的技术章节），近邻质量与窗口效应都受此限制，结论只能作方向性参考。
- lab-02 的语料是模板生成的合成语料，类比成功率不代表真实语料上的表现；它验证的是「算法实现 + 关系可学性」，不是「word2vec 在中文上的效果」。
- lab-05 的属性词表是手工挑选的，未做多词表稳健性检验（那需要更大的语料才有意义）。
