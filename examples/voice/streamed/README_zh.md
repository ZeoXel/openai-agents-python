# 流式语音演示

这是一个交互式演示，你可以与 Agent 进行对话式交流。它使用了语音管道内置的轮次检测功能，因此当你停止说话时，Agent 会自动响应。

运行方式：

```
python -m examples.voice.streamed.main
```

## 工作原理

1. 我们创建一个 `VoicePipeline`，使用 `SingleAgentVoiceWorkflow` 进行设置。这是一个从助手 Agent 开始的工作流，包含工具和切换功能。
2. 从终端捕获音频输入。
3. 使用录制的音频运行管道，这会导致：
    1. 转录音频
    2. 将转录文本传递给工作流，工作流运行 Agent。
    3. 将 Agent 的输出流式传输到文本转语音模型。
4. 播放音频。

一些建议尝试的示例：

-   Tell me a joke (_助手会给你讲一个笑话_)
-   What's the weather in Tokyo? (_会调用 `get_weather` 工具然后说话_)
-   Hola, como estas? (_会切换到西班牙语 Agent_)
