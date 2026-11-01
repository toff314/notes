# SLP3 第 13 章　机器翻译（Machine Translation）

- **书目**：《Speech and Language Processing》（第 3 版，Daniel Jurafsky & James H. Martin），第 13 章。
- **实际输入**：`raw/13/13-machine-translation.md`（中译正文，约 1.1k 行）+ `raw/13/meta.json`（`chapter_source=13`，`goal=理解`）。
- **书型判定**：**教材型**。因此采用「章 — 节 — 知识点」三级分块，每块给定义框摘录、例题复算、章末小结与练习覆盖，而不是按论点自由组织结构。
- **定位口径**：中文译文无印刷页码，全包引用一律用节号 `§x.y`（含 `§历史注记`），不写 `P.123`。
- **处理范围**：正文全文（§13.1–§13.8 及历史注记），不外扩到第 14 章或评估章。

## 产物清单

| 文件 | 内容 | 规模 |
|---|---|---|
| `book-notes.md` | 12 个知识块，每块「摘录 / 思考 / 行动」三区，末尾全章 takeaway 与复习优先级 | 31 KB |
| `cards.md` | 21 张原子卡，一卡一主张，均带 § 出处 | 10.7 KB |
| `self-test.md` | 遮住作答协议 + 10 题（4 概念、3 计算、3 辨析）+ 费曼检验 + 例题重做表 | 6.3 KB |
| `actions.md` | 3 条行动，一条对一个 lab，含验收标准与真实结果 | 5.1 KB |
| `spinoffs.md` | 5 个衍生选题（4 送 write-zhihu-tech，1 送 write-tech-tutorial），含主题串/锚点/为什么/增益/发布 | 5.7 KB |
| `glossary.md` | 43 条术语 + 6 组易混对照 | 7.0 KB |
| `labs/` | lab-01/02/03 脚本 + `out/` 真实产物 + 各自 README | 见下 |
| `topics.json` | 5 个衍生选题的结构化登记（与 `spinoffs.md` 同源） | 5 条 |

## 摘录忠实度

- `book-notes.md` 摘录区共 **63 条**原文照抄，逐条用脚本回溯 `raw/13/13-machine-translation.md`：**63/63 命中，0 条改写**（去空白后做子串匹配）。
- 跨行断句的片段一律不拼接，只保留单行内完整句；公式如长度归一化 `(5+|y|)^α/6^α` 在抽取文本里上下标丢失，故**不进摘录区**，改由 lab-03 数值复算反证（k=2 找回 `ok ok EOS`，翻转率 .1135 vs .2280）。
- 思考区与摘录区无连续 12 汉字重合（门禁 G4 自动校验）。

## labs 一览（全部真实运行，未重跑改写）

| lab | 主题 | 对应行动 | 关键输出 |
|---|---|---|---|
| lab-01 | IBM Model 1 的 EM 词对齐 | 行动 1 | 对数似然 −33.183845 → −1.710718（15 轮单调）；`t(is→ist)=.9752`、`t(a→ein)=.9573`；对齐 `P=.7917 / R=.5375 / F1=.631`；反例 `t(the→hund)=.1040` |
| lab-02 | chrF 与 BLEU 手算复现 | 行动 2 | n≤6：`chrF2` HYP1 `.6552` / HYP2 `.4162`；书中手算口径（只 1–2 元）：`.8644 / .6198` ≈ 书中 §13.6.2 的 .86/.62；BLEU-4 HYP1 `.8091`（平滑）`.7598`（不平滑）、HYP2 `0.0000`；语料级 BLEU-4 `.5528`、平均 chrF2 `.7254` |
| lab-03 | 贪心 vs 束搜索 vs 长度归一化 | 行动 3 | 贪心 `yes yes EOS`（0.2）；束搜索 k=2 选 `ok ok EOS`（logP −1.2730，优于贪心 −1.6094）；2000 次试验 × 6 候选，翻转率 GNMT `.1135` vs 平均归一化 `.2280` |

复现命令：

```bash
cd labs
python3 lab-01/ibm1_em.py
python3 lab-02/chrf_bleu.py
python3 lab-03/beam_search.py
```

依赖：Python 3 标准库；lab-02 额外需要 numpy 与 matplotlib。lab-03 使用 `default_rng(0)`，结果确定。

## 未产出说明

- `cross-check.md`：**未产出**。`raw/13/` 下无 `lecture-notes/`，没有第二来源可做交叉核对。
- 划线去向表：**未产出**。`raw/13/` 下无 highlights 文件，无划线可映射。

## 六维自评

| 维度 | 分 | 理由 |
|---|---|---|
| 理解深度 | 9 | 每块都写到机制层（为何必然如此）而非结论层；用 lab 数据反证了三处原文未讲透的地方（chrF 双口径、长度归一化翻转率、IBM-1 错配泄漏）。扣 1 分：§13.5.3 的数据审计部分只做了定性归纳，没做定量复算。 |
| 结构完整 | 10 | 教材型三级分块全覆盖 §13.1–§13.8 + 历史注记，12 块与节次一一对应，无遗漏小节。 |
| 摘录忠实 | 10 | 63 条摘录 100% 回溯命中；跨行片段不拼接；乱码公式不进摘录区。 |
| 行动闭环 | 8 | 3 条行动全部有真实产物与验收数字，且与三个 lab 一一对应。扣 2 分：行动只覆盖了对齐、指标、解码三块，§13.5 低资源与 §13.7 偏见只到「读」的层面，没落成 lab。 |
| 迁移衍生 | 8 | 5 个选题都有明确锚点与可复用增益，其中 2 个直接用 lab 数字当论据。扣 2 分：尚未追踪外部文献，锚点全部来自本章。 |
| 可复习性 | 8 | 21 张卡 + 10 题 + 费曼检验 + 例题重做表 + 术语易混对照，形成「读—测—补」闭环。扣 2 分：计算题只有 3 道，偏少。 |
| **合计** | **53/60** | 单项均 ≥8，达到 ≥42 且单项 ≥7 的门槛。 |

## 自检

```bash
cd /home/yuanwu/notes/reading/slp3
python3 /home/yuanwu/zhihu-wiki/.opencode/skills/write-read-notes/scripts/check_read_notes.py \
  13-machine-translation --raw raw/13
```

摘录回溯（自建）：

```bash
python3 - <<'EOF'
import re
n=re.sub(r'\s+','',open('raw/13/13-machine-translation.md',encoding='utf-8').read())
notes=open('13-machine-translation/book-notes.md',encoding='utf-8').read()
qs=re.findall(r'「([^」]+)」',notes.split('### 摘录区')[1])  # 逐块跑时替换索引
print(sum(re.sub(r'\s+','',q) in n for q in qs),'/',len(qs))
EOF
```
