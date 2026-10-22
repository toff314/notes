#!/usr/bin/env bash
# 自动扫描渲染：仓库内全部 .md → 同名 .html（供在线阅读）。
# 新增课次 / 产物后无需改本脚本，直接重跑：bash scripts/build-html.sh
# 排除：scripts/、.git/、.cache/、以及各级 raw/（本地素材，不入站点）。
set -euo pipefail
cd "$(dirname "$0")/.."

h1() { # <md> 取第一个 H1 做显示名，兜底文件名
  local t
  t=$(grep -m1 -s '^# ' "$1" | sed 's/^# \+//')
  printf '%s' "${t:-$(basename "${1%.md}")}"
}

rep() { # <n> 生成 n 层 ../ 回溯前缀（n=0 输出空）
  local s="" i=0
  while [ "$i" -lt "$1" ]; do s+="../"; i=$((i + 1)); done
  printf '%s' "$s"
}

crumb() { # <rel-dir> 生成面包屑导航（相对当前页目录回溯；每级显示名取该级 README.md 的 H1）
  local d="$1" nav p cur="" disp link oldIFS=$IFS n=0
  [ "$d" != "." ] && { IFS='/'; set -- $d; n=$#; }
  IFS=$oldIFS
  nav="<div class=\"nav\"><a href=\"$(rep "$n")index.html\">笔记架首页</a>"
  if [ "$d" != "." ]; then
    local j=0
    IFS='/'
    for p in $d; do
      j=$((j + 1)); cur="${cur:+$cur/}$p"
      if [ -f "$cur/index.md" ]; then disp=$(h1 "$cur/index.md")
      elif [ -f "$cur/README.md" ]; then disp=$(h1 "$cur/README.md")
      else disp="$p"; fi
      link="$(rep $((n - j)))index.html"; [ -f "$cur/index.md" ] || link="$(rep $((n - j)))README.html"
      nav+="<a href=\"$link\">$disp</a>"
    done
  fi
  IFS=$oldIFS
  printf '%s</div>' "$nav"
}

n=0
while IFS= read -r -d '' md; do
  rel="${md#./}"
  dir="$(dirname "$rel")"; name="$(basename "$rel" .md)"
  title="$(h1 "$rel")"
  nav="$(crumb "$dir")"
  python3 scripts/md2html.py "$rel" -o "$dir" --name "$name" --title "$title" --nav "$nav"
  n=$((n + 1))
done < <(find . \( -name .git -o -name .cache -o -name scripts -o -name raw \) -prune \
            -o -type f -name '*.md' -print0 | sort -z)

echo "== 完成：渲染 $n 个 .md =="
