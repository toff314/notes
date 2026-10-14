#!/usr/bin/env bash
# 把全部笔记 Markdown 渲染成同名 HTML（供在线阅读）。
# 改完 .md 后重跑本脚本即可。
set -euo pipefail
cd "$(dirname "$0")/.."

NAV_ROOT='<div class="nav"><a href="./index.html">笔记架首页</a></div>'
NAV_COURSE='<div class="nav"><a href="../index.html">笔记架</a><a href="./index.html">计算语言学基础</a><a href="./SUMMARY.html">目录</a></div>'
NAV_LEC='<div class="nav"><a href="../../index.html">笔记架</a><a href="../index.html">计算语言学基础</a><a href="./README.html">本讲索引</a></div>'

render() { # <md> <title> <nav>
  local md="$1" title="$2" nav="$3"
  local dir name
  dir="$(dirname "$md")"
  name="$(basename "$md" .md)"
  python3 scripts/md2html.py "$md" -o "$dir" --name "$name" --title "$title" --nav "$nav"
}

render README.md "Notes · 听课笔记" "$NAV_ROOT"

C=computational-linguistics
render "$C/README.md" "计算语言学基础 · 听课笔记" "$NAV_COURSE"
render "$C/SUMMARY.md" "计算语言学基础 · 目录" "$NAV_COURSE"

L="$C/01-introduction"
render "$L/README.md"      "听课笔记：第 1 课 绪论 · 索引"     "$NAV_LEC"
render "$L/notes.md"       "听课笔记：第 1 课 绪论 · 主笔记"   "$NAV_LEC"
render "$L/outline.md"     "听课笔记：第 1 课 绪论 · 思路大纲" "$NAV_LEC"
render "$L/questions.md"   "听课笔记：第 1 课 绪论 · 自测"     "$NAV_LEC"
render "$L/corrections.md" "听课笔记：第 1 课 绪论 · 勘误"     "$NAV_LEC"
render "$L/spinoffs.md"    "听课笔记：第 1 课 绪论 · 衍生选题" "$NAV_LEC"

echo "== 完成 =="
