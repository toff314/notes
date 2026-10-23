# 读书笔记：《Speech and Language Processing》第三版 · 第 2 章 词与词元

## 书目元信息

- 作者：Daniel Jurafsky、James H. Martin　版次：第三版（中文译文）　来源：`raw/02/02-words-and-tokens.md`
- 页码口径：本书中文译文无印刷页码，统一用节号（§x.y）定位。
- 阅读目标：理解（`raw/02/meta.json` 的 `goal` 为「理解」）。
- **书型判定：教材型**。依据：章—节—小节层级完整；定义密集（每节均有术语框）；含公式（Heaps 定律、编辑距离递推）、例题（intention→execution）、章末小结与 10 道习题。
- 交叉对照：未提供课堂笔记，故不产出 `cross-check.md`。

## 处理范围与进度

| 章 | 状态 | 说明 |
|---|---|---|
| 第 2 章 词与词元 | ✅ 本次完成 | §2.1–§2.9 全部处理，含历史注记与习题线索 |
| 第 1 章 | ⬜ 未处理 | 建议前序补读 |
| 第 3 章 N-gram 语言模型 | ⬜ 未处理 | 建议下次；与 §2.4 的困惑度口径直接衔接 |

## 实际输入（G1 依据）

| 角色 | 实际文件 | 说明 |
|---|---|---|
| 书稿（必选） | `02-words-and-tokens.md` | 中文译文全文 1491 行，已通读；摘录逐字取自该文件 |
| 英文对照（可选） | `02-words-and-tokens.dual.md` | 仅用于术语核对，未作为摘录来源 |
| 划线摘录（可选） | 未提供 | 无 `highlights` 文件，故无划线去向表 |
| 课堂笔记（可选） | 未提供 | 不做书 ↔ 课堂对照 |
| 阅读目标 | `raw/02/meta.json` | `{"goal":"理解"}`，按教材型 SQ3R 路径处理 |

## 产物清单

| 文件 | 内容 | 规模 |
|---|---|---|
| `book-notes.md` | 主笔记：10 个知识节，逐节三区（摘录／思考／行动） | 约 5000 汉字 |
| `cards.md` | 永久卡片：概念卡、公式卡、例题卡 | 14 张 |
| `self-test.md` | 提取自测：协议 + 9 题 + 例题重做记录 | 9 题 |
| `actions.md` | 行动清单 | 3 条 |
| `spinoffs.md` | 衍生选题（送 write-zhihu-tech / write-tech-tutorial） | 5 条 |
| `glossary.md` | 术语表 | 26 条 |
| `labs/index.md` | 行动执行闭环 | 覆盖 3 条行动 |
| `labs/lab-01/` | BPE 从零实现 + 压缩率图表 | 脚本 1、产物 6 |
| `labs/lab-02/` | 最小编辑距离 + 回溯对齐 | 脚本 1、产物 5 |
| `labs/lab-03/` | 正则预词元化审计 | 脚本 1、产物 3 |

## labs 关键结果

| Lab | 真实产物 | 关键数字 |
|---|---|---|
| lab-01 BPE | `out/metrics.json`、`out/compression_curve.png` | 291 字符 → 210 词元（−27.84%），1.386 字符/词元 |
| lab-02 编辑距离 | `out/dp_matrix_intention_execution.csv`、`out/edit_distance_matrix.png` | intention→execution = 8，与书中图 2.20 一致 |
| lab-03 预词元化 | `out/pretokenization.json`、`out/token_counts.png` | 书中例句 5 空白词 → 9 词元；混合句 6 → 18 |

## 自评分（六维，门槛 ≥42/60 且单项 ≥7）

| 维度 | 得分 | 依据 |
|---|---|---|
| ① 摘录忠实度 | 9/10 | 每条带 § 定位，全部逐字回原文校验通过；因无印刷页码只到节级，未给 10 |
| ② 消化深度 | 9/10 | 思考区均为自己的话，含具体经验（分词口径、len(emoji)、AT&T 切分）与实质质疑 |
| ③ 行动可执行性 | 9/10 | 每条含动词、对象、时间与验收；labs 已实际执行并留产物 |
| ④ 卡片复用性 | 8/10 | 一卡一主张、独立可读、出处齐全，链接多为同章真实关联，未连到外部笔记 |
| ⑤ 覆盖完整性 | 9/10 | §2.1–§2.9 全覆盖，含小结与习题线索；无划线可登记，已在输入表说明 |
| ⑥ 可复习性 | 9/10 | 9 题覆盖各节与 ⭐ 节，含提取协议、费曼检验、错题归因表 |
| **合计** | **53/60** | 达标 |

## 复现与自检

```bash
# labs
cd labs/lab-01 && python3 bpe_lab.py
cd labs/lab-02 && python3 edit_distance_lab.py
cd labs/lab-03 && python3 pretokenize_lab.py

# 产物自检
python3 /home/yuanwu/zhihu-wiki/.opencode/skills/write-read-notes/scripts/check_read_notes.py \
  /home/yuanwu/notes/reading/slp3/02-words-and-tokens \
  --raw /home/yuanwu/notes/reading/slp3/raw/02
```
