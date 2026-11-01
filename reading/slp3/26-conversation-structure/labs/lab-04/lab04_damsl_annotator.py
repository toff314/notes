#!/usr/bin/env python3
"""lab-04 DAMSL 对话行为标注实验（对应 §26.2）。

对图 26.1 前 12 个话轮做 DAMSL 前向/后向功能标注，
与书中图 26.5 的标注对照，计算一致率。
"""
import csv
import os

# 我的简易标注（前向, 后向）
MY_ANNOTATION = {
    "C1":  ("STATEMENT", "-"),
    "A2":  ("INFO-REQUEST", "ACK"),
    "C3":  ("STATEMENT", "ANSWER"),
    "A4":  ("INFO-REQUEST", "ACK"),
    "C5":  ("STATEMENT", "ANSWER"),
    "A6":  ("INFO-REQUEST", "ACK"),
    "C7":  ("CHECK", "HOLD"),
    "A8":  ("ACCEPT", "ACK"),
    "C9":  ("INFO-REQUEST", "-"),
    "A10": ("STATEMENT", "ANSWER"),
    "C11": ("ACCEPT", "ACK"),
    "A12": ("CHECK", "ACK"),
}

# 书中图 26.5 的标注（前向, 后向）— 按 raw 文本转录
BOOK_ANNOTATION = {
    "C1":  ("assert", "-"),
    "A2":  ("info-req", "ack"),
    "C3":  ("assert", "answer"),
    "A4":  ("info-req", "ack"),
    "C5":  ("assert", "answer"),
    "A6":  ("info-req", "ack"),
    "C7":  ("check", "hold"),
    "A8":  ("accept", "ack"),
    "C9":  ("info-req", "-"),
    "A10": ("assert", "answer"),
    "C11": ("accept", "ack"),
    "A12": ("check", "ack"),
}

# DAMSL 标签映射：书中粗粒度标签 → DAMSL 细粒度
LABEL_MAP = {
    "assert": "STATEMENT",
    "info-req": "INFO-REQUEST",
    "answer": "ANSWER",
    "ack": "ACK",
    "accept": "ACCEPT",
    "check": "CHECK",
    "hold": "HOLD",
}


def main():
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(out_dir, exist_ok=True)

    rows = []
    agree = 0
    total = 0
    for tid, (fwd_mine, bwd_mine) in MY_ANNOTATION.items():
        fwd_book_raw, bwd_book_raw = BOOK_ANNOTATION[tid]
        fwd_book = LABEL_MAP.get(fwd_book_raw, fwd_book_raw.upper())
        bwd_book = LABEL_MAP.get(bwd_book_raw, bwd_book_raw.upper())

        fwd_ok = fwd_mine == fwd_book
        bwd_ok = bwd_mine == bwd_book
        agree += int(fwd_ok) + int(bwd_ok)
        total += 2
        rows.append({
            "turn": tid,
            "fwd_mine": fwd_mine, "fwd_book": fwd_book, "fwd_ok": "✓" if fwd_ok else "✗",
            "bwd_mine": bwd_mine, "bwd_book": bwd_book, "bwd_ok": "✓" if bwd_ok else "✗",
        })

    agreement = agree / total
    print(f"agreement: {agree}/{total} = {agreement:.4f}")
    for r in rows:
        flag = "" if (r["fwd_ok"] == "✓" and r["bwd_ok"] == "✓") else "  ← 分歧"
        print(f"{r['turn']}: fwd {r['fwd_mine']}/{r['fwd_book']} {r['fwd_ok']}  bwd {r['bwd_mine']}/{r['bwd_book']} {r['bwd_ok']}{flag}")

    out_path = os.path.join(out_dir, "damsl_agreement.csv")
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["turn", "fwd_mine", "fwd_book", "fwd_ok", "bwd_mine", "bwd_book", "bwd_ok"])
        w.writeheader()
        w.writerows(rows)

    print(f"saved: {out_path}")


if __name__ == "__main__":
    main()
