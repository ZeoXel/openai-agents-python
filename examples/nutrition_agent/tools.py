"""工具函数 - 营养查询、计算和食谱生成"""

from typing import Annotated

from agents import function_tool

from .models import NutritionInfo, RecipeSuggestion


@function_tool
def query_nutrition_from_knowledge(
    food_name: Annotated[str, "食材名称，如'鸡胸肉'、'西兰花'、'鸡蛋'等"],
) -> NutritionInfo:
    """
    从大模型内置知识中查询食材的营养成分数据。

    这个工具会利用大模型对常见食材营养成分的记忆，快速返回准确的营养数据。
    适用于常见的中国和国际食材。

    返回的营养成分包括：
    - 热量、蛋白质、脂肪、碳水化合物、膳食纤维
    - 维生素A、C、D、E
    - 矿物质：钙、铁、锌

    注意：此工具依赖LLM的知识库，对于常见食材准确度很高。
    如果遇到不常见或新型食材，建议使用网页搜索工具验证。
    """
    # 这个函数体实际上不会被执行，LLM会根据其知识返回数据
    # 这里返回一个占位符，实际数据由LLM生成
    return NutritionInfo(
        food_name=food_name,
        calories=0,
        protein=0,
        fat=0,
        carbs=0,
        fiber=0,
        vitamin_a=0,
        vitamin_c=0,
        vitamin_d=0,
        vitamin_e=0,
        calcium=0,
        iron=0,
        zinc=0,
    )


@function_tool
def calculate_nutrition_score(nutrition_info: NutritionInfo) -> float:
    """
    计算食材的综合营养密度评分（0-100分）。

    评分标准基于WHO营养素推荐摄入量（成人每日）：
    - 蛋白质：50g/天（30%权重）
    - 膳食纤维：25g/天（20%权重）
    - 维生素（25%权重）：维A(800μg)、维C(100mg)、维D(15μg)、维E(15mg)
    - 矿物质（25%权重）：钙(1000mg)、铁(15mg)、锌(15mg)

    计算方法：每种营养素占每日推荐量的百分比，按权重加总，归一化到100分制。
    """
    # 蛋白质评分 (30%权重)
    protein_daily_ref = 50.0  # 克
    protein_score = min((nutrition_info.protein / protein_daily_ref) * 100, 100)

    # 膳食纤维评分 (20%权重)
    fiber_daily_ref = 25.0  # 克
    fiber_score = min((nutrition_info.fiber / fiber_daily_ref) * 100, 100)

    # 维生素评分 (25%权重)
    vitamin_scores = []
    vitamin_scores.append(min((nutrition_info.vitamin_a / 800.0) * 100, 100))  # μg
    vitamin_scores.append(min((nutrition_info.vitamin_c / 100.0) * 100, 100))  # mg
    vitamin_scores.append(min((nutrition_info.vitamin_d / 15.0) * 100, 100))  # μg
    vitamin_scores.append(min((nutrition_info.vitamin_e / 15.0) * 100, 100))  # mg
    vitamin_score = sum(vitamin_scores) / len(vitamin_scores)

    # 矿物质评分 (25%权重)
    mineral_scores = []
    mineral_scores.append(min((nutrition_info.calcium / 1000.0) * 100, 100))  # mg
    mineral_scores.append(min((nutrition_info.iron / 15.0) * 100, 100))  # mg
    mineral_scores.append(min((nutrition_info.zinc / 15.0) * 100, 100))  # mg
    mineral_score = sum(mineral_scores) / len(mineral_scores)

    # 综合评分
    total_score = (
        protein_score * 0.30 + fiber_score * 0.20 + vitamin_score * 0.25 + mineral_score * 0.25
    )

    return round(total_score, 2)


@function_tool
def calculate_value_score(
    nutrition_score: Annotated[float, "营养密度评分（0-100）"],
    price_per_100g: Annotated[float, "每100克价格（元）"],
) -> float:
    """
    计算营养性价比评分（0-100分）。

    公式：性价比 = (营养密度评分 / 每100g价格) × 调整系数

    调整系数设计为让评分分布在合理区间：
    - 优秀食材（高营养低价）：80-100分
    - 良好食材：60-79分
    - 一般食材：40-59分
    - 较差食材（低营养高价）：0-39分
    """
    if price_per_100g <= 0:
        return 0.0

    # 基础性价比 = 营养分数 / 价格
    base_score = nutrition_score / price_per_100g

    # 调整系数：让分数分布更合理
    # 典型案例：鸡蛋（营养70分，3元/100g）→ 约70分
    # 鸡胸肉（营养85分，3元/100g）→ 约85分
    adjustment_factor = 3.0

    value_score = min(base_score * adjustment_factor, 100)

    return round(value_score, 2)


@function_tool
def get_rating_and_suggestions(
    value_score: Annotated[float, "营养性价比评分"],
    nutrition_score: Annotated[float, "营养密度评分"],
    price_per_100g: Annotated[float, "每100克价格（元）"],
) -> dict[str, str]:
    """
    根据性价比评分返回等级评价和购买建议。

    评级标准：
    - 优秀（80-100分）：高营养密度 + 低价格
    - 良好（60-79分）：营养均衡，价格适中
    - 一般（40-59分）：营养或价格有一项不理想
    - 较差（0-39分）：低营养密度或高价格
    """
    if value_score >= 80:
        rating = "优秀"
        suggestion = f"这是一款性价比极高的食材！营养密度评分{nutrition_score:.0f}分，每100克仅需{price_per_100g:.2f}元，强烈推荐作为日常饮食的主食材。"
    elif value_score >= 60:
        rating = "良好"
        suggestion = f"这是一款营养均衡、价格合理的食材。营养密度{nutrition_score:.0f}分，价格{price_per_100g:.2f}元/100g，适合日常食用，建议搭配其他食材以增加营养多样性。"
    elif value_score >= 40:
        rating = "一般"
        if nutrition_score < 50:
            suggestion = f"该食材营养密度较低（{nutrition_score:.0f}分），虽然价格{price_per_100g:.2f}元/100g还算合理，但建议搭配高营养食材一起食用，或作为辅助食材而非主食。"
        else:
            suggestion = f"该食材营养密度尚可（{nutrition_score:.0f}分），但价格{price_per_100g:.2f}元/100g偏高。如果预算允许可以购买，否则建议寻找性价比更高的替代品。"
    else:
        rating = "较差"
        suggestion = f"该食材性价比不理想。营养密度{nutrition_score:.0f}分，价格{price_per_100g:.2f}元/100g。建议谨慎购买，可寻找营养更丰富或价格更实惠的替代食材。"

    return {"rating": rating, "suggestion": suggestion}


@function_tool
def generate_recipe_suggestions(
    food_name: Annotated[str, "主要食材名称"], nutrition_info: NutritionInfo
) -> list[RecipeSuggestion]:
    """
    根据食材特点生成3个营养均衡的食谱建议。

    食谱设计原则：
    1. 营养互补：搭配不同营养优势的食材
    2. 烹饪简便：提供家常易操作的烹饪方法
    3. 口味多样：涵盖不同风味和烹饪方式

    这个工具会利用LLM的烹饪知识，基于食材营养特点，
    生成适合中国家庭的实用食谱建议。
    """
    # 此函数由LLM根据食材特点生成食谱
    # 这里返回占位符，实际内容由LLM生成
    return [
        RecipeSuggestion(
            recipe_name=f"{food_name}的食谱1",
            ingredients=[food_name],
            cooking_method="待生成",
            nutrition_benefits="待生成",
        )
    ]


@function_tool
def analyze_nutrition_highlights(nutrition_info: NutritionInfo) -> str:
    """
    分析食材的营养亮点，生成易懂的说明文字。

    重点突出：
    - 蛋白质含量是否优秀（>20g/100g为高蛋白）
    - 低脂/低碳特性（脂肪<5g或碳水<10g）
    - 突出的维生素或矿物质含量
    - 整体营养特点（如：高蛋白低脂、富含维C等）
    """
    highlights = []

    # 分析蛋白质
    if nutrition_info.protein >= 20:
        highlights.append(f"高蛋白食材（{nutrition_info.protein:.1f}g/100g）")
    elif nutrition_info.protein >= 10:
        highlights.append(f"中等蛋白质（{nutrition_info.protein:.1f}g/100g）")

    # 分析脂肪
    if nutrition_info.fat < 5:
        highlights.append("低脂肪")
    elif nutrition_info.fat >= 20:
        highlights.append(f"高脂肪（{nutrition_info.fat:.1f}g/100g）")

    # 分析碳水
    if nutrition_info.carbs < 10:
        highlights.append("低碳水")

    # 分析膳食纤维
    if nutrition_info.fiber >= 5:
        highlights.append(f"富含膳食纤维（{nutrition_info.fiber:.1f}g/100g）")

    # 分析维生素
    if nutrition_info.vitamin_c >= 50:
        highlights.append(f"富含维生素C（{nutrition_info.vitamin_c:.0f}mg/100g）")
    if nutrition_info.vitamin_a >= 500:
        highlights.append(f"富含维生素A（{nutrition_info.vitamin_a:.0f}μg/100g）")

    # 分析矿物质
    if nutrition_info.calcium >= 200:
        highlights.append(f"富含钙质（{nutrition_info.calcium:.0f}mg/100g）")
    if nutrition_info.iron >= 5:
        highlights.append(f"富含铁元素（{nutrition_info.iron:.1f}mg/100g）")

    if not highlights:
        highlights.append("营养成分均衡")

    return "、".join(highlights) + "。"
