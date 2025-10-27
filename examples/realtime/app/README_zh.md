# Realtime 演示应用

一个基于 Web 的实时语音助手演示，采用 FastAPI 后端和 HTML/JS 前端。

## 安装

安装所需依赖：

```bash
uv add fastapi uvicorn websockets
```

## 使用

使用单个命令启动应用：

```bash
cd examples/realtime/app && uv run python server.py
```

然后在浏览器中打开：http://localhost:8000

## 自定义

要使用相同的 UI 配合您自己的代理，请编辑 `agent.py` 并确保 get_starting_agent() 返回适合您用例的正确起始代理。

## 如何使用

1. 点击 **Connect** 建立实时会话
2. 音频捕获会自动启动 - 只需自然说话即可
3. 点击 **Mic On/Off** 按钮来静音/取消静音您的麦克风
4. 要发送图像，输入可选提示并点击 **🖼️ Send Image**（选择文件）
5. 在左侧窗格中观察对话展开（显示图像缩略图）
6. 在右侧窗格中监控原始事件（点击展开/折叠）
7. 完成后点击 **Disconnect**

## 架构

-   **后端**：FastAPI 服务器，使用 WebSocket 连接进行实时通信
-   **会话管理**：每个连接都会获得与 OpenAI Realtime API 的唯一会话
-   **图像输入**：UI 上传图像，服务器转发一个包含 `input_image`（以及可选的 `input_text`）的
    `conversation.item.create` 事件，然后发送 `response.create` 来启动模型响应。消息窗格
    为 `input_image` 内容渲染图像气泡。
-   **音频处理**：24kHz 单声道音频捕获和播放
-   **事件处理**：完整的事件流处理与转录生成
-   **前端**：原生 JavaScript 配合简洁、响应式的 CSS

该演示展示了使用 OpenAI Agents SDK 构建实时语音应用的核心模式。
