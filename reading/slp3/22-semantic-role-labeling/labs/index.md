# Labs 索引 · 第 22 章 语义角色标注

## 行动执行闭环总览

| Lab | 行动来源 | 主题 | 脚本 | 产物 | 状态 |
|---|---|---|---|---|---|
| lab-01 | actions.md #1 | 语态交替与题元网格归纳 | `lab01_alternations.py` | `out/alternations.json` | ✅ 完成 |
| lab-02 | actions.md #2 | PropBank 框架文件解析与角色标注 | `lab02_propbank.py` | `out/propbank_annotations.json` | ✅ 完成 |
| lab-03 | actions.md #3 | Resnik 选择偏好强度与选择关联复算 | `lab03_selectional.py` | `out/selectional_association.json` | ✅ 完成 |
| lab-04 | actions.md #4 | 基于特征的 SRL 特征抽取器 | `lab04_features.py` | `out/feature_vector.json` | ✅ 完成 |
| lab-05 | actions.md #5 | BIO 序列标注 + Viterbi 解码 | `lab05_bio_viterbi.py` | `out/bio_viterbi_output.json` | ✅ 完成 |

## 关键发现

1. **语态交替的多样性**（lab-01）：break 有 5 种语态交替，give 有 2 种与格交替，open 有 3 种实现。语义角色是这些表层变化背后的不变量。

2. **PropBank 的角色相对性**（lab-02）：Arg0/Arg1 不是全局语义标签，而是相对于动词义项的编号。fall.01 没有 Arg0，因为 fall 的主语是原型受事。

3. **选择关联的表达力**（lab-03）：Resnik 的 A_R(v,c) 不仅能表示偏好（正值），还能表示「反偏好」（负值），比简单共现频率表达力更强。

4. **句法路径特征的巧妙**（lab-04）：NP↑S↓VP↓VBD 这样的路径字符串紧凑地编码了成分与谓词之间的句法关系，是 Gildea & Jurafsky 2000 最具表达力的特征。

5. **BIO 标注的双重挑战**（lab-05）：边界检测（B vs I）和角色分类（ARG0 vs ARG1）必须同时正确，基于规则的方法 F1 仅 0.452，验证了监督学习的必要性。
