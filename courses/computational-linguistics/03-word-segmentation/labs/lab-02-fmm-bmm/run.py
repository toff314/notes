# -*- coding: utf-8 -*-
"""FMM/BMM 复现（课堂第3讲方法）：小词典 + MaxLen=3，复现 OA/CA/OOV 三类歧义"""
import json

LEX = {"结婚","的","和","尚未","和尚","未","研究","生命","起源","研究生",
       "学生","会","学生会","说","英语","北京","人和","足球","俱乐部","疫情","如此"}

def fmm(text, lexicon, maxlen=3):
    res, i = [], 0
    while i < len(text):
        hit = None
        for L in range(min(maxlen, len(text)-i), 0, -1):
            if text[i:i+L] in lexicon: hit = text[i:i+L]; break
        if hit: res.append(hit); i += len(hit)
        else: res.append(text[i]); i += 1
    return res

def bmm(text, lexicon, maxlen=3):
    res, i = [], len(text)
    while i > 0:
        hit = None
        for L in range(min(maxlen, i), 0, -1):
            if text[i-L:i] in lexicon: hit = text[i-L:i]; break
        if hit: res.append(hit); i -= len(hit)
        else: res.append(text[i-1]); i -= 1
    return res[::-1]

CASES = [
    ("结婚的和尚未结婚的", "OA 交集歧义（FMM/BMM 分歧可发现）"),
    ("研究生命起源", "CA 组合歧义 + FMM 贪婪陷阱"),
    ("学生会说英语", "CA 组合歧义（双向均不可见）"),
    ("北京人和足球俱乐部", "实体歧义（词典未收实体则不可见）"),
    ("新冠疫情反复", "OOV（新/冠 退化为单字）"),
]
for s, kind in CASES:
    f, b = fmm(s, LEX), bmm(s, LEX)
    mark = "  <== 分歧" if f != b else ""
    print(f"[{kind}] {s}\n  FMM: {'/'.join(f)}\n  BMM: {'/'.join(b)}{mark}\n")
