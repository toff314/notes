# 读书笔记：Speech and Language Processing（第 3 版）· 第 21 章 信息抽取

## 书目元信息

- 作者：Daniel Jurafsky、James H. Martin　版次：第三版（2026 年 8 月版）
- 章节：第 21 章 信息抽取：关系、事件与时间（§21–§21.8，含小结、历史注记、练习）
- 中文译本来源：`/home/yuanwu/books/slp3/zh/md/21-information-extraction.md`
- 页码口径：中文 Markdown 无印刷页码，**全部用 §节号定位**（如 §21.2.4）；章首导论统一记 §21
- 阅读目标：**理解**（非应试）
- **书型判定**：**教材型**。依据：章-节-知识点层级完整、定义框与公式密集、每章有小结/历史注记/练习

## 处理范围

- 本次范围：**第 21 章单章**（全书 26 章，本章为信息抽取章）
- 覆盖小节：§21 导论、§21.1 关系抽取、§21.2.1–21.2.6 六种关系抽取算法、§21.3 抽取事件、§21.4 表示时间（含 §21.4.1 Reichenbach）、§21.5 表示体、§21.6 TimeBank、§21.7.1–21.7.3 自动时间分析、§21.8.1–21.8.2 模板填充
- 未纳入：练习 21.1–21.4 仅列为 lab 选题，不逐题作答；图 21.1/21.2/21.11/21.19 等图版内容按正文转述，不复制原图

## 实际输入

| 角色 | 实际文件 | 说明 |
|---|---|---|
| 书稿（必选） | `raw/21/21-information-extraction.md`（→ `books/slp3/zh/md/21-information-extraction.md`） | 1,034 行 / 75,354 字节，全文读完；81 条摘录逐条回检 |
| 英文对照（核对用） | `books/slp3/zh/md/21-information-extraction.dual.md` | 1,821 行 / 143,812 字节，仅核对术语与原句，不单独引用 |
| 章元数据 | `raw/21/meta.json` | 提供章名与 goal |
| 划线摘录 | 未提供 | `raw/21/` 下无 highlight 文件，不做划线去向表 |
| 课堂笔记 | 未提供 | 不做书 ↔ 课堂交叉对照 |

## 摘录口径

- 全部摘录用 `「…」` 包裹并标注 `（§节号）`；已用脚本逐条比对源文件，**81/81 条为源文连续子串**（零改写、零拼接）。
- 原文定义框里的 `释义：` 前缀在摘录时剥离，只保留释义正文，仍属连续子串。
- 公式（21.10）RlogF 在中文排版中丢失分母与对数项，式（21.11）noisy-or 被拆行；笔记保留原文摘录，并在思考区显式标注 ❓ 与重建方式。

## 本章产物

| 文件 | 内容 | 数量 |
|---|---|---|
| [`book-notes.md`](book-notes.md) | 逐节三区笔记（摘录 / 思考 / 行动） | 12 节块 + 全章 takeaway |
| [`cards.md`](cards.md) | 永久卡片（每张带 §出处 + 链接位） | 14 |
| [`self-test.md`](self-test.md) | 提取自测（遮住作答） | 12 |
| [`actions.md`](actions.md) | 行动清单（每条对应一个 lab） | 5 |
| [`spinoffs.md`](spinoffs.md) | 衍生选题（含发布回流位） | 5 |
| [`glossary.md`](glossary.md) | 术语表（中英对照 + 出处） | 24 |
| [`topics.json`](topics.json) | 选题索引（机器可读） | 5 |
| [`labs/`](labs/index.md) | 5 个可运行实验（脚本 + out/ + README） | 5 |

## 全章结构速查

```
§21    导论：IE 定义 / 关系 / 事件 / 模板（航空票价贯穿例）
§21.1  关系抽取：ACE-17、UMLS-54、WordNet is-a、infobox→RDF、TACRED
§21.2.1 模式法（Hearst 五模式）        §21.2.2 有监督（特征 + 过滤分类器）
§21.2.3 自举（RlogF / 语义漂移）        §21.2.4 远程监督（KB 对齐，精度低）
§21.2.5 无监督 / Open IE（ReVerb）      §21.2.6 评测（元组级 P，召回不可测）
§21.3  事件抽取（事件提及 / 轻动词 / REPORTING / IOB）
§21.4  时间表示（Allen 13 关系、Reichenbach E-R-S）
§21.5  体（Vendler 四类：状态/活动/完结/达成）
§21.6  TimeBank / TimeML（EVENT、TIMEX、TLINK/ALINK/SLINK）
§21.7  自动时间分析（TIMEX3 抽取 → ISO 8601 归一化 → TLINK 排序）
§21.8  模板填充（模板识别 + 角色填充值抽取；FASTUS 级联 FST）
```

## 阅读路线建议

1. **第一遍（2 小时）**：§21 导论 → §21.2.1 → §21.2.2 → §21.9 小结。先建立「模式 vs 有监督」这条主轴。
2. **第二遍（3 小时）**：§21.2.3–21.2.6 四种「缺标注」路线，重点记两句话——自举的病是漂移，远程监督的病是噪声。
3. **第三遍（3 小时）**：§21.3 → §21.7，把事件和时间连起来读；配合 lab-05 跑一遍归一化。
4. **收尾（1 小时）**：§21.8 模板填充 + 历史注记，理解 FASTUS 为什么必须用级联。

## 环境与复现

- Python 3.12，numpy 2.4.6、matplotlib 3.10.9、scikit-learn 1.9.1
- 全部 lab 只依赖标准库 + 上述三个包，无网络调用；`python3 lab.py` 即可复现 `out/` 下产物
- 门禁：`python3 /home/yuanwu/zhihu-wiki/.opencode/skills/write-read-notes/scripts/check_read_notes.py /home/yuanwu/notes/reading/slp3/21-information-extraction --raw /home/yuanwu/notes/reading/slp3/raw/21`
