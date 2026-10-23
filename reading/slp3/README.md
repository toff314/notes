# 读书笔记：Speech and Language Processing（第 1–11 章）

## 书目元信息

- 作者：Daniel Jurafsky、James H. Martin　版次：第三版（2026 年 8 月版）
- 中文译本来源：`/home/yuanwu/books/slp3/zh/md/`（26 章全译）
- 页码口径：中文 Markdown 无印刷页码，全部用 **§节号**（如 §3.3.1）定位
- 阅读目标：**理解**（非应试）
- **书型判定**：**教材型**。依据：章-节-知识点层级完整、定义/公式密集、每章有小结与练习

## 处理范围与进度

| 章 | 目录 | 状态 | 摘录 | 卡片 | 自测 | 行动 | 实验 |
|---|---|---|---|---|---|---|---|
| 1 引言 | [`01-introduction/`](01-introduction/README.html) | ✅ | 65 | 16 | 10 | 4 | 4 |
| 2 词与词元 | [`02-words-and-tokens/`](02-words-and-tokens/README.html) | ✅ | 62 | 14 | 9 | 3 | 3 |
| 3 N-gram 语言模型 | [`03-ngram-language-models/`](03-ngram-language-models/README.html) | ✅ | 62 | 15 | 11 | 3 | 3 |
| 4 逻辑回归 | [`04-logistic-regression/`](04-logistic-regression/README.html) | ✅ | 70 | 16 | 11 | 4 | 2 |
| 5 嵌入 | [`05-embeddings/`](05-embeddings/README.html) | ✅ | 60 | 14 | 11 | 5 | 5 |
| 6 神经网络 | [`06-neural-networks/`](06-neural-networks/README.html) | ✅ | 73 | 18 | 10 | 3 | 3 |
| 7 Transformer 与预训练 | [`07-transformers-and-pretraining/`](07-transformers-and-pretraining/README.html) | ✅ | 122 | 16 | 12 | 4 | 4 |
| 8 后训练 | [`08-post-training/`](08-post-training/README.html) | ✅ | 78 | 15 | 12 | 3 | 3 |
| 9 掩码语言模型 | [`09-masked-language-models/`](09-masked-language-models/README.html) | ✅ | 61 | 14 | 12 | 3 | 3 |
| 10 可解释性 | [`10-interpretability/`](10-interpretability/README.html) | ✅ | 42 | 15 | 10 | 3 | 3 |
| 11 基于检索的模型 | [`11-retrieval-based-models/`](11-retrieval-based-models/README.html) | ✅ | 75 | 20 | 12 | 4 | 4 |
| 12 智能体 | — | ⛔ 原文占位 | — | — | — | — | — |
| 13–26 章 | — | ⬜ 未处理 | — | — | — | — | — |

**本次范围**：第 1–11 章（第 12 章中文稿仅 7 行占位符，跳过）。合计 770 条逐字摘录、173 张卡片、120 道自测、39 条行动、55 条衍生选题、37 个可运行实验。

## 实际输入

| 角色 | 实际文件 | 说明 |
|---|---|---|
| 书稿（必选） | `raw/01/01-introduction.md` 等 11 份 | 中文译本对应章节，逐章全文读完；第 12 章为占位稿未处理 |
| 英文对照（核对用） | `zh/md/NN-*.dual.md` | 核对术语与原句，不单独引用 |
| 划线摘录 | 未提供 | 无划线去向表 |
| 课堂笔记 | 未提供 | 不做书 ↔ 课堂交叉对照 |

## 每章产物

每个章节目录都是一套独立笔记包：

```
<NN-chapter>/
├── README.md          # 本章索引 + 书型/范围/输入 + 六维自评分
├── book-notes.md      # 逐节三区（摘录 / 思考 / 行动）
├── cards.md           # 永久卡片（一卡一主张）
├── self-test.md       # 提取自测协议 + 题目 + 错题归因
├── actions.md         # 行动清单（动词 + 对象 + 时间/验收）
├── spinoffs.md        # 衍生选题（送 write-tech-tutorial / write-zhihu-tech）
├── glossary.md        # 术语表（选做）
└── labs/              # 行动执行闭环（脚本 + 真实产物 + 结论 + 反思）
```

## 自评分

各章六维自评：53 / 53 / 51 / 53 / 51 / 52 / 50 / 52 / 53 / 51 / 51（满分 60），平均约 **51.8/60**，单项均 ≥7，全部通过门槛。明细见各章 `README.md`。

## 机器自检

```bash
python3 /home/yuanwu/zhihu-wiki/.opencode/skills/write-read-notes/scripts/check_read_notes.py \
  <章节目录> --raw ../raw/<NN>
```

第 1–11 章均为 `FAIL=0`（第 12 章无正文，未生成笔记）；第 4 章有 1 条 WARN（2 个 lab 覆盖 4 条同类行动，映射见 `labs/index.md`）。

## 新增后续章节

1. 指定下一章书稿路径（`books/slp3/zh/md/NN-*.md`）；
2. 用 `write-read-notes` 在本目录建 `<NN-slug>/` 并产出六件套 + `labs/`；
3. 建 `../raw/<NN>/` 放入该章文本与 `meta.json`，跑上面的自检；
4. 更新本页表格与 `reading/index.md`；
5. `bash scripts/build-html.sh` 重渲染。
