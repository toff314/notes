# 《Claude Code 工程化实战》— 5 分钟速览

## 如果你只记住一件事
**Claude Code 不是工具，是 Harness（智能体编排框架）**——它把"只会输出文本"的模型变成"能行动"的 Agent；而多 Agent 的复杂度不靠更聪明的模型解决，靠更好的结构消化。

## 3 个核心框架
1. **Agentic Loop**（hot-02/03）：推理→工具调用→结果回注→继续推理。Claude Code 的引擎叫 QueryEngine，用 generator 模式实现，工具权限门控每个调用。
2. **四模式+决策树**（04）：多 Agent 只有四种模式——Sub-Agents（隔离）、Skills（渐进加载）、Handoffs（状态切换）、Router（并行分发）。铁律：先单 Agent，遇瓶颈再升级；先加工具，再加 Agent。
3. **控制流位置**（hot-05）：编排逻辑放哪——Claude 上下文里（Sub-Agent，灵活不可重复）还是脚本里（Workflow，可重复可并发）。流程稳定了才值得搬进 Workflow。

## 5 个可操作方法
1. **子代理隔离高噪声**（06）：命令输出>50 行且你只关心<10 行 → 配子代理消化，输出格式按"结果→细节→建议"三层设计。
2. **Stop Hook 质量门控**（16）：`continue: true` 让"测试不过就不让 Claude 停"，配 `stop_hook_active` 防死循环——把检查变成交付前置条件。
3. **Skill 渐进式披露**（11）：SKILL.md 只做路由（Quick Reference 表格），公式放 reference/，脚本放 scripts/——用最少 token 换最高质量。
4. **精确授权**（10/15）：`allowed-tools: Bash(git commit:*)` 而非 `Bash(*)`；PreToolUse 正则拦截危险命令，exit 2 拒绝。
5. **CI 最小权限**（19）：无人值守时 `--allowedTools` 白名单 + `--max-turns` 控成本 + 权限配置兜底——AI 不会主动判断安全，责任全在配置端。

## 1 个反直觉观点
**Harness 本身就是 IP，比模型更值钱**（hot-03）：Anthropic 用假工具注入污染竞品训练数据（反蒸馏）、对推理中间过程加密封签名——工具定义和系统提示词的商业价值被提升到与模型同级。泄露后社区 2 小时复刻出代码结构，却复刻不了"模型-Harness 共同进化"的提示词知识。上下文工程（Git 注入/去重/大结果落盘/LSP）才是真正的秘密武器，不是模型。

## 值不值得花时间？
**值** —— 如果你是 Claude Code 重度用户且想从"会用"升级到"会建"：04（多 Agent 决策树）、16（质量门控）、hot-03（源码实证）三讲就值回票价。**但**：Agent Teams/Workflow 是实验功能，Skills 生态数据有出版时点性；纯想看文档的人直接看官方文档更快。
