#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""lab-05：中文时间表达式归一化（最小规则版）

对应 §21.7.2「时间归一化」。书中说当前主流方法以规则为主
（Chang & Manning 2012, Strötgen & Gertz 2013），把识别到的
时间表达式映射到 ISO 8601 的 VALUE 上（YYYY-MM-DD / YYYY-Wnn /
PnD / HH:MM:SS / PnY …）。

这里实现一个针对中文新闻小语料的最小规则归一化器，覆盖三类：
  - 绝对日期：「2023年10月25日」「2023-10-25」「2023/10/25」
  - 相对日期：「今天」「昨天」「明天」「上周」「下周」「本周」「X天前」「X天后」
  - 持续时间：「三周」「两天」「五年」「6小时」「30分钟」

时间锚：语料所有句共享一个文档日期 DOC_DATE（模拟「日期行」）。
"""
import json, os, re
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

# 文档时间锚（模拟新闻的日期行 dateline）
DOC_DATE = date(2024, 6, 15)  # 2024-06-15 周六

CN_NUM = {"一": 1, "两": 2, "二": 2, "三": 3, "四": 4, "五": 5,
          "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}

UNIT_DAY = {"天", "日", "号"}
UNIT_WEEK = {"周", "星期", "礼拜"}
UNIT_MONTH = {"月"}
UNIT_YEAR = {"年"}
UNIT_HOUR = {"小时", "钟头"}
UNIT_MIN = {"分钟", "分"}
UNIT_SEC = {"秒", "秒钟"}


def cn_to_int(s):
    """中文数字 -> int；返回 None 表示失败"""
    if not s:
        return None
    if s.isdigit():
        return int(s)
    # 「十」「十一」「二十」
    if s == "十":
        return 10
    if s.startswith("十"):
        return 10 + CN_NUM.get(s[1], 0)
    if s.endswith("十"):
        return CN_NUM.get(s[0], 0) * 10
    if "十" in s:
        a, b = s.split("十", 1)
        return CN_NUM.get(a, 1) * 10 + CN_NUM.get(b, 0)
    return CN_NUM.get(s)


# ---------------------------------------------------------------------------
# 三类模式
# ---------------------------------------------------------------------------

# 绝对日期：2023年10月25日 / 2023-10-25 / 2023/10/25
PAT_ABS = re.compile(
    r"(\d{4})\s*[年\-/]\s*(\d{1,2})\s*[月\-/]\s*(\d{1,2})\s*[日号]?"
)

# 相对日期
PAT_TODAY = re.compile(r"^(今天|今日|今)$")
PAT_YESTERDAY = re.compile(r"^(昨天|昨日|昨)$")
PAT_TOMORROW = re.compile(r"^(明天|明日|明)$")
PAT_THIS_WEEK = re.compile(r"^(本周|这周|这一周)$")
PAT_LAST_WEEK = re.compile(r"^(上周|上一周|上星期|上周)$")
PAT_NEXT_WEEK = re.compile(r"^(下周|下一周|下星期)$")
# X天前 / X天后 / X周前 / X周后 …
PAT_OFFSET = re.compile(
    r"^([零一二两三四五六七八九十\d]+)\s*"
    r"(天|日|周|星期|礼拜|个月|月|年|小时|钟头|分钟|分|秒|秒钟)"
    r"(前|之前|以前|后|之后|以后)$"
)
# 星期X（本/上/下）
PAT_WEEKDAY = re.compile(r"^(本|上|下)?\s*周\s*([一二三四五六日天])$")

# 持续时间（不带前/后）：三周 / 两天 / 五年 / 6小时 / 30分钟
PAT_DURATION = re.compile(
    r"^([零一二两三四五六七八九十\d]+)\s*"
    r"(天|日|周|星期|礼拜|个月|月|年|小时|钟头|分钟|分|秒|秒钟)$"
)


def iso_week(d: date) -> str:
    """返回 ISO 周 'YYYY-Wnn'"""
    iso = d.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def monday_of_week(d: date) -> date:
    """返回 d 所在 ISO 周的周一"""
    return d - timedelta(days=d.isoweekday() - 1)


def normalize(expr: str):
    """把中文时间表达式归一化。返回 (value, kind) 或 (None, 'unmatched')。"""
    expr = expr.strip()
    m = PAT_ABS.match(expr)
    if m:
        y, mo, dd = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            d = date(y, mo, dd)
        except ValueError:
            return None, "invalid"
        return d.isoformat(), "date"

    if PAT_TODAY.match(expr):
        return DOC_DATE.isoformat(), "date"
    if PAT_YESTERDAY.match(expr):
        return (DOC_DATE - timedelta(days=1)).isoformat(), "date"
    if PAT_TOMORROW.match(expr):
        return (DOC_DATE + timedelta(days=1)).isoformat(), "date"
    if PAT_THIS_WEEK.match(expr):
        return iso_week(DOC_DATE), "week"
    if PAT_LAST_WEEK.match(expr):
        return iso_week(DOC_DATE - timedelta(days=7)), "week"
    if PAT_NEXT_WEEK.match(expr):
        return iso_week(DOC_DATE + timedelta(days=7)), "week"

    m = PAT_OFFSET.match(expr)
    if m:
        n = cn_to_int(m.group(1))
        unit = m.group(2)
        dirn = m.group(3)
        if n is None:
            return None, "unmatched"
        sign = -1 if dirn in {"前", "之前", "以前"} else 1
        if unit in UNIT_DAY:
            d = DOC_DATE + timedelta(days=sign * n)
            return d.isoformat(), "date"
        if unit in UNIT_WEEK:
            return iso_week(DOC_DATE + timedelta(days=sign * 7 * n)), "week"
        if unit in UNIT_MONTH:
            # 简化：按 30 天算（不处理真实月份天数）
            return f"P{sign * n}M", "duration"  # 简写
        if unit in UNIT_YEAR:
            return f"P{sign * n}Y", "duration"
        if unit in UNIT_HOUR:
            return f"PT{sign * n}H", "duration"
        if unit in UNIT_MIN:
            return f"PT{sign * n}M", "duration"
        if unit in UNIT_SEC:
            return f"PT{sign * n}S", "duration"

    m = PAT_WEEKDAY.match(expr)
    if m:
        prefix = m.group(1) or "本"
        wd_cn = m.group(2)
        wd = 7 if wd_cn in {"日", "天"} else CN_NUM.get(wd_cn)
        if wd is None:
            return None, "unmatched"
        base_monday = monday_of_week(DOC_DATE)
        if prefix == "上":
            base_monday -= timedelta(days=7)
        elif prefix == "下":
            base_monday += timedelta(days=7)
        target = base_monday + timedelta(days=wd - 1)
        return target.isoformat(), "date"

    m = PAT_DURATION.match(expr)
    if m:
        n = cn_to_int(m.group(1))
        unit = m.group(2)
        if n is None:
            return None, "unmatched"
        if unit in UNIT_DAY:
            return f"P{n}D", "duration"
        if unit in UNIT_WEEK:
            return f"P{n}W", "duration"
        if unit in UNIT_MONTH:
            return f"P{n}M", "duration"
        if unit in UNIT_YEAR:
            return f"P{n}Y", "duration"
        if unit in UNIT_HOUR:
            return f"PT{n}H", "duration"
        if unit in UNIT_MIN:
            return f"PT{n}M", "duration"
        if unit in UNIT_SEC:
            return f"PT{n}S", "duration"

    return None, "unmatched"


# ---------------------------------------------------------------------------
# 测试用例：14 条中文时间表达式 + 1 条干扰
# ---------------------------------------------------------------------------
CASES = [
    ("2023年10月25日",                "date"),      # 绝对
    ("2024-01-01",                    "date"),
    ("2024/6/1",                      "date"),
    ("今天",                          "date"),      # 相对：锚点
    ("昨天",                          "date"),
    ("明天",                          "date"),
    ("本周",                          "week"),
    ("上周",                          "week"),      # 对应书中 2007-W26 例子
    ("下周",                          "week"),
    ("三天前",                        "date"),
    ("两周后",                        "week"),
    ("周三",                          "date"),      # 本周三
    ("上周五",                        "date"),
    ("三周",                          "duration"),  # 对应书中 two weeks → P2W
    ("两天",                          "duration"),
    ("五年",                          "duration"),
    ("6小时",                         "duration"),
    ("30分钟",                        "duration"),
    ("苹果",                          "unmatched"), # 干扰：非时间词
]


def main():
    print("=" * 70)
    print(f"Temporal normalization (doc anchor = {DOC_DATE.isoformat()})")
    print("=" * 70)
    rows = []
    n_ok, n_bad = 0, 0
    for expr, expected_kind in CASES:
        value, kind = normalize(expr)
        ok = (kind == expected_kind) and (value is not None or kind in {"unmatched", "invalid"})
        if kind == "unmatched" and expected_kind == "unmatched":
            ok = True
        if ok:
            n_ok += 1
        else:
            n_bad += 1
        rows.append({
            "expr": expr, "expected": expected_kind,
            "value": value, "kind": kind, "ok": ok,
        })
        mark = "✓" if ok else "✗"
        print(f"{mark}  {expr:20s} -> {str(value):12s} ({kind})")

    print()
    print(f"Total: {len(CASES)}  OK: {n_ok}  FAIL: {n_bad}")
    print(f"Accuracy (kind match): {n_ok / len(CASES):.4f}")

    with open(os.path.join(OUT, "results.json"), "w", encoding="utf-8") as f:
        json.dump({
            "doc_date": DOC_DATE.isoformat(),
            "n_cases": len(CASES),
            "n_ok": n_ok,
            "n_bad": n_bad,
            "accuracy": round(n_ok / len(CASES), 4),
            "rows": rows,
        }, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
