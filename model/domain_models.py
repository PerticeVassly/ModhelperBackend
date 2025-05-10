from pydantic import BaseModel
from enum import Enum
from typing import Literal
from typing import Optional

class Reference(BaseModel):
    description: str
    content: str

class intentionEnum(str, Enum):
    basic_info = "basic_info"
    gameplay_guide = "gameplay_guide"
    mod_recommendation = "mod_recommendation"
    pack_customization = "pack_customization"
    other = "other"

class ExtractedFields(BaseModel):
    mod_name: list[str] = []
    item_name: list[str] = []
    block_name: list[str] = []
    world_name: list[str] = []
    biome_name: list[str] = []

class ExtractedInfo(BaseModel):
    is_mc: Literal[0, 1]
    extraction_fields: Optional[ExtractedFields]
    intention: intentionEnum

class SummarizeTitle(BaseModel):
    title: str

    