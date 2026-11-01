# lab-04 共指评价指标

## 目的
实现 MUC、B³、CEAF-e，对比同一预测在三指标下的差异。

## 运行
```bash
python3 lab04_evaluation_metrics.py
```

## 产物
- `out/metric_comparison.json`：完美 vs 错误预测的指标值

## 结果
| 预测 | MUC F1 | B³ F1 | CEAFe F1 | CoNLL F1 |
|------|--------|-------|----------|----------|
| 完美 | 1.0 | 1.0 | 1.0 | 1.0 |
| 有错误 | 0.909 | 0.897 | 0.875 | 0.894 |

MUC 偏好大链，B³ 对单例敏感，CEAFe 居中。
