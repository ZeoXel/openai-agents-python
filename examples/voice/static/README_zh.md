# 静态语音演示

此演示通过捕获录音，然后在其上运行语音管道来操作。

运行方式：

```
python -m examples.voice.static.main
```

## 工作原理

1. 我们创建一个 `VoicePipeline`，使用自定义工作流进行设置。该工作流运行一个 Agent，但如果您说出秘密单词，它也会有一些自定义响应。
2. 当您说话时，音频会被转发到语音管道。当您停止说话时，agent 开始运行。
3. 管道使用音频运行，这会导致它：
    1. 转录音频
    2. 将转录内容提供给工作流，工作流运行 agent。
    3. 将 agent 的输出流式传输到文本转语音模型。
4. 播放音频。

一些建议尝试的示例：

-   Tell me a joke (_助手会给你讲一个笑话_)
-   What's the weather in Tokyo? (_将调用 `get_weather` 工具然后说话_)
-   Hola, como estas? (_将切换到西班牙语 agent_)
-   Tell me about dogs. (_将响应硬编码的"你猜到了秘密单词"消息_)
