from model import *

summarizeTitleExample = SummarizeTitle(
    title="复用或生成的标题"
)

extractedInfoExample = ExtractedInfo(
    is_mc=1,
    extraction_fields=ExtractedFields(
        mod_name=["mod1", "mod2"],
        item_name=["item1", "item2"],
        block_name=["block1", "block2"],
        world_name=["world1", "world2"],
        biome_name=["biome1", "biome2"]
    ),
    intention=intentionEnum.basic_info
)