from model import *

summarizeLLMResponseExample = SummarizeLLMResponse(
    title="复用或生成的标题"
)

extracLLMResponseExample = PreProcessResult(
    extraction_fields=ExtractedFields(
        mods=["mod1", "mod2"],
        items=["item1", "item2"],
        entities=["entity1", "entity2"],
        biomes=["biome1", "biome2"],
        structures=["structure1", "structure2"]
    ),
)

classifyLLMResponseExample = ClassifyLLMResponse(
    is_mc=1
)

intentionAnalyzeLLMResponseExample = IntentionAnalyzeLLMResponse(
    intention=intentionEnum.gameplay_guide
)

HyDELLMResponseExample = HyDELLMResponse(
    hyde_answer="HyDE回答"
)

setBackLLMResponseExample = SetBackLLMResponse(
    step_back_question="退后问题",
    step_back_answer="退后问题的回答"
)

categorizeLLMResponseExample = CategorizeLLMResponse(
    categories=["category1", "category2"]
)

modRecommendLLMResponseExample = ModRecommendLLMResponse(
    recommendations=[
        RecommendationItem(name="mod1", url="http://example.com/mod1", reason="推荐理由1"),
        RecommendationItem(name="mod2", url="http://example.com/mod2", reason="推荐理由2")
    ]
)