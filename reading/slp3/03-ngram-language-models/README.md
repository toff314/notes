# 读书笔记：《Speech and Language Processing》第三版 · 第 3 章 N-gram 语言模型

## 书目元信息

- 作者：Daniel Jurafsky & James H. Martin　版次：第三版（中文译本，章节 md）
- 来源：`/home/yuanwu/books/slp3/zh/md/03-ngram-language-models.md`
- 页码口径：中文电子版无印刷页码，全部引用统一用 **§节号**（如 §3.6.1）
- 阅读目标：理解（`raw/03/meta.json` 的 `goal` = 理解），同时按教材方式做例题与练习
- **书型判定**：**教材型**（依据：章-节-知识点三级编号；定义/公式密集，式 3.1–3.42 连续编号；章末有小结、历史注记与 12 道练习；术语表以边栏释义形式给出）
- 交叉对照：未提供 `raw/lecture-notes/`，本次不做书 ↔ 课堂对照

## 处理范围与进度

| 章 | 状态 | 说明 |
|---|---|---|
| 第 3 章 N-gram 语言模型 | ✅ 本次完成 | §3.1–§3.8 全章 + 章末练习 |
| 第 4 章 Logistic 回归 | ⬜ 未处理 | 建议下次 |

范围声明：只处理第 3 章，未读其他章节；练习 3.1–3.12 中，3.4/3.5/3.7/3.12 已用代码复核；编程题 3.8–3.11 未逐题实现，其核心（困惑度、采样、平滑、插值）由 `labs/lab-01..02` 覆盖。

## 实际输入

| 角色 | 实际文件 | 说明 |
|---|---|---|
| 书稿（必选） | `raw/03-ngram-language-models.md`（软链到 `/home/yuanwu/books/slp3/zh/md/03-ngram-language-models.md`） | 第 3 章中文全文，1044 行，含公式、边栏术语与练习 |
| 英文对照（可选） | `/home/yuanwu/books/slp3/zh/md/03-ngram-language-models.dual.md` | 仅用于核对被中文排版拆散的公式位置，未直接摘录 |
| 划线（可选） | 未提供 | `raw/03/` 下无 highlights；不做划线去向表 |
| 课堂笔记（可选） | 未提供 | 无 `raw/lecture-notes/` |
| 元信息 | `raw/03/meta.json` | 书名、章节来源、阅读目标、页码口径 |

## 产物清单

| 文件 | 内容 |
|---|---|
| `book-notes.md` | 14 个知识节的三区笔记（摘录/思考/行动），62 条原文摘录，全文约 6.6k 汉字 |
| `cards.md` | 15 张永久卡片（概念卡 6 / 公式卡 7 / 例题卡 2） |
| `self-test.md` | 11 道提取自测 + 遮住作答协议 + 未掌握清单 + 例题重做记录 |
| `actions.md` | 3 条可执行行动（含时间与验收） |
| `spinoffs.md` | 5 个衍生选题（3 个送 write-zhihu-tech，2 个送 write-tech-tutorial） |
| `glossary.md` | 28 条术语表 |
| `labs/index.md` + `labs/lab-01..03/` | 3 个可运行脚本与真实产物（CSV/PNG/JSON），覆盖全部行动 |

## labs 快速复现

```bash
cd labs/lab-01 && python3 ngram_perplexity.py   # 困惑度随 n 与训练量变化
cd ../lab-02 && python3 smoothing_compare.py    # 四种平滑对比
cd ../lab-03 && python3 verify_book_numbers.py  # 书中 20 个数字断言
```

实测要点：248 句去重语料上，2-gram 困惑度 6.68（最低），4-gram 回升到 13.26；插值 7.28，比最优 add-k（8.86）低 17.8%；书中数字 20/20 可复现。

## 自评分（六维，门槛 ≥42/60 且单项 ≥7）

| 维度 | 得分 | 依据 |
|---|---|---|
| ① 摘录忠实度 | 9/10 | 62 条摘录全部经脚本比对为原文连续子串；公式排版断裂处只摘完整句，未猜补 |
| ② 消化深度 | 8/10 | 每节有 I 重述与 A1 关联（编译器的有限状态、检索的预计算之争、加权抽奖），并含质疑 |
| ③ 行动可执行性 | 9/10 | 3 条行动均含对象、时间与可检验验收；全部已跑通并留产物 |
| ④ 卡片复用性 | 9/10 | 一卡一主张，含出处与真实互链；公式卡带条件与例题指引 |
| ⑤ 覆盖完整性 | 8/10 | §3.1–§3.8 全覆盖，⭐/🔴/🔵/⚪ 分拣齐全；无划线可对照，故未满分 |
| ⑥ 可复习性 | 8/10 | 11 题含应用题与 lab 数据题，协议要求遮住笔记；附未掌握与错题归因 |
| **合计** | **51/60** | 单项均 ≥8，过线 |

## 自检

```bash
python3 /home/yuanwu/zhihu-wiki/.opencode/skills/write-read-notes/scripts/check_read_notes.py \
  /home/yuanwu/notes/reading/slp3/03-ngram-language-models \
  --raw /home/yuanwu/notes/reading/slp3/raw/03
```

结果见下方「自检结果」小节（每次改动后重跑，以最后一次为准）。

## 自检结果

- FAIL = 0，WARN = 0（G1–G10 机器可判部分全部通过）。
- 人工复核：摘录已逐条回溯原文；思考区无同义改写凑数；labs 脚本均已实际运行。
- 遗留说明：中文版公式排版有断裂（根号、求和号跨行），本笔记不摘录公式原字符，改用文字与卡片重述，避免把排版噪声当成原文。
