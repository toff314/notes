# Notes · 听课笔记

一个「多课程笔记架」仓库：每门课一个子目录，统一提供**中文 Markdown 在线阅读**（Caddy 静态托管 + 目录浏览），
保留**主笔记 / 思路大纲 / 自测 / 勘误 / 衍生选题**五类产物。

## 站点

| 入口 | 地址 |
|---|---|
| 笔记首页 | `http://<host>:17001/` |
| 课程页 | `http://<host>:17001/<course-slug>/` |

部署方式：`docker compose up -d`（Caddy 静态托管 + 目录浏览，见 [`docker-compose.yaml`](docker-compose.yaml) 与 [`Caddyfile`](Caddyfile)）。
若需对外域名，在上层反向代理加一条 `notes.<域> → 127.0.0.1:17001` 即可（本仓库只负责站点本身）。

## 已收录

| 课程 | 目录 | 讲次 | 进度 |
|---|---|---|---|
| 计算语言学基础（北京邮电大学） | [`computational-linguistics/`](computational-linguistics/) | 第 1 讲 绪论 | 1 / 3 讲 |

## 目录约定

```
notes/
├── index.html                       # 笔记首页（课程卡片）
├── docker-compose.yaml              # Caddy 部署（宿主机 17001）
├── Caddyfile
└── <course-slug>/                   # 每门课
    ├── README.md                    # 课程说明
    ├── SUMMARY.md                   # 讲次目录与进度（带相对链接）
    ├── index.html                   # 课程页
    └── <NN-lecture-slug>/           # 每一讲
        ├── README.md                # 讲次索引（元信息 + 产物清单 + 自评分）
        ├── notes.md                 # 主笔记
        ├── outline.md               # 思路大纲（含 Mermaid）
        ├── questions.md             # 自测题 + 疑问 + 待查
        ├── corrections.md           # 勘误（转写 ↔ PPT 差异 + 存疑）
        └── spinoffs.md              # 衍生选题（可编辑；含成文链接）
```

## 新增一讲

1. 在 `<course-slug>/` 下建 `<NN-lecture-slug>/`；
2. 把该讲的 5 类产物（`notes.md` / `outline.md` / `questions.md` / `corrections.md` / `spinoffs.md`）+ `README.md` 放进去；
3. 更新本讲 `README.md` 的元信息、本书（课程）`SUMMARY.md` 与 `index.html`。

> 笔记由 **`write-notes` 技能**产出（输入：录音转写文本 + PPT；输出：以上产物）。
> 本仓库是**交付/阅读位置**，工作副本在 zhihu-wiki 仓库的 `output/` 下。

## 关于「衍生选题」

`spinoffs.md` 是**可编辑的 Markdown**：每条候选含「主题串（可直接投喂下游技能）/ 讲座锚点 / 为什么 / 增益 / 素材种子 / 缺口」，
以及一列 **成文链接**。链接写的是线上站点 URL，**可随时手改**——发布后把 URL 填/改到这里即可。

## 版权

课堂内容（讲稿、课件）版权归授课教师与学校所有。本仓库为**个人学习笔记**，供本人复习使用，非公开传播材料。
