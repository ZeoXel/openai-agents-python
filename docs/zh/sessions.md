# 会话 (Sessions)

Agents SDK 提供内置的会话内存功能，可以在多次 agent 运行之间自动维护对话历史，无需在每轮对话之间手动处理 `.to_input_list()`。

会话存储特定会话的对话历史，允许 agent 在不需要显式手动内存管理的情况下维护上下文。这对于构建聊天应用程序或多轮对话特别有用，在这些场景中您希望 agent 记住之前的交互。

## 快速开始

```python
from agents import Agent, Runner, SQLiteSession

# 创建 agent
agent = Agent(
    name="Assistant",
    instructions="Reply very concisely.",
)

# 使用会话 ID 创建会话实例
session = SQLiteSession("conversation_123")

# 第一轮对话
result = await Runner.run(
    agent,
    "What city is the Golden Gate Bridge in?",
    session=session
)
print(result.final_output)  # "San Francisco"

# 第二轮对话 - agent 自动记住之前的上下文
result = await Runner.run(
    agent,
    "What state is it in?",
    session=session
)
print(result.final_output)  # "California"

# 也可以使用同步运行器
result = Runner.run_sync(
    agent,
    "What's the population?",
    session=session
)
print(result.final_output)  # "Approximately 39 million"
```

## 工作原理

当启用会话内存时：

1. **每次运行前**：运行器自动检索该会话的对话历史并将其添加到输入项的前面。
2. **每次运行后**：运行期间生成的所有新项（用户输入、助手响应、工具调用等）都会自动存储在会话中。
3. **上下文保留**：使用相同会话的每次后续运行都包含完整的对话历史，允许 agent 维护上下文。

这消除了在运行之间手动调用 `.to_input_list()` 和管理对话状态的需要。

## 内存操作

### 基本操作

会话支持几种用于管理对话历史的操作：

```python
from agents import SQLiteSession

session = SQLiteSession("user_123", "conversations.db")

# 获取会话中的所有项
items = await session.get_items()

# 向会话添加新项
new_items = [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there!"}
]
await session.add_items(new_items)

# 移除并返回最近的一项
last_item = await session.pop_item()
print(last_item)  # {"role": "assistant", "content": "Hi there!"}

# 清除会话中的所有项
await session.clear_session()
```

### 使用 pop_item 进行更正

当您想要撤销或修改对话中的最后一项时，`pop_item` 方法特别有用：

```python
from agents import Agent, Runner, SQLiteSession

agent = Agent(name="Assistant")
session = SQLiteSession("correction_example")

# 初始对话
result = await Runner.run(
    agent,
    "What's 2 + 2?",
    session=session
)
print(f"Agent: {result.final_output}")

# 用户想要更正他们的问题
assistant_item = await session.pop_item()  # 移除 agent 的响应
user_item = await session.pop_item()  # 移除用户的问题

# 提问更正后的问题
result = await Runner.run(
    agent,
    "What's 2 + 3?",
    session=session
)
print(f"Agent: {result.final_output}")
```

## 内存选项

### 无内存（默认）

```python
# 默认行为 - 无会话内存
result = await Runner.run(agent, "Hello")
```

### OpenAI Conversations API 内存

使用 [OpenAI Conversations API](https://platform.openai.com/docs/api-reference/conversations/create) 来持久化
[对话状态](https://platform.openai.com/docs/guides/conversation-state?api-mode=responses#using-the-conversations-api)，而无需管理您自己的数据库。当您已经依赖 OpenAI 托管的基础设施来存储对话历史时，这会很有帮助。

```python
from agents import OpenAIConversationsSession

session = OpenAIConversationsSession()

# 可选：通过传递对话 ID 来恢复之前的对话
# session = OpenAIConversationsSession(conversation_id="conv_123")

result = await Runner.run(
    agent,
    "Hello",
    session=session,
)
```

### SQLite 内存

```python
from agents import SQLiteSession

# 内存数据库（进程结束时丢失）
session = SQLiteSession("user_123")

# 基于持久文件的数据库
session = SQLiteSession("user_123", "conversations.db")

# 使用会话
result = await Runner.run(
    agent,
    "Hello",
    session=session
)
```

### 多个会话

```python
from agents import Agent, Runner, SQLiteSession

agent = Agent(name="Assistant")

# 不同的会话维护独立的对话历史
session_1 = SQLiteSession("user_123", "conversations.db")
session_2 = SQLiteSession("user_456", "conversations.db")

result1 = await Runner.run(
    agent,
    "Hello",
    session=session_1
)
result2 = await Runner.run(
    agent,
    "Hello",
    session=session_2
)
```

### 基于 SQLAlchemy 的会话

对于更高级的用例，您可以使用基于 SQLAlchemy 的会话后端。这允许您使用 SQLAlchemy 支持的任何数据库（PostgreSQL、MySQL、SQLite 等）进行会话存储。

**示例 1：使用 `from_url` 与内存 SQLite**

这是最简单的入门方式，非常适合开发和测试。

```python
import asyncio
from agents import Agent, Runner
from agents.extensions.memory.sqlalchemy_session import SQLAlchemySession

async def main():
    agent = Agent("Assistant")
    session = SQLAlchemySession.from_url(
        "user-123",
        url="sqlite+aiosqlite:///:memory:",
        create_tables=True,  # 自动为演示创建表
    )

    result = await Runner.run(agent, "Hello", session=session)

if __name__ == "__main__":
    asyncio.run(main())
```

**示例 2：使用现有的 SQLAlchemy 引擎**

在生产应用程序中，您可能已经有一个 SQLAlchemy `AsyncEngine` 实例。您可以直接将其传递给会话。

```python
import asyncio
from agents import Agent, Runner
from agents.extensions.memory.sqlalchemy_session import SQLAlchemySession
from sqlalchemy.ext.asyncio import create_async_engine

async def main():
    # 在您的应用程序中，您将使用现有的引擎
    engine = create_async_engine("sqlite+aiosqlite:///conversations.db")

    agent = Agent("Assistant")
    session = SQLAlchemySession(
        "user-456",
        engine=engine,
        create_tables=True,  # 自动为演示创建表
    )

    result = await Runner.run(agent, "Hello", session=session)
    print(result.final_output)

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
```

### 加密会话

对于需要对静态对话数据进行加密的应用程序，您可以使用 `EncryptedSession` 来包装任何会话后端，提供透明加密和基于 TTL 的自动过期。这需要 `encrypt` 扩展：`pip install openai-agents[encrypt]`。

`EncryptedSession` 使用 Fernet 加密和每个会话的密钥派生（HKDF），并支持旧消息的自动过期。当项超过 TTL 时，它们在检索期间会被静默跳过。

**示例：加密 SQLAlchemy 会话数据**

```python
import asyncio
from agents import Agent, Runner
from agents.extensions.memory import EncryptedSession, SQLAlchemySession

async def main():
    # 创建底层会话（适用于任何 SessionABC 实现）
    underlying_session = SQLAlchemySession.from_url(
        session_id="user-123",
        url="postgresql+asyncpg://app:secret@db.example.com/agents",
        create_tables=True,
    )

    # 使用加密和基于 TTL 的过期进行包装
    session = EncryptedSession(
        session_id="user-123",
        underlying_session=underlying_session,
        encryption_key="your-encryption-key",  # 使用来自您的秘密管理的安全密钥
        ttl=600,  # 10 分钟 - 比这更旧的项会被静默跳过
    )

    agent = Agent("Assistant")
    result = await Runner.run(agent, "Hello", session=session)
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

**主要特性：**

-   **透明加密**：在存储前自动加密所有会话项，并在检索时解密
-   **每个会话的密钥派生**：使用 HKDF 和会话 ID 作为盐来派生唯一的加密密钥
-   **基于 TTL 的过期**：根据可配置的生存时间自动过期旧消息（默认：10 分钟）
-   **灵活的密钥输入**：接受 Fernet 密钥或原始字符串作为加密密钥
-   **包装任何会话**：适用于 SQLite、SQLAlchemy 或自定义会话实现

!!! warning "重要的安全注意事项"

    -   安全地存储您的加密密钥（例如，环境变量、秘密管理器）
    -   过期的令牌基于应用程序服务器的系统时钟被拒绝 - 确保所有服务器与 NTP 时间同步，以避免由于时钟漂移而导致有效令牌被拒绝
    -   底层会话仍然存储加密数据，因此您保持对数据库基础设施的控制


## 自定义内存实现

您可以通过创建一个遵循 [`Session`][agents.memory.session.Session] 协议的类来实现自己的会话内存：

```python
from agents.memory.session import SessionABC
from agents.items import TResponseInputItem
from typing import List

class MyCustomSession(SessionABC):
    """遵循 Session 协议的自定义会话实现。"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        # 您的初始化代码

    async def get_items(self, limit: int | None = None) -> List[TResponseInputItem]:
        """检索此会话的对话历史。"""
        # 您的实现代码
        pass

    async def add_items(self, items: List[TResponseInputItem]) -> None:
        """为此会话存储新项。"""
        # 您的实现代码
        pass

    async def pop_item(self) -> TResponseInputItem | None:
        """从此会话中移除并返回最近的一项。"""
        # 您的实现代码
        pass

    async def clear_session(self) -> None:
        """清除此会话的所有项。"""
        # 您的实现代码
        pass

# 使用您的自定义会话
agent = Agent(name="Assistant")
result = await Runner.run(
    agent,
    "Hello",
    session=MyCustomSession("my_session")
)
```

## 会话管理

### 会话 ID 命名

使用有意义的会话 ID 来帮助您组织对话：

-   基于用户：`"user_12345"`
-   基于线程：`"thread_abc123"`
-   基于上下文：`"support_ticket_456"`

### 内存持久化

-   使用内存 SQLite（`SQLiteSession("session_id")`）用于临时对话
-   使用基于文件的 SQLite（`SQLiteSession("session_id", "path/to/db.sqlite")`）用于持久对话
-   使用基于 SQLAlchemy 的会话（`SQLAlchemySession("session_id", engine=engine, create_tables=True)`）用于具有 SQLAlchemy 支持的现有数据库的生产系统
-   当您希望在 OpenAI Conversations API 中存储历史时，使用 OpenAI 托管存储（`OpenAIConversationsSession()`）
-   使用加密会话（`EncryptedSession(session_id, underlying_session, encryption_key)`）来包装任何具有透明加密和基于 TTL 的过期的会话
-   考虑为更高级的用例（Redis、Django 等）实现自定义会话后端的其他生产系统

### 会话管理

```python
# 当对话应该重新开始时清除会话
await session.clear_session()

# 不同的 agent 可以共享同一个会话
support_agent = Agent(name="Support")
billing_agent = Agent(name="Billing")
session = SQLiteSession("user_123")

# 两个 agent 将看到相同的对话历史
result1 = await Runner.run(
    support_agent,
    "Help me with my account",
    session=session
)
result2 = await Runner.run(
    billing_agent,
    "What are my charges?",
    session=session
)
```

## 完整示例

这是一个展示会话内存的完整示例：

```python
import asyncio
from agents import Agent, Runner, SQLiteSession


async def main():
    # 创建一个 agent
    agent = Agent(
        name="Assistant",
        instructions="Reply very concisely.",
    )

    # 创建一个将在运行之间持久化的会话实例
    session = SQLiteSession("conversation_123", "conversation_history.db")

    print("=== Sessions Example ===")
    print("The agent will remember previous messages automatically.\n")

    # 第一轮
    print("First turn:")
    print("User: What city is the Golden Gate Bridge in?")
    result = await Runner.run(
        agent,
        "What city is the Golden Gate Bridge in?",
        session=session
    )
    print(f"Assistant: {result.final_output}")
    print()

    # 第二轮 - agent 将记住之前的对话
    print("Second turn:")
    print("User: What state is it in?")
    result = await Runner.run(
        agent,
        "What state is it in?",
        session=session
    )
    print(f"Assistant: {result.final_output}")
    print()

    # 第三轮 - 继续对话
    print("Third turn:")
    print("User: What's the population of that state?")
    result = await Runner.run(
        agent,
        "What's the population of that state?",
        session=session
    )
    print(f"Assistant: {result.final_output}")
    print()

    print("=== Conversation Complete ===")
    print("Notice how the agent remembered the context from previous turns!")
    print("Sessions automatically handles conversation history.")


if __name__ == "__main__":
    asyncio.run(main())
```

## API 参考

有关详细的 API 文档，请参见：

-   [`Session`][agents.memory.Session] - 协议接口
-   [`SQLiteSession`][agents.memory.SQLiteSession] - SQLite 实现
-   [`OpenAIConversationsSession`](ref/memory/openai_conversations_session.md) - OpenAI Conversations API 实现
-   [`SQLAlchemySession`][agents.extensions.memory.sqlalchemy_session.SQLAlchemySession] - 基于 SQLAlchemy 的实现
-   [`EncryptedSession`][agents.extensions.memory.encrypt_session.EncryptedSession] - 带 TTL 的加密会话包装器
