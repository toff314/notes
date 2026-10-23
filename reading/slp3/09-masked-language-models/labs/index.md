# 第 9 章 · 行动执行闭环（labs/index）

> `actions.md` 是「要做什么」，本目录是「已经跑了、看到了什么」。
> 环境：Linux + Python 3；仅使用标准库 + numpy + matplotlib（`Agg` 后端，无需显示器）。
> 三个脚本均已实际运行，产物在各自 `out/` 下；运行时间：lab-01 数秒、lab-02 约 73 秒、lab-03 数秒。

## 行动覆盖总表

| 行动（actions.md） | 对应 lab | 脚本 | 关键产物 | 结论落点 |
|---|---|---|---|---|
| 第 1 条：对账 15%/80/10/10，解释 leak_rate | `lab-01` | `lab-01/lab01_mask_policy.py` | `masking_stats.csv`、`predictability.csv`、`samples.json`、`masking_rates.png` | §9.3.1 期望 12%/1.5%/1.5% 与实测 11.88%/1.51%/1.48% 一致；「原样保留」仍会泄漏 |
| 第 2 条：复算 MLM 损失，与一元基线对照 | `lab-02` | `lab-02/lab02_toy_mlm.py` | `loss.csv`、`metrics.csv`、`rank_hist.csv`、`predictions.json`、`loss_and_topk.png` | 只有被挖掉的位置进损失；上下文把 top-1 从 0.166 提到 0.333 |
| 第 3 条：BIO→子词→解码 + 实体级评估 + bootstrap | `lab-03` | `lab-03/lab03_bio_alignment.py` | `alignment.csv`、`metrics.csv`、`bootstrap.csv`、`errors.json`、`word_vs_entity.png` | 词级 0.760 时实体 F1 仅 0.500；6 句下 95% 区间宽达 0.60 |

## 复现命令

```bash
cd labs/lab-01 && python3 lab01_mask_policy.py
cd ../lab-02 && python3 lab02_toy_mlm.py
cd ../lab-03 && python3 lab03_bio_alignment.py
```

## lab-01：掩码策略的账

- **脚本与输入**：`lab01_mask_policy.py`；模板生成 6,000 句 × 7 词元，词表 26，种子 20261020。
- **产物**：`lab-01/out/masking_stats.csv`（三种策略的比例与泄漏）、`predictability.csv`（top-1/top-5）、`samples.json`（12 个样例）、`masking_rates.png`。
- **结论**：
  - BERT 80/10/10 的 `[MASK]` 占全文 11.88%、随机词 1.51%、原样 1.48%，与 12%/1.5%/1.5% 的期望差均 <0.3 个百分点。
  - `leak_rate` 为 10.7%，高于 10%：除「原样保留」分支外，随机替换也会以约 7.2% 的概率撞回目标词。
  - `0/50/50` 的 `leak_rate` 为 54.2%，说明「不放 `[MASK]`」不等于「目标不在输入里」；这正是 BERT 要保留 10% 原样、又必须接受 1.5% 错误信号的由来。
- **反思**：我原来把「15% 掩码」当成一个数，跑完才把它拆成「选中率 × 分支比例 × 碰撞率」三层；以后看到任何「X% 掩码」的说法，我会先问它指选中率、`[MASK]` 率，还是进损失的比例。

## lab-02：玩具 MLM 的损失口径

- **脚本与输入**：`lab02_toy_mlm.py`；4,000 训练句 / 1,000 验证句，每句 7 词，词表 26，每句挖 1 个位置（约 14.3%），种子 7。
- **产物**：`lab-02/out/loss.csv`（300 epoch 曲线）、`metrics.csv`（玩具 vs 一元）、`rank_hist.csv`（名次分布）、`predictions.json`、`loss_and_topk.png`。
- **结论**：
  - dev loss 1.766 vs 一元基线 2.889；top-1 0.333 vs 0.166，top-5 0.702 vs 0.513。
  - 训练循环只对 `target` 计算负对数概率，其余 6 个词只提供上下文，实测印证「只有 M 中的词元起作用」；在每句 `|M|=1` 时，这就是式 9.4 的特例。
  - top-1 停在 0.333：词袋均值丢掉词序，`rank_hist.csv` 里 74/1000 的样本排名 ≥10，说明同类别词无法仅凭词袋区分。
- **反思**：我原以为「上下文模型一定远胜一元基线」，但玩具模型只把 top-1 翻了一倍就封顶；这让我更直观地理解为什么真实 MLM 需要多层自注意力，而不是一个上下文词袋。

## lab-03：BIO、子词与实体级评估

- **脚本与输入**：`lab03_bio_alignment.py`；6 句手写数据、42 个词标签；简化 WordPiece 切分；四个预测变体（gold / boundary / type / noise15%）；种子 11；bootstrap 2,000 次。
- **产物**：`lab-03/out/alignment.csv`（词级→子词级标签）、`metrics.csv`（四变体指标）、`bootstrap.csv`（区间）、`errors.json`（FP/FN 明细）、`word_vs_entity.png`。
- **结论**：
  - 词级→子词→首子词解码往返一致率 42/42 = 1.000，流程对金标准无损。
  - boundary 变体词级仍 0.979，但实体 F1 0.917（11 TP / 1 FP / 1 FN）；type 变体词级 0.938、实体 F1 0.917。一个边界错误同时制造 FP 与 FN，与 §9.5.4 的 Jane 例子完全对应。
  - noise15% 词级 0.760、实体 F1 0.500（8 TP / 12 FP / 4 FN）；词级指标明显高估系统能力。
  - 6 句下 bootstrap 95% 区间 [0.242, 0.846]，宽约 0.60，不能据此判断两个系统的 0.1 分差是否真实。
- **反思**：我以前报告 NER 结果时习惯只写 F1，不写匹配口径与响应单位；lab-03 让我看到同一个预测在「词级」和「实体级」下能差 26 个百分点。以后无论看论文还是做项目，我都会先确认「TP 是按词算还是按实体算、边界是否严格匹配」。

## 未做成脚本的行动（说明）

- `actions.md` 的「错题归因」与「复习节奏」是学习行为，不是可计算实验，因此没有单独 lab；其中「α 方向」「15% 口径」「实体级差距」三项已分别由 lab-01、lab-02、lab-03 的产物覆盖。
- `book-notes.md` 各节行动区里还有「手算 BERT-base 参数量」「查 RoBERTa 消融表」等核查型行动；它们依赖外部论文表格或纯手算，按 SKILL §10.1 降级为核查记录，未强行包装成脚本。本页的 3 个 lab 对应 `actions.md` 的 3 条编号行动，编号一一对齐。
