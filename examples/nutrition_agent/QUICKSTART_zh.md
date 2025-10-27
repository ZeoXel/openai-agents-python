# 🚀 快速启动指南

## 一键运行

```bash
uv run python -m examples.nutrition_agent.main
```

## 🎯 已预配置信息

本项目已完成以下配置，**无需额外设置**即可运行：

| 配置项 | 值 |
|-------|-----|
| **API 端点** | `https://api.bltcy.ai/v1` |
| **模型** | `gpt-5` |
| **API 密钥** | 已内置 |

## 📝 使用流程

### 1. 启动程序

```bash
uv run python -m examples.nutrition_agent.main
```

### 2. 查看配置信息

程序启动后会显示：
```
============================================================
🥗 营养性价比计算Agent
============================================================

🤖 AI配置信息：
   模型：gpt-5
   API：https://api.bltcy.ai/v1
```

### 3. 输入食材信息

按照格式输入：`食材名称 重量 价格`

**示例：**
```
> 鸡胸肉 500克 15元
> 西兰花 300克 6元
> 鸡蛋 10个(约500克) 8元
```

### 4. 获取分析结果

Agent 会自动：
- 🔍 查询营养成分（利用 GPT-5 知识库）
- 📊 计算营养密度评分（0-100分）
- 💰 计算性价比评分（0-100分）
- 📋 生成购买建议
- 🍳 推荐3个实用食谱

## 🔧 自定义配置（可选）

如需使用其他 API 或模型：

### 方式1：环境变量

```bash
export OPENAI_API_BASE="https://your-api-endpoint.com/v1"
export OPENAI_API_KEY="your-api-key"
export OPENAI_MODEL="your-model-name"

uv run python -m examples.nutrition_agent.main
```

### 方式2：修改代码

编辑 `main.py` 第 69-71 行：

```python
api_base_url = os.getenv("OPENAI_API_BASE", "your-custom-endpoint")
api_key = os.getenv("OPENAI_API_KEY", "your-custom-key")
model_name = os.getenv("OPENAI_MODEL", "your-custom-model")
```

## ❓ 常见问题

### Q: 需要安装什么依赖？

A: 只需安装 OpenAI Agents SDK：
```bash
uv add openai-agents
# 或
pip install openai-agents
```

### Q: 程序卡住不动怎么办？

A: 检查以下几点：
1. 网络连接是否正常
2. API 端点是否可访问
3. API 密钥是否有效
4. 尝试使用 Ctrl+C 中断并重启

### Q: 如何验证 API 配置？

A: 运行配置测试：
```bash
uv run python -c "
import os
os.environ['OPENAI_API_BASE'] = 'https://api.bltcy.ai/v1'
os.environ['OPENAI_API_KEY'] = 'sk-JO438PQ5WpZFtR9Gt5tMN119FmD1bG6YDtmczNgGyDIMCHc1'
os.environ['OPENAI_MODEL'] = 'gpt-5'

from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel

client = AsyncOpenAI(
    base_url=os.getenv('OPENAI_API_BASE'),
    api_key=os.getenv('OPENAI_API_KEY')
)

print('✅ API 配置成功')
print(f'端点: {os.getenv(\"OPENAI_API_BASE\")}')
print(f'模型: {os.getenv(\"OPENAI_MODEL\")}')
"
```

### Q: 支持哪些食材？

A: GPT-5 拥有丰富的营养学知识，支持：
- ✅ 所有常见中国食材（蔬菜、肉类、蛋奶、豆类等）
- ✅ 国际常见食材
- ✅ 加工食品和品牌食品
- ⚠️ 特殊品种可能需要网页搜索验证

### Q: 如何退出程序？

A: 输入以下任意命令：
- `quit`
- `q`
- `退出`
- 或按 `Ctrl+C`

## 📊 输出示例

```
📋 营养性价比分析报告
============================================================

【基本信息】
食材名称：鸡胸肉
购买重量：500克
购买总价：¥15.00
单位价格：¥3.00/100克

【评分结果】
营养密度评分：85.3/100
性价比评分：85.3/100
综合评级：优秀

【营养亮点】
高蛋白食材（31.0g/100g）、低脂肪、低碳水。

【详细营养成分】（每100克）
热量：165 千卡
蛋白质：31.0g | 脂肪：3.6g | 碳水：0.0g | 纤维：0.0g
维生素A：21μg | 维C：0.0mg | 维D：0.3μg | 维E：0.7mg
钙：15mg | 铁：1.0mg | 锌：1.0mg

【购买建议】
这是一款性价比极高的食材！营养密度评分85分，
每100克仅需3.00元，强烈推荐作为日常饮食的主食材。

【推荐食谱】
  1. 西兰花炒鸡胸肉
     食材：鸡胸肉、西兰花、大蒜、生抽、料酒
     做法：鸡胸肉切片腌制，西兰花焯水...
     营养：高蛋白低脂，富含维C和纤维，营养全面

  2. 鸡胸沙拉
  3. 香煎鸡胸肉
```

## 🎉 开始使用

现在就运行程序，体验 GPT-5 驱动的智能营养分析吧！

```bash
uv run python -m examples.nutrition_agent.main
```

---

**祝您饮食健康，营养均衡！** 🥗🍎🥩
