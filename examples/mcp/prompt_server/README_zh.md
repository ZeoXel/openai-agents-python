# MCP 提示服务器示例

此示例使用 [server.py](server.py) 中的本地 MCP 提示服务器。

通过以下命令运行示例：

```
uv run python examples/mcp/prompt_server/main.py
```

## 详细说明

此示例使用 `agents.mcp` 中的 `MCPServerStreamableHttp` 类。服务器在 `http://localhost:8000/mcp` 的子进程中运行，并提供用户控制的提示来生成智能体指令。

服务器公开了诸如 `generate_code_review_instructions` 之类的提示，这些提示接受诸如关注领域和编程语言等参数。智能体调用这些提示，根据用户提供的参数动态生成其系统指令。

## 工作流程

此示例演示了两个关键功能：

1. **`show_available_prompts`** - 列出 MCP 服务器上所有可用的提示，向用户展示他们可以选择的提示。这演示了 MCP 提示的发现功能。

2. **`demo_code_review`** - 展示完整的用户控制提示工作流程：
   - 使用特定参数调用 `generate_code_review_instructions`（关注点："security vulnerabilities"，语言："python"）
   - 使用生成的指令创建具有专门代码审查能力的智能体
   - 针对存在漏洞的示例代码运行智能体（通过 `os.system` 的命令注入）
   - 智能体使用可用工具分析代码并提供以安全为重点的反馈

这种模式允许用户通过 MCP 提示动态配置智能体行为，而不是使用硬编码的指令。
