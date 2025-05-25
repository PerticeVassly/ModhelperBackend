from model import *

summarizeTitleInfoExample = SummarizedTitleInfo(
    title="复用或生成的标题"
)

extractedInfoExample = ExtractedInfo(
    is_mc=1,
    extraction_fields=ExtractedFields(
        mods=["mod1", "mod2"],
        items=["item1", "item2"],
        entities=["entity1", "entity2"],
        biomes=["biome1", "biome2"],
        structures=["structure1", "structure2"]
    ),
    intention=intentionEnum.basic_info,
    answer="回答",
    stepBackQuestion="退后提示的问题",
    stepBackQuestionAnswer="退后提示的问题的回答"
)

categoryInfoExample = CategoryInfo(
    categories=["category1", "category2"]
)

modRecommendationInfoExample = ModRecommendationInfo(
    recommendations=[
        RecommendationItem(name="mod1", url="http://example.com/mod1", reason="推荐理由1"),
        RecommendationItem(name="mod2", url="http://example.com/mod2", reason="推荐理由2")
    ]
)