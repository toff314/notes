# 读书笔记：《Speech and Language Processing》第 3 版 · 第 16 章 自动语音识别

## 书目元信息

- 书名：Speech and Language Processing (3rd ed.)｜作者：Daniel Jurafsky & James H. Martin
- 本章：第 16 章 Automatic Speech Recognition（自动语音识别）｜中文译文
- 来源：`/home/yuanwu/books/slp3/zh/md/16-speech-recognition.md`（英文对照：`16-speech-recognition.dual.md`）
- 页码口径：**中文版无印刷页码，统一用节号 §x.y 定位**（raw/meta.json 明确要求）
- 阅读目标：理解（meta.json `goal=理解`；非应试，但仍按教材型做分拣与例题复算）
- **书型判定：教材型**。依据：章-节-知识点三级编号清晰；§16.2 有可手算的卷积/感受野例子；§16.5 有可枚举的 CTC 折叠过程；§16.6 有可复算的 WER 例题；章末有小结与历史注记。
- 交叉对照：未提供课堂笔记（`raw/` 下无 `lecture-notes/`），故不产出 `cross-check.md`。

## 处理范围与进度

| 章 | 覆盖小节 | 状态 | 说明 |
|---|---|---|---|
| 第 16 章 | §16.1–§16.6（含 16.3.1–16.3.3、16.4.1–16.4.3、16.5.1–16.5.4）、小结、历史注记 | ✅ 本次完成 | book-notes 拆为 12 个知识块；labs 落 2 个（lab-01 WER、lab-02 CTC） |
| 第 17 章 文本转语音 | — | ⬜ 未处理 | 建议下次；与第 16 章共用前端与波形工具 |

## 实际输入（G1 依据）

| 角色 | 实际文件 | 说明 |
|---|---|---|
| 书稿（必选） | `/home/yuanwu/books/slp3/zh/md/16-speech-recognition.md` | 中文译文全文；本次**全文读完** |
| 英文对照（核对用） | `/home/yuanwu/books/slp3/zh/md/16-speech-recognition.dual.md` | 用于核对术语与 CTC/WER 例子 |
| 元信息 | `/home/yuanwu/notes/reading/slp3/raw/16/meta.json` | `goal=理解`，注明「无印刷页码，引用用 §节号」 |
| 划线/摘录（可选） | 未提供 | 无 highlights，故不产出「划线去向表」 |

## 产物清单

| 文件 | 内容 | 规模 |
|---|---|---|
| `book-notes.md` | 逐节三区（摘录/思考/行动），12 个知识块 + 全章 takeaway + 复习优先级依据 | 12 块 |
| `cards.md` | 永久卡片（概念卡/公式卡/例题卡） | 见 cards.md |
| `self-test.md` | 提取自测协议 + 题目 + 答案要点 + 例题重做记录 | 见 self-test.md |
| `actions.md` | 3 条编号行动（含日期与验收）+ 错题归因表 | 3 条 |
| `spinoffs.md` | 衍生选题（送 write-zhihu-tech / write-tech-tutorial） | 5 条 |
| `glossary.md` | 教材术语表 | 见 glossary.md |
| `topics.json` | 结构化衍生选题（5 条，含优先级与命中标准） | 5 条 |
| `labs/index.md` + `labs/lab-01-wer-tools/` + `labs/lab-02-ctc-collapse/` + `labs/lab-03-kmeans-units/` | 行动执行闭环：脚本 + 真实产物 + 结论 + 反思 | 3 个 lab |

## 摘录忠实度说明

- 摘录全部来自章节原文，逐条带 § 节号定位；未做拼接式改写。
- 公式区（式 16.2、16.3、16.12、16.13、16.21）在抽取文本中运算符与上下标错乱，摘录区不引用乱码公式；改在思考区说明「按上下文重建」，并由 `labs/lab-02` 的前向 DP 与暴力枚举对照（最大绝对差 < 1e-12，空串除外）反向验证重建正确。
- §16.3.1「每 .0625 ms 一个表示」与 §16.3.2「90% 标准答案 / 0.1 概率」两处数字可疑，已在 book-notes 中标注并按上下文理解。

## labs 一览（真实运行，非编造）

| lab | 主题 | 关键结果 |
|---|---|---|
| lab-01-wer-tools | 词级最小编辑距离 / WER 复算 | 书中 13 词例子复算 76.92%（书中 76.9%）；5 组句对 raw/norm 双口径 WER；对齐歧义路径数 |
| lab-02-ctc-collapse | CTC 折叠函数与前向 DP | 27 条对齐 → 9 个输出；暴力 vs DP 最大差 5.6e-17；argmax 不一致率 28.03%；dinner/diner 对照 |
| lab-03-kmeans-units | k-means 粒度效应 toy 实验 | k=3 时 purity=0.9967/ARI=0.9956 最高；k>3 后 purity 仍高但 ARI 持续下降 |

## 自评分（六维，门槛 ≥42/60 且单项 ≥7）

| 维度 | 得分 | 理由 |
|---|---|---|
| ① 摘录忠实度 | 9/10 | 全部摘录带 § 节号；公式乱码不引用、改数值校验反向验证；扣 1 分因无印刷页码只能给节号 |
| ② 消化深度 | 8/10 | 每块 3–5 条【我】，含具体经验（WER 当唯一指标的误区、长度失配主线）与真质疑（单位笔误、90%/0.1 不自洽） |
| ③ 行动可执行性 | 9/10 | 3 条均含日期 + 可检验验收，且全部执行完毕、产物落盘；扣 1 分因 lab-03 用了 2 维 toy 数据而非真实 39 维 MFCC |
| ④ 卡片复用性 | 8/10 | 一卡一主张、独立可读、带 § 出处；部分链接指向 labs 真实产物 |
| ⑤ 覆盖完整性 | 9/10 | 12 个知识块覆盖全部小节 + 小结 + 历史注记；例题复算与错题归因齐备 |
| ⑥ 可复习性 | 8/10 | 自测覆盖全部 ⭐ 与 🔴；含遮住作答协议、费曼检验、答案指向；题目仍以解释型为主 |
| **合计** | **51/60** | 过门槛（≥42，单项均 ≥7） |

## 自检

```bash
python3 /home/yuanwu/zhihu-wiki/.opencode/skills/write-read-notes/scripts/check_read_notes.py \
  /home/yuanwu/notes/reading/slp3/16-speech-recognition --raw /home/yuanwu/notes/reading/slp3/raw/16
```

结果：**FAIL=0，WARN=0**（退出码 0）。机器无法判定的项（摘录回溯、同义改写、假行动语义、卡片独立可读、六维评分）已在上文逐项说明。
