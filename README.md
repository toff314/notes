# Notes · 听课笔记

一个「多课程笔记架」仓库：每门课一个子目录，统一提供**中文笔记在线阅读（HTML）**与源 Markdown，
并保留**主笔记 / 思路大纲 / 自测 / 勘误 / 衍生选题**五类产物；课程课件（PPT）走 **Git LFS** 一并托管。

## 站点

| 入口 | 地址 |
|---|---|
| 笔记首页 | `http://<host>:17001/` |
| 课程页 | `http://<host>:17001/<course-slug>/` |
| 读书架（姊妹仓，读书笔记） | `http://<host>:17002/`（仓库 `~/readings/`） |

部署方式：`docker compose up -d`（Caddy 静态托管 + 目录浏览，见 [`docker-compose.yaml`](docker-compose.yaml) 与 [`Caddyfile`](Caddyfile)）。
若需对外域名，在上层反向代理加一条 `notes.<域> → 127.0.0.1:17001` 即可（本仓库只负责站点本身）。

## 已收录

| 课程 | 目录 | 课次 | 课件 | 进度 |
|---|---|---|---|---|
| 移动通信技术前沿（北京邮电大学 · 信息与通信工程学院） | [`mobile-communication-frontier/`](mobile-communication-frontier/) | 第 1 讲 课程介绍 + 智能空口技术 | 见 slides/ | 1 讲已完成 |
| 计算语言学基础（北京邮电大学） | [`computational-linguistics/`](computational-linguistics/) | 第 1 课 绪论 | 10 章 / 19 份 PPT | 1 课已完成 |

## 目录约定

```
notes/
├── index.html                       # 笔记首页（课程卡片）
├── docker-compose.yaml              # Caddy 部署（宿主机 17001）
├── Caddyfile
├── .gitattributes                   # 大二进制走 Git LFS（pptx / pdf / 图片）
├── scripts/
│   ├── md2html.py                   # Markdown → 在线阅读 HTML（零依赖）
│   └── build-html.sh                # 批量渲染：全部 .md → 同名 .html
└── <course-slug>/                   # 每门课
    ├── README.md                    # 课程说明
    ├── SUMMARY.md / SUMMARY.html    # 课次目录与进度
    ├── index.html                   # 课程页
    ├── slides/                      # 课件 PPT（Git LFS）
    └── <NN-lecture-slug>/           # 每一课（产物平铺；本地素材放 raw/，不入库）
        ├── README.md                # 本课索引（元信息 + 产物清单 + 自评分）
        ├── notes.md                 # 主笔记
        ├── outline.md               # 思路大纲（含 Mermaid，HTML 已接 CDN 渲染成图）
        ├── questions.md             # 自测题 + 疑问 + 待查（含提取自测协议）
        ├── corrections.md           # 勘误（转写 ↔ PPT 差异 + 存疑）
        ├── spinoffs.md              # 衍生选题（可编辑；含成文链接）
        ├── my-notes.md              # 可选：课上笔记存档
        ├── flashcards.md            # 可选：背诵卡（Anki）
        └── raw/                     # 转写 / 课件源 / 课上笔记照片（.gitignore 忽略）
```

> **`.md` 与 `.html` 并存**：阅读用 `.html`，编辑改 `.md`；改完执行 `bash scripts/build-html.sh` 重渲染。
> **渲染脚本自动扫描**全部 `.md`（排除 `scripts/`、各级 `raw/`），按目录层级自动生成面包屑导航、
> 取文件首个 `# ` 标题作页题——**新增课次或产物无需登记**，直接重跑即可。

## 新增一课

1. 在 `<course-slug>/` 下建 `<NN-lecture-slug>/`（产物平铺，本地素材放 `raw/`）；
2. 放入本课 5 类产物（`notes.md` / `outline.md` / `questions.md` / `corrections.md` / `spinoffs.md`）+ `README.md`（可选产物 `my-notes.md` / `flashcards.md` 同样平铺）；
3. `bash scripts/build-html.sh` 渲染 HTML（自动扫描，无需登记）；
4. 更新本课 `README.md`、课程 `SUMMARY.md` 与 `index.html`。

## 课件与 Git LFS

课件（PPT/PDF）与图片由 `.gitattributes` 交给 **Git LFS** 管理：

```bash
git lfs install            # 首次
git lfs ls-files           # 查看被 LFS 跟踪的文件
git lfs pull               # 克隆后拉取大文件
```

## 关于「衍生选题」

`spinoffs.md` 是**可编辑的 Markdown**：每条候选含「主题串（可直接投喂下游写作技能）/ 讲座锚点 / 为什么 / 增益 / 素材种子 / 缺口」，
以及一列 **成文链接**。链接写的是线上站点 URL，**可随时手改**。

## 版权

课堂内容（讲稿、课件）版权归授课教师与学校所有。本仓库为**个人学习笔记与资料存档**，供本人复习使用。
