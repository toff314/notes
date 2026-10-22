# 计算语言学基础 · 第 2 讲 词形态分析 · 差异与存疑

> **双源模式**：转写（`raw/transcript.md`，约 4.2 万汉字课堂逐字稿）+ PPT（`raw/slides-1-word-morphology.pptx` 165 页、`raw/slides-2-min-edit-distance.pptx` 29 页，已抽 `raw/slides-outline.md`）。
> 依据格式：转写侧（§主题 / 原话）＋ PPT 侧（页码）。**PPU 术语一律以 PPT 为准**。

## 一、转写 ↔ PPT 差异

| # | 类型 | 转写 | PPT | 裁决 | 依据 |
|---|---|---|---|---|---|
| 1 | 术语 | 「limitization / demutation / 词音还原」 | **Lemmatization 词形还原** | 以 PPT 为准 | 转写 §英语·词形还原（"apply a demutation"）／ PPT P8、P14、P16 |
| 2 | 术语 | 「passing（剖析）」 | **Parsing（剖析）** | 以 PPT 为准 | 转写 §英语·剖析生成／ PPT P16 |
| 3 | 术语 | 「finish state automator / SSA / SST / FSD」 | **有限状态自动机 FSA / 有限状态转录机 FST** | 以 PPT 为准 | 转写 §三类知识建模、FST／ PPT P20、P21 |
| 4 | 术语 | 「正字法 / ortho graphic」 | **Orthographic(Phonological) Rules（正字法）** | 以 PPT 为准（补英文全称） | 转写 §三类知识／ PPT P18 |
| 5 | 术语 | 「配列规则」（先生口述，未给英文） | **Morphotactics（配列规则）** | 以 PPT 为准（补英文） | 转写 §FST／ PPT P18 |
| 6 | 术语 | 「英文当中还有所谓的字词 sub」「词素」 | **子词（Subwords）/ 子词切割** | 以 PPT 为准 | 转写 §单元识别／ PPT P6、P148 |
| 7 | 数字 | 「100 多页」「170 多页」 | 02-1 分册**共 165 页** | 以 PPT 为准（老师为概数） | 转写 §第2章开场／ PPT 分册页眉 165 页 |

## 二、ASR 噪声（PPT 裁决，正文已采用 PPT 写法）

- 「tokenization 断词」：转写多处作"段词/断词"，PPT 作 **Tokenization（断词）**（P8）
- 「segmentation 切分」：转写作"介词/切分"，PPT 作 **Segmentation（切分）**（P38）
- 「Overlap / Combination ambiguity」：转写作"交集歧义/组合歧义"，PPT 作 **OA / CA**（P41/P43/P46）
- 「OOV out of vocabulary」：转写作"未登词/ov"，PPT 作 **未登录词（Out Of Vocabulary）**（P51）
- 「《你好，李焕英》/ 胜利化工厂」：转写口语提及，PPT 给出规范切分示例（P39/P40）
- 「差点没上上上上海的车」：PPT 确认切分 **差点/没/上/上/上/上海的车**（P8）
- 「A → B → FSA」构图：转写"输入个 B 到一个状态…两个圈儿"，与 PPT FSA 小例（bag/bit）一致（P20）

## 三、存疑（❓ 未定论，不猜答案）

- ❓ 中国先驱人名（转写 §绪论收尾）：**「刘卓」** 疑为 **刘倬**（第 1 讲 PPT 确认）；**「黄昌明」** 疑为 **黄昌宁**；**「于世文」** 疑为 **俞士汶**；**「王知津」（哈工大）**、**「李成树」「方传宁」**、答辩主席 **「周院士」** 均无法核对——第 2 章 PPT 未收录此页
- ❓ 转写"著名华人的科学家叫**徐飞**，推了图像挑战赛"：疑为 **李飞飞 / ImageNet**，PPT 无对应页，请核对原音
- ❓ 转写"我在隔壁的就是**王慧**老师，他们去了联通"：是否为**王小捷**老师或口误，无法判定
- ❓ 转写"复综语"一段指称的具体语言未点名，无法定位到 PPT 的语种分类（P15 只列了复综语/黏着语/屈折语/分析语）
- ❓ 转写"土耳其语…一个词 Uygarlastiramadiklarimizdanmissinizcasina"与 PPT P15 英文串一致，但转写口播"civilized+become+tir(cause)…"多处含糊，以 PPT 英文串为准，口播细节存疑

## 四、PPT 有、转写未覆盖（转写实际讲到"未登录词"后即行下课）

- 【PPT】P41–P52：汉语切分两大难点（边界歧义 / 未登录词）的**规范定义与更多例子**——转写只口语举例，未逐条讲定义
- 【PPT】P53–P67：**基于规则的切分**——朴素算法、**FMM 前向最大匹配**（词典、MaxLen、"语言学很重要"逐步示例）、**BMM 后向最大匹配**、FMM 处理 OA/OOV、扩展 FMM、规则切分总结
- 【PPT】P60–P62：**性能评估**（P/R/F1、Baseline、Ceiling）
- 【PPT】P68–P75：**基于分类的切分**（二分类视角、朴素贝叶斯、特征、MaxEnt、深度表示、联合决策）
- 【PPT】P76–P132：**基于序标的切分**（BIO 标签集、HMM 五元组/Viterbi/Baum-Welch、MEMM 与局部归一化/模型偏置、CRF、特征模板、深度网络+CRF）
- 【PPT】P133–P145：**SIGHAN 评测**数据与结果、跨领域/微博、SOTA（BERT-CRF）、"汉语切分是否必要"（[MengYX2019ACL] P145）
- 【PPT】P146–P165：**子词分割（Subwords）**——两个任务、BPE token learner/parser、unigram language modeling、WordPiece、词 vs 子词
- 【PPT】02-2 P1–P29：**最小编辑距离（MED）**——Levenshtein、三种编辑操作（插/删代价 1、替换代价 2）、动态规划矩阵（execution→intention）、汉语非字/非词错误、汉字形态距离 open question、Glyce 田字格 CNN

## 五、交付说明

- 输入：`raw/transcript.md`（约 4.2 万汉字）+ `raw/slides-1-word-morphology.pptx`（165 页）+ `raw/slides-2-min-edit-distance.pptx`（29 页）+ `raw/slides-outline.md`
- 差异检查按 §1.4 矩阵执行：A 类 ASR 噪声 7 处（以 PPT 裁决）、B 类实质差异 7 条（均双侧出处）、C 类【PPT】补强 8 组；G1 双源就位
