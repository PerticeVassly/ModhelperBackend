from model import *

summarizeTitleExample = SummarizeTitle(
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
    intention=intentionEnum.basic_info
)