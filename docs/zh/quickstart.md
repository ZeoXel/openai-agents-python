# 快速开始

## 创建项目和虚拟环境

您只需要执行一次此操作。

```bash
mkdir my_project
cd my_project
python -m venv .venv
```

### 激活虚拟环境

每次启动新终端会话时都要执行此操作。

```bash
source .venv/bin/activate
```

### 安装 Agents SDK

```bash
pip install openai-agents # 或 `uv add openai-agents` 等
```

### 设置 OpenAI API 密钥

如果您还没有,请按照[这些说明](https://platform.openai.com/docs/quickstart#create-and-export-an-api-key)创建 OpenAI API 密钥。

```bash
export OPENAI_API_KEY=sk-...
```

## 创建您的第一个代理

代理使用指令、名称和可选配置(例如 `model_config`)定义

```python
from agents import Agent

agent = Agent(
    name="Math Tutor",
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples",
)
```

## 添加更多代理

可以以相同的方式定义其他代理。`handoff_descriptions` 为确定交接路由提供额外的上下文

```python
from agents import Agent

history_tutor_agent = Agent(
    name="History Tutor",
    handoff_description="Specialist agent for historical questions",
    instructions="You provide assistance with historical queries. Explain important events and context clearly.",
)

math_tutor_agent = Agent(
    name="Math Tutor",
    handoff_description="Specialist agent for math questions",
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples",
)
```

## 定义交接

在每个代理上,您可以定义代理可以选择的传出交接选项清单,以决定如何推进任务。

```python
triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent to use based on the user's homework question",
    handoffs=[history_tutor_agent, math_tutor_agent]
)
```

## 运行代理编排

让我们检查工作流是否运行,以及分流代理是否正确地在两个专业代理之间路由。

```python
from agents import Runner

async def main():
    result = await Runner.run(triage_agent, "What is the capital of France?")
    print(result.final_output)
```

## 添加护栏

您可以定义自定义护栏以在输入或输出上运行。

```python
from agents import GuardrailFunctionOutput, Agent, Runner
from pydantic import BaseModel


class HomeworkOutput(BaseModel):
    is_homework: bool
    reasoning: str

guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user is asking about homework.",
    output_type=HomeworkOutput,
)

async def homework_guardrail(ctx, agent, input_data):
    result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
    final_output = result.final_output_as(HomeworkOutput)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_homework,
    )
```

## 整合所有内容

让我们整合所有内容并运行整个工作流,使用交接和输入护栏。

```python
from agents import Agent, InputGuardrail, GuardrailFunctionOutput, Runner
from agents.exceptions import InputGuardrailTripwireTriggered
from pydantic import BaseModel
import asyncio

class HomeworkOutput(BaseModel):
    is_homework: bool
    reasoning: str

guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user is asking about homework.",
    output_type=HomeworkOutput,
)

math_tutor_agent = Agent(
    name="Math Tutor",
    handoff_description="Specialist agent for math questions",
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples",
)

history_tutor_agent = Agent(
    name="History Tutor",
    handoff_description="Specialist agent for historical questions",
    instructions="You provide assistance with historical queries. Explain important events and context clearly.",
)


async def homework_guardrail(ctx, agent, input_data):
    result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
    final_output = result.final_output_as(HomeworkOutput)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_homework,
    )

triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent to use based on the user's homework question",
    handoffs=[history_tutor_agent, math_tutor_agent],
    input_guardrails=[
        InputGuardrail(guardrail_function=homework_guardrail),
    ],
)

async def main():
    # 示例 1: 历史问题
    try:
        result = await Runner.run(triage_agent, "who was the first president of the united states?")
        print(result.final_output)
    except InputGuardrailTripwireTriggered as e:
        print("Guardrail blocked this input:", e)

    # 示例 2: 一般/哲学问题
    try:
        result = await Runner.run(triage_agent, "What is the meaning of life?")
        print(result.final_output)
    except InputGuardrailTripwireTriggered as e:
        print("Guardrail blocked this input:", e)

if __name__ == "__main__":
    asyncio.run(main())
```

## 查看跟踪

要查看代理运行期间发生的情况,请导航到 [OpenAI Dashboard 中的跟踪查看器](https://platform.openai.com/traces)以查看代理运行的跟踪。

## 下一步

了解如何构建更复杂的代理流程:

- 了解如何配置[代理](agents.md)。
- 了解[运行代理](running_agents.md)。
- 了解[工具](tools.md)、[护栏](guardrails.md)和[模型](models/index.md)。
