# 自定义 HTTP 客户端工厂示例

本示例演示如何使用 `MCPServerStreamableHttp` 中新的 `httpx_client_factory` 参数来配置 MCP StreamableHTTP 连接的自定义 HTTP 客户端行为。

## 演示功能

- **自定义 SSL 配置**：配置 SSL 证书和验证设置
- **自定义请求头**：为所有 HTTP 请求添加自定义请求头
- **自定义超时**：为请求设置自定义超时值
- **代理配置**：配置 HTTP 代理设置
- **自定义重试逻辑**：设置自定义重试行为（通过 httpx 配置）

## 运行示例

1. 确保已安装 `uv`：https://docs.astral.sh/uv/getting-started/installation/

2. 运行示例：
   ```bash
   cd examples/mcp/streamablehttp_custom_client_example
   uv run main.py
   ```

## 代码示例

### 基础自定义客户端

```python
import httpx
from agents.mcp import MCPServerStreamableHttp

def create_custom_http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        verify=False,  # Disable SSL verification for testing
        timeout=httpx.Timeout(60.0, read=120.0),
        headers={"X-Custom-Client": "my-app"},
    )

async with MCPServerStreamableHttp(
    name="Custom Client Server",
    params={
        "url": "http://localhost:8000/mcp",
        "httpx_client_factory": create_custom_http_client,
    },
) as server:
    # Use the server...
```

## 使用场景

- **企业网络**：为企业环境配置代理设置
- **SSL/TLS 要求**：使用自定义 SSL 证书进行安全连接
- **自定义认证**：为 API 认证添加自定义请求头
- **网络优化**：配置超时和连接池
- **调试**：在开发环境中禁用 SSL 验证

## 优势

- **灵活性**：配置 HTTP 客户端行为以匹配您的网络要求
- **安全性**：使用自定义 SSL 证书和认证方法
- **性能**：针对您的使用场景优化超时和连接设置
- **兼容性**：兼容企业代理和网络限制
