# 第 20 章 依存句法分析 · 读书笔记包

## 1. 书目元信息

| 项 | 值 |
|---|---|
| 书名 | Speech and Language Processing（第 3 版） |
| 章节 | 第 20 章 依存句法分析（Dependency Parsing） |
| 中文译为 | 「依存句法分析」 |
| 阅读目标 | 理解（`meta.goal = 理解`） |
| 引用方式 | 中文译文无印刷页码，全部引用使用 `§节号` |
| 生成日期 | 2026-11-01 |

## 2. 处理范围与进度

- 覆盖范围：§20 导论、§20.1（含 20.1.1–20.1.3）、§20.2（含 20.2.1–20.2.4）、§20.3（含 20.3.1–20.3.3）、§20.4、§20.5 小结与历史注记。
- 状态：**全章已读完并落盘**。知识块 12 个，永久卡片 15 张，自测 11 题，行动 5 条，lab 5 个（全部真实运行）。
- 未覆盖：`Further Reading` 中的具体文献评述与脚注只做了取舍性提及（历史注记并入最后一节），未逐条追踪。

## 3. 实际输入

| 用途 | 文件 |
|---|---|
| 中文正文（摘录源） | `/home/yuanwu/books/slp3/zh/md/20-dependency-parsing.md` |
| 原始抽取稿（摘录逐字校验用） | `/home/yuanwu/notes/reading/slp3/raw/20/20-dependency-parsing.md` |
| 中英对照（术语核对） | `/home/yuanwu/books/slp3/zh/md/20-dependency-parsing.dual.md` |
| 章节元数据 | `/home/yuanwu/notes/reading/slp3/raw/20/meta.json` |

> 摘录全部逐字取自 `raw/20/20-dependency-parsing.md`（与中文正文同文件、同 957 行），逐条用脚本比对，0 处改写。行内跨行的句子一律不摘，避免拼行。

## 4. 产物清单

| 文件 | 作用 | 规模 |
|---|---|---|
| `README.md` | 本索引：范围、输入、产物、labs 一览、自评分、自检 | 本文件 |
| `book-notes.md` | 主体笔记：12 个知识块 × （摘录 / 思考 / 行动）+ 5 条 takeaway + 优先级依据 | 约 4.2 万字节 |
| `cards.md` | 永久卡片 15 张，卡卡带 `**出处**：§x.y` | 15 卡 |
| `self-test.md` | 提取自测协议 + 11 题 + 答案要点 + 未掌握清单 + 重做记录 | 11 题 |
| `actions.md` | 5 条可验收行动 + 错题归因表 + 行动↔lab 对照 | 5 条 |
| `spinoffs.md` | 6 个衍生选题（主题串 / 锚点 / 增益 / 缺口 / 体量） | 6 选题 |
| `topics.json` | 选题机读清单（schema 为对象，含 6 条 topics） | 6 条 |
| `labs/index.md` | lab 总览：行动↔lab 对照、复现命令、实测耗时、结论与反思 | 1 份 |
| `labs/lab-01..05/` | 5 个可复现实验（脚本 + 输出 + README） | 见下 |

## 5. 摘录忠实度说明

- 每条摘录形如 `「……」(§x.y)`，圆括号内只写节号，不写页码。
- 校验方法：`python3 /tmp/verify_notes.py` 对每个「」内文本做 `in` 判断（子串匹配，不做任何归一化），结果为 **0 处不匹配**。
- 已剔除的情形：跨行断句的原文（抽取稿里一行一个排版块，拼行即改写）、含图片占位符的段落、以及公式被 OCR 打散的句子。
- 公式区（式 20.11 / 20.14 / 20.16）排版错乱，处理方式见 `book-notes.md` 开头「可疑处」，并在 lab-03/lab-04/lab-05 用可运行代码重建校验。

## 6. labs 一览

| lab | 主题 | 对应行动 | 关键产物 |
|---|---|---|---|
| lab-01 | arc-standard 转移系统 + 训练神谕，4 句金标全还原 | 行动 3 | `transitions.csv`、`parse_results.csv` |
| lab-02 | arc-standard vs arc-eager 的弧建立步号；非投射交叉检测 | 行动 1、2 | `delay.csv`、`crossing.json` |
| lab-03 | Chu-Liu-Edmonds 实现 + 与穷举最优树对拍 | 行动 4 | `mst_vs_brute.csv`、`summary.json` |
| lab-04 | 投射约束的代价：穷举投影最优 vs 全局最优 | 行动 4 | `projective_gap.csv`、`summary.json` |
| lab-05 | LAS / UAS / LS / EM 复算 §20.4 例子 | 行动 5 | `metrics.csv`、`per_word.csv` |

复现：

```bash
cd /home/yuanwu/notes/reading/slp3/20-dependency-parsing/labs
for d in lab-0*; do (cd "$d" && python3 *.py); done
```

## 7. 六维自评分

| 维度 | 分 | 依据 |
|---|---|---|
| 忠实度 | 9 | 60 条摘录逐字比对 0 处偏差；跨行句一律不摘 |
| 覆盖度 | 8 | §20.1–§20.5 全覆盖；Further Reading 只做取舍性提及 |
| 深度 | 8 | 神谕、CLE 减权、双仿射三处都做到「能实现 + 能对拍」 |
| 可复现性 | 9 | 5 个 lab 全部一键运行，产物 CSV 落盘，结论逐条对应输出 |
| 可复习性 | 8 | 15 张卡 + 11 题自测 + 优先级四档，均带出处 |
| 行动性 | 9 | 5 条行动全部有验收标准，且已由 lab 兑现 |
| **合计** | **51/60** | 各项 ≥8，无短板项 |

## 8. 自检

门禁命令：

```bash
cd /home/yuanwu/notes/reading/slp3 && python3 \
  /home/yuanwu/zhihu-wiki/.opencode/skills/write-read-notes/scripts/check_read_notes.py \
  ./20-dependency-parsing --raw ./raw/20
```

预期：`FAIL=0 WARN=0`，退出码 0。逐题复测用 `self-test.md` 的「提取自测协议」，间隔 24 小时 / 3 天 / 7 天各一次。
