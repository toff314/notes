#!/usr/bin/env python3
"""lab-05: 中文内涵框架手工构建
对应 actions.md 第 5 条，书中 §23.9
"""
import csv
import os

# 手工构建 5 个中文动词的内涵框架
# 字段：动词, 主语(Role1)情感, 宾语(Role2)情感, 权力差异, 能动性, 例句, 例句分析
frames = [
    {
        "verb": "侵犯",
        "role1_sentiment": "负面",  # 施事（侵犯者）是负面
        "role2_sentiment": "正面",  # 受事（被侵犯者）是受害者，值得同情
        "power_relation": "Role1 > Role2",  # 侵犯者权力高于被侵犯者
        "agency_role1": "高",
        "example": "A 国侵犯了 B 国的主权",
        "analysis": "作者表达对 B 国（受事）的同情，把 B 国描绘成受害者；对 A 国（施事）表达敌意。"
    },
    {
        "verb": "幸存",
        "role1_sentiment": "正面",  # 主语（幸存者）是正面
        "role2_sentiment": "负面",  # 宾语（灾难）是负面
        "power_relation": "Role1 < Role2",  # 幸存者相对于灾难是弱势
        "agency_role1": "低",  # 幸存更多是被动承受
        "example": "那名少年从波士顿马拉松爆炸案中幸存下来",
        "analysis": "作者表达对主语（幸存者）的同情和正面情感；对宾语（爆炸案）表达负面情感。"
    },
    {
        "verb": "批评",
        "role1_sentiment": "中性偏负面",  # 批评者可以是正当的也可以是恶意的
        "role2_sentiment": "中性偏负面",  # 被批评者通常不被同情，但也可能值得同情
        "power_relation": "Role1 ≥ Role2",  # 批评者通常处于评判地位
        "agency_role1": "高",
        "example": "专家批评了这项政策",
        "analysis": "「批评」的情感方向高度依赖语境：建设性批评中主语是正面（监督者），恶意批评中主语是负面（攻击者）。"
    },
    {
        "verb": "感谢",
        "role1_sentiment": "正面",  # 感谢者是正面（感恩的人）
        "role2_sentiment": "正面",  # 被感谢者是正面（施惠者）
        "power_relation": "Role1 < Role2",  # 被感谢者处于施惠地位
        "agency_role1": "高",
        "example": "市民感谢消防员的英勇行为",
        "analysis": "作者对主语（感谢者）和宾语（消防员）都表达正面情感；权力上被感谢者（消防员）高于感谢者。"
    },
    {
        "verb": "等待",
        "role1_sentiment": "中性",  # 等待者本身无明确褒贬
        "role2_sentiment": "中性",  # 被等待的对象也无明确褒贬
        "power_relation": "Role1 < Role2",  # 等待者处于被动地位
        "agency_role1": "低",  # 等待是低能动性动作
        "example": "顾客等待了两个小时",
        "analysis": "「等待」本身不携带强烈情感，但低能动性标注呼应了书中 Sap 等人对 waited 的标注。"
    },
]

print("中文内涵框架表（手工构建，5 个动词）\n")
print(f"{'动词':<6} {'Role1情感':<12} {'Role2情感':<12} {'权力关系':<15} {'Role1能动性':<12}")
print("-" * 70)
for f in frames:
    print(f"{f['verb']:<6} {f['role1_sentiment']:<12} {f['role2_sentiment']:<12} {f['power_relation']:<15} {f['agency_role1']:<12}")

print("\n" + "=" * 70)
print("例句验证")
print("=" * 70)
for f in frames:
    print(f"\n【{f['verb']}】")
    print(f"  例句：{f['example']}")
    print(f"  分析：{f['analysis']}")

# 验证 survive 和 violate 的方向与书中一致
print("\n" + "=" * 70)
print("与书中方向对照")
print("=" * 70)
print("survive（幸存）: Role1（主语）正面 ✓, Role2（宾语/灾难）负面 ✓ — 与书中一致")
print("violate（侵犯）: Role1（施事）负面 ✓, Role2（受事）正面 ✓ — 与书中一致")
print("等待: Role1 能动性低 ✓ — 与书中 Sap et al. 2017 对 waited 的标注一致")

os.makedirs("out", exist_ok=True)
with open("out/connotation_frames.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "verb", "role1_sentiment", "role2_sentiment",
        "power_relation", "agency_role1", "example", "analysis"
    ])
    writer.writeheader()
    for frame in frames:
        writer.writerow(frame)

print("\nsaved: out/connotation_frames.csv")
