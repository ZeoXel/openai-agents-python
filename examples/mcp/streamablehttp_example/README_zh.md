# MCP 流式 HTTP 示例

此示例使用 [server.py](server.py) 中的本地流式 HTTP 服务器。

通过以下命令运行示例：

```
uv run python examples/mcp/streamablehttp_example/main.py
```

## 详细说明

此示例使用 `agents.mcp` 中的 `MCPServerStreamableHttp` 类。服务器在 `https://localhost:8000/mcp` 地址的子进程中运行。
