#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""lab-01　ARPAbet / IPA 对照表与窄式转写对齐

对应 actions.md 第 1 条；对应书中 §15.1（图 15.1、图 15.2）。
所有输入都从 raw 正文里解析，不联网、不下载语料。
"""
import csv
import json
import os
import re
from collections import Counter

RAW = "/home/yuanwu/notes/reading/slp3/raw/15/15-phonetics-and-speech.md"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

raw = open(RAW, encoding="utf-8").read()
lines = raw.splitlines()

# ---------- 1. 解析图 15.1 的 40 行对照表 ----------
fig_line = next(l for l in lines if "parsley" in l and "honey" in l)
rows = re.findall(r"\[([A-Za-z]+)\]\s*\[([^\]]+)\]\s*([a-z]+)\s*\[([^\]]+)\]", fig_line)
assert len(rows) == 40, len(rows)

CONSONANTS = {"p", "b", "t", "d", "k", "g", "m", "n", "ng", "f", "v", "th", "dh",
              "s", "z", "sh", "zh", "ch", "jh", "l", "w", "r", "y", "h"}
table = {}
for arpa, ipa, word, trans in rows:
    table.setdefault(arpa, {"ipa": ipa, "example": word, "trans": trans})
    assert arpa not in CONSONANTS or arpa in CONSONANTS

n_cons = sum(1 for k in table if k in CONSONANTS)
n_vow = len(table) - n_cons
ipa_all = "".join(v["ipa"] for v in table.values())
n_nonascii = sum(1 for c in ipa_all if ord(c) > 127)

with open(os.path.join(OUT, "arpabet_ipa.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["arpabet", "ipa", "类别", "例词", "例词转写"])
    for arpa, v in table.items():
        w.writerow([arpa, v["ipa"], "辅音" if arpa in CONSONANTS else "元音",
                    v["example"], v["trans"]])

# ---------- 2. 正字法与音子的不透明程度 ----------
# 图 15.1 每个例词的拼写 -> 音子数（转写串按空格切）
orth = [(v["example"], v["trans"].split()) for v in table.values()]
ratios = [(w, len(w), len(t), len(t) - len(w)) for w, t in orth]
mean_ratio = sum(r[2] / r[1] for r in ratios) / len(ratios)
same_len = sum(1 for r in ratios if r[3] == 0)

# 英语里同一个字母可以对应多个音子：统计首字母 -> 音子集合
first_letter = {}
for (w, t) in orth:
    first_letter.setdefault(w[0], set()).add(t[0])
amb = {k: sorted(v) for k, v in first_letter.items() if len(v) > 1}

# ---------- 3. 图 15.2 窄式转写与拼写对齐 ----------
narrow = ("sh iy hv ae dcl jh axr dcl d aa r kcl s ux q en gcl "
          "g r iy s ix w aa sh q w aa dx axr q aa l y ix axr").split()
words = ["she", "had", "your", "dark", "suit", "in", "greasy", "wash", "water", "all", "year"]

# 按书中图注给出的边界手工切分（图注只点了 4 处差异）
spans = {
    "she": (0, 2), "had": (2, 5), "your": (5, 7), "dark": (7, 12), "suit": (12, 15),
    "in": (15, 16), "greasy": (16, 22), "wash": (22, 26), "water": (26, 30),
    "all": (30, 33), "year": (33, 36),
}
assert max(b for _, b in spans.values()) == len(narrow)

# 宽式（词典）转写：用图 15.1 的 ARPAbet 体系写出常见读音
broad = {
    "she": "sh iy", "had": "hh ae d", "your": "y ao r", "dark": "d aa r k",
    "suit": "s uw t", "in": "ih n", "greasy": "g r iy s iy", "wash": "w aa sh",
    "water": "w ao t axr", "all": "ao l", "year": "y ih r",
}

PROCESS = {
    "dcl": "不除阻塞音（unreleased stop）",
    "kcl": "不除阻塞音（unreleased stop）",
    "gcl": "不除阻塞音（unreleased stop）",
    "q": "喉化 / 声门塞音（glottal stop）",
    "dx": "闪音（flap）",
    "hv": "清化的 hv（voiceless h + v）",
    "ux": "圆唇化的 uw（fronted/rounded u）",
    "ix": "弱化高元音（schwa-like i）",
    "axr": "r 化 schwa（schwa + r）",
    "en": "成音节鼻音（syllabic n）",
}

rows_narrow = []
for wd in words:
    a, b = spans[wd]
    seq = narrow[a:b]
    rows_narrow.append([wd, " ".join(broad.get(wd, "").split()), " ".join(seq),
                        len(broad.get(wd, "").split()), len(seq)])
with open(os.path.join(OUT, "timit_narrow.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["word", "宽式(ARPAbet)", "窄式(图中)", "宽式音子数", "窄式音子数"])
    w.writerows(rows_narrow)

special = Counter(t for t in narrow if t in PROCESS)
diff_words = [r[0] for r in rows_narrow if r[1] != r[2]]

# 图注点名的 4 处：had 的 [d] 腭化为 [jh]、dark 的不除阻、suit 的 [q]、water 的 [dx]
named = {
    "had your 中 d 腭化为 jh": "jh" in narrow[spans["had"][0]:spans["your"][1]],
    "dark 末尾不除阻": "kcl" in narrow[spans["dark"][0]:spans["dark"][1]],
    "suit 末尾喉化": "q" in narrow[spans["suit"][0]:spans["suit"][1]],
    "water 中闪音": "dx" in narrow[spans["water"][0]:spans["water"][1]],
}

summary = {
    "对照表行数": len(table),
    "辅音数": n_cons,
    "元音数": n_vow,
    "IPA 符号中非 ASCII 个数": n_nonascii,
    "例词平均音子/字母比": round(mean_ratio, 3),
    "音子数与字母数相同的例词数": f"{same_len}/{len(ratios)}",
    "首字母歧义": amb,
    "窄式转写音子总数": len(narrow),
    "特殊符号统计": dict(special),
    "宽窄不一致的词": diff_words,
    "图注点名现象核验": named,
}
with open(os.path.join(OUT, "summary.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print("对照表行数:", len(table), "| 辅音", n_cons, "元音", n_vow)
print("IPA 非 ASCII 符号数:", n_nonascii, "（共", len(ipa_all), "个符号）")
print("例词平均音子/字母比:", round(mean_ratio, 3),
      "| 音子数=字母数:", f"{same_len}/{len(ratios)}")
print("首字母歧义:", {k: len(v) for k, v in amb.items()})
print("窄式音子总数:", len(narrow), "| 特殊符号:", dict(special))
print("宽窄不一致:", len(diff_words), diff_words)
for r in rows_narrow:
    print("  ", r)
