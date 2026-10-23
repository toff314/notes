# 笔记架 Notes · 统一设计规范（DESIGN.md）

> 本规范约束全站所有页面的视觉与信息架构。改样式先改这里，再改 `scripts/build.py` 中的 `STYLE`。

## 一、设计定位

- **气质**：青墨极简——纸感留白 + 单一青墨 accent，拒绝花哨；内容（笔记文字）是唯一主角。
- **一致性**：所有页面共用同一套导航、卡片、正文排版、配色；禁止页面自造样式。

## 二、设计令牌

| 令牌 | 值 | 用途 |
|---|---|---|
| `--ink` | `#1f2328` | 标题、正文主色 |
| `--muted` | `#6b7280` | 次级文字、meta |
| `--line` | `#e5e7eb` | 边框、分割线 |
| `--accent` | `#1a6b5a`（青墨） | 链接、hover 边、当前层级 |
| `--accent-soft` | `#e6f5f0` | 链接 hover 底色、tag |
| `--canvas` | `#f6f7f9` | 页面背景 |
| `--card` | `#ffffff` | 卡片表面 |

- 字体：系统栈（PingFang SC / Microsoft YaHei / sans-serif）；正文 `16px/1.8`；h1 `30px/700`，h2 `20px`，正文页 h1 `28px`。
- 圆角：卡片 `12px`，小元素 `8px`；卡片阴影仅 hover 时出现（`0 8px 24px rgba(26,107,90,.10)`）。
- 内容宽度：`max-width 1020px` 居中，页边距 `≥20px`。

## 三、信息架构（2–3 级，全站统一）

```
L0  index.html            四分区卡片（读书 / 课堂 / 会议 / 极客时间）
L1  <分区>/index.html     记录卡：一门课一条、一本书一条、一场会议一条
L2  <分区>/<记录>/index.html  记录页：README 摘要 + 条目卡（章/讲/议题/digest 产物目录）+ 文档链接
L3  <分区>/<记录>/<条目>/index.html（按需）+ 所有 .md 的内容页（统一 .prose 排版）
```

- **一条记录一张卡**：L1 卡片 = 标题 + 一行 meta（章节数/讲数/产物数），点击进入 L2。
- 每个含 md 或子目录的目录都必须有 `index.html`（构建脚本保证）。
- 面包屑（`.crumb`）全站常驻：笔记架首页 / 分区 / 记录 / [条目]；当前层级青墨高亮、不可点。

## 四、组件

1. **面包屑**：14px，accent 链接 + ` / ` 分隔 + 当前级 plain。
2. **卡片 `.card`**：白底、1px `--line`、圆角 12、无下划线继承文字色；hover：边框变 accent、上浮 2px、出现阴影。
3. **卡片网格 `.grid`**：`repeat(auto-fill, minmax(280px, 1fr))`，gap `16px`——天然响应式。
4. **正文 `.prose`**：h1–h4 分级缩进；`table` 全宽、表头 `--accent-soft` 底色、横向滚动；`pre` 深色底（`#0e0f11` / `#d4d4d4` 文字）横向滚动；`img` 最大 100% 圆角 8；`blockquote` 左侧 3px accent 边 + 灰底。
5. **文档链接 `.doc-link`**：L2/L3 列表里的 md 条目，行高 44px 可点区。

## 五、响应式

- 移动优先（< 640px）：单列卡片、`body` padding `20px 16px`、h1 26px、表格/代码横向滚动。
- 平板（≥ 640px）：双列卡片。
- 桌面（≥ 1024px）：内容宽 1020px，卡片最多 3–4 列（auto-fill 自适应）。
- 面包屑不换行截断，超出省略。

## 六、构建约定

- 唯一构建入口：`bash scripts/build-html.sh`（内部调用 `scripts/build.py`）。
- md → html 复用 `scripts/md2html.py` 的 `convert()`；样式与壳由 `build.py` 统一注入（STYLE 内联，避免相对路径问题）。
- 排除：`.git/`、`.cache/`、`scripts/`、各级 `raw/`、隐藏文件。
- 新增分区：在 `build.py` 的 `SECTIONS` 注册（key=目录名，label=显示名，root=记录根目录解析）。
