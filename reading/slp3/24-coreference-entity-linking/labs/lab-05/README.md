# lab-05 Winograd 与性别偏见

## 目的
复现 §24.9 Winograd 模式 + §24.10 性别偏见的玩具演示。

## 运行
```bash
python3 lab05_winograd_gender_bias.py
```

## 产物
- `out/winograd_and_bias.json`：Winograd 结果 + 偏见统计

## 结果
- Winograd 词汇基线：4/4 = 100%（玩具语料太小，实际会过拟合）
- 性别偏见：pro=100%, anti=0%, gap=100%（玩具规则模型，方向与 §24.10 一致）
