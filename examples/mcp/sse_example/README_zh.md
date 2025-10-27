# MCP SSE 示例

此示例使用 [server.py](server.py) 中的本地 SSE 服务器。

运行示例：

```
uv run python examples/mcp/sse_example/main.py
```

## 详细说明

该示例使用 `agents.mcp` 中的 `MCPServerSse` 类。服务器在子进程中运行于 `https://localhost:8000/sse`。
