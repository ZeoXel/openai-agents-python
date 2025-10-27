# Realtime Twilio 集成

本示例演示如何使用 Twilio 的媒体流将 OpenAI Realtime API 连接到电话呼叫。服务器处理来电并在 Twilio 和 OpenAI Realtime API 之间流式传输音频,实现通过电话与 AI 代理进行实时语音对话。

## 前置要求

-   Python 3.9+
-   具有 [Realtime API](https://platform.openai.com/docs/guides/realtime) 访问权限的 OpenAI API 密钥
-   拥有电话号码的 [Twilio](https://www.twilio.com/docs/voice) 账户
-   隧道服务(如 [ngrok](https://ngrok.com/))以公开您的本地服务器

## 设置

1. **启动服务器:**

    ```bash
    uv run server.py
    ```

    服务器将默认在 8000 端口启动。

2. **公开暴露服务器,例如通过 ngrok:**

    ```bash
    ngrok http 8000
    ```

    记下公共 URL(例如 `https://abc123.ngrok.io`)

3. **配置您的 Twilio 电话号码:**
    - 登录您的 Twilio 控制台
    - 选择您的电话号码
    - 将来电的 webhook URL 设置为: `https://your-ngrok-url.ngrok.io/incoming-call`
    - 将 HTTP 方法设置为 POST

## 使用方法

1. 拨打您的 Twilio 电话号码
2. 您将听到:"Hello! You're now connected to an AI assistant. You can start talking!"
3. 开始说话 - AI 将实时响应
4. 助手可以访问天气信息和当前时间等工具

## 工作原理

1. **来电**: 当有人拨打您的 Twilio 号码时,Twilio 会向 `/incoming-call` 发送请求
2. **TwiML 响应**: 服务器返回 TwiML,它将:
    - 播放问候消息
    - 将呼叫连接到 `/media-stream` 的 WebSocket 流
3. **WebSocket 连接**: Twilio 建立用于双向音频流传输的 WebSocket 连接
4. **传输层**: `TwilioRealtimeTransportLayer` 类负责 WebSocket 消息处理:
    - 在初始握手后接管 Twilio WebSocket
    - 运行自己的消息循环来处理所有 Twilio 消息
    - 处理 Twilio 和 OpenAI 之间的协议差异
    - 自动设置 G.711 μ-law 音频格式以兼容 Twilio
    - 管理音频块跟踪以支持中断
    - 包装 OpenAI 实时模型而不是子类化它
5. **音频处理**:
    - 来自呼叫者的音频经过 base64 解码后发送到 OpenAI Realtime API
    - 来自 OpenAI 的音频响应经过 base64 编码后发送回 Twilio
    - Twilio 向呼叫者播放音频

## 配置

-   **端口**: 设置 `PORT` 环境变量(默认: 8000)
-   **OpenAI API 密钥**: 设置 `OPENAI_API_KEY` 环境变量
-   **代理指令**: 修改 `server.py` 中的 `RealtimeAgent` 配置
-   **工具**: 在 `server.py` 中添加或修改函数工具

## 故障排除

-   **WebSocket 连接问题**: 确保您的 ngrok URL 正确且可公开访问
-   **音频质量**: Twilio 以 8kHz 的 mulaw 格式流式传输音频,这可能会影响质量
-   **延迟**: Twilio、您的服务器和 OpenAI 之间的网络延迟会影响响应时间
-   **日志**: 检查控制台输出以获取详细的连接和错误日志

## 架构

```
Phone Call → Twilio → WebSocket → TwilioRealtimeTransportLayer → OpenAI Realtime API
                                              ↓
                                      RealtimeAgent with Tools
                                              ↓
                           Audio Response → Twilio → Phone Call
```

`TwilioRealtimeTransportLayer` 充当 Twilio 媒体流和 OpenAI Realtime API 之间的桥梁,处理协议差异和音频格式转换。它包装了 OpenAI 实时模型,为 Twilio 集成提供简洁的接口。
