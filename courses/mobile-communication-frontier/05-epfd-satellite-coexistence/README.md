# 第 5 讲 · EPFD 与低轨卫星频率共存

## 元信息

| 项 | 值 |
|---|---|
| 课程 | 移动通信技术前沿（2026 秋，北京邮电大学 信息与通信工程学院） |
| 讲次 | 第 5 讲（4 节课连排） |
| 讲题 | EPFD 与低轨卫星频率共存（老师开场："今天主要讲 EPFD"） |
| 讲师 | 尹良（与第 4 讲同一老师；本讲转写未出现姓名，按课程一贯署名，见 corrections 待核） |
| 日期 | 2026-11 上旬（第 4 讲 11-03 之后） |
| 转写 | 23,686 汉字 / 999 行，4 个课时标记（原文 L2/L408/L675/L995） |
| 课件 | 用户消息标注"ppt 是附件"但**附件未到达**（网关 media=0）；暂以第 4 讲课件后半段 **P92–P169**（英文专题 LEO Satellite Internet: Frequency Compatibility and Coexistence）作锚点——本讲内容与之逐节对应。若老师有独立第 5 讲课件，后续补挂重核 |
| 笔记 | notes.md 10 节 |
| 生成 | 2026-11-11 |

## 实际输入

- **转写**：飞书 wiki `CWZDwTL5diNS96kz69CcvZJXn6b`（docx `Nln6dqe8ioUBzZx1zwPcv6twn5c`，标题「移动通信前沿技术5」）经 OpenAPI 导出 → `raw/transcript.md`（成品 1013 行，含 4 个课时标题）。
- **PPT 课件**：`raw/slides-outline.md` = `slides/04 频谱管理/移动通信技术前沿-频谱管理-2026秋.pdf` P92–P169 页级骨架（`raw/meta.json` 已声明 used/not_used 与对应关系）。本讲核心概念（EPFD 公式 P128、限值表 P137–P140、I/N 案例 P141–P142、BT/Ofcom P151–P156、渐进倾斜 P130–P131）全部在该范围内有锚点。
- **个人笔记**：用户未提供，`my-notes.md` 保留空槽位（不代填），并写明三源冲突合并规则。

## 口径与取舍

- 转写听写噪声极多（"IPU/IPU/IPO"→ITU、"电路预算"→链路预算、"皮夫/epsd/EPMD"→EPFD、"西格玛尔"→σ₂ 等），corrections 统一勘误；无法唯一确定原文的（如"科一阶段""1527/22157 建议书编号"）标待核。
- 数字口径：EPFD 分档限值（−174/−167.8/−166）、里程碑计划（7 年 50%/10 年 90%）、Lynk 报告时间百分比（73.9%/77.5%）均按老师课堂口径记录并标注待核——限值表在 PPT 里是图片，pdftotext 抽不到，未按记忆补数。
- "WRC-27 明年在上海开"按转写记录；老师原话，未另行核实。
- 第 4 讲课件 P1–P91 的频谱仪/频谱管理内容本讲未重讲，不纳入正文。

## 产物清单

notes.md / outline.md / questions.md / corrections.md / spinoffs.md / topics.json / my-notes.md / README.md / raw/{transcript.md, slides-outline.md, meta.json}

## 闸门结果

check_notes.py：FAIL=0 WARN=0（G1 PPT 锚点为 04 课件后半段，已在上方声明）

## 六维自评

| 维度 | 分 | 说明 |
|---|---|---|
| 完整 | 8 | 四节课全部覆盖；限值表具体分档为图片未抄数 |
| 准确 | 8 | 公式与条款双侧可追溯；含混数字一律待核 |
| 结构 | 9 | 指标链（雷达方程→EIRP/G/T→PFD/EPFD/I/N）为主线 |
| 洞见 | 9 | "EPFD 拦的不是信号是星座开机权""规则=技术能力写进条款" |
| 可用 | 9 | 五条 takeaway + Excel 链路预算练习可直接复做 |
| 诚实 | 9 | PPT 附件缺失的处置、所有待核处均已声明 |
| **合计** | **52/60** | 过线（下限 42，单项 ≥7） |

## 复现命令

```bash
cd /home/yuanwu/notes/courses/mobile-communication-frontier/05-epfd-satellite-coexistence
python3 /home/yuanwu/zhihu-wiki/.opencode/skills/write-lecture-notes/scripts/check_notes.py . --raw raw
```

## 修订记录

- 2026-11-11 初版。
