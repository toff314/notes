# 16 Stop Hook：把验收变成交付前置条件

**结论**：PreToolUse 是入口安检，PostToolUse 是过程质检，Stop Hook 是出厂终检。它让 Claude"检查通过才算做完"，而不是"做完再检查"。

**证据**：`continue: true` 把测试失败反馈回模型并强制继续；脚本按 package.json / pyproject.toml / go.mod / Cargo.toml 自动识别项目；输出截断 50 行控制噪声；`stop_hook_active` 防死循环；Prompt 型 Hook 用另一个模型做二审。

**关系**：依赖 15 的事件体系，与 20 的权限规则互补——一个管"做完没有"，一个管"能做不能做"。

**批判**：脚本依赖 jq 等外部工具，课程未充分强调环境前提；Prompt 型 Hook 会漏检/误报，只能当第二层防线。
