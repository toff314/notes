#!/usr/bin/env python3
"""lab-01: arc-standard 转移系统 + 训练神谕（§20.2 / §20.2.1）。

三操作（按原文约定）：
  LEFTARC  栈顶 S1 作中心词、第二个词 S2 作依存词，弹出 S2
  RIGHTARC 第二个词 S2 作中心词、栈顶 S1 作依存词，弹出 S1
  SHIFT    缓冲区首词压栈
"""
import csv, json, os

ROOT = 0
SENTS = [
    ("Book me the morning flight",
     ["book", "me", "the", "morning", "flight"],
     [(0, 1, "root"), (1, 2, "iobj"), (1, 5, "obj"), (5, 3, "det"), (5, 4, "compound")]),
    ("Book the flight through Houston",
     ["book", "the", "flight", "through", "houston"],
     [(0, 1, "root"), (1, 3, "obj"), (3, 2, "det"), (3, 4, "nmod"), (4, 5, "pobj")]),
    ("I prefer the morning flight through Denver",
     ["I", "prefer", "the", "morning", "flight", "through", "denver"],
     [(0, 2, "root"), (2, 1, "nsubj"), (2, 5, "obj"), (5, 3, "det"),
      (5, 4, "compound"), (5, 6, "nmod"), (6, 7, "pobj")]),
    ("United canceled the morning flights to Houston",
     ["united", "canceled", "the", "morning", "flights", "to", "houston"],
     [(0, 2, "root"), (2, 1, "nsubj"), (2, 5, "obj"), (5, 3, "det"),
      (5, 4, "compound"), (5, 6, "nmod"), (6, 7, "pobj")]),
]


def deps_of(gold, w):
    return {d for (h, d, _) in gold if h == w}


def parse_standard(tokens, gold):
    gm = {(h, d): l for (h, d, l) in gold}
    stack, buf = [ROOT], list(range(1, len(tokens) + 1))
    arcs, attached, trace = [], set(), []
    for step in range(4 * len(tokens) + 5):
        if not buf and len(stack) == 1:
            break
        s1 = stack[-1]
        s2 = stack[-2] if len(stack) > 1 else None
        act = None
        if s2 is not None:
            # LEFTARC: S1 中心词, S2 依存词；S2 离开栈，须先接完它的孩子
            if (s1, s2) in gm and s2 != ROOT and all(d in attached for d in deps_of(gold, s2)):
                act = ("LEFTARC", gm[(s1, s2)], s2, (s1, s2))
            # RIGHTARC: S2 中心词, S1 依存词；S1 离开栈
            elif (s2, s1) in gm and all(d in attached for d in deps_of(gold, s1)):
                act = ("RIGHTARC", gm[(s2, s1)], s1, (s2, s1))
        if act is None:
            act = ("SHIFT", "", None, None)
        name, lab, dep, arc = act
        if name == "SHIFT":
            stack.append(buf.pop(0))
        elif name == "LEFTARC":
            arcs.append((s1, s2, lab)); attached.add(s2); stack.pop(-2)
        else:
            arcs.append((s2, s1, lab)); attached.add(s1); stack.pop()
        trace.append({
            "step": step,
            "stack": " ".join(tokens[i - 1] for i in stack),
            "buffer": " ".join(tokens[i - 1] for i in buf),
            "action": name + (f"({lab})" if lab else ""),
            "arc": f"{tokens[arc[0]-1] if arc[0] else 'ROOT'}->{tokens[arc[1]-1]}({lab})" if arc else "",
            "arc_pair": arc,
        })
    return arcs, trace


def main():
    os.makedirs("out", exist_ok=True)
    rows, results, n_ok = [], [], 0
    total_actions = 0
    per_sent_steps = []
    for sent, toks, gold in SENTS:
        arcs, trace = parse_standard(toks, gold)
        ok = sorted(arcs) == sorted(gold)
        n_ok += ok
        total_actions += len(trace)
        per_sent_steps.append(len(trace))
        for t in trace:
            rows.append([sent, t["step"], t["stack"], t["buffer"], t["action"], t["arc"]])
        results.append([sent, len(toks), len(gold), len(trace), len(arcs), ok])
    with open("out/transitions.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["sentence", "step", "stack", "buffer", "action", "added_arc"])
        w.writerows(rows)
    with open("out/parse_results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["sentence", "n_words", "n_gold_arcs", "n_actions",
                                       "n_recovered_arcs", "exact_match"])
        w.writerows(results)
    summary = {
        "gold_exact_match": f"{n_ok}/{len(SENTS)}",
        "total_actions": total_actions,
        "actions_per_sentence": per_sent_steps,
        "check_actions_eq_2n": all(s == 2 * len(SENTS[i][1]) for i, s in enumerate(per_sent_steps)),
        "note": "每句动作数 = 词数(全 SHIFT) + 弧数(含 root 弧，每弧一次归约) = 2n",
    }
    json.dump(summary, open("out/summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("== lab-01 arc-standard + oracle ==")
    for sent, n, ng, na, nr, ok in results:
        print(f"  {sent:46s} n={n} arcs={ng:2d} actions={na:2d} recovered={nr:2d} exact={ok}")
    print(f"  exact match: {n_ok}/{len(SENTS)}  total actions: {total_actions}")
    print(f"  actions == 2n for all sentences: {summary['check_actions_eq_2n']}")


if __name__ == "__main__":
    main()
