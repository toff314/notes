# lab-02 共指模型三种架构

## 目的
对比提及对、提及排序、基于实体三种架构，验证 §24.4.3 基于实体模型的优势。

## 运行
```bash
python3 lab02_coreference_architectures.py
```

## 产物
- `out/compare_architectures.json`：三种架构的链、P/R/F1
- `out/e2e_coref_loss.csv`：合成 e2e-coref 训练 loss 曲线（演示用）

## 结果
| 架构 | P | R | F1 |
|------|---|---|-----|
| mention_pair | 0.5 | 0.222 | 0.308 |
| mention_rank | 0.667 | 0.444 | 0.533 |
| entity_based | 1.0 | 1.0 | 1.0 |

entity_based 胜出：簇级决策避免单例被错并入大链。
