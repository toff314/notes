import jieba, json

sentences = [
    "我的刀盾，你在干什么",
    "他今天又在班里说比比拉布",
    "我勒个豆，这也太抽象了",
    "数学老师讲的我直接emo了",
    "董振东先生标注了知网",
]
out = {}
for s in sentences:
    out[s] = list(jieba.cut(s))

# 关键新词能否作为词被切出来
for w in ["刀盾", "比比拉布", "emo", "抽象", "知网"]:
    segs = list(jieba.cut(w))
    out[f"word::{w}"] = segs

print(json.dumps(out, ensure_ascii=False, indent=1))
