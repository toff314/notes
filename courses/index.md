# 课程 · Courses

按课程组织的听课笔记：每门课一个子目录，逐讲保留**主笔记 / 思路大纲 / 自测 / 勘误 / 衍生选题**五类产物。

## 已收录

| 课程 | 目录 | 课次 | 课件 | 进度 |
|---|---|---|---|---|
| 计算语言学基础（北京邮电大学 · 人工智能学院） | [`computational-linguistics/`](computational-linguistics/) | 第 1–3 课（绪论 · 词形态分析 · 汉语切分） | 10 章 / 19 份 PPT | 3 课已完成 |
| 移动通信技术前沿（北京邮电大学 · 信息与通信工程学院） | [`mobile-communication-frontier/`](mobile-communication-frontier/) | 第 1–2 讲（课程介绍 + 智能空口技术 · 电波传播与信道建模） | 见 slides/ | 2 讲已完成 |
| 习近平著作选读（北京邮电大学 · 马克思主义学院） | [`xi-jinping-selected-works/`](xi-jinping-selected-works/) | 第 1 讲 导论（开课第一讲） | 无课件 | 1 讲已完成 |

## 新增一门课

1. 在 `courses/` 下建 `<course-slug>/`；
2. 放入课程 `README.md`、`SUMMARY.md`，每讲建 `<NN-lecture-slug>/` 并放五类产物；
3. 跑 `bash scripts/build-html.sh`（自动扫描，无需登记）；
4. 更新本页、根 `README.md` 与根 `index.html`。
