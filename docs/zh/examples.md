# 示例

在[仓库](https://github.com/openai/openai-agents-python/tree/main/examples)的示例部分查看 SDK 的各种示例实现。这些示例按多个类别组织，展示了不同的模式和功能。

## 类别

-   **[agent_patterns](https://github.com/openai/openai-agents-python/tree/main/examples/agent_patterns):**
    此类别中的示例展示了常见的智能体设计模式，例如

    -   确定性工作流
    -   智能体作为工具
    -   并行智能体执行
    -   条件工具使用
    -   输入/输出护栏
    -   LLM 作为评判者
    -   路由
    -   流式护栏

-   **[basic](https://github.com/openai/openai-agents-python/tree/main/examples/basic):**
    这些示例展示了 SDK 的基础功能，例如

    -   Hello world 示例（默认模型、GPT-5、开源权重模型）
    -   智能体生命周期管理
    -   动态系统提示词
    -   流式输出（文本、项目、函数调用参数）
    -   提示词模板
    -   文件处理（本地和远程、图像和 PDF）
    -   使用量跟踪
    -   非严格输出类型
    -   先前响应 ID 的使用

-   **[customer_service](https://github.com/openai/openai-agents-python/tree/main/examples/customer_service):**
    航空公司客户服务系统示例。

-   **[financial_research_agent](https://github.com/openai/openai-agents-python/tree/main/examples/financial_research_agent):**
    金融研究智能体，展示了使用智能体和工具进行金融数据分析的结构化研究工作流。

-   **[handoffs](https://github.com/openai/openai-agents-python/tree/main/examples/handoffs):**
    查看带有消息过滤的智能体切换的实际示例。

-   **[hosted_mcp](https://github.com/openai/openai-agents-python/tree/main/examples/hosted_mcp):**
    展示如何使用托管的 MCP（模型上下文协议）连接器和审批的示例。

-   **[mcp](https://github.com/openai/openai-agents-python/tree/main/examples/mcp):**
    学习如何使用 MCP（模型上下文协议）构建智能体，包括：

    -   文件系统示例
    -   Git 示例
    -   MCP 提示词服务器示例
    -   SSE（服务器发送事件）示例
    -   可流式传输的 HTTP 示例

-   **[memory](https://github.com/openai/openai-agents-python/tree/main/examples/memory):**
    智能体的不同内存实现示例，包括：

    -   SQLite 会话存储
    -   高级 SQLite 会话存储
    -   Redis 会话存储
    -   SQLAlchemy 会话存储
    -   加密会话存储
    -   OpenAI 会话存储

-   **[model_providers](https://github.com/openai/openai-agents-python/tree/main/examples/model_providers):**
    探索如何在 SDK 中使用非 OpenAI 模型，包括自定义提供商和 LiteLLM 集成。

-   **[realtime](https://github.com/openai/openai-agents-python/tree/main/examples/realtime):**
    展示如何使用 SDK 构建实时体验的示例，包括：

    -   Web 应用程序
    -   命令行界面
    -   Twilio 集成

-   **[reasoning_content](https://github.com/openai/openai-agents-python/tree/main/examples/reasoning_content):**
    展示如何处理推理内容和结构化输出的示例。

-   **[research_bot](https://github.com/openai/openai-agents-python/tree/main/examples/research_bot):**
    简单的深度研究克隆，展示了复杂的多智能体研究工作流。

-   **[tools](https://github.com/openai/openai-agents-python/tree/main/examples/tools):**
    学习如何实现 OAI 托管工具，例如：

    -   网络搜索和带过滤器的网络搜索
    -   文件搜索
    -   代码解释器
    -   计算机使用
    -   图像生成

-   **[voice](https://github.com/openai/openai-agents-python/tree/main/examples/voice):**
    查看使用我们的 TTS 和 STT 模型的语音智能体示例，包括流式语音示例。
