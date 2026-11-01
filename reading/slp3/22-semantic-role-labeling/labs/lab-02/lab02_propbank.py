#!/usr/bin/env python3
"""Lab-02: PropBank 框架文件解析与角色标注
解析 agree.01 / fall.01 / increase.01 框架文件，自动标注 6 个测试句子。
"""
import json
import re

# 书中 (22.11)-(22.13) 的框架文件（简化）
frame_files = {
    "agree.01": {
        "roles": {"Arg0": "同意者", "Arg1": "命题", "Arg2": "其他表示同意的实体"},
        "examples": [
            "[Arg0 The group] agreed [Arg1 it wouldn't make an offer].",
            "[ArgM-TMP Usually] [Arg0 John] agrees [Arg2 with Mary] [Arg1 on everything].",
        ],
    },
    "fall.01": {
        "roles": {"Arg1": "逻辑主语、受事、下落之物", "Arg2": "幅度、落下的量", "Arg3": "起始点", "Arg4": "终点、arg1 的结束状态"},
        "examples": [
            "[Arg1 Sales] fell [Arg4 to $25 million] [Arg3 from $27 million].",
            "[Arg1 The average junk bond] fell [Arg2 by 4.2%].",
        ],
    },
    "increase.01": {
        "roles": {"Arg0": "增加的致使者", "Arg1": "增加之物", "Arg2": "增加量、EXT 或 MNR", "Arg3": "起始点", "Arg4": "终点"},
        "examples": [
            "[Arg0 Big Fruit Co.] increased [Arg1 the price of bananas].",
            "[Arg1 The price of bananas] was increased again [Arg0 by Big Fruit Co.].",
            "[Arg1 The price of bananas] increased [Arg2 5%].",
        ],
    },
}

# 解析框架文件：提取角色定义
def parse_frame(verb, frame):
    roles = {}
    for arg, desc in frame["roles"].items():
        roles[arg] = desc
    return {"verb": verb, "roles": roles, "num_roles": len(roles)}

# 自动标注：用正则提取 [ArgX ...] 模式的标注
def auto_annotate(sentence):
    annotations = []
    pattern = r"\[(ArgM?-[A-Z0-9]+|Arg[0-9])\s+([^\]]+)\]"
    for m in re.finditer(pattern, sentence):
        tag = m.group(1)
        text = m.group(2).strip()
        annotations.append({"tag": tag, "text": text})
    return annotations

parsed_frames = {v: parse_frame(v, f) for v, f in frame_files.items()}

all_annotations = []
for verb, frame in frame_files.items():
    for sent in frame["examples"]:
        anns = auto_annotate(sent)
        all_annotations.append({"verb": verb, "sentence": sent, "annotations": anns})

result = {
    "parsed_frames": parsed_frames,
    "annotations": all_annotations,
    "total_sentences": len(all_annotations),
}

with open("out/propbank_annotations.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("=== 解析的框架文件 ===")
for v, pf in parsed_frames.items():
    print(f"{v}: {pf['num_roles']} 个角色 -> {list(pf['roles'].keys())}")

print(f"\n=== 自动标注 {len(all_annotations)} 个句子 ===")
for item in all_annotations:
    print(f"\n[{item['verb']}] {item['sentence']}")
    for a in item["annotations"]:
        print(f"  {a['tag']}: {a['text']}")
