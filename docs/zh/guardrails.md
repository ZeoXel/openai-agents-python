# 护栏机制

护栏与您的智能体*并行*运行,使您能够对用户输入进行检查和验证。例如,假设您有一个智能体,它使用非常智能的模型(因此速度慢/成本高)来帮助处理客户请求。您不希望恶意用户要求模型帮助他们做数学作业。因此,您可以使用快速/廉价的模型运行护栏。如果护栏检测到恶意使用,它可以立即引发错误,从而阻止昂贵的模型运行并为您节省时间/金钱。

护栏有两种类型:

1. 输入护栏在初始用户输入上运行
2. 输出护栏在最终智能体输出上运行

## 输入护栏

输入护栏分 3 个步骤运行:

1. 首先,护栏接收传递给智能体的相同输入。
2. 接下来,护栏函数运行以生成 [`GuardrailFunctionOutput`][agents.guardrail.GuardrailFunctionOutput],然后将其包装在 [`InputGuardrailResult`][agents.guardrail.InputGuardrailResult] 中
3. 最后,我们检查 [`.tripwire_triggered`][agents.guardrail.GuardrailFunctionOutput.tripwire_triggered] 是否为 true。如果为 true,则会引发 [`InputGuardrailTripwireTriggered`][agents.exceptions.InputGuardrailTripwireTriggered] 异常,以便您可以适当地响应用户或处理异常。

!!! Note

    输入护栏旨在对用户输入运行,因此智能体的护栏仅在该智能体是*第一个*智能体时运行。您可能想知道,为什么 `guardrails` 属性在智能体上而不是传递给 `Runner.run`?这是因为护栏往往与实际的智能体相关 - 您会为不同的智能体运行不同的护栏,因此将代码放在一起有助于提高可读性。

## 输出护栏

输出护栏分 3 个步骤运行:

1. 首先,护栏接收智能体生成的输出。
2. 接下来,护栏函数运行以生成 [`GuardrailFunctionOutput`][agents.guardrail.GuardrailFunctionOutput],然后将其包装在 [`OutputGuardrailResult`][agents.guardrail.OutputGuardrailResult] 中
3. 最后,我们检查 [`.tripwire_triggered`][agents.guardrail.GuardrailFunctionOutput.tripwire_triggered] 是否为 true。如果为 true,则会引发 [`OutputGuardrailTripwireTriggered`][agents.exceptions.OutputGuardrailTripwireTriggered] 异常,以便您可以适当地响应用户或处理异常。

!!! Note

    输出护栏旨在对最终智能体输出运行,因此智能体的护栏仅在该智能体是*最后一个*智能体时运行。与输入护栏类似,我们这样做是因为护栏往往与实际的智能体相关 - 您会为不同的智能体运行不同的护栏,因此将代码放在一起有助于提高可读性。

## 触发器

如果输入或输出未通过护栏检查,护栏可以通过触发器发出信号。一旦我们看到触发了触发器的护栏,我们会立即引发 `{Input,Output}GuardrailTripwireTriggered` 异常并停止智能体执行。

## 实现护栏

您需要提供一个接收输入并返回 [`GuardrailFunctionOutput`][agents.guardrail.GuardrailFunctionOutput] 的函数。在此示例中,我们将通过在底层运行智能体来实现这一点。

```python
from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
)

class MathHomeworkOutput(BaseModel):
    is_math_homework: bool
    reasoning: str

guardrail_agent = Agent( # (1)!
    name="Guardrail check",
    instructions="Check if the user is asking you to do their math homework.",
    output_type=MathHomeworkOutput,
)


@input_guardrail
async def math_guardrail( # (2)!
    ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output, # (3)!
        tripwire_triggered=result.final_output.is_math_homework,
    )


agent = Agent(  # (4)!
    name="Customer support agent",
    instructions="You are a customer support agent. You help customers with their questions.",
    input_guardrails=[math_guardrail],
)

async def main():
    # This should trip the guardrail
    try:
        await Runner.run(agent, "Hello, can you help me solve for x: 2x + 3 = 11?")
        print("Guardrail didn't trip - this is unexpected")

    except InputGuardrailTripwireTriggered:
        print("Math homework guardrail tripped")
```

1. 我们将在护栏函数中使用此智能体。
2. 这是接收智能体输入/上下文并返回结果的护栏函数。
3. 我们可以在护栏结果中包含额外信息。
4. 这是定义工作流的实际智能体。

输出护栏也是类似的。

```python
from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    output_guardrail,
)
class MessageOutput(BaseModel): # (1)!
    response: str

class MathOutput(BaseModel): # (2)!
    reasoning: str
    is_math: bool

guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the output includes any math.",
    output_type=MathOutput,
)

@output_guardrail
async def math_guardrail(  # (3)!
    ctx: RunContextWrapper, agent: Agent, output: MessageOutput
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, output.response, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_math,
    )

agent = Agent( # (4)!
    name="Customer support agent",
    instructions="You are a customer support agent. You help customers with their questions.",
    output_guardrails=[math_guardrail],
    output_type=MessageOutput,
)

async def main():
    # This should trip the guardrail
    try:
        await Runner.run(agent, "Hello, can you help me solve for x: 2x + 3 = 11?")
        print("Guardrail didn't trip - this is unexpected")

    except OutputGuardrailTripwireTriggered:
        print("Math output guardrail tripped")
```

1. 这是实际智能体的输出类型。
2. 这是护栏的输出类型。
3. 这是接收智能体输出并返回结果的护栏函数。
4. 这是定义工作流的实际智能体。
