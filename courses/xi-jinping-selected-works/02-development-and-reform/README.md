# 第 2 讲 · 专题三（新发展理念引领高质量发展）+ 专题四（全面深化改革与制度建设）

## 元信息

| 项 | 值 |
|---|---|
| 课程 | 习近平著作选读（北京邮电大学马克思主义学院） |
| 讲次 | 第 2 讲（一次课连讲四节，两个专题） |
| 课型判定 | **专题课 · 4 课时（约 180 分钟）**；转写 43,735 汉字（含旁白与同学发言）→ 按"单份笔记可读性上限 4,000 字 / 10 节"压缩 |
| 命名 | 按讲课文本用词，不按框架外概念命名；两专题并列，标题用「专题三 + 专题四」 |
| 转写来源 | 飞书 wiki 文档《习近平著作选读2》（token `FPPHw7hRhiR3bIkNszTcuH3mnZf`），OpenAPI `docx/v1/documents/{id}/raw_content` 导出 |
| 文档体量 | 纯文本 143,905 字符 / 43,735 汉字 / 1,033 行（含 4 个独立的课时标记：1、2、3、4） |
| 文献与页码 | 基本经济制度 56—59 页；高质量发展 62—63 页；新发展理念（五词）；新发展格局（双循环）；十八届三中全会《决定》说明 75—77 页；十九届四中全会《决定》82—84 页 |
| 产出时间 | 2026-10-24 |
| 技能版本 | `.opencode/skills/write-lecture-notes`（`.opencode` 为唯一权威源） |

## 实际输入（输入契约）

| 输入 | 状态 | 说明 |
|---|---|---|
| 课堂转写 | ✅ 有 | 飞书 docx 全文，1,033 行；已落盘 `raw/transcript.md`（含 4 个课时分隔标记） |
| 课件 PPT | ❌ 无 | **本课与第 1 讲均无课件**，老师全程口述 + 讲义页码提示 → G1 降级（见下） |
| 我的笔记 | ❌ 无 | `my-notes.md` 已留占位与合并规则 |
| 讲义 | ❌ 无电子版 | 页码照转写录入，未能核对纸质讲义 |

> **G1 降级声明**：`check_notes.py` 的 G1（双源）判 FAIL，属**已声明降级**——本课不存在 PPT，任何"与课件页核对"的动作都无法执行。因此：术语只用转写内部可自证者修正（如「控制的福率」→「控制幅度」）；数字全部标"老师口径"或 ❓；不引外部记忆改写任何专名。

## 产物清单

| 文件 | 作用 | 规模 |
|---|---|---|
| `notes.md` | 主笔记：10 节，每节"线索 / 内容（【师】）/ 一句话总结" + 全篇 takeaway | 3,994 汉字 |
| `outline.md` | 思路大纲：10 步主线 + Mermaid 概念关系 + 只记三件事 | 约 780 字 |
| `questions.md` | 18 题自测（含提取练习协议）+ 我没懂的 + 待查 | 18 题 |
| `corrections.md` | 转写勘误：17 条存疑 + 7 类未采用内容 + 覆盖对照 | — |
| `spinoffs.md` | 5 条衍生选题（Mode B「观点：」前缀，送 `write-zhihu-tech`） | 5 条 |
| `topics.json` | 同上，机器可读（`spinoff-topics.schema.json` 结构） | 5 条 |
| `my-notes.md` | 课上笔记占位 + 三源冲突合并规则 | 占位 |
| `raw/transcript.md` | 转写原件（**不入库**，仅本地核对用） | 1,033 行 |
| `raw/meta.json` | 转写元信息（来源 token、汉字数、课时行号） | — |

## 验收

`check_notes.py` 与本讲的实际结果（2026-10-24 复核）：

| 闸门 | 结果 |
|---|---|
| G1 双源 | **FAIL（已声明降级）**：无 PPT |
| G6 篇幅 | OK：3,994 汉字 ≤ 4,000；10 节在 4—10 区间 |
| G7 结构完整 | OK：10/10 节有「一句话总结」；outline 含「主线」与 Mermaid；自测 18 题 |
| G4 勘误可追溯 | OK：17 条差异每条都给了"转写行号 + 课件页（本课无）" |
| G5 存疑标记 | OK：正文 4 处 ❓，corrections 17 处 ❓，均未补全为事实 |
| G9 衍生选题 | OK：5 条（3—8 区间），含 主题串/锚点/为什么/增益 + 状态/链接回流位 |
| G2/G3/G8/六维 | 人工判定（见下） |

## 六维自评（满分 60，下限 42 且单项 ≥7）

| 维度 | 分 | 依据 |
|---|---|---|
| ① 脉络还原 | 8 | 10 节完全沿讲者顺序（制度 → 换挡事实 → 三因 → 五词 → 双循环 → 计划/市场 → 政府失灵 → 治理骨架 → 制度评价）；四节课按主题归并而非按时间切，已在 `outline.md` 说明 |
| ② 概括力 | 8 | 43,735 汉字压到 3,994 字（9.1%），保留全部关键数字与论证链；删去的是点名、重复强调、个案枝节（见 corrections §2） |
| ③ 差异检查 | 7 | 无 PPT，只能做"转写内部一致性"核对（如 12% 与"两位数"的口径冲突已记录）；未做课件页比对，扣分 |
| ④ 覆盖完整 | 8 | 转写 10/10 节都有锚点；未覆盖的仅 940 行语义截断处，已声明 |
| ⑤ 可复习 | 9 | 每节"线索"是可自答的问题、每节有"一句话总结"、`questions.md` 有 18 题 + 提取练习协议、`outline.md` 有 Mermaid 与"只记三件事" |
| ⑥ 忠实 | 9 | 每个数字都回到 raw 行号核过；老师口径与规范表述分开标注；17 条存疑未擅自补全 |
| **合计** | **49** | 达标（≥42，单项均 ≥7） |

## 复现

```bash
cd /home/yuanwu/notes/courses/xi-jinping-selected-works/02-development-and-reform
python3 /home/yuanwu/zhihu-wiki/.opencode/skills/write-lecture-notes/scripts/check_notes.py . --raw raw
cd /home/yuanwu/notes && ./scripts/build-html.sh
```

转写重新导出（飞书 OpenAPI，需要 app 凭据）：

```bash
# 1) 取 tenant_access_token → 2) wiki get_node 拿 obj_token → 3) docx raw_content
curl -s -X POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal \
  -H 'Content-Type: application/json' -d '{"app_id":"$FEISHU_APP_ID","app_secret":"$FEISHU_APP_SECRET"}'
curl -s "https://open.feishu.cn/open-apis/wiki/v2/spaces/get_node?token=FPPHw7hRhiR3bIkNszTcuH3mnZf" \
  -H "Authorization: Bearer $TOKEN"
curl -s "https://open.feishu.cn/open-apis/docx/v1/documents/OaYUdDBQcomBONxMQJKc9T8bnKf/raw_content" \
  -H "Authorization: Bearer $TOKEN"
```

## 修订

- 2026-10-24 初稿：转写 → 10 节笔记（3,994 字）+ 大纲 + 18 题自测 + 勘误 17 条 + 5 条衍生选题；G1 声明降级。
