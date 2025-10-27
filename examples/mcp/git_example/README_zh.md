# MCP Git 示例

本示例使用通过 `uvx` 在本地运行的 [git MCP 服务器](https://github.com/modelcontextprotocol/servers/tree/main/src/git)。

运行方式：

```
uv run python examples/mcp/git_example/main.py
```

## 详细说明

本示例使用 `agents.mcp` 中的 `MCPServerStdio` 类，执行命令：

```bash
uvx mcp-server-git
```

在运行代理之前，会提示用户提供本地 git 仓库的目录路径。使用该路径，代理可以调用 Git MCP 工具（如 `git_log`）来检查 git 提交日志。

底层实现原理：

1. 服务器在子进程中启动，并暴露一系列工具，如 `git_log()`
2. 我们通过 `mcp_agents` 将服务器实例添加到代理中
3. 每次代理运行时，我们通过 `server.list_tools()` 调用 MCP 服务器获取工具列表。结果会被缓存
4. 如果 LLM 选择使用 MCP 工具，我们通过 `server.run_tool()` 调用 MCP 服务器来运行该工具
