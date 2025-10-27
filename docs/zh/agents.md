# 代理

代理是您应用程序中的核心构建块。代理是一个大型语言模型 (LLM),配置有指令和工具。

## 基本配置

您将配置的代理的最常见属性是:

- `name`: 标识代理的必需字符串。
- `instructions`: 也称为开发人员消息或系统提示。
- `model`: 使用哪个 LLM,以及可选的 `model_settings` 来配置模型调优参数,如 temperature、top_p 等。
- `tools`: 代理可以使用的工具来完成其任务。

```python
from agents import Agent, ModelSettings, function_tool

@function_tool
def get_weather(city: str) -> str:
    """返回指定城市的天气信息。"""
    return f"The weather in {city} is sunny"

agent = Agent(
    name="Haiku agent",
    instructions="Always respond in haiku form",
    model="gpt-5-nano",
    tools=[get_weather],
)
```

## 上下文

代理对其 `context` 类型是泛型的。上下文是一个依赖注入工具:它是您创建并传递给 `Runner.run()` 的对象,该对象会传递给每个代理、工具、交接等,它充当代理运行的依赖项和状态的集合。您可以提供任何 Python 对象作为上下文。

```python
@dataclass
class UserContext:
    name: str
    uid: str
    is_pro_user: bool

    async def fetch_purchases() -> list[Purchase]:
        return ...

agent = Agent[UserContext](
    ...,
)
```

## 输出类型

默认情况下,代理产生纯文本(即 `str`)输出。如果您希望代理产生特定类型的输出,可以使用 `output_type` 参数。一个常见的选择是使用 [Pydantic](https://docs.pydantic.dev/) 对象,但我们支持任何可以包装在 Pydantic [TypeAdapter](https://docs.pydantic.dev/latest/api/type_adapter/) 中的类型 - dataclass、list、TypedDict 等。

```python
from pydantic import BaseModel
from agents import Agent


class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]

agent = Agent(
    name="Calendar extractor",
    instructions="Extract calendar events from text",
    output_type=CalendarEvent,
)
```

!!! note

    当您传递 `output_type` 时,这会告诉模型使用[结构化输出](https://platform.openai.com/docs/guides/structured-outputs)而不是常规纯文本响应。

## 多代理系统设计模式

有许多设计多代理系统的方法,但我们通常看到两种广泛适用的模式:

1. 管理器(代理作为工具): 中央管理器/编排器调用专业子代理作为工具,并保留对话的控制权。
2. 交接: 对等代理将控制权交给接管对话的专业代理。这是去中心化的。

有关更多详细信息,请参阅[我们的构建代理实用指南](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)。

### 管理器(代理作为工具)

`customer_facing_agent` 处理所有用户交互并调用作为工具公开的专业子代理。在[工具](tools.md#agents-as-tools)文档中阅读更多内容。

```python
from agents import Agent

booking_agent = Agent(...)
refund_agent = Agent(...)

customer_facing_agent = Agent(
    name="Customer-facing agent",
    instructions=(
        "Handle all direct user communication. "
        "Call the relevant tools when specialized expertise is needed."
    ),
    tools=[
        booking_agent.as_tool(
            tool_name="booking_expert",
            tool_description="Handles booking questions and requests.",
        ),
        refund_agent.as_tool(
            tool_name="refund_expert",
            tool_description="Handles refund questions and requests.",
        )
    ],
)
```

### 交接

交接是代理可以委托的子代理。当发生交接时,被委托的代理接收对话历史并接管对话。这种模式使模块化、专业化的代理能够擅长单一任务。在[交接](handoffs.md)文档中阅读更多内容。

```python
from agents import Agent

booking_agent = Agent(...)
refund_agent = Agent(...)

triage_agent = Agent(
    name="Triage agent",
    instructions=(
        "Help the user with their questions. "
        "If they ask about booking, hand off to the booking agent. "
        "If they ask about refunds, hand off to the refund agent."
    ),
    handoffs=[booking_agent, refund_agent],
)
```

## 动态指令

在大多数情况下,您可以在创建代理时提供指令。但是,您也可以通过函数提供动态指令。该函数将接收代理和上下文,并且必须返回提示。接受常规函数和 `async` 函数。

```python
def dynamic_instructions(
    context: RunContextWrapper[UserContext], agent: Agent[UserContext]
) -> str:
    return f"The user's name is {context.context.name}. Help them with their questions."


agent = Agent[UserContext](
    name="Triage agent",
    instructions=dynamic_instructions,
)
```

## 生命周期事件(钩子)

有时,您想要观察代理的生命周期。例如,您可能想要记录事件,或在某些事件发生时预先获取数据。您可以使用 `hooks` 属性钩入代理生命周期。子类化 [`AgentHooks`][agents.lifecycle.AgentHooks] 类,并覆盖您感兴趣的方法。

## 护栏

护栏允许您与代理运行并行地对用户输入运行检查/验证,以及在代理输出产生后对其进行检查。例如,您可以筛选用户输入和代理输出的相关性。在[护栏](guardrails.md)文档中阅读更多内容。

## 克隆/复制代理

通过使用代理上的 `clone()` 方法,您可以复制代理,并可选择更改您喜欢的任何属性。

```python
pirate_agent = Agent(
    name="Pirate",
    instructions="Write like a pirate",
    model="gpt-4.1",
)

robot_agent = pirate_agent.clone(
    name="Robot",
    instructions="Write like a robot",
)
```

## 强制使用工具

提供工具列表并不总是意味着 LLM 会使用工具。您可以通过设置 [`ModelSettings.tool_choice`][agents.model_settings.ModelSettings.tool_choice] 来强制使用工具。有效值为:

1. `auto`,允许 LLM 决定是否使用工具。
2. `required`,要求 LLM 使用工具(但它可以智能地决定使用哪个工具)。
3. `none`,要求 LLM _不_使用工具。
4. 设置特定字符串,例如 `my_tool`,要求 LLM 使用该特定工具。

```python
from agents import Agent, Runner, function_tool, ModelSettings

@function_tool
def get_weather(city: str) -> str:
    """返回指定城市的天气信息。"""
    return f"The weather in {city} is sunny"

agent = Agent(
    name="Weather Agent",
    instructions="Retrieve weather details.",
    tools=[get_weather],
    model_settings=ModelSettings(tool_choice="get_weather")
)
```

## 工具使用行为

`Agent` 配置中的 `tool_use_behavior` 参数控制如何处理工具输出:

- `"run_llm_again"`: 默认值。运行工具,LLM 处理结果以产生最终响应。
- `"stop_on_first_tool"`: 第一个工具调用的输出用作最终响应,无需进一步的 LLM 处理。

```python
from agents import Agent, Runner, function_tool, ModelSettings

@function_tool
def get_weather(city: str) -> str:
    """返回指定城市的天气信息。"""
    return f"The weather in {city} is sunny"

agent = Agent(
    name="Weather Agent",
    instructions="Retrieve weather details.",
    tools=[get_weather],
    tool_use_behavior="stop_on_first_tool"
)
```

- `StopAtTools(stop_at_tool_names=[...])`: 如果调用任何指定的工具,则停止,使用其输出作为最终响应。

```python
from agents import Agent, Runner, function_tool
from agents.agent import StopAtTools

@function_tool
def get_weather(city: str) -> str:
    """返回指定城市的天气信息。"""
    return f"The weather in {city} is sunny"

@function_tool
def sum_numbers(a: int, b: int) -> int:
    """将两个数字相加。"""
    return a + b

agent = Agent(
    name="Stop At Stock Agent",
    instructions="Get weather or sum numbers.",
    tools=[get_weather, sum_numbers],
    tool_use_behavior=StopAtTools(stop_at_tool_names=["get_weather"])
)
```

- `ToolsToFinalOutputFunction`: 处理工具结果并决定是停止还是继续使用 LLM 的自定义函数。

```python
from agents import Agent, Runner, function_tool, FunctionToolResult, RunContextWrapper
from agents.agent import ToolsToFinalOutputResult
from typing import List, Any

@function_tool
def get_weather(city: str) -> str:
    """返回指定城市的天气信息。"""
    return f"The weather in {city} is sunny"

def custom_tool_handler(
    context: RunContextWrapper[Any],
    tool_results: List[FunctionToolResult]
) -> ToolsToFinalOutputResult:
    """处理工具结果以决定最终输出。"""
    for result in tool_results:
        if result.output and "sunny" in result.output:
            return ToolsToFinalOutputResult(
                is_final_output=True,
                final_output=f"Final weather: {result.output}"
            )
    return ToolsToFinalOutputResult(
        is_final_output=False,
        final_output=None
    )

agent = Agent(
    name="Weather Agent",
    instructions="Retrieve weather details.",
    tools=[get_weather],
    tool_use_behavior=custom_tool_handler
)
```

!!! note

    为了防止无限循环,框架会在工具调用后自动将 `tool_choice` 重置为 "auto"。此行为可通过 [`agent.reset_tool_choice`][agents.agent.Agent.reset_tool_choice] 进行配置。无限循环是因为工具结果被发送到 LLM,然后由于 `tool_choice` 而生成另一个工具调用,如此循环往复。
