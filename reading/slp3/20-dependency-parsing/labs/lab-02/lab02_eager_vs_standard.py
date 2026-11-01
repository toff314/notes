#!/usr/bin/env python3
"""lab-02: arc-standard vs arc-eager 的「弧建立步号」，以及非投射的交叉检测。

arc-eager（§20.2.4）：RIGHTARC 把缓冲区首词压栈（故它仍可当中心词），
LEFTARC 弹出栈顶，REDUCE 弹出已完成任务的栈顶。
"""
import csv, json, os

ROOT = 0
SENTS = [
    ("Book the flight through Houston",
     ["book", "the", "flight", "through", "houston"],
     [(0, 1, "root"), (1, 3, "obj"), (3, 2, "det"), (3, 4, "nmod"), (4, 5, "pobj")]),
    ("Book me the morning flight",
     ["book", "me", "the", "morning", "flight"],
     [(0, 1, "root"), (1, 2, "iobj"), (1, 5, "obj"), (5, 3, "det"), (5, 4, "compound")]),
    ("I prefer the morning flight through Denver",
     ["I", "prefer", "the", "morning", "flight", "through", "denver"],
     [(0, 2, "root"), (2, 1, "nsubj"), (2, 5, "obj"), (5, 3, "det"),
      (5, 4, "compound"), (5, 6, "nmod"), (6, 7, "pobj")]),
]

NONPROJ = ("JetBlue canceled our flight this morning which was already late",
           ["JetBlue", "canceled", "our", "flight", "this", "morning",
            "which", "was", "already", "late"],
           [(0, 2, "root"), (2, 1, "nsubj"), (2, 4, "obj"), (4, 3, "det"),
            (2, 6, "obl"), (6, 5, "det"), (4, 10, "acl:relcl"), (10, 7, "nsubj"),
            (10, 8, "cop"), (10, 9, "adv")])


def deps_of(gold, w):
    return {d for (h, d, _) in gold if h == w}


def standard(tokens, gold):
    gm = {(h, d): l for (h, d, l) in gold}
    stack, buf, arcs, attached, when = [ROOT], list(range(1, len(tokens) + 1)), [], set(), {}
    for step in range(6 * len(tokens) + 5):
        if not buf and len(stack) == 1:
            break
        s1 = stack[-1]
        s2 = stack[-2] if len(stack) > 1 else None
        if s2 is not None and (s1, s2) in gm and s2 != ROOT and \
                all(d in attached for d in deps_of(gold, s2)):
            arcs.append((s1, s2, gm[(s1, s2)])); attached.add(s2)
            when[(s1, s2)] = step + 1; stack.pop(-2)
        elif s2 is not None and (s2, s1) in gm and all(d in attached for d in deps_of(gold, s1)):
            arcs.append((s2, s1, gm[(s2, s1)])); attached.add(s1)
            when[(s2, s1)] = step + 1; stack.pop()
        else:
            stack.append(buf.pop(0))
    return arcs, when, len(arcs) + len(tokens) - (len(stack) - 1) if False else None


def eager(tokens, gold):
    gm = {(h, d): l for (h, d, l) in gold}
    stack, buf, arcs, attached, when = [ROOT], list(range(1, len(tokens) + 1)), [], set(), {}
    steps = 0
    for step in range(8 * len(tokens) + 5):
        if not buf and len(stack) == 1:
            break
        s1 = stack[-1]
        b1 = buf[0] if buf else None
        done = False
        if b1 is not None and (s1, b1) in gm and b1 not in attached:
            arcs.append((s1, b1, gm[(s1, b1)])); attached.add(b1); when[(s1, b1)] = step + 1
            stack.append(buf.pop(0)); done = True
        elif b1 is not None and (b1, s1) in gm and s1 != ROOT and s1 not in attached and \
                all(d in attached for d in deps_of(gold, s1)):
            arcs.append((b1, s1, gm[(b1, s1)])); attached.add(s1); when[(b1, s1)] = step + 1
            stack.pop(); done = True
        if not done and s1 in attached and all(d in attached for d in deps_of(gold, s1)) \
                and (b1 is not None or len(stack) > 1):
            stack.pop(); done = True
        if not done:
            if not buf:
                # 收尾：缓冲区空时只能在栈内建左向弧
                if len(stack) > 1 and (stack[-2], s1) in gm:
                    arcs.append((stack[-2], s1, gm[(stack[-2], s1)])); attached.add(s1)
                    when[(stack[-2], s1)] = step + 1; stack.pop()
                else:
                    stack.pop()
            else:
                stack.append(buf.pop(0))
        steps += 1
    return arcs, when, steps


def crosses(a, b):
    (h1, d1), (h2, d2) = a, b
    lo1, hi1 = min(h1, d1), max(h1, d1)
    lo2, hi2 = min(h2, d2), max(h2, d2)
    if 0 in (h1, d1) or 0 in (h2, d2):
        return False
    return (lo1 < lo2 < hi1 < hi2) or (lo2 < lo1 < hi2 < hi1)


def main():
    os.makedirs("out", exist_ok=True)
    delay, compare = [], []
    for sent, toks, gold in SENTS:
        a_std, w_std, _ = standard(toks, gold)
        a_eag, w_eag, n_eag = eager(toks, gold)
        n_std = 2 * len(toks)
        compare.append([sent, len(toks), n_std, n_eag,
                        sorted(a_std) == sorted(gold), sorted(a_eag) == sorted(gold)])
        for arc in sorted(gold, key=lambda x: (x[1])):
            hs, ws = w_std.get((arc[0], arc[1]), ""), w_eag.get((arc[0], arc[1]), "")
            delay.append([sent, f"{arc[0]}->{arc[1]}", arc[2], hs, ws,
                          (int(hs) - int(ws)) if hs != "" and ws != "" else ""])
    with open("out/delay.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["sentence", "arc", "label", "step_standard", "step_eager", "delay_std_minus_eager"])
        w.writerows(delay)
    with open("out/compare.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["sentence", "n_words", "steps_standard", "steps_eager",
                    "gold_match_standard", "gold_match_eager"])
        w.writerows(compare)

    sent, toks, gold = NONPROJ
    pairs = [(a, b) for i, a in enumerate(gold) for b in gold[i + 1:]
             if crosses((a[0], a[1]), (b[0], b[1]))]
    info = {
        "sentence": sent,
        "n_words": len(toks),
        "n_arcs": len(gold),
        "crossing_pairs": [{"arc1": f"{a[0]}->{a[1]}", "arc2": f"{b[0]}->{b[1]}"} for a, b in pairs],
        "n_crossing_pairs": len(pairs),
        "projective": len(pairs) == 0,
        "implication": "转移式系统只能生成投射树：该句的交叉弧结构在 arc-standard / arc-eager 的合法转移序列中不可达。",
    }
    json.dump(info, open("out/crossing.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print("== lab-02 arc-standard vs arc-eager ==")
    for row in compare:
        print(f"  {row[0]:44s} n={row[1]} steps_std={row[2]:2d} steps_eager={row[3]:2d} "
              f"match_std={row[4]} match_eager={row[5]}")
    bf = [r for r in delay if r[1] == "1->3"]
    for r in bf:
        print(f"  弧 {r[1]}（{r[2]}）: standard 第 {r[3]} 步建，eager 第 {r[4]} 步建，提前 {r[5]} 步")
    print(f"  非投射句：{len(toks)} 词 / {len(gold)} 弧，交叉对 {len(pairs)} 个 -> projective={info['projective']}")
    for p in pairs:
        print(f"    交叉: {p[0][0]}->{p[0][1]} × {p[1][0]}->{p[1][1]}")


if __name__ == "__main__":
    main()
