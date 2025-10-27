# 工具

工具让代理可以执行操作：例如获取数据、运行代码、调用外部 API，甚至使用计算机。Agent SDK 中有三类工具：

-   托管工具：这些工具在 LLM 服务器上与 AI 模型一起运行。OpenAI 提供检索、网页搜索和计算机使用作为托管工具。
-   函数调用：允许您将任何 Python 函数用作工具。
-   代理作为工具：允许您将一个代理用作工具，使代理可以调用其他代理而无需交接给它们。

## 托管工具

使用 [`OpenAIResponsesModel`][agents.models.openai_responses.OpenAIResponsesModel] 时，OpenAI 提供了一些内置工具：

-   [`WebSearchTool`][agents.tool.WebSearchTool] 让代理可以搜索网页。
-   [`FileSearchTool`][agents.tool.FileSearchTool] 允许从您的 OpenAI 向量存储中检索信息。
-   [`ComputerTool`][agents.tool.ComputerTool] 允许自动化计算机使用任务。
-   [`CodeInterpreterTool`][agents.tool.CodeInterpreterTool] 让 LLM 在沙盒环境中执行代码。
-   [`HostedMCPTool`][agents.tool.HostedMCPTool] 将远程 MCP 服务器的工具暴露给模型。
-   [`ImageGenerationTool`][agents.tool.ImageGenerationTool] 根据提示生成图像。
-   [`LocalShellTool`][agents.tool.LocalShellTool] 在您的机器上运行 shell 命令。

```python
from agents import Agent, FileSearchTool, Runner, WebSearchTool

agent = Agent(
    name="Assistant",
    tools=[
        WebSearchTool(),
        FileSearchTool(
            max_num_results=3,
            vector_store_ids=["VECTOR_STORE_ID"],
        ),
    ],
)

async def main():
    result = await Runner.run(agent, "Which coffee shop should I go to, taking into account my preferences and the weather today in SF?")
    print(result.final_output)
```

## 函数工具

您可以将任何 Python 函数用作工具。Agents SDK 会自动设置工具：

-   工具的名称将是 Python 函数的名称（或者您可以提供一个名称）
-   工具描述将从函数的文档字符串中获取（或者您可以提供描述）
-   函数输入的模式会自动从函数的参数创建
-   每个输入的描述从函数的文档字符串中获取，除非禁用

我们使用 Python 的 `inspect` 模块来提取函数签名，使用 [`griffe`](https://mkdocstrings.github.io/griffe/) 来解析文档字符串，使用 `pydantic` 来创建模式。

```python
import json

from typing_extensions import TypedDict, Any

from agents import Agent, FunctionTool, RunContextWrapper, function_tool


class Location(TypedDict):
    lat: float
    long: float

@function_tool  # (1)!
async def fetch_weather(location: Location) -> str:
    # (2)!
    """Fetch the weather for a given location.

    Args:
        location: The location to fetch the weather for.
    """
    # In real life, we'd fetch the weather from a weather API
    return "sunny"


@function_tool(name_override="fetch_data")  # (3)!
def read_file(ctx: RunContextWrapper[Any], path: str, directory: str | None = None) -> str:
    """Read the contents of a file.

    Args:
        path: The path to the file to read.
        directory: The directory to read the file from.
    """
    # In real life, we'd read the file from the file system
    return "<file contents>"


agent = Agent(
    name="Assistant",
    tools=[fetch_weather, read_file],  # (4)!
)

for tool in agent.tools:
    if isinstance(tool, FunctionTool):
        print(tool.name)
        print(tool.description)
        print(json.dumps(tool.params_json_schema, indent=2))
        print()

```

1.  您可以使用任何 Python 类型作为函数的参数，函数可以是同步或异步的。
2.  文档字符串（如果存在）用于捕获描述和参数描述
3.  函数可以选择性地接受 `context`（必须是第一个参数）。您还可以设置覆盖项，例如工具的名称、描述、使用哪种文档字符串风格等。
4.  您可以将装饰后的函数传递给工具列表。

??? note "展开查看输出"

    ```
    fetch_weather
    Fetch the weather for a given location.
    {
    "$defs": {
      "Location": {
        "properties": {
          "lat": {
            "title": "Lat",
            "type": "number"
          },
          "long": {
            "title": "Long",
            "type": "number"
          }
        },
        "required": [
          "lat",
          "long"
        ],
        "title": "Location",
        "type": "object"
      }
    },
    "properties": {
      "location": {
        "$ref": "#/$defs/Location",
        "description": "The location to fetch the weather for."
      }
    },
    "required": [
      "location"
    ],
    "title": "fetch_weather_args",
    "type": "object"
    }

    fetch_data
    Read the contents of a file.
    {
    "properties": {
      "path": {
        "description": "The path to the file to read.",
        "title": "Path",
        "type": "string"
      },
      "directory": {
        "anyOf": [
          {
            "type": "string"
          },
          {
            "type": "null"
          }
        ],
        "default": null,
        "description": "The directory to read the file from.",
        "title": "Directory"
      }
    },
    "required": [
      "path"
    ],
    "title": "fetch_data_args",
    "type": "object"
    }
    ```

### 自定义函数工具

有时候，您不想使用 Python 函数作为工具。如果您愿意，可以直接创建一个 [`FunctionTool`][agents.tool.FunctionTool]。您需要提供：

-   `name`
-   `description`
-   `params_json_schema`，即参数的 JSON 模式
-   `on_invoke_tool`，这是一个异步函数，接收一个 [`ToolContext`][agents.tool_context.ToolContext] 和参数作为 JSON 字符串，并且必须将工具输出作为字符串返回。

```python
from typing import Any

from pydantic import BaseModel

from agents import RunContextWrapper, FunctionTool



def do_some_work(data: str) -> str:
    return "done"


class FunctionArgs(BaseModel):
    username: str
    age: int


async def run_function(ctx: RunContextWrapper[Any], args: str) -> str:
    parsed = FunctionArgs.model_validate_json(args)
    return do_some_work(data=f"{parsed.username} is {parsed.age} years old")


tool = FunctionTool(
    name="process_user",
    description="Processes extracted user data",
    params_json_schema=FunctionArgs.model_json_schema(),
    on_invoke_tool=run_function,
)
```

### 自动参数和文档字符串解析

如前所述，我们会自动解析函数签名以提取工具的模式，并解析文档字符串以提取工具和各个参数的描述。关于这点的一些注意事项：

1. 签名解析是通过 `inspect` 模块完成的。我们使用类型注解来理解参数的类型，并动态构建一个 Pydantic 模型来表示整体模式。它支持大多数类型，包括 Python 原语、Pydantic 模型、TypedDicts 等。
2. 我们使用 `griffe` 来解析文档字符串。支持的文档字符串格式有 `google`、`sphinx` 和 `numpy`。我们会尝试自动检测文档字符串格式，但这只是尽力而为，您可以在调用 `function_tool` 时显式设置它。您也可以通过将 `use_docstring_info` 设置为 `False` 来禁用文档字符串解析。

模式提取的代码位于 [`agents.function_schema`][]。

## 代理作为工具

在某些工作流中，您可能希望一个中心代理编排一个专门代理网络，而不是交接控制权。您可以通过将代理建模为工具来实现这一点。

```python
from agents import Agent, Runner
import asyncio

spanish_agent = Agent(
    name="Spanish agent",
    instructions="You translate the user's message to Spanish",
)

french_agent = Agent(
    name="French agent",
    instructions="You translate the user's message to French",
)

orchestrator_agent = Agent(
    name="orchestrator_agent",
    instructions=(
        "You are a translation agent. You use the tools given to you to translate."
        "If asked for multiple translations, you call the relevant tools."
    ),
    tools=[
        spanish_agent.as_tool(
            tool_name="translate_to_spanish",
            tool_description="Translate the user's message to Spanish",
        ),
        french_agent.as_tool(
            tool_name="translate_to_french",
            tool_description="Translate the user's message to French",
        ),
    ],
)

async def main():
    result = await Runner.run(orchestrator_agent, input="Say 'Hello, how are you?' in Spanish.")
    print(result.final_output)
```

### 自定义工具代理

`agent.as_tool` 函数是一个便捷方法，可以轻松地将代理转换为工具。但它不支持所有配置；例如，您无法设置 `max_turns`。对于高级用例，请直接在工具实现中使用 `Runner.run`：

```python
@function_tool
async def run_my_agent() -> str:
    """A tool that runs the agent with custom configs"""

    agent = Agent(name="My agent", instructions="...")

    result = await Runner.run(
        agent,
        input="...",
        max_turns=5,
        run_config=...
    )

    return str(result.final_output)
```

### 自定义输出提取

在某些情况下，您可能希望在将工具代理的输出返回给中心代理之前修改它。这在以下情况下可能很有用：

- 从子代理的聊天历史中提取特定信息片段（例如，JSON 负载）。
- 转换或重新格式化代理的最终答案（例如，将 Markdown 转换为纯文本或 CSV）。
- 在代理的响应缺失或格式错误时验证输出或提供回退值。

您可以通过向 `as_tool` 方法提供 `custom_output_extractor` 参数来实现这一点：

```python
async def extract_json_payload(run_result: RunResult) -> str:
    # Scan the agent's outputs in reverse order until we find a JSON-like message from a tool call.
    for item in reversed(run_result.new_items):
        if isinstance(item, ToolCallOutputItem) and item.output.strip().startswith("{"):
            return item.output.strip()
    # Fallback to an empty JSON object if nothing was found
    return "{}"


json_tool = data_agent.as_tool(
    tool_name="get_data_json",
    tool_description="Run the data agent and return only its JSON payload",
    custom_output_extractor=extract_json_payload,
)
```

### 条件工具启用

您可以使用 `is_enabled` 参数在运行时有条件地启用或禁用代理工具。这允许您根据上下文、用户偏好或运行时条件动态过滤哪些工具对 LLM 可用。

```python
import asyncio
from agents import Agent, AgentBase, Runner, RunContextWrapper
from pydantic import BaseModel

class LanguageContext(BaseModel):
    language_preference: str = "french_spanish"

def french_enabled(ctx: RunContextWrapper[LanguageContext], agent: AgentBase) -> bool:
    """Enable French for French+Spanish preference."""
    return ctx.context.language_preference == "french_spanish"

# Create specialized agents
spanish_agent = Agent(
    name="spanish_agent",
    instructions="You respond in Spanish. Always reply to the user's question in Spanish.",
)

french_agent = Agent(
    name="french_agent",
    instructions="You respond in French. Always reply to the user's question in French.",
)

# Create orchestrator with conditional tools
orchestrator = Agent(
    name="orchestrator",
    instructions=(
        "You are a multilingual assistant. You use the tools given to you to respond to users. "
        "You must call ALL available tools to provide responses in different languages. "
        "You never respond in languages yourself, you always use the provided tools."
    ),
    tools=[
        spanish_agent.as_tool(
            tool_name="respond_spanish",
            tool_description="Respond to the user's question in Spanish",
            is_enabled=True,  # Always enabled
        ),
        french_agent.as_tool(
            tool_name="respond_french",
            tool_description="Respond to the user's question in French",
            is_enabled=french_enabled,
        ),
    ],
)

async def main():
    context = RunContextWrapper(LanguageContext(language_preference="french_spanish"))
    result = await Runner.run(orchestrator, "How are you?", context=context.context)
    print(result.final_output)

asyncio.run(main())
```

`is_enabled` 参数接受：

- **布尔值**：`True`（始终启用）或 `False`（始终禁用）
- **可调用函数**：接受 `(context, agent)` 并返回布尔值的函数
- **异步函数**：用于复杂条件逻辑的异步函数

禁用的工具在运行时完全对 LLM 隐藏，这对以下情况很有用：

- 基于用户权限的功能门控
- 特定于环境的工具可用性（开发环境 vs 生产环境）
- A/B 测试不同的工具配置
- 基于运行时状态的动态工具过滤

## 处理函数工具中的错误

当您通过 `@function_tool` 创建函数工具时，可以传递一个 `failure_error_function`。这是一个函数，在工具调用崩溃时向 LLM 提供错误响应。

-   默认情况下（即如果您不传递任何内容），它会运行一个 `default_tool_error_function`，告诉 LLM 发生了错误。
-   如果您传递自己的错误函数，它会运行该函数，并将响应发送给 LLM。
-   如果您显式传递 `None`，那么任何工具调用错误都会被重新抛出供您处理。这可能是 `ModelBehaviorError`（如果模型生成了无效的 JSON），或者是 `UserError`（如果您的代码崩溃了），等等。

```python
from agents import function_tool, RunContextWrapper
from typing import Any

def my_custom_error_function(context: RunContextWrapper[Any], error: Exception) -> str:
    """A custom function to provide a user-friendly error message."""
    print(f"A tool call failed with the following error: {error}")
    return "An internal server error occurred. Please try again later."

@function_tool(failure_error_function=my_custom_error_function)
def get_user_profile(user_id: str) -> str:
    """Fetches a user profile from a mock API.
     This function demonstrates a 'flaky' or failing API call.
    """
    if user_id == "user_123":
        return "User profile for user_123 successfully retrieved."
    else:
        raise ValueError(f"Could not retrieve profile for user_id: {user_id}. API returned an error.")

```

如果您手动创建一个 `FunctionTool` 对象，则必须在 `on_invoke_tool` 函数内部处理错误。
