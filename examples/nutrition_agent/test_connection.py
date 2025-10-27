"""测试 API 连接和配置"""

import asyncio
import os

from openai import AsyncOpenAI


async def test_api_connection():
    """测试 API 连接"""
    print("=" * 60)
    print("🔧 API 连接测试")
    print("=" * 60)

    api_base_url = os.getenv("OPENAI_API_BASE", "https://api.bltcy.ai/v1")
    api_key = os.getenv("OPENAI_API_KEY", "sk-JO438PQ5WpZFtR9Gt5tMN119FmD1bG6YDtmczNgGyDIMCHc1")
    model_name = os.getenv("OPENAI_MODEL", "gpt-5")

    print(f"\n📍 API 端点: {api_base_url}")
    print(f"🤖 模型: {model_name}")
    print(f"🔑 API 密钥: {api_key[:20]}...")

    print("\n🔍 正在测试连接...")

    try:
        client = AsyncOpenAI(
            base_url=api_base_url,
            api_key=api_key,
            timeout=30.0,
            max_retries=1,
        )

        # 测试简单的聊天完成
        print("💬 发送测试请求...")
        response = await client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "请用一句话介绍鸡蛋的营养价值"}],
            max_tokens=100,
        )

        print("\n✅ 连接成功！")
        print(f"\n🤖 AI 回复: {response.choices[0].message.content}")
        print("\n" + "=" * 60)
        print("✅ 配置正常，可以开始使用营养性价比计算Agent")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 连接失败: {str(e)}")
        print("\n💡 可能的原因：")
        print("   1. API 端点不正确或不可用")
        print("   2. API 密钥无效")
        print("   3. 网络连接问题")
        print("   4. 模型名称不正确")
        print("\n🔧 建议：")
        print("   1. 检查 API 端点是否可访问")
        print("   2. 确认 API 密钥是否有效")
        print("   3. 尝试使用浏览器访问 API 端点")
        print("   4. 检查网络连接")


if __name__ == "__main__":
    asyncio.run(test_api_connection())
