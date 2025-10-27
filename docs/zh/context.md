# 上下文管理

上下文是一个多义词。你可能关心的主要有两类上下文:

1. 代码本地可用的上下文: 这是你在工具函数运行时、回调函数(如 `on_handoff`)中、生命周期钩子等场景中可能需要的数据和依赖项。
2. LLM 可用的上下文: 这是 LLM 在生成响应时可以看到的数据。

## 本地上下文

这通过 [`RunContextWrapper`][agents.run_context.RunContextWrapper] 类及其内部的 [`context`][agents.run_context.RunContextWrapper.context] 属性来表示。工作方式如下:

1. 你创建任何你想要的 Python 对象。常见的模式是使用 dataclass 或 Pydantic 对象。
2. 你将该对象传递给各种运行方法(例如 `Runner.run(..., **context=whatever**))`)。
3. 所有工具调用、生命周期钩子等都会收到一个包装器对象 `RunContextWrapper[T]`,其中 `T` 代表你的上下文对象类型,你可以通过 `wrapper.context` 访问它。

**最重要**的一点是: 对于给定的 agent 运行,每个 agent、工具函数、生命周期等都必须使用相同的上下文_类型_。

你可以将上下文用于以下用途:

-   运行的上下文数据(例如用户名/uid 或关于用户的其他信息)
-   依赖项(例如日志记录器对象、数据获取器等)
-   辅助函数

!!! danger "注意"

    上下文对象**不会**发送给 LLM。它纯粹是一个本地对象,你可以从中读取、写入并调用其方法。

```python
import asyncio
from dataclasses import dataclass

from agents import Agent, RunContextWrapper, Runner, function_tool

@dataclass
class UserInfo:  # (1)!
    name: str
    uid: int

@function_tool
async def fetch_user_age(wrapper: RunContextWrapper[UserInfo]) -> str:  # (2)!
    """Fetch the age of the user. Call this function to get user's age information."""
    return f"The user {wrapper.context.name} is 47 years old"

async def main():
    user_info = UserInfo(name="John", uid=123)

    agent = Agent[UserInfo](  # (3)!
        name="Assistant",
        tools=[fetch_user_age],
    )

    result = await Runner.run(  # (4)!
        starting_agent=agent,
        input="What is the age of the user?",
        context=user_info,
    )

    print(result.final_output)  # (5)!
    # The user John is 47 years old.

if __name__ == "__main__":
    asyncio.run(main())
```

1. 这是上下文对象。我们在这里使用了 dataclass,但你可以使用任何类型。
2. 这是一个工具。你可以看到它接收一个 `RunContextWrapper[UserInfo]`。工具实现从上下文中读取数据。
3. 我们用泛型 `UserInfo` 标记 agent,以便类型检查器可以捕获错误(例如,如果我们尝试传递一个接收不同上下文类型的工具)。
4. 上下文被传递给 `run` 函数。
5. agent 正确调用了工具并获得了年龄。

## Agent/LLM 上下文

当调用 LLM 时,它能看到的**唯一**数据来自对话历史。这意味着,如果你想让 LLM 获得一些新数据,你必须以某种方式使其在该历史记录中可用。有几种方法可以做到这一点:

1. 你可以将其添加到 Agent 的 `instructions` 中。这也称为"系统提示"或"开发者消息"。系统提示可以是静态字符串,也可以是接收上下文并输出字符串的动态函数。这是一种常用的策略,适用于始终有用的信息(例如用户名或当前日期)。
2. 调用 `Runner.run` 函数时将其添加到 `input` 中。这类似于 `instructions` 策略,但允许你拥有在[命令链](https://cdn.openai.com/spec/model-spec-2024-05-08.html#follow-the-chain-of-command)中优先级较低的消息。
3. 通过函数工具暴露它。这对_按需_上下文很有用 - LLM 决定何时需要某些数据,并可以调用工具来获取该数据。
4. 使用检索或网络搜索。这些是特殊的工具,能够从文件或数据库(检索)或从网络(网络搜索)中获取相关数据。这对于在相关上下文数据中"奠定基础"的响应很有用。
