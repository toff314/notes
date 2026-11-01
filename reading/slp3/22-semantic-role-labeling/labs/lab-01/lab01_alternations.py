#!/usr/bin/env python3
"""Lab-01: 语态交替与题元网格归纳
对 break/give/open 三个动词，归纳题元网格和语态交替形式。
复算书中 (22.3)-(22.8) 的例句。
"""
import json
from collections import defaultdict

# 书中 (22.3)-(22.8) 的例句及语义角色标注
examples = [
    {"verb": "break", "sent": "John broke the window.", "roles": {"John": "施事", "the window": "主题"}, "syntax": "施事/主语, 主题/宾语"},
    {"verb": "break", "sent": "John broke the window with a stone.", "roles": {"John": "施事", "the window": "主题", "a stone": "工具"}, "syntax": "施事/主语, 主题/宾语, 工具/介词短语with"},
    {"verb": "break", "sent": "The stone broke the window.", "roles": {"The stone": "工具", "the window": "主题"}, "syntax": "工具/主语, 主题/宾语"},
    {"verb": "break", "sent": "The window broke.", "roles": {"The window": "主题"}, "syntax": "主题/主语"},
    {"verb": "break", "sent": "The window was broken by John.", "roles": {"The window": "主题", "John": "施事"}, "syntax": "主题/主语, 施事/介词短语by"},
    {"verb": "give", "sent": "Doris gave the book to Cary.", "roles": {"Doris": "施事", "the book": "主题", "Cary": "目标"}, "syntax": "施事/主语, 主题/宾语, 目标/介词短语to"},
    {"verb": "give", "sent": "Doris gave Cary the book.", "roles": {"Doris": "施事", "Cary": "目标", "the book": "主题"}, "syntax": "施事/主语, 目标/间接宾语, 主题/直接宾语"},
    {"verb": "open", "sent": "John opened the door.", "roles": {"John": "施事", "the door": "主题"}, "syntax": "施事/主语, 主题/宾语"},
    {"verb": "open", "sent": "The door opened.", "roles": {"The door": "主题"}, "syntax": "主题/主语"},
    {"verb": "open", "sent": "The door was opened by John.", "roles": {"The door": "主题", "John": "施事"}, "syntax": "主题/主语, 施事/介词短语by"},
]

# 归纳题元网格
thematic_grids = defaultdict(set)
for ex in examples:
    for role in ex["roles"].values():
        thematic_grids[ex["verb"]].add(role)

# 归纳语态交替（主语角色变化）
subject_alternations = defaultdict(list)
for ex in examples:
    subj = ex["sent"].split()[0] if not ex["sent"].startswith("The") else "The " + ex["sent"].split()[1]
    for np, role in ex["roles"].items():
        if np.startswith(subj) or subj.startswith(np.split()[0]):
            subject_alternations[ex["verb"]].append((np, role, ex["syntax"]))
            break

result = {
    "thematic_grids": {v: sorted(list(r)) for v, r in thematic_grids.items()},
    "subject_alternations": {v: list(set(a[1] for a in alts)) for v, alts in subject_alternations.items()},
    "examples_count": len(examples),
    "verbs": sorted(thematic_grids.keys()),
}

with open("out/alternations.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("=== 题元网格 ===")
for v, roles in result["thematic_grids"].items():
    print(f"{v}: {', '.join(roles)}")
print("\n=== 主语交替 ===")
for v, roles in result["subject_alternations"].items():
    print(f"{v}: 主语可为 {', '.join(roles)}")
print(f"\n共复算 {len(examples)} 个例句，覆盖 {len(result['verbs'])} 个动词")
