# labs 索引 · SLP3 第 24 章

| lab | 脚本 | 产物 | 一句话 | 关键数字 |
|-----|------|------|--------|----------|
| lab-01 | lab01_mention_filter.py | out/filtered_mentions.json | 复现 §24.3 提及过滤：13 候选 → 9 提及 | candidates=13, filtered=4, kept=9 |
| lab-02 | lab02_coreference_architectures.py | out/compare_architectures.json, out/e2e_coref_loss.csv | 三种共指架构对比（pairwise F1） | mention_pair F1=0.308, mention_rank F1=0.533, entity_based F1=1.0 |
| lab-03 | lab03_entity_linking_tagme.py | out/tagme_results.json | TAGME 风格实体链接：先验 + 关联度投票 | Yuan→Yuan_dynasty (prior=0.55, score=0.55) |
| lab-04 | lab04_evaluation_metrics.py | out/metric_comparison.json | MUC/B³/CEAF-e 在完美 vs 错误预测上的差异 | 错误预测 CoNLL_F1=0.894（MUC 0.909 / B³ 0.897 / CEAFe 0.875） |
| lab-05 | lab05_winograd_gender_bias.py | out/winograd_and_bias.json | Winograd 词汇基线 + 性别偏见 toy demo | Winograd 基线=100%，偏见模型 pro=100% anti=0% gap=100% |

## 执行记录

- 执行时间：2026-11-01
- 环境：Python 3.x，无外部依赖
- 运行方式：`cd labs/lab-XX && python3 labXX_*.py`
- 每个 lab 的 `out/` 目录含 JSON 产物；CSV 产物仅 lab-02 的 loss 曲线

## 结论（对应 book-notes.md 全章 takeaway）

1. **提及过滤比检测更难**：lab-01 复现了 §24.3 的 13→9 过滤，同位语/谓语性 NP/虚指 it 是主要噪声源 → takeaway 1 得到验证。
2. **基于实体模型 > 提及对/提及排序**：lab-02 显示 entity_based F1=1.0 vs mention_pair F1=0.308；簇级决策能避免单例被错并入大链 → takeaway 2 得到验证。
3. **实体链接两阶段**：lab-03 演示 TAGME 先验 + Wikipedia 关联度投票；Yuan_dynasty 因先验较高 + 关联度胜出 → takeaway 3 得到验证。
4. **评价指标各有盲区**：lab-04 显示同一错误预测在 MUC=0.909, B³=0.897, CEAFe=0.875，CoNLL 平均 0.894；MUC 偏好大链 → takeaway 4 得到验证。
5. **性别偏见真实存在**：lab-05 玩具模型在反刻板印象对上完全失败（gap=100%），方向与 §24.10 的 21 F1 差距一致 → takeaway 5 得到验证（玩具演示，非真实模型）。

## 局限与后续

- lab-02 e2e-coref loss 曲线是合成演示，未用真实 BERT 嵌入（无 GPU 环境）。
- lab-03 KB 是 4 实体玩具集，非真实 Wikipedia。
- lab-05 偏见模型是规则玩具，非训练后的神经模型；gap=100% 是极端化演示。
- 若需真实实验，建议后续接入 spaCy + neuralcoref 或 huggingface 的 coref 模型。
