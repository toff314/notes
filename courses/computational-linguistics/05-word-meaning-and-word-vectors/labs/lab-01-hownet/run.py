import OpenHowNet, json
hownet_dict = OpenHowNet.HowNetDict()

out = {}
# 1) 苹果：全部义项
senses = hownet_dict.get_sense("苹果")
out["apple_sense_count"] = len(senses)
out["apple_senses"] = [str(s) for s in senses]

# 2) 苹果树义：义原树
tree = hownet_dict.get_sememes_by_word(word="苹果", display="list", K=2)
out["apple_sememe_trees"] = [str(t) for t in tree][:8]

# 3) 义原间关系：圆 vs 形状值
try:
    rel = hownet_dict.get_sememe_relation("FormValue|形状值", "圆", return_type="list")
    out["sememe_relation_圆"] = str(rel)
except Exception as e:
    out["sememe_relation_圆"] = f"ERR {e}"

# 4) OOV 实测：儿童空耳新词 vs 老词
for w in ["刀盾", "我的刀盾", "比比拉布", "奥特曼", "苹果"]:
    try:
        s = hownet_dict.get_sense(w)
        out[f"lookup_{w}"] = len(s)
    except Exception as e:
        out[f"lookup_{w}"] = f"ERR {e}"

print(json.dumps(out, ensure_ascii=False, indent=1))
