# 交接(Handoffs)

交接允许一个代理将任务委托给另一个代理。这在不同代理专门处理不同领域的场景中特别有用。例如,一个客户支持应用可能有多个代理,每个代理专门处理订单状态、退款、常见问题等任务。

交接在 LLM 中以工具的形式表示。因此,如果有一个交接到名为 `Refund Agent` 的代理,该工具将被称为 `transfer_to_refund_agent`。

## 创建交接

所有代理都有一个 [`handoffs`][agents.agent.Agent.handoffs] 参数,它可以直接接收 `Agent`,也可以接收自定义交接的 `Handoff` 对象。

你可以使用 Agents SDK 提供的 [`handoff()`][agents.handoffs.handoff] 函数创建交接。此函数允许你指定要交接到的代理,以及可选的覆盖和输入过滤器。

### 基本用法

以下是创建简单交接的方法:

```python
from agents import Agent, handoff

billing_agent = Agent(name="Billing agent")
refund_agent = Agent(name="Refund agent")

# (1)!
triage_agent = Agent(name="Triage agent", handoffs=[billing_agent, handoff(refund_agent)])
```

1. 你可以直接使用代理(如 `billing_agent`),也可以使用 `handoff()` 函数。

### 通过 `handoff()` 函数自定义交接

[`handoff()`][agents.handoffs.handoff] 函数允许你自定义内容。

-   `agent`: 这是将被交接到的代理。
-   `tool_name_override`: 默认情况下,使用 `Handoff.default_tool_name()` 函数,它解析为 `transfer_to_<agent_name>`。你可以覆盖此设置。
-   `tool_description_override`: 覆盖 `Handoff.default_tool_description()` 的默认工具描述
-   `on_handoff`: 在调用交接时执行的回调函数。这对于在知道正在调用交接时立即启动某些数据获取等操作很有用。此函数接收代理上下文,也可以选择性地接收 LLM 生成的输入。输入数据由 `input_type` 参数控制。
-   `input_type`: 交接期望的输入类型(可选)。
-   `input_filter`: 这允许你过滤下一个代理接收的输入。详见下文。
-   `is_enabled`: 交接是否启用。这可以是布尔值或返回布尔值的函数,允许你在运行时动态启用或禁用交接。

```python
from agents import Agent, handoff, RunContextWrapper

def on_handoff(ctx: RunContextWrapper[None]):
    print("Handoff called")

agent = Agent(name="My agent")

handoff_obj = handoff(
    agent=agent,
    on_handoff=on_handoff,
    tool_name_override="custom_handoff_tool",
    tool_description_override="Custom description",
)
```

## 交接输入

在某些情况下,你希望 LLM 在调用交接时提供一些数据。例如,想象一个到"升级代理"的交接。你可能希望提供一个原因,以便可以记录它。

```python
from pydantic import BaseModel

from agents import Agent, handoff, RunContextWrapper

class EscalationData(BaseModel):
    reason: str

async def on_handoff(ctx: RunContextWrapper[None], input_data: EscalationData):
    print(f"Escalation agent called with reason: {input_data.reason}")

agent = Agent(name="Escalation agent")

handoff_obj = handoff(
    agent=agent,
    on_handoff=on_handoff,
    input_type=EscalationData,
)
```

## 输入过滤器

当发生交接时,就好像新代理接管了对话,并可以看到整个之前的对话历史。如果你想改变这一点,可以设置 [`input_filter`][agents.handoffs.Handoff.input_filter]。输入过滤器是一个函数,它通过 [`HandoffInputData`][agents.handoffs.HandoffInputData] 接收现有输入,并必须返回一个新的 `HandoffInputData`。

有一些常见模式(例如从历史记录中删除所有工具调用),这些已在 [`agents.extensions.handoff_filters`][] 中为你实现。

```python
from agents import Agent, handoff
from agents.extensions import handoff_filters

agent = Agent(name="FAQ agent")

handoff_obj = handoff(
    agent=agent,
    input_filter=handoff_filters.remove_all_tools, # (1)!
)
```

1. 这将在调用 `FAQ agent` 时自动从历史记录中删除所有工具。

## 推荐提示词

为了确保 LLM 正确理解交接,我们建议在代理中包含有关交接的信息。我们在 [`agents.extensions.handoff_prompt.RECOMMENDED_PROMPT_PREFIX`][] 中有一个建议的前缀,或者你可以调用 [`agents.extensions.handoff_prompt.prompt_with_handoff_instructions`][] 来自动将推荐数据添加到你的提示词中。

```python
from agents import Agent
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

billing_agent = Agent(
    name="Billing agent",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    <Fill in the rest of your prompt here>.""",
)
```
