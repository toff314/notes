# Notes · 课程 / 读书 / 会议笔记

一个「课程 + 读书 + 会议」三分区的笔记仓库，统一提供**中文笔记在线阅读（HTML）**与源 Markdown。

| 分区 | 目录 | 内容 |
|---|---|---|
| **课程** | [`courses/`](courses/) | 听课笔记：主笔记 / 思路大纲 / 自测 / 勘误 / 衍生选题（五类产物） |
| **读书** | [`reading/`](reading/) | 读书笔记：三区笔记 / 永久卡片 / 自测 / 行动清单 / 可执行验证（七类产物） |
| **会议** | [`meetings/`](meetings/) | 会议纪要：决策 / 行动 / 待定 / 结转 / 勘误；论坛型另加讲者矩阵与横向主题 |

## 站点

| 入口 | 地址 |
|---|---|
| 笔记首页 | `http://<host>:17001/`（课程 / 读书 / 会议三个入口） |
| 课程分区 | `http://<host>:17001/courses/` |
| 读书分区 | `http://<host>:17001/reading/` |
| 会议分区 | `http://<host>:17001/meetings/` |

部署方式：`docker compose up -d`（Caddy 静态托管，见 [`docker-compose.yaml`](docker-compose.yaml) 与 [`Caddyfile`](Caddyfile)）。

## 已收录

### 课程

| 课程 | 目录 | 课次 | 课件 | 进度 |
|---|---|---|---|---|
| 习近平著作选读（北京邮电大学 · 马克思主义学院） | [`xi-jinping-selected-works/`](courses/xi-jinping-selected-works/) | 第 1 讲 导论（开课第一讲） | 无课件 | 1 讲已完成 |
| 移动通信技术前沿（北京邮电大学 · 信息与通信工程学院） | [`mobile-communication-frontier/`](courses/mobile-communication-frontier/) | 第 1–2 讲（课程介绍 + 智能空口技术 · 电波传播与信道建模） | 见 slides/ | 2 讲已完成 |
| 计算语言学基础（北京邮电大学） | [`computational-linguistics/`](courses/computational-linguistics/) | 第 1–3 课（绪论 · 词形态分析 · 汉语切分） | 10 章 / 19 份 PPT | 3 课已完成 |

### 读书

| 书 | 目录 | 范围 | 进度 |
|---|---|---|---|
| Speech and Language Processing（第三版） | [`slp3/`](reading/slp3/README.html) | 第 1–11 章 | 11 章完成 / 26 章 |

指定一本书的书稿路径后，用 `write-read-notes` 技能产出笔记并放入 `reading/`。

### 会议

| 会议 | 日期 | 类型 | 纪要 |
|---|---|---|---|
| 高中学校特色发展的路径与策略（分论坛一） | 2026-10-21 | 论坛型 | [`meetings/2026-10-21-high-school-feature-forum/`](meetings/2026-10-21-high-school-feature-forum/README.html) |

会议转写用 `write-meeting-notes` 生成纪要包；论坛型不要求 PPT，也不会硬造决策与行动项。

## 目录约定

```
notes/
├── index.html                       # 笔记首页（课程 / 读书 / 会议 三个入口）
├── courses/                         # 课程分区
│   ├── index.md / index.html        # 课程分区页
│   └── <course-slug>/               # 每门课
│       ├── README.md                # 课程说明
│       ├── SUMMARY.md / SUMMARY.html# 课次目录与进度
│       ├── index.html               # 课程页
│       ├── slides/                  # 课件 PPT（Git LFS）
│       └── <NN-lecture-slug>/       # 每一课（产物平铺；本地素材放 raw/，不入库）
├── reading/                         # 读书分区
│   ├── index.md / index.html        # 读书分区页
│   └── <book-slug>/                 # 每本书
│       ├── README.md                # 书目索引（进度 + 各章链接）
│       └── <NN-chapter>/            # 每章一套笔记（三区/卡片/自测/行动/选题/labs）
├── meetings/                        # 会议分区
│   ├── index.md / index.html        # 会议分区页
│   └── <YYYY-MM-DD-slug>/           # 每场会（纪要/决策/行动/待定/结转/勘误）
├── docker-compose.yaml              # Caddy 部署（宿主机 17001）
├── Caddyfile
├── .gitattributes                   # 大二进制走 Git LFS（pptx / pdf / 图片）
└── scripts/
    ├── md2html.py                   # Markdown → 在线阅读 HTML（零依赖）
    └── build-html.sh                # 批量渲染：全部 .md → 同名 .html
```

> **`.md` 与 `.html` 并存**：阅读用 `.html`，编辑改 `.md`；改完执行 `bash scripts/build-html.sh` 重渲染。
> **渲染脚本自动扫描**全部 `.md`（排除 `scripts/`、各级 `raw/`），按目录层级自动生成面包屑导航、
> 取文件首个 `# ` 标题作页题——**新增课程 / 书目无需登记**，直接重跑即可。

## 新增内容

### 新增一门课

1. 在 `courses/<course-slug>/` 下建 `<NN-lecture-slug>/`（产物平铺，本地素材放 `raw/`）；
2. 放入本课 5 类产物（`notes.md` / `outline.md` / `questions.md` / `corrections.md` / `spinoffs.md`）+ `README.md`；
3. `bash scripts/build-html.sh` 渲染 HTML；
4. 更新本课 `README.md`、课程 `SUMMARY.md`、`courses/index.md` 与根索引。

### 新增一本书

1. 指定书稿路径（`.pdf` / `.epub` / `.md` / `.txt`），用 `write-read-notes` 按章产出；
2. 在 `reading/<book-slug>/` 下为每章建 `<NN-chapter>/`，放入六件套 + `labs/`；书目级 `README.md` 做索引；
3. `raw/` 书稿与划线留在本地，不入库；
4. `bash scripts/build-html.sh` 渲染 HTML；
5. 更新 `reading/index.md` 与根索引。

### 新增一场会

1. 把转写（`.docx/.srt/.vtt/.txt/.md`）与可选的议程、名单、上次行动项放进 `meetings/<YYYY-MM-DD-slug>/raw/`；
2. 用 `write-meeting-notes` 判定会议类型（决策 / 论坛 / 宣讲）并产出纪要包；
3. `raw/` 原素材留在本地，不入库；
4. `bash scripts/build-html.sh` 渲染 HTML；
5. 更新 `meetings/index.md` 与根索引。

## 课件与 Git LFS

课件（PPT/PDF）与图片由 `.gitattributes` 交给 **Git LFS** 管理：

```bash
git lfs install            # 首次
git lfs ls-files           # 查看被 LFS 跟踪的文件
git lfs pull               # 克隆后拉取大文件
```

## 关于「衍生选题」

`spinoffs.md` 是**可编辑的 Markdown**：每条候选含「主题串（可直接投喂下游写作技能）/ 锚点 / 为什么 / 增益 / 素材种子 / 缺口」，
以及一列 **成文链接**。链接写的是线上站点 URL，**可随时手改**。

## 版权

课堂内容（讲稿、课件）版权归授课教师与学校所有；书籍原文版权归原作者与出版社所有。
本仓库为**个人学习笔记与资料存档**，供本人复习使用。
