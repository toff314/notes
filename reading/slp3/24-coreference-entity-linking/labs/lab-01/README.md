# lab-01 提及检测与过滤

## 目的
复现 §24.3 示例：13 候选提及 → 过滤后 9 提及，验证「过滤比检测更难」。

## 运行
```bash
python3 lab01_mention_filter.py
```

## 产物
- `out/filtered_mentions.json`：过滤明细（含理由）

## 结果
candidates=13, filtered=4, kept=9（对齐 §24.3 原例）
