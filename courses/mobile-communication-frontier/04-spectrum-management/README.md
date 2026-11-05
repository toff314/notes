# 第 4 讲 频谱管理

| 项 | 值 |
|---|---|
| 课程 | 移动通信技术前沿（2026 秋，北京邮电大学 信息与通信工程学院） |
| 讲次 | 第 4 讲 |
| 讲题 | 频谱管理 |
| 讲师 | 李阳（转写 L12 自我介绍：北邮信通院；连续讲授本周及随后两周） |
| 日期 | 2026 秋（课件 PDF 创建时间 2026-11-03，授课约 11 月上旬） |
| 转写 | 40,299 汉字（4 课时，含 2 处课间） |
| 课件 | 168 页 PDF（`频谱管理20261101.pdf`，封面署名尹良 YinL@bupt.edu.cn） |
| 笔记 | notes.md 3,407 汉字 / 10 节 |
| 生成 | 2026-11-05 |

**一句话**：频谱不是"带宽"，是被国家切好、标好价、写进条约的稀缺土地；会看频谱的人，能从一条曲线上读出对方的设备、参数甚至来意。

## 实际输入

- **转写**：飞书 wiki 文档 `EjQxwEJo2iPV2jkuPZucg7CrnT0`（obj_token `Gpnxd2sRgoVXfkxDzl4cBbN6nLs`，标题「移动通信技术前沿4」）经 OpenAPI `docx/raw_content` 导出 → `raw/transcript.md`，40,299 汉字，含 4 个课时标记（原文行号 L2/L415/L781/L1124，成品文件对应 L9/L424/L792/L1137）。
- **PPT 课件**：`raw/slides.pdf`（168 页），课程 slide 库中为 `slides/04 频谱管理/移动通信技术前沿-频谱管理-2026秋.pdf`；页级骨架见 `raw/slides-outline.md`。
- **个人笔记**：用户未提供，`my-notes.md` 保留空槽位（不代填），并写明三源冲突合并规则。

## 课件目录处理（2026-11-05）

用户把新课件放在 `/home/yuanwu/notes/频谱管理20261101.pdf`（24.8 MB，168 页），整理如下：

- 新建 `slides/04 频谱管理/`，移入并按本课程约定改名为 `移动通信技术前沿-频谱管理-2026秋.pdf`（去掉日期后缀）。
- md5 判重：四份课件 `fce9c3c8…`（04）、`da2b465f…`（01）、`305b26af…`（02）、`b57b2ff1…`（03）互不相同，**无重复**，无需删除。
- 课程页「课件 PPT」现为 4 份，与 01–04 四讲一一对应。
- 课件封面署「尹良 YinL@bupt.edu.cn」，而课堂自我介绍为「李阳」，两者不一致；转写 L12 明确「我叫李阳」，故讲师以转写为准，课件署名差异记录在此不写入正文。

## 文件说明

| 文件 | 内容 |
|---|---|
| `notes.md` | 主笔记，10 节，每节「线索 / 内容 / 一句话总结」，【师】与【PPT】P## 分别标注 |
| `outline.md` | 主线 11 步 + Mermaid 结构图 + 三条线索递进 + 只记三件事 + 记忆钩子 |
| `questions.md` | 23 道自测（看图/架构/反推/识别管理/制度博弈）+ 提取练习协议 + 待查 + PPT 有转写未覆盖清单 |
| `corrections.md` | 14 处术语误识 + 未采用内容（5 类）+ 覆盖对照（4 课时）+ 5 项待核，逐条两侧可追溯 |
| `spinoffs.md` | 6 条衍生选题（含主题串、锚点、为什么、增益、更新建议、素材种子、发布回流位） |
| `topics.json` | 与 spinoffs 对应的机读选题，`version: 1`，id 前缀 `mobile-frontier-04-tN` |
| `my-notes.md` | 课上笔记槽位（空）+ 三源冲突合并规则 |

## 口径与取舍

- **PPT 后半段（P92–P165）为英文课件「Low Earth Orbit Satellite Internet: Frequency Compatibility and Coexistence」**，课堂仅最后约 10 分钟零星提及手机直连与 EPFD，主体未展开。已在 `questions.md` 的「待归类」中说明，正文未纳入，避免把未讲授内容写成课堂结论。
- 转写含大量口语重复与跑题（点名、读博劝勉、大模型工具闲聊），一律压缩为一句或不采用，明细见 `corrections.md`「未采用内容」。
- 三处关键数字（欧洲 3G 拍卖额、美国 5G 拍卖额、中国频率占用费）中，前两者按老师口径写入正文并注明来源，第三者语气不确定，标「待核」不补全。
- 每节课对应 PPT 页码范围见 `corrections.md`「覆盖对照」，四段合计覆盖 P1–P91、P166–P167。

## 校验结果

```
check_notes.py . --raw raw
[PASS] G1 输入齐备（转写 + PPT）
[PASS] G4 差异条目两侧可追溯
[PASS] G5 存疑已标记
[PASS] G6 notes.md 3,407 汉字 ≤ 4,000；10 节（4–10）
[PASS] G7 七份产物齐备；每节均有「一句话总结」；outline 有主线与 Mermaid；questions 有自测与「PPT 有、转写未覆盖」
[PASS] G9 6 条候选，含主题串/锚点/为什么/增益/状态/链接
FAIL=0 WARN=0
```

## 复现命令

```bash
cd /home/yuanwu/notes/courses/mobile-communication-frontier/04-spectrum-management
python3 /home/yuanwu/zhihu-wiki/.opencode/skills/write-lecture-notes/scripts/check_notes.py . --raw raw
cd /home/yuanwu/notes && ./scripts/build-html.sh
```

## 修订记录

- 2026-11-05 首版：从飞书 wiki 导出转写，整理课件到 `slides/04 频谱管理/`，产出 8 件套并过闸门。
