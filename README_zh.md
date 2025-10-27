# OpenAI Agents SDK

OpenAI Agents SDK 是一个轻量级但功能强大的框架,用于构建多代理工作流。它是提供商无关的,支持 OpenAI Responses 和 Chat Completions API,以及 100 多个其他 LLM。

<img src="https://cdn.openai.com/API/docs/images/orchestration.png" alt="Agents Tracing UI 图像" style="max-height: 803px;">

> [!NOTE]
> 正在寻找 JavaScript/TypeScript 版本?请查看 [Agents SDK JS/TS](https://github.com/openai/openai-agents-js)。

### 核心概念:

1. [**代理 (Agents)**](https://openai.github.io/openai-agents-python/agents): 使用指令、工具、护栏和交接配置的 LLM
2. [**交接 (Handoffs)**](https://openai.github.io/openai-agents-python/handoffs/): Agents SDK 使用的专用工具调用,用于在代理之间传递控制权
3. [**护栏 (Guardrails)**](https://openai.github.io/openai-agents-python/guardrails/): 用于输入和输出验证的可配置安全检查
4. [**会话 (Sessions)**](#sessions): 跨代理运行的自动对话历史管理
5. [**跟踪 (Tracing)**](https://openai.github.io/openai-agents-python/tracing/): 内置的代理运行跟踪,允许您查看、调试和优化工作流

浏览 [examples](examples) 目录以查看 SDK 的实际应用,并阅读我们的[文档](https://openai.github.io/openai-agents-python/)以获取更多详细信息。

## 快速开始

首先,设置您的 Python 环境(需要 Python 3.9 或更高版本),然后安装 OpenAI Agents SDK 包。

### venv

```bash
python -m venv .venv
source .venv/bin/activate  # Windows 系统: .venv\Scripts\activate
pip install openai-agents
```

如需语音支持,请使用可选的 `voice` 组安装:`pip install 'openai-agents[voice]'`。

如需 Redis 会话支持,请使用可选的 `redis` 组安装:`pip install 'openai-agents[redis]'`。

### uv

如果您熟悉 [uv](https://docs.astral.sh/uv/),使用该工具会更加简单:

```bash
uv init
uv add openai-agents
```

如需语音支持,请使用可选的 `voice` 组安装:`uv add 'openai-agents[voice]'`。

如需 Redis 会话支持,请使用可选的 `redis` 组安装:`uv add 'openai-agents[redis]'`。

## Hello World 示例

```python
from agents import Agent, Runner

agent = Agent(name="Assistant", instructions="You are a helpful assistant")

result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
print(result.final_output)

# Code within the code,
# Functions calling themselves,
# Infinite loop's dance.
```

(_运行此示例时,请确保设置 `OPENAI_API_KEY` 环境变量_)

(_对于 Jupyter notebook 用户,请参见 [hello_world_jupyter.ipynb](examples/basic/hello_world_jupyter.ipynb)_)

## 交接示例

```python
from agents import Agent, Runner
import asyncio

spanish_agent = Agent(
    name="Spanish agent",
    instructions="You only speak Spanish.",
)

english_agent = Agent(
    name="English agent",
    instructions="You only speak English",
)

triage_agent = Agent(
    name="Triage agent",
    instructions="Handoff to the appropriate agent based on the language of the request.",
    handoffs=[spanish_agent, english_agent],
)


async def main():
    result = await Runner.run(triage_agent, input="Hola, ¿cómo estás?")
    print(result.final_output)
    # ¡Hola! Estoy bien, gracias por preguntar. ¿Y tú, cómo estás?


if __name__ == "__main__":
    asyncio.run(main())
```

## 函数示例

```python
import asyncio

from agents import Agent, Runner, function_tool


@function_tool
def get_weather(city: str) -> str:
    return f"The weather in {city} is sunny."


agent = Agent(
    name="Hello world",
    instructions="You are a helpful agent.",
    tools=[get_weather],
)


async def main():
    result = await Runner.run(agent, input="What's the weather in Tokyo?")
    print(result.final_output)
    # The weather in Tokyo is sunny.


if __name__ == "__main__":
    asyncio.run(main())
```

## 代理循环

当您调用 `Runner.run()` 时,我们会运行一个循环,直到获得最终输出。

1. 我们使用代理上的模型和设置以及消息历史调用 LLM。
2. LLM 返回一个响应,可能包括工具调用。
3. 如果响应有最终输出(有关详细信息,请参见下文),我们将其返回并结束循环。
4. 如果响应有交接,我们将代理设置为新代理,然后返回到步骤 1。
5. 我们处理工具调用(如果有)并附加工具响应消息。然后我们进入步骤 1。

您可以使用 `max_turns` 参数来限制循环执行的次数。

### 最终输出

最终输出是代理在循环中产生的最后一件事。

1. 如果您在代理上设置了 `output_type`,则最终输出是 LLM 返回该类型的内容时。我们使用[结构化输出](https://platform.openai.com/docs/guides/structured-outputs)来实现这一点。
2. 如果没有 `output_type`(即纯文本响应),则第一个没有任何工具调用或交接的 LLM 响应被视为最终输出。

因此,代理循环的思维模型是:

1. 如果当前代理有 `output_type`,则循环运行直到代理产生与该类型匹配的结构化输出。
2. 如果当前代理没有 `output_type`,则循环运行直到当前代理产生没有任何工具调用/交接的消息。

## 常见代理模式

Agents SDK 设计为高度灵活,允许您对各种 LLM 工作流进行建模,包括确定性流程、迭代循环等。请参见 [`examples/agent_patterns`](examples/agent_patterns) 中的示例。

## 跟踪

Agents SDK 会自动跟踪您的代理运行,使您可以轻松跟踪和调试代理的行为。跟踪在设计上是可扩展的,支持自定义跨度和各种外部目标,包括 [Logfire](https://logfire.pydantic.dev/docs/integrations/llms/openai/#openai-agents)、[AgentOps](https://docs.agentops.ai/v1/integrations/agentssdk)、[Braintrust](https://braintrust.dev/docs/guides/traces/integrations#openai-agents-sdk)、[Scorecard](https://docs.scorecard.io/docs/documentation/features/tracing#openai-agents-sdk-integration) 和 [Keywords AI](https://docs.keywordsai.co/integration/development-frameworks/openai-agent)。有关如何自定义或禁用跟踪的更多详细信息,请参见[跟踪](http://openai.github.io/openai-agents-python/tracing),其中还包括更大的[外部跟踪处理器列表](http://openai.github.io/openai-agents-python/tracing/#external-tracing-processors-list)。

## 长期运行的代理和人在环路中

您可以使用 Agents SDK [Temporal](https://temporal.io/) 集成来运行持久的长期运行工作流,包括人在环路中的任务。观看 [此视频](https://www.youtube.com/watch?v=fFBZqzT4DD8) 中 Temporal 和 Agents SDK 协同工作完成长期运行任务的演示,[在此处查看文档](https://github.com/temporalio/sdk-python/tree/main/temporalio/contrib/openai_agents)。

## 会话

Agents SDK 提供内置的会话内存,可以在多个代理运行之间自动维护对话历史,无需在轮次之间手动处理 `.to_input_list()`。

### 快速开始

```python
from agents import Agent, Runner, SQLiteSession

# 创建代理
agent = Agent(
    name="Assistant",
    instructions="Reply very concisely.",
)

# 创建会话实例
session = SQLiteSession("conversation_123")

# 第一轮
result = await Runner.run(
    agent,
    "What city is the Golden Gate Bridge in?",
    session=session
)
print(result.final_output)  # "San Francisco"

# 第二轮 - 代理自动记住之前的上下文
result = await Runner.run(
    agent,
    "What state is it in?",
    session=session
)
print(result.final_output)  # "California"

# 也适用于同步运行器
result = Runner.run_sync(
    agent,
    "What's the population?",
    session=session
)
print(result.final_output)  # "Approximately 39 million"
```

### 会话选项

- **无内存**(默认):省略 session 参数时没有会话内存
- **`session: Session = DatabaseSession(...)`**: 使用 Session 实例管理对话历史

```python
from agents import Agent, Runner, SQLiteSession

# SQLite - 基于文件或内存数据库
session = SQLiteSession("user_123", "conversations.db")

# Redis - 用于可扩展的分布式部署
# from agents.extensions.memory import RedisSession
# session = RedisSession.from_url("user_123", url="redis://localhost:6379/0")

agent = Agent(name="Assistant")

# 不同的会话 ID 维护单独的对话历史
result1 = await Runner.run(
    agent,
    "Hello",
    session=session
)
result2 = await Runner.run(
    agent,
    "Hello",
    session=SQLiteSession("user_456", "conversations.db")
)
```

### 自定义会话实现

您可以通过创建遵循 `Session` 协议的类来实现自己的会话内存:

```python
from agents.memory import Session
from typing import List

class MyCustomSession:
    """遵循 Session 协议的自定义会话实现。"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        # 在此处初始化

    async def get_items(self, limit: int | None = None) -> List[dict]:
        # 检索会话的对话历史
        pass

    async def add_items(self, items: List[dict]) -> None:
        # 为会话存储新项目
        pass

    async def pop_item(self) -> dict | None:
        # 从会话中删除并返回最新项目
        pass

    async def clear_session(self) -> None:
        # 清除会话的所有项目
        pass

# 使用自定义会话
agent = Agent(name="Assistant")
result = await Runner.run(
    agent,
    "Hello",
    session=MyCustomSession("my_session")
)
```

## 开发(仅在需要编辑 SDK/示例时需要)

0. 确保已安装 [`uv`](https://docs.astral.sh/uv/)。

```bash
uv --version
```

1. 安装依赖项

```bash
make sync
```

2. (进行更改后) lint/测试

```
make check # 运行测试、linter 和类型检查器
```

或单独运行它们:

```
make tests  # 运行测试
make mypy   # 运行类型检查器
make lint   # 运行 linter
make format-check # 运行样式检查器
```

## 致谢

我们要感谢开源社区的出色工作,特别是:

- [Pydantic](https://docs.pydantic.dev/latest/)(数据验证)和 [PydanticAI](https://ai.pydantic.dev/)(高级代理框架)
- [LiteLLM](https://github.com/BerriAI/litellm)(100 多个 LLM 的统一接口)
- [MkDocs](https://github.com/squidfunk/mkdocs-material)
- [Griffe](https://github.com/mkdocstrings/griffe)
- [uv](https://github.com/astral-sh/uv) 和 [ruff](https://github.com/astral-sh/ruff)

我们致力于继续将 Agents SDK 构建为一个开源框架,以便社区中的其他人可以在我们的方法上进行扩展。
