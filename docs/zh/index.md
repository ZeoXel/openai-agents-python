# OpenAI Agents SDK

[OpenAI Agents SDK](https://github.com/openai/openai-agents-python) 使您能够在一个轻量级、易于使用的包中构建 AI 代理应用程序,并且只有很少的抽象。这是我们之前用于代理实验的 [Swarm](https://github.com/openai/swarm/tree/main) 的生产就绪升级版。Agents SDK 有一组非常小的基本组件:

- **代理 (Agents)**,它们是配备了指令和工具的 LLM
- **交接 (Handoffs)**,允许代理将特定任务委托给其他代理
- **护栏 (Guardrails)**,可以对代理输入和输出进行验证
- **会话 (Sessions)**,可以在代理运行之间自动维护对话历史

结合 Python,这些基本组件足够强大,可以表达工具和代理之间的复杂关系,并允许您构建真实世界的应用程序而无需陡峭的学习曲线。此外,SDK 附带内置的**跟踪**功能,让您可以可视化和调试代理流程,以及评估它们,甚至为您的应用程序微调模型。

## 为什么使用 Agents SDK

SDK 有两个驱动设计原则:

1. 功能足够多以值得使用,但基本组件足够少以便快速学习。
2. 开箱即用效果很好,但您可以精确自定义发生的事情。

以下是 SDK 的主要功能:

- 代理循环: 内置的代理循环,处理调用工具、将结果发送到 LLM,并循环直到 LLM 完成。
- Python 优先: 使用内置语言功能来编排和链接代理,而不需要学习新的抽象。
- 交接: 一个强大的功能,用于协调和委托多个代理。
- 护栏: 与您的代理并行运行输入验证和检查,如果检查失败则提前中断。
- 会话: 跨代理运行的自动对话历史管理,消除手动状态处理。
- 函数工具: 将任何 Python 函数转换为工具,具有自动模式生成和 Pydantic 驱动的验证。
- 跟踪: 内置跟踪,让您可以可视化、调试和监控工作流,以及使用 OpenAI 的评估、微调和蒸馏工具套件。

## 安装

```bash
pip install openai-agents
```

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

```bash
export OPENAI_API_KEY=sk-...
```
