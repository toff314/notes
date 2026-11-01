# lab-01　CNF 转换 + CKY 填表 + 枚举全部解析树

对应行动：`actions.md` 第 1 条。对应书中 §19.4（CNF 与弱等价）、§19.6.1（CNF 转换三步）、§19.6.2–19.6.3（CKY 识别与分析）。

## 怎么跑

```bash
cd labs/lab-01
python3 parse_l1.py
```

依赖：纯标准库（共用工具在 `../cfgkit.py`）。<1 秒。

## 输入

- 文法：书中图 19.8 的 L1 文法（16 条非词汇规则 + 36 条词汇规则），写死在 `../cfgkit.py` 的 `L1_RULES` 与 `LEXICON` 中，外加 §19.5 例句所需的 5 个词（elephant、pajamas、shot、an、my）。
- 例句：`book the flight through houston`（§19.6.2 图 19.11 的例句）。

## 产物

| 文件 | 内容 |
|---|---|
| `out/cnf_rules.csv` | 转换后的 CNF 规则（64 条，含二元与词汇规则） |
| `out/parse_table.csv` | 填好的上三角表（15 个 cell，每格的非终结符集合） |
| `out/parses.txt` | 回溯指针枚举出的 3 棵解析树（含哑节点的括号记法） |
| `out/unbinarized.txt` | 折叠哑节点后的 3 棵树（恢复原始 L1 文法形状） |
| `out/equiv.csv` | 20 个句子在「转换前/转换后」的成员判定 |
| `out/summary.json` | 关键计数（规则数、cell 数、分析数、一致性比例） |

## 关键输出（真实运行）

```json
{
  "sentence": "book the flight through houston",
  "n_words": 5,
  "n_cnf_rules": 64,
  "n_cells_filled": 11,
  "n_cells_total": 15,
  "n_parses": 3,
  "n_parses_enumerated": 3,
  "cnf_ok": true,
  "equiv_agree": "20/20",
  "dummy_terminals": {},
  "root_cell": ["S", "VP"]
}
```

3 棵解析树（unbinarized 后）：

```
(S (Verb book) (NP (Det the) (Nominal (Nominal flight) (PP (Preposition through) (NP houston)))))
(S (Verb book) (X3 (NP (Det the) (Nominal flight)) (PP (Preposition through) (NP houston))))
(S (VP (Verb book) (NP (Det the) (Nominal flight))) (PP (Preposition through) (NP houston)))
```

等价性验证（20 句，节选）：

| 句子 | 转换前 | 转换后 |
|---|---|---|
| book the flight through houston | True | True |
| i prefer a morning flight | False | False |
| does houston include the meal | True | True |
| i shot an elephant in my pajamas | True | True |
| she book the money | True | True |
| the flight from houston to united | False | False |
| … | … | … |
| **合计** | — | **20/20 一致** |

## 结论

1. **CNF 转换正确**：64 条 CNF 规则全部满足「右部两个非终结符或一个终结符」的形状断言（`cnf_ok=True`）；20 个测试句在转换前后成员判定 20/20 一致，验证了弱等价（§19.4）。
2. **CKY 填表正确**：5 词例句的 15 个上三角 cell 填了 11 个；cell [0,5] 含 {S, VP}，说明该句既可分析为完整句子（S），也可分析为动词短语（VP）——这是因为 L1 文法中 S → VP 是一条合法规则。
3. **枚举出 3 种分析**：与书中图 19.14 的描述一致——PP 修饰 the flight（Nominal→Nominal PP）、PP 修饰 the booking（VP→Verb NP PP 的第二个论元，经 X3 间接表示）、PP 作为 VP→VP PP 的右附加。
4. **单元产生式消除的副作用**：unbinarized 后的第 3 棵树显示 `(S (VP (Verb book) (NP ...)) (PP ...))`——S 直接展开为 VP + PP，这是因为 S → VP 与 VP → VP PP 的单元链被消除后，S 直接继承了 VP → VP PP 的右部。这正是 §19.6.4 说的「单元产生式消除会使终结符在最终得到的树中被提升到相当高的层次」。

## 反思

我原以为 CNF 转换只是「换个写法」，跑完才发现单元产生式消除会把词性提升到 VP 甚至 S——同一个词在表里同时是 Verb、VP、S。这不是实现 bug，而是 CNF 转换的固有结果（§19.6.1）。后处理时必须用 `unbinarize` 把哑节点折叠掉，否则树里会多出 X1/X2 这类没人认识的非终结符。

另一个意外是 `root_cell` 里同时有 S 和 VP。起初以为多算了一种分析，检查后发现 L1 文法中 S → VP 是一条合法规则，所以 VP 本身就是 S 的一种合法展开。这说明 CKY 表里的非终结符集合不是「句子的成分」，而是「能覆盖整个输入的合法范畴」——成分分析需要回溯指针才能确定层级。
