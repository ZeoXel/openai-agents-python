"""
营养性价比计算Agent - 主程序

功能：
1. 用户输入食材名称、重量和价格
2. Agent利用LLM知识或网页搜索查询营养成分
3. 计算营养密度评分和性价比评分
4. 提供购买建议和食谱推荐

运行方式：
    uv run python -m examples.nutrition_agent.main

示例输入：
    鸡胸肉 500克 15元
    西兰花 300g 6元
    鸡蛋 10个(约500克) 8元
"""

import asyncio
import os

from openai import AsyncOpenAI

from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled

from .models import NutritionAnalysis
from .tools import (
    analyze_nutrition_highlights,
    calculate_nutrition_score,
    calculate_value_score,
    generate_recipe_suggestions,
    get_rating_and_suggestions,
    query_nutrition_from_knowledge,
)


async def main() -> None:
    """主程序入口"""
    # 禁用 tracing 以避免 OPENAI_API_KEY 警告
    set_tracing_disabled(disabled=True)

    # 配置 API 端点（支持环境变量和默认值）
    api_base_url = os.getenv("OPENAI_API_BASE", "https://api.bltcy.ai/v1")
    api_key = os.getenv("OPENAI_API_KEY", "sk-JO438PQ5WpZFtR9Gt5tMN119FmD1bG6YDtmczNgGyDIMCHc1")
    model_name = os.getenv("OPENAI_MODEL", "gpt-5")

    # 创建自定义 API 客户端（增加超时时间）
    custom_client = AsyncOpenAI(
        base_url=api_base_url,
        api_key=api_key,
        timeout=120.0,  # 120秒超时
        max_retries=2,  # 最多重试2次
    )

    # 创建自定义模型配置
    custom_model = OpenAIChatCompletionsModel(model=model_name, openai_client=custom_client)

    # 创建营养分析Agent
    nutrition_agent = Agent(
        name="营养分析师",
        model=custom_model,
        instructions="""你是一位专业的营养分析师和饮食顾问。你的任务是：

**理解用户输入**：
- 用户会用自然语言描述食材的购买信息，例如：
  * "鸡胸肉 500克 15元"
  * "辣椒 5元 一斤"
  * "西兰花 300g 6元"
  * "牛肉 50元 1公斤"
- 你需要从输入中提取：食材名称、重量（克）、总价（元）
- 如果单位是"斤"，换算为500克；如果是"公斤/kg"，换算为1000克
- 如果信息不完整，请礼貌地要求用户补充

**营养数据获取**：
- 使用 `query_nutrition_from_knowledge` 工具，利用你的营养学知识快速返回准确数据
- 对于常见食材（如鸡胸肉、鸡蛋、牛奶、西兰花、番茄、辣椒等），直接返回准确的营养数据
- 返回的营养数据必须是每100克的标准值

**营养评分计算**：
- 使用 `calculate_nutrition_score` 工具计算营养密度评分（0-100分）
- 计算每100克价格：(总价 / 重量) × 100
- 使用 `calculate_value_score` 工具计算性价比评分（0-100分）
- 使用 `get_rating_and_suggestions` 工具获取评级和建议

**营养亮点分析**：
- 使用 `analyze_nutrition_highlights` 工具分析食材的营养特点
- 用通俗易懂的语言解释营养优势

**食谱推荐**：
- 使用 `generate_recipe_suggestions` 工具生成3个实用食谱
- 食谱应该：
  * 营养互补：搭配其他食材以平衡营养
  * 简单易做：适合家庭日常烹饪
  * 口味多样：提供不同的烹饪方式（如清蒸、炒、煮、烤等）
- 每个食谱包含：名称、食材清单、烹饪方法、营养优势

**输出要求**：
- 必须使用中文
- 数据要准确，基于科学的营养学知识
- 建议要实用，考虑中国家庭的饮食习惯
- 最终输出必须符合 NutritionAnalysis 模型的结构

记住：你拥有丰富的营养学知识，对常见食材的营养成分非常了解，可以自信地返回准确数据。
""",
        tools=[
            query_nutrition_from_knowledge,
            calculate_nutrition_score,
            calculate_value_score,
            get_rating_and_suggestions,
            analyze_nutrition_highlights,
            generate_recipe_suggestions,
        ],
        output_type=NutritionAnalysis,
    )

    print("=" * 60)
    print("🥗 营养性价比计算Agent")
    print("=" * 60)
    print("\n🤖 AI配置信息：")
    print(f"   模型：{model_name}")
    print(f"   API：{api_base_url}")
    print("\n功能说明：")
    print("- 自由输入食材信息，AI自动理解")
    print("- 自动查询营养成分（利用AI知识库）")
    print("- 计算营养密度和性价比评分")
    print("- 提供购买建议和食谱推荐")
    print("\n输入示例（格式自由）：")
    print("  ✅ 鸡胸肉 500克 15元")
    print("  ✅ 辣椒 5元 一斤")
    print("  ✅ 西兰花 300g 6元")
    print("  ✅ 牛肉 50元 1公斤")
    print("\n输入 'quit' 或 'q' 退出程序")
    print("=" * 60)

    while True:
        print("\n请输入食材信息（或输入 quit 退出）：")
        user_input = input("> ").strip()

        if user_input.lower() in ["quit", "q", "退出"]:
            print("\n感谢使用！祝您饮食健康！👋")
            break

        if not user_input:
            print("⚠️  输入不能为空，请重新输入。")
            continue

        print("\n📊 正在分析，请稍候...")
        print("💭 AI正在理解您的输入...")
        print("⏱️  预计需要 10-30 秒，请耐心等待...")

        try:
            # 直接将用户输入传给Agent，由Agent理解并提取信息
            agent_input = f"""
用户输入：{user_input}

请分析这个食材的营养性价比。步骤：
1. 从用户输入中提取食材名称、重量（克）和价格（元）
2. 查询该食材的详细营养成分（每100克）
3. 计算营养密度评分和性价比评分
4. 分析营养亮点
5. 生成评级和建议
6. 推荐3个实用食谱

请确保数据准确，分析全面。
"""

            print("🔍 正在调用 GPT-5 查询营养数据...")

            # 运行Agent，增加超时设置和最大轮次
            result = await Runner.run(
                nutrition_agent,
                input=agent_input,
                max_turns=20,  # 增加最大轮次
            )

            print("✅ 分析完成！")

            # 获取结构化输出
            analysis: NutritionAnalysis = result.final_output

            # 打印分析结果
            print("\n" + "=" * 60)
            print("📋 营养性价比分析报告")
            print("=" * 60)

            print("\n【基本信息】")
            print(f"食材名称：{analysis.food_name}")
            print(f"购买重量：{analysis.weight}克")
            print(f"购买总价：¥{analysis.total_price:.2f}")
            print(f"单位价格：¥{analysis.price_per_100g:.2f}/100克")

            print("\n【评分结果】")
            print(f"营养密度评分：{analysis.nutrition_score:.1f}/100")
            print(f"性价比评分：{analysis.value_score:.1f}/100")
            print(f"综合评级：{analysis.rating}")

            print("\n【营养亮点】")
            print(f"{analysis.nutrition_highlights}")

            print("\n【详细营养成分】（每100克）")
            nut = analysis.detailed_nutrition
            print(f"热量：{nut.calories:.0f} 千卡")
            print(
                f"蛋白质：{nut.protein:.1f}g | 脂肪：{nut.fat:.1f}g | 碳水：{nut.carbs:.1f}g | 纤维：{nut.fiber:.1f}g"
            )
            print(
                f"维生素A：{nut.vitamin_a:.0f}μg | 维C：{nut.vitamin_c:.1f}mg | 维D：{nut.vitamin_d:.1f}μg | 维E：{nut.vitamin_e:.1f}mg"
            )
            print(f"钙：{nut.calcium:.0f}mg | 铁：{nut.iron:.1f}mg | 锌：{nut.zinc:.1f}mg")

            print("\n【购买建议】")
            print(f"{analysis.suggestions}")

            print("\n【推荐食谱】")
            for i, recipe in enumerate(analysis.recipe_ideas, 1):
                print(f"\n  {i}. {recipe.recipe_name}")
                print(f"     食材：{', '.join(recipe.ingredients)}")
                print(f"     做法：{recipe.cooking_method}")
                print(f"     营养：{recipe.nutrition_benefits}")

            print("\n" + "=" * 60)

        except Exception as e:
            error_msg = str(e)
            print(f"\n❌ 分析过程中出现错误：{error_msg}")

            # 提供具体的错误建议
            if "timed out" in error_msg.lower() or "timeout" in error_msg.lower():
                print("\n💡 超时原因可能是：")
                print("   1. API 响应较慢，请稍后重试")
                print("   2. 网络连接不稳定")
                print("   3. 模型正在处理中，建议等待30秒后重试")
                print("\n🔄 建议：直接重新输入相同内容即可重试")
            elif "api" in error_msg.lower() or "connection" in error_msg.lower():
                print("\n💡 连接问题可能是：")
                print("   1. API 端点暂时不可用")
                print("   2. 网络连接中断")
                print("   3. API 密钥无效")
                print("\n🔧 建议：检查网络连接，或稍后重试")
            else:
                print("\n💡 建议：")
                print("   1. 检查输入格式（食材名、重量、价格）")
                print("   2. 确保输入信息完整")
                print("   3. 稍后重试")


if __name__ == "__main__":
    asyncio.run(main())
