# 读书笔记：《Speech and Language Processing》第 3 版 · 第 22 章 语义角色标注

## 书目元信息

- 书名：Speech and Language Processing (3rd ed.)｜作者：Daniel Jurafsky & James H. Martin
- 本章：第 22 章 Semantic Role Labeling（语义角色标注）｜中文译文
- 来源：`/home/yuanwu/books/slp3/zh/md/22-semantic-role-labeling.md`（英文对照：`22-semantic-role-labeling.dual.md`）
- 页码口径：**中文版无印刷页码，统一用节号 §x.y 定位**（raw/meta.json 明确要求）
- 阅读目标：理解（meta.json `goal=理解`；非应试，但仍按教材型做分拣与例题复算）
- **书型判定：教材型**。依据：章-节-知识点三级编号清晰；密集给出定义框（`> 释义`）；§22.2 有可手算例题（break/give 的语态交替）；§22.7.2 有完整 KL 散度与选择关联公式；章末有小结、历史注记与练习。
- 交叉对照：未提供课堂笔记（`raw/` 下无 `lecture-notes/`），故不产出 `cross-check.md`。

## 处理范围与进度

| 章 | 覆盖小节 | 状态 | 说明 |
|---|---|---|---|
| 第 22 章 | §22.1–§22.9、历史注记、练习 | ✅ 本次完成 | book-notes 拆为 10 个知识块（22.6 拆为「基于特征」与「神经算法+评估」） |

## 实际输入（G1 依据）

| 角色 | 实际文件 | 说明 |
|---|---|---|
| 书稿（必选） | `/home/yuanwu/books/slp3/zh/md/22-semantic-role-labeling.md` | 816 行 / 53,356 字节，中文译文全文；本次**全文读完** |
| 英文对照（核对用） | `/home/yuanwu/books/slp3/zh/md/22-semantic-role-labeling.dual.md` | 用于核对术语与例句 |
| 元信息 | `/home/yuanwu/notes/reading/slp3/raw/22/meta.json` | `goal=理解`，注明「无印刷页码，引用用 §节号」 |
| 划线/摘录（可选） | 未提供 | 无 highlights，故不产出「划线去向表」 |

## 产物清单

| 文件 | 内容 | 规模 |
|---|---|---|
| `book-notes.md` | 逐节三区（摘录/思考/行动），10 个知识块 + 全章 takeaway + 分拣依据 | 10 块 |
| `cards.md` | 永久卡片（概念卡/公式卡/例题卡） | 14 张 |
| `self-test.md` | 提取自测协议 + 10 题 + 答案要点 + 例题重做记录 | 10 题 |
| `actions.md` | 5 条行动（含日期与验收）+ 错题归因表 | 5 条 |
| `spinoffs.md` | 衍生选题（3 送 write-zhihu-tech + 1 送 write-tech-tutorial 等） | 5 条 |
| `labs/index.md` + `labs/lab-01…05/` | 行动执行闭环：脚本 + 真实产物 + 结论 + 反思 | 5 个 lab |

## 摘录忠实度说明

- 55 条摘录全部逐条回溯校验：每条均能在 `raw/22/22-semantic-role-labeling.md` 中定位到唯一来源行，**0 处改写、0 处拼接**。
- 抽取文本存在断行（如公式区 §22.7.2 的 KL 散度与选择关联公式在抽取文本中分式与上下标错乱），凡跨行公式一律改选单行内可完整引用的文字片段，**未做任何拼接式改写**。
- 公式区（式 22.38–22.40）在抽取文本中运算符与上下标错乱，摘录区不引用乱码公式；改在思考区说明「按上下文重建」，并由 `labs/lab-03` 的数值复算反向验证重建正确。

## labs 一览（真实运行，非编造）

| lab | 主题 | 关键结果 |
|---|---|---|
| lab-01 | 语态交替与题元网格归纳 | 对 break/give/open 等动词归纳题元网格，复算书中 (22.3)–(22.8) 全部 8 个例句 |
| lab-02 | PropBank 框架文件解析与角色标注 | 解析 agree.01 / fall.01 / increase.01 框架文件，自动标注 6 个测试句 |
| lab-03 | 选择偏好强度与选择关联复算 | 复算 Resnik SR(v) 与 A_R(v,c)，与书中表 22.1 对照（read/WRITE 等） |
| lab-04 | 基于特征的 SRL 特征抽取器 | 实现 Gildea & Jurafsky 2000 特征模板，对 PropBank 例句抽取特征向量 |
| lab-05 | BIO 序列标注与 Viterbi 解码 | 实现 BIO 标注 + 简单 Viterbi，对测试句输出标签序列并计算 F1 |

## 自评分（六维，门槛 ≥42/60 且单项 ≥7）

| 维度 | 得分 | 理由 |
|---|---|---|
| ① 摘录忠实度 | 9/10 | 55/55 条脚本回溯命中，全部带 §；扣 1 分因中文版无印刷页码，只能给节号，定位精度低于页码 |
| ② 消化深度 | 8/10 | 每块 3–5 条【我】，含具体经验（检索系统中的浅层语义、事件抽取的槽位填充）与真质疑（原型角色 vs 题元角色的取舍、FrameNet 框架的粒度）；部分 A1 仍偏概括 |
| ③ 行动可执行性 | 9/10 | 5 条均含日期 + 可检验验收，且全部执行完毕、产物落盘；扣 1 分因第 4 条范围略大 |
| ④ 卡片复用性 | 8/10 | 14 张一卡一主张、独立可读、带 § 出处、链接多指向真实卡片/lab；2 张链接仍为「待补」 |
| ⑤ 覆盖完整性 | 9/10 | 10 个知识块覆盖全部小节 + 小结 + 历史注记；无划线可丢；分拣依据写明；例题复算与错题归因齐备 |
| ⑥ 可复习性 | 8/10 | 10 题覆盖全部 ⭐ 与 🔴；含遮住作答协议、费曼检验、答案指向、例题重做表；题目仍以解释型为主，缺计算型限时题 |
| **合计** | **51/60** | 过门槛（≥42，单项均 ≥7） |

## 自检

```bash
python3 /home/yuanwu/zhihu-wiki/.opencode/skills/write-read-notes/scripts/check_read_notes.py \
  /home/yuanwu/notes/reading/slp3/22-semantic-role-labeling --raw /home/yuanwu/notes/reading/slp3/raw/22
```

结果：**FAIL=0，WARN=0**（退出码 0）。机器无法判定的项（摘录回溯、同义改写、假行动语义、卡片独立可读、六维评分）已在上文逐项说明。
