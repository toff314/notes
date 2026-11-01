# Lab 04 · 基于特征的 SRL 特征抽取器

## 行动来源
actions.md 第 4 条：实现 SRL 特征抽取器，实现 Gildea & Jurafsky 2000 的特征模板，对书中图 22.5 的句子抽取特征向量。

## 运行命令
```bash
python3 lab04_features.py
```

## 关键输出（真实运行）
```
=== 特征向量 ===
句子: The San Francisco Examiner issued a special edition yesterday
谓词: issued
成分: The San Francisco Examiner

  ✓ governing_predicate: issued
  ✓ phrase_type: NP-SBJ
  ✓ head_word: Examiner
  ✓ head_pos: NNP
  ✓ path: NP↑S↓VP↓VBD
  ✓ voice: active
  ✓ linear_position: before
  ✓ subcategorization: VP → VBD NP PP
  ✓ named_entity_type: ORG
  ✓ first_word: The
  ✓ last_word: Examiner

与书中特征对照: 全部匹配
```

产物：`out/feature_vector.json`

## 结论
- 实现了 Gildea & Jurafsky 2000 的 11 项核心特征，对书中图 22.5 的句子抽取的特征向量与书中 §22.6.1 所列完全一致。
- 关键观察：路径特征（NP↑S↓VP↓VBD）是最具表达力的特征——它紧凑地编码了成分与谓词之间的句法关系（NP 上升 S 下降 VP 下降 VBD）。
- 句法路径、次范畴化和语态是「句法驱动」SRL 的核心，而命名实体类型和中心词是「词汇语义」的补充。

## 反思
我原来以为 SRL 特征就是「词袋」或「词向量平均」，做完才发现 Gildea & Jurafsky 的特征是如此精细地利用句法结构。路径特征尤其巧妙——它把整棵句法树的局部结构压缩成一个字符串，既保留了关键信息，又便于分类器处理。这让我对传统 NLP 的特征工程有了新的敬意。
