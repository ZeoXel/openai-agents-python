"""数据模型定义 - 营养信息和分析结果的结构化数据"""

from pydantic import BaseModel, Field


class NutritionInfo(BaseModel):
    """食材营养信息模型"""

    food_name: str = Field(description="食材名称")
    calories: float = Field(description="热量(千卡/100g)")
    protein: float = Field(description="蛋白质(克/100g)")
    fat: float = Field(description="脂肪(克/100g)")
    carbs: float = Field(description="碳水化合物(克/100g)")
    fiber: float = Field(description="膳食纤维(克/100g)")
    vitamin_a: float = Field(description="维生素A(微克/100g)")
    vitamin_c: float = Field(description="维生素C(毫克/100g)")
    vitamin_d: float = Field(description="维生素D(微克/100g)")
    vitamin_e: float = Field(description="维生素E(毫克/100g)")
    calcium: float = Field(description="钙(毫克/100g)")
    iron: float = Field(description="铁(毫克/100g)")
    zinc: float = Field(description="锌(毫克/100g)")


class RecipeSuggestion(BaseModel):
    """食谱建议模型"""

    recipe_name: str = Field(description="食谱名称")
    ingredients: list[str] = Field(description="所需食材")
    cooking_method: str = Field(description="烹饪方法")
    nutrition_benefits: str = Field(description="营养优势")


class NutritionAnalysis(BaseModel):
    """营养性价比分析结果模型"""

    food_name: str = Field(description="食材名称")
    weight: float = Field(description="重量(克)")
    total_price: float = Field(description="总价(元)")
    price_per_100g: float = Field(description="每100克价格(元)")
    nutrition_score: float = Field(
        description="营养密度评分(0-100分,综合评估蛋白质、纤维、维生素、矿物质)"
    )
    value_score: float = Field(description="营养性价比评分(0-100分,营养密度与价格的比值)")
    rating: str = Field(description="综合评级(优秀/良好/一般/较差)")
    detailed_nutrition: NutritionInfo = Field(description="详细营养成分")
    nutrition_highlights: str = Field(description="营养亮点说明")
    suggestions: str = Field(description="购买和食用建议")
    recipe_ideas: list[RecipeSuggestion] = Field(description="推荐食谱")
