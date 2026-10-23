#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""笔记架统一构建器：按 DESIGN.md 的 2-3 级信息架构生成全站 HTML。

层级：L0 首页（分区卡）→ L1 分区记录卡 → L2 记录页 → L3 条目索引 + md 内容页。
复用 md2html.convert() 渲染正文；样式内联（STYLE），排除 raw/.git/scripts/.cache。
"""
import os
import re
import sys
import html

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from md2html import convert  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".git", ".cache", "scripts", "raw", "node_modules"}

# (目录名, 显示名)；geektime 记录根为 <课程>/digest（课程原文不出站，见 DESIGN.md）
SECTIONS = [
    ("reading", "读书", None),
    ("courses", "课堂", None),
    ("meetings", "会议", None),
    ("geektime", "极客时间", "digest"),
]

STYLE = """
:root{--ink:#1f2328;--muted:#6b7280;--line:#e5e7eb;--accent:#1a6b5a;--accent-soft:#e6f5f0;--canvas:#f6f7f9;--card:#ffffff;--code-bg:#0e0f11;--code-fg:#d4d4d4}
*{box-sizing:border-box}
body{margin:0;background:var(--canvas);color:var(--ink);line-height:1.8;font-size:16px;font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei","WenQuanYi Micro Hei",sans-serif}
.wrap{max-width:1020px;margin:0 auto;padding:48px 20px 80px}
.crumb{font-size:14px;margin:0 0 28px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.crumb a{color:var(--accent);text-decoration:none}
.crumb a:hover{background:var(--accent-soft);border-radius:4px}
.crumb .cur{color:var(--ink);font-weight:600}
h1.title{font-size:30px;line-height:1.3;margin:0 0 .2em}
p.sub{color:var(--muted);margin:0 0 2em}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px;margin:8px 0 24px}
.card{display:block;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px;text-decoration:none;color:inherit;transition:.18s;box-shadow:0 1px 2px rgba(0,0,0,.04)}
.card:hover{border-color:var(--accent);transform:translateY(-2px);box-shadow:0 8px 24px rgba(26,107,90,.10)}
.card h2{font-size:17px;margin:0 0 .35em;line-height:1.45}
.card p{font-size:13px;color:#4b5563;margin:0}
.card .meta{font-size:12px;color:var(--muted);margin-top:.7em;border-top:1px solid var(--line);padding-top:.55em}
.docs{list-style:none;margin:0 0 24px;padding:0;border:1px solid var(--line);border-radius:12px;background:var(--card);overflow:hidden}
.docs li{border-bottom:1px solid var(--line)}
.docs li:last-child{border-bottom:none}
.doc-link{display:flex;align-items:center;gap:8px;min-height:44px;padding:8px 16px;color:var(--ink);text-decoration:none;font-size:14.5px}
.doc-link:hover{background:var(--accent-soft);color:var(--accent)}
.doc-link .arrow{margin-left:auto;color:var(--muted);font-size:12px}
.empty{color:var(--muted);font-size:13px;margin:1em 0}
.prose{max-width:820px}
.prose h1{font-size:28px;line-height:1.35;margin:0 0 .6em}
.prose h2{font-size:21px;margin:1.6em 0 .5em;padding-bottom:.25em;border-bottom:1px solid var(--line)}
.prose h3{font-size:17.5px;margin:1.3em 0 .4em}
.prose h4{font-size:16px;margin:1.1em 0 .3em}
.prose p{margin:.7em 0}
.prose a{color:var(--accent)}
.prose img{max-width:100%;border-radius:8px;border:1px solid var(--line)}
.prose blockquote{margin:1em 0;padding:.6em 1em;border-left:3px solid var(--accent);background:#fafafa;color:#4b5563}
.prose pre{background:var(--code-bg);color:var(--code-fg);padding:14px 16px;border-radius:8px;overflow-x:auto;font-size:13.5px;line-height:1.6}
.prose code{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.92em}
.prose p code,.prose li code{background:#eef0f2;padding:.1em .35em;border-radius:4px;color:#c7254e}
.prose table{border-collapse:collapse;width:100%;margin:1em 0;font-size:14.5px;display:block;overflow-x:auto}
.prose th,.prose td{border:1px solid var(--line);padding:7px 12px;text-align:left;white-space:nowrap}
.prose th{background:var(--accent-soft)}
.prose ul,.prose ol{padding-left:1.5em}
.prose hr{border:none;border-top:1px solid var(--line);margin:2em 0}
.prose .mermaid{background:#fff;border:1px solid var(--line);border-radius:8px;padding:12px;margin:1em 0}
footer{margin-top:56px;font-size:13px;color:var(--muted);border-top:1px solid var(--line);padding-top:16px}
@media(min-width:640px){.wrap{padding:56px 28px 90px}}
@media(max-width:639px){body{font-size:15px}h1.title{font-size:26px}.prose h1{font-size:24px}}
"""


def esc(text):
    return html.escape(text, quote=True)


def rep(depth):
    return "../" * depth


def h1_of(md_path, fallback):
    try:
        with open(md_path, encoding="utf-8") as f:
            for line in f:
                m = re.match(r"^#\s+(.+)", line.strip())
                if m:
                    return m.group(1).strip()
    except OSError:
        pass
    return fallback


def list_dirs(path):
    if not os.path.isdir(path):
        return []
    return sorted(
        d for d in os.listdir(path)
        if os.path.isdir(os.path.join(path, d)) and not d.startswith(".") and d not in SKIP_DIRS
    )


def list_md(path):
    if not os.path.isdir(path):
        return []
    return sorted(
        f for f in os.listdir(path)
        if os.path.isfile(os.path.join(path, f)) and f.endswith(".md") and not f.startswith(".")
    )


def index_href(from_dir, target_dir):
    r = os.path.relpath(target_dir, from_dir)
    return "index.html" if r == "." else f"{r}/index.html"


def crumb_html(items, from_dir):
    """items: [(label, target_dir|None)]；target 为根相对目录，None=当前级"""
    parts = [f'<a href="{index_href(from_dir, ".")}">笔记架首页</a>']
    for label, target in items:
        if target is not None:
            parts.append(f'<a href="{index_href(from_dir, target)}">{esc(label)}</a>')
        else:
            parts.append(f'<span class="cur">{esc(label)}</span>')
    return '<nav class="crumb">' + ' <span>/</span> '.join(parts) + "</nav>"


def page(title, crumb, body, description=""):
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · Notes</title>
<style>{STYLE}</style>
</head>
<body>
<div class="wrap">
{crumb}
{body}
<footer>笔记架 Notes · 内容以 Markdown 形式开放 · 样式遵循 <code>DESIGN.md</code></footer>
</div>
</body>
</html>
"""


def card(title, desc, meta, href):
    meta_html = f'<div class="meta">{esc(meta)}</div>' if meta else ""
    desc_html = f"<p>{esc(desc)}</p>" if desc else ""
    return f'<a class="card" href="{esc(href)}"><h2>{esc(title)}</h2>{desc_html}{meta_html}</a>'


def write(rel_path, content):
    out = os.path.join(ROOT, rel_path)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(content)


def render_md(rel_md, trail):
    """trail: [(label, target_dir|None)]，target 为根相对目录。"""
    src = os.path.join(ROOT, rel_md)
    with open(src, encoding="utf-8") as f:
        md = f.read()
    title = h1_of(src, os.path.basename(rel_md)[:-3])
    body = f'<article class="prose">{convert(md)}</article>'
    out_rel = rel_md[:-3] + ".html"
    write(out_rel, page(title, crumb_html(trail, os.path.dirname(rel_md)), body))
    return title


def dir_index(rel_dir, title, items_cards, docs, trail, intro_rel=None):
    """为目录生成 index.html；items_cards: (title,desc,meta,href)；docs: (label, href)；trail: [(label, target_dir|None)]"""
    body = f'<h1 class="title">{esc(title)}</h1>'
    if intro_rel:
        intro_src = os.path.join(ROOT, intro_rel)
        if os.path.isfile(intro_src):
            with open(intro_src, encoding="utf-8") as f:
                body += f'<div class="prose">{convert(f.read())}</div>'
    if items_cards:
        body += '<div class="grid">' + "".join(
            card(t, d, m, h) for t, d, m, h in items_cards
        ) + "</div>"
    if docs:
        lis = "".join(
            f'<li><a class="doc-link" href="{esc(h)}">{esc(label)}<span class="arrow">→</span></a></li>'
            for label, h in docs
        )
        body += f'<ul class="docs">{lis}</ul>'
    if not items_cards and not docs:
        body += '<p class="empty">此处留空——产物生成后自动出现。</p>'
    write(os.path.join(rel_dir, "index.html"), page(title, crumb_html(trail, rel_dir), body))


def record_root(section_key, sub, root_marker):
    return os.path.join(section_key, sub, root_marker) if root_marker else os.path.join(section_key, sub)


def rel(cur_dir, target_dir):
    """目录间相对链接（不含末尾 /index.html）。"""
    return os.path.relpath(target_dir, cur_dir)


def build_record(section_key, section_label, sub, root_marker):
    """L2 记录页（位于 <分区>/<记录>/index.html）+ L3 条目索引 + 全部内容页。

    root_marker 分区（geektime）内容根在 <记录>/digest，但记录页锚定在 <记录>/index.html。
    返回 (title, meta) 供 L1 卡片使用。
    """
    page_rel = os.path.join(section_key, sub)              # L2 页所在目录
    root_rel = record_root(section_key, sub, root_marker)  # 内容根
    root_abs = os.path.join(ROOT, root_rel)
    if root_rel != page_rel:
        stale = os.path.join(root_abs, "index.html")
        if os.path.isfile(stale):
            os.remove(stale)  # 旧版构建在内容根残留的索引页，避免与 L2 记录页双头
    readme_rel = os.path.join(root_rel, "README.md")
    title = h1_of(os.path.join(ROOT, readme_rel), sub)
    subs = list_dirs(root_abs)
    mds = [f for f in list_md(root_abs) if f != "README.md"]

    # L2 记录页
    cards, docs = [], []
    for d in subs:
        d_rel = os.path.join(root_rel, d)
        n_md = len(list_md(os.path.join(ROOT, d_rel)))
        n_sub = len(list_dirs(os.path.join(ROOT, d_rel)))
        d_title = h1_of(os.path.join(ROOT, d_rel, "README.md"),
                        h1_of(os.path.join(ROOT, d_rel, "index.md"), d))
        meta = f"{n_md} 份文档 · {n_sub} 个子目录" if n_sub else f"{n_md} 份文档"
        cards.append((d_title, "", meta, index_href(page_rel, d_rel)))
    for f in mds:
        label = h1_of(os.path.join(ROOT, root_rel, f), f[:-3])
        docs.append((label, rel(page_rel, os.path.join(root_rel, f[:-3])) + ".html"))
    trail = [(section_label, section_key), (title, None)]
    dir_index(page_rel, title, cards, docs, trail, intro_rel=readme_rel)

    # L3 及以下：子目录索引与全部内容页（trail 全用根相对目录，链接随页深自动计算）
    def build_dir_index(d_rel, trail):
        d_abs = os.path.join(ROOT, d_rel)
        d_title = h1_of(os.path.join(d_abs, "README.md"),
                        h1_of(os.path.join(d_abs, "index.md"), os.path.basename(d_rel)))
        cards, docs = [], []
        for d2 in list_dirs(d_abs):
            d2_rel = os.path.join(d_rel, d2)
            n_md = len(list_md(os.path.join(ROOT, d2_rel)))
            d2_title = h1_of(os.path.join(ROOT, d2_rel, "README.md"),
                             h1_of(os.path.join(ROOT, d2_rel, "index.md"), d2))
            cards.append((d2_title, "", f"{n_md} 份文档", index_href(d_rel, d2_rel)))
        for f in [x for x in list_md(d_abs) if x not in ("README.md", "index.md")]:
            label = h1_of(os.path.join(ROOT, d_rel, f), f[:-3])
            docs.append((label, rel(d_rel, os.path.join(d_rel, f[:-3])) + ".html"))
        dir_index(d_rel, d_title, cards, docs, trail + [(d_title, None)],
                  intro_rel=os.path.join(d_rel, "README.md"))
        for d2 in list_dirs(d_abs):
            d2_rel = os.path.join(d_rel, d2)
            d2_title = h1_of(os.path.join(ROOT, d2_rel, "README.md"),
                             h1_of(os.path.join(ROOT, d2_rel, "index.md"), d2))
            build_dir_index(d2_rel, trail + [(d_title, d_rel), (d2_title, None)])

    def content_pages(dir_rel, trail):
        dir_abs = os.path.join(ROOT, dir_rel)
        for f in list_md(dir_abs):
            rel_md = os.path.join(dir_rel, f)
            label = h1_of(os.path.join(ROOT, rel_md), f[:-3])
            render_md(rel_md, trail + [(label, None)])
        for d in list_dirs(dir_abs):
            d_rel = os.path.join(dir_rel, d)
            d_title = h1_of(os.path.join(ROOT, d_rel, "README.md"),
                            h1_of(os.path.join(ROOT, d_rel, "index.md"), d))
            content_pages(d_rel, trail + [(d_title, d_rel)])

    for d in subs:
        d_rel = os.path.join(root_rel, d)
        d_title = h1_of(os.path.join(ROOT, d_rel, "README.md"),
                        h1_of(os.path.join(ROOT, d_rel, "index.md"), d))
        base = [(section_label, section_key), (title, page_rel), (d_title, d_rel)]
        build_dir_index(d_rel, base)
        content_pages(d_rel, base)

    # 内容根直属的 md（README 已内嵌进 L2，仍生成独立页供直达）
    for f in list_md(root_abs):
        rel_md = os.path.join(root_rel, f)
        label = h1_of(os.path.join(ROOT, rel_md), f[:-3])
        trail = [(section_label, section_key), (title, page_rel), (label, None)]
        render_md(rel_md, trail)

    meta = f"{len(subs)} 个条目 · {len(mds)} 份文档" if subs else f"{len(mds)} 份文档"
    return title, meta


def build():
    # L1 分区 + 记录
    section_cards = []
    for key, label, marker in SECTIONS:
        sec_abs = os.path.join(ROOT, key)
        if not os.path.isdir(sec_abs):
            continue
        records = []
        for sub in list_dirs(sec_abs):
            rec_rel = record_root(key, sub, marker)
            if os.path.isfile(os.path.join(ROOT, rec_rel, "README.md")):
                records.append(sub)
        cards = []
        for sub in records:
            rec_rel = record_root(key, sub, marker)
            title = h1_of(os.path.join(ROOT, rec_rel, "README.md"), sub)
            meta = build_record(key, label, sub, marker)
            n_items = ""
            cards.append((title, "", meta[1], f"{sub}/index.html"))
        dir_index(key, label, cards, [], [(label, None)])
        n_desc = f"{len(records)} 条记录"
        section_cards.append((label, section_blurb(key), n_desc, f"{key}/index.html"))

    # 根上的游离 md（README.md / digest_index.md 等）
    root_docs = []
    for f in list_md(ROOT):
        label = h1_of(os.path.join(ROOT, f), f[:-3])
        render_md(f, [(label, None)])
        if f != "README.md":
            root_docs.append((label, f"{f[:-3]}.html"))

    body = '<h1 class="title">笔记架</h1><p class="sub">课程 / 读书 / 会议 / 极客时间 · 个人学习笔记</p>'
    body += '<div class="grid">' + "".join(
        card(t, d, m, h) for t, d, m, h in section_cards) + "</div>"
    if root_docs:
        body += "<h2>索引</h2><ul class=\"docs\">" + "".join(
            f'<li><a class="doc-link" href="{esc(h)}">{esc(l)}<span class="arrow">→</span></a></li>'
            for l, h in root_docs) + "</ul>"
    write("index.html", page("笔记架", crumb_html([], "."), body))
    print("== 构建完成 ==")


def section_blurb(key):
    return {
        "reading": "按书组织的阅读笔记：三区笔记 / 永久卡片 / 自测 / 行动清单",
        "courses": "按课程组织的听课笔记：主笔记 / 大纲 / 自测 / 衍生选题",
        "meetings": "按会议组织的纪要：决策 / 行动 / 待定 / 勘误",
        "geektime": "极客时间课程消化产物：一页纸 / 精华讲卡 / 分拣 / 写作简报",
    }.get(key, "")


if __name__ == "__main__":
    build()
