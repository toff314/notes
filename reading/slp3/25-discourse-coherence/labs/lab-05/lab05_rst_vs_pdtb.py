#!/usr/bin/env python3
"""lab-05: RST vs PDTB 对比

对应 §25.1.1 (RST) 和 §25.1.2 (PDTB)。
对同一段文本，分别用 RST 和 PDTB 两种范式进行标注，对比二者的
标注单位、关系类型、结构形式、覆盖范围。
"""
import json
import os

out_dir = os.path.join(os.path.dirname(__file__), 'out')
os.makedirs(out_dir, exist_ok=True)

# ── 输入文本（书中 §25.1 的例句组合）──
text = """Jane took the train from Paris to Istanbul. She had to attend a conference. The conference was about advances in natural language processing. Jane presented her work on discourse coherence. Many researchers attended the session."""

sentences = [
    "Jane took the train from Paris to Istanbul.",
    "She had to attend a conference.",
    "The conference was about advances in natural language processing.",
    "Jane presented her work on discourse coherence.",
    "Many researchers attended the session.",
]

# ═══════════════════════════════════════════════
# RST 标注（层级树结构，核心-卫星关系）
# ═══════════════════════════════════════════════
rst_annotation = {
    "paradigm": "RST (Rhetorical Structure Theory)",
    "source": "Mann and Thompson, 1987; Carlson et al., 2001",
    "structure": "tree",  # 层级树
    "units": "EDU (Elementary Discourse Units)",
    "relations": [
        {
            "id": "rst-1",
            "type": "Reason",
            "nucleus": "Jane took the train from Paris to Istanbul.",
            "satellite": "She had to attend a conference.",
            "direction": "satellite→nucleus",
            "example_ref": "(25.7)",
        },
        {
            "id": "rst-2",
            "type": "Elaboration",
            "nucleus": "She had to attend a conference.",
            "satellite": "The conference was about advances in natural language processing.",
            "direction": "satellite→nucleus",
            "example_ref": "(25.8)",
        },
        {
            "id": "rst-3",
            "type": "Elaboration",
            "nucleus": "Jane presented her work on discourse coherence.",
            "satellite": "Many researchers attended the session.",
            "direction": "satellite→nucleus",
            "example_ref": "(25.8)",
        },
    ],
    "tree_structure": {
        "relation": "Elaboration",
        "nucleus": {
            "relation": "Elaboration",
            "nucleus": {
                "relation": "Reason",
                "nucleus": "Jane took the train from Paris to Istanbul.",
                "satellite": "She had to attend a conference.",
            },
            "satellite": "The conference was about advances in natural language processing.",
        },
        "satellite": {
            "relation": "Elaboration",
            "nucleus": "Jane presented her work on discourse coherence.",
            "satellite": "Many researchers attended the session.",
        },
    },
    "num_relations": 3,
    "coverage": "full-tree",  # 覆盖整个篇章
}

# ═══════════════════════════════════════════════
# PDTB 标注（扁平关系对，以连接词为入口）
# ═══════════════════════════════════════════════
pdtb_annotation = {
    "paradigm": "PDTB (Penn Discourse Treebank)",
    "source": "Miltsakaki et al., 2004; Prasad et al., 2008",
    "structure": "flat-pairs",  # 扁平关系对
    "units": "Arg1 / Arg2 (text spans around connectives)",
    "relations": [
        {
            "id": "pdtb-1",
            "connective": "because",  # 隐式，标注者选择
            "type": "Contingency.Cause.Reason",
            "arg1": "Jane took the train from Paris to Istanbul.",
            "arg2": "She had to attend a conference.",
            "explicit": False,
            "example_ref": "(25.14) implicit style",
        },
        {
            "id": "pdtb-2",
            "connective": "in particular",  # 隐式
            "type": "Expansion.Restatement.Specification",
            "arg1": "She had to attend a conference.",
            "arg2": "The conference was about advances in natural language processing.",
            "explicit": False,
            "example_ref": "(25.14) implicit style",
        },
        {
            "id": "pdtb-3",
            "connective": "and",  # 显式
            "type": "Expansion.Conjunction",
            "arg1": "Jane presented her work on discourse coherence.",
            "arg2": "Many researchers attended the session.",
            "explicit": True,
            "example_ref": "(25.24) explicit style",
        },
    ],
    "num_relations": 3,
    "coverage": "pair-only",  # 只覆盖片段对，不建全局树
}

# ═══════════════════════════════════════════════
# 对比分析
# ═══════════════════════════════════════════════
comparison = {
    "dimensions": [
        {
            "dimension": "结构形式",
            "rst": "层级树（覆盖全篇）",
            "pdtb": "扁平关系对（仅相邻片段）",
            "note": "RST 构建完整篇章树；PDTB 不承诺高于片段对的结构",
        },
        {
            "dimension": "标注单位",
            "rst": "EDU（基本篇章单元）",
            "pdtb": "Arg1 / Arg2（连接词两侧的文本片段）",
            "note": "RST 的 EDU 可由任意长度文本跨度构成；PDTB 以连接词为锚点",
        },
        {
            "dimension": "关系来源",
            "rst": "标注者直接判断语义关系",
            "pdtb": "从篇章连接词列表出发（because, although, as a result...）",
            "note": "PDTB 也标注隐式关系（如 25.14），但需标注者先选定可能的连接词",
        },
        {
            "dimension": "关系类型",
            "rst": "78 种关系，归 16 大类（Reason, Elaboration, Evidence...）",
            "pdtb": "4 顶层类别，16 类型，23 子类型（Temporal, Contingency, Comparison, Expansion）",
            "note": "RST 关系更细；PDTB 层级更规范",
        },
        {
            "dimension": "对称性",
            "rst": "核心-卫星不对称；List 等多核心关系例外",
            "pdtb": "Arg1/Arg2 在理论上对称（但连接词位置带来轻微不对称）",
            "note": "RST 的核性（nucleus/satellite）对摘要等任务很重要",
        },
        {
            "dimension": "标注成本",
            "rst": "高（需构建完整树）",
            "pdtb": "较低（只需标注片段对）",
            "note": "PDTB 标注量更大（~34K 关系），但单条成本低",
        },
        {
            "dimension": "典型应用",
            "rst": "自动文摘（核心保留、卫星删除）、篇章分析",
            "pdtb": "连接词消歧、隐式关系分类、浅层篇章分析",
            "note": "RST 适合全局结构任务；PDTB 适合局部关系识别",
        },
    ],
    "summary": {
        "rst_total_relations": rst_annotation["num_relations"],
        "pdtb_total_relations": pdtb_annotation["num_relations"],
        "rst_structure": "3 层树",
        "pdtb_structure": "3 个扁平关系对",
        "shared_relations": 3,
    },
}

# ═══════════════════════════════════════════════
# 输出
# ═══════════════════════════════════════════════
print("=" * 60)
print("lab-05: RST vs PDTB 对比")
print("=" * 60)

print(f"\n文本: {text[:80]}...")

print(f"\n── RST 标注（{rst_annotation['num_relations']} 个关系）──")
for r in rst_annotation["relations"]:
    print(f"  [{r['type']}] NUC: {r['nucleus'][:50]}...")
    print(f"           SAT: {r['satellite'][:50]}...")

print(f"\n── PDTB 标注（{pdtb_annotation['num_relations']} 个关系）──")
for r in pdtb_annotation["relations"]:
    conn = f"[{r['connective']}]" + (" (显式)" if r["explicit"] else " (隐式)")
    print(f"  {conn} {r['type']}")
    print(f"    Arg1: {r['arg1'][:50]}...")
    print(f"    Arg2: {r['arg2'][:50]}...")

print(f"\n── 对比 ──")
print(f"{'维度':<12} {'RST':<35} {'PDTB'}")
print("-" * 80)
for d in comparison["dimensions"]:
    print(f"{d['dimension']:<12} {d['rst']:<35} {d['pdtb']}")

print(f"\n关键差异:")
for d in comparison["dimensions"][:3]:
    print(f"  • {d['dimension']}: {d['note']}")

# 保存
output = {
    "text": text,
    "sentences": sentences,
    "rst": rst_annotation,
    "pdtb": pdtb_annotation,
    "comparison": comparison,
}
output_file = os.path.join(out_dir, 'rst_vs_pdtb.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print(f"\n结果已保存到 {output_file}")
