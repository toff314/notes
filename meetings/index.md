# 会议 · Meetings

按会议组织的纪要包：每场会一个子目录，先判定会议类型，再产出对应台账。

| 类型 | 识别信号 | 产物 |
|---|---|---|
| **决策型** | 有表决、拍板、明确取舍 | 纪要 / 决策 / 行动 / 待定 / 结转 / 勘误 |
| **论坛型** | 多位讲者轮流分享 + 点评，无表决 | 上述六件 + 讲者矩阵 / 横向主题 |
| **宣讲型** | 单向传达政策/方案，Q&A 为主 | 上述六件 + 关键信息 / 问答 |

## 已收录

| 会议 | 日期 | 类型 | 讲者 | 纪要 |
|---|---|---|---|---|
| 高中学校特色发展的路径与策略（分论坛一） | 2026-10-21 | 论坛 | 5 位汇报 + 2 位专家点评 | [README](2026-10-21-high-school-feature-forum/README.html) · [纪要](2026-10-21-high-school-feature-forum/minutes.html) · [讲者矩阵](2026-10-21-high-school-feature-forum/speakers.html) · [横向主题](2026-10-21-high-school-feature-forum/themes.html) |

## 新增一场会

1. 在 `meetings/<YYYY-MM-DD-slug>/` 下放本地产物，`raw/` 放转写、议程、名单（不入库）；
2. 用 `write-meeting-notes` 生成纪要包；
3. 跑 `bash scripts/build-html.sh`（自动扫描，无需登记）；
4. 更新本页与根 `README.md` / 根 `index.html`。
