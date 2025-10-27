# 运行代理

你可以通过 [`Runner`][agents.run.Runner] 类来运行代理。你有 3 个选项:

1. [`Runner.run()`][agents.run.Runner.run],异步运行并返回一个 [`RunResult`][agents.result.RunResult]。
2. [`Runner.run_sync()`][agents.run.Runner.run_sync],这是一个同步方法,底层调用 `.run()`。
3. [`Runner.run_streamed()`][agents.run.Runner.run_streamed],异步运行并返回一个 [`RunResultStreaming`][agents.result.RunResultStreaming]。它以流式模式调用 LLM,并在接收到事件时将其流式传输给你。

```python
from agents import Agent, Runner

async def main():
    agent = Agent(name="Assistant", instructions="You are a helpful assistant")

    result = await Runner.run(agent, "Write a haiku about recursion in programming.")
    print(result.final_output)
    # Code within the code,
    # Functions calling themselves,
    # Infinite loop's dance
```

在[结果指南](results.md)中阅读更多内容。

## 代理循环

当你在 `Runner` 中使用 run 方法时,你传入一个起始代理和输入。输入可以是字符串(被视为用户消息),或者是一个输入项列表,这些是 OpenAI Responses API 中的项。

运行器然后运行一个循环:

1. 我们为当前代理调用 LLM,使用当前输入。
2. LLM 产生其输出。
    1. 如果 LLM 返回一个 `final_output`,循环结束并返回结果。
    2. 如果 LLM 执行交接,我们更新当前代理和输入,并重新运行循环。
    3. 如果 LLM 产生工具调用,我们运行这些工具调用,追加结果,并重新运行循环。
3. 如果我们超过传入的 `max_turns`,我们抛出一个 [`MaxTurnsExceeded`][agents.exceptions.MaxTurnsExceeded] 异常。

!!! note

    LLM 输出被视为"最终输出"的规则是:它产生所需类型的文本输出,并且没有工具调用。

## 流式传输

流式传输允许你在 LLM 运行时额外接收流式事件。一旦流完成,[`RunResultStreaming`][agents.result.RunResultStreaming] 将包含关于运行的完整信息,包括所有产生的新输出。你可以调用 `.stream_events()` 获取流式事件。在[流式传输指南](streaming.md)中阅读更多内容。

## 运行配置

`run_config` 参数让你配置代理运行的一些全局设置:

-   [`model`][agents.run.RunConfig.model]: 允许设置要使用的全局 LLM 模型,无论每个 Agent 有什么 `model`。
-   [`model_provider`][agents.run.RunConfig.model_provider]: 用于查找模型名称的模型提供者,默认为 OpenAI。
-   [`model_settings`][agents.run.RunConfig.model_settings]: 覆盖代理特定的设置。例如,你可以设置全局 `temperature` 或 `top_p`。
-   [`input_guardrails`][agents.run.RunConfig.input_guardrails], [`output_guardrails`][agents.run.RunConfig.output_guardrails]: 要在所有运行中包含的输入或输出护栏列表。
-   [`handoff_input_filter`][agents.run.RunConfig.handoff_input_filter]: 应用于所有交接的全局输入过滤器,如果交接还没有输入过滤器的话。输入过滤器允许你编辑发送到新代理的输入。有关更多详细信息,请参阅 [`Handoff.input_filter`][agents.handoffs.Handoff.input_filter] 中的文档。
-   [`tracing_disabled`][agents.run.RunConfig.tracing_disabled]: 允许你禁用整个运行的[跟踪](tracing.md)。
-   [`trace_include_sensitive_data`][agents.run.RunConfig.trace_include_sensitive_data]: 配置跟踪是否包含潜在的敏感数据,例如 LLM 和工具调用的输入/输出。
-   [`workflow_name`][agents.run.RunConfig.workflow_name], [`trace_id`][agents.run.RunConfig.trace_id], [`group_id`][agents.run.RunConfig.group_id]: 设置运行的跟踪工作流名称、跟踪 ID 和跟踪组 ID。我们建议至少设置 `workflow_name`。组 ID 是一个可选字段,让你可以跨多个运行链接跟踪。
-   [`trace_metadata`][agents.run.RunConfig.trace_metadata]: 要在所有跟踪中包含的元数据。

## 对话/聊天线程

调用任何 run 方法可能导致一个或多个代理运行(因此一个或多个 LLM 调用),但它代表聊天对话中的单个逻辑回合。例如:

1. 用户回合:用户输入文本
2. 运行器运行:第一个代理调用 LLM,运行工具,交接给第二个代理,第二个代理运行更多工具,然后产生输出。

在代理运行结束时,你可以选择向用户显示什么。例如,你可能向用户显示代理生成的每个新项,或者只显示最终输出。无论哪种方式,用户可能会提出后续问题,在这种情况下,你可以再次调用 run 方法。

### 手动对话管理

你可以使用 [`RunResultBase.to_input_list()`][agents.result.RunResultBase.to_input_list] 方法手动管理对话历史,以获取下一回合的输入:

```python
async def main():
    agent = Agent(name="Assistant", instructions="Reply very concisely.")

    thread_id = "thread_123"  # Example thread ID
    with trace(workflow_name="Conversation", group_id=thread_id):
        # First turn
        result = await Runner.run(agent, "What city is the Golden Gate Bridge in?")
        print(result.final_output)
        # San Francisco

        # Second turn
        new_input = result.to_input_list() + [{"role": "user", "content": "What state is it in?"}]
        result = await Runner.run(agent, new_input)
        print(result.final_output)
        # California
```

### 使用会话自动管理对话

对于更简单的方法,你可以使用[会话](sessions.md)来自动处理对话历史,而无需手动调用 `.to_input_list()`:

```python
from agents import Agent, Runner, SQLiteSession

async def main():
    agent = Agent(name="Assistant", instructions="Reply very concisely.")

    # Create session instance
    session = SQLiteSession("conversation_123")

    thread_id = "thread_123"  # Example thread ID
    with trace(workflow_name="Conversation", group_id=thread_id):
        # First turn
        result = await Runner.run(agent, "What city is the Golden Gate Bridge in?", session=session)
        print(result.final_output)
        # San Francisco

        # Second turn - agent automatically remembers previous context
        result = await Runner.run(agent, "What state is it in?", session=session)
        print(result.final_output)
        # California
```

会话自动:

-   在每次运行之前检索对话历史
-   在每次运行之后存储新消息
-   为不同的会话 ID 维护单独的对话

有关更多详细信息,请参阅[会话文档](sessions.md)。


### 服务器管理的对话

你也可以让 OpenAI 对话状态功能在服务器端管理对话状态,而不是使用 `to_input_list()` 或 `Sessions` 在本地处理。这允许你保留对话历史,而无需手动重新发送所有过去的消息。有关更多详细信息,请参阅 [OpenAI 对话状态指南](https://platform.openai.com/docs/guides/conversation-state?api-mode=responses)。

OpenAI 提供两种方式来跨回合跟踪状态:

#### 1. 使用 `conversation_id`

你首先使用 OpenAI Conversations API 创建一个对话,然后在每次后续调用中重用其 ID:

```python
from agents import Agent, Runner
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def main():
    # Create a server-managed conversation
    conversation = await client.conversations.create()
    conv_id = conversation.id

    agent = Agent(name="Assistant", instructions="Reply very concisely.")

    # First turn
    result1 = await Runner.run(agent, "What city is the Golden Gate Bridge in?", conversation_id=conv_id)
    print(result1.final_output)
    # San Francisco

    # Second turn reuses the same conversation_id
    result2 = await Runner.run(
        agent,
        "What state is it in?",
        conversation_id=conv_id,
    )
    print(result2.final_output)
    # California
```

#### 2. 使用 `previous_response_id`

另一个选项是**响应链接**,其中每个回合明确链接到前一回合的响应 ID。

```python
from agents import Agent, Runner

async def main():
    agent = Agent(name="Assistant", instructions="Reply very concisely.")

    # First turn
    result1 = await Runner.run(agent, "What city is the Golden Gate Bridge in?")
    print(result1.final_output)
    # San Francisco

    # Second turn, chained to the previous response
    result2 = await Runner.run(
        agent,
        "What state is it in?",
        previous_response_id=result1.last_response_id,
    )
    print(result2.final_output)
    # California
```


## 长时间运行的代理和人机协作

你可以使用 Agents SDK [Temporal](https://temporal.io/) 集成来运行持久的、长时间运行的工作流,包括人机协作任务。观看 Temporal 和 Agents SDK 协同工作以完成长时间运行任务的演示[视频](https://www.youtube.com/watch?v=fFBZqzT4DD8),并[在此处查看文档](https://github.com/temporalio/sdk-python/tree/main/temporalio/contrib/openai_agents)。

## 异常

SDK 在某些情况下会抛出异常。完整列表在 [`agents.exceptions`][] 中。概述如下:

-   [`AgentsException`][agents.exceptions.AgentsException]: 这是 SDK 中抛出的所有异常的基类。它作为派生所有其他特定异常的通用类型。
-   [`MaxTurnsExceeded`][agents.exceptions.MaxTurnsExceeded]: 当代理的运行超过传递给 `Runner.run`、`Runner.run_sync` 或 `Runner.run_streamed` 方法的 `max_turns` 限制时,会抛出此异常。这表明代理无法在指定的交互回合数内完成其任务。
-   [`ModelBehaviorError`][agents.exceptions.ModelBehaviorError]: 当底层模型(LLM)产生意外或无效输出时发生此异常。这可能包括:
    -   格式错误的 JSON:当模型为工具调用或其直接输出提供格式错误的 JSON 结构时,特别是如果定义了特定的 `output_type`。
    -   意外的工具相关失败:当模型未能以预期的方式使用工具时
-   [`UserError`][agents.exceptions.UserError]: 当你(使用 SDK 编写代码的人)在使用 SDK 时出错时,会抛出此异常。这通常是由于代码实现不正确、配置无效或滥用 SDK 的 API 造成的。
-   [`InputGuardrailTripwireTriggered`][agents.exceptions.InputGuardrailTripwireTriggered], [`OutputGuardrailTripwireTriggered`][agents.exceptions.OutputGuardrailTripwireTriggered]: 当输入护栏或输出护栏的条件分别满足时,会抛出此异常。输入护栏在处理之前检查传入的消息,而输出护栏在传递之前检查代理的最终响应。
