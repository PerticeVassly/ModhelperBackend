from pydantic import BaseModel
from enum import Enum
from typing import Literal
from typing import Optional
from typing import Union

# retrieved reference
class Reference(BaseModel):
    description: str
    content: str

# document type which need vector compare


# extracted user intention type from user input
class intentionEnum(str, Enum):
    basic_info = "basic_info"
    gameplay_guide = "gameplay_guide"
    mod_recommendation = "mod_recommendation"
    pack_customization = "pack_customization"
    other = "other"

# extracted userinput related Entity
class intrestedEntityEnum(str, Enum):
    mod = "mod"
    item = "item"
    entity = "entity"
    biome = "biome"
    structure = "structure"

# extractedInfo BaseModel generate by extractor llm
class ExtractedFields(BaseModel):
    mods = []
    items = []
    entities = []
    biomes = []
    structures = []

class ExtractedInfo(BaseModel):
    is_mc: Literal[0, 1]
    extraction_fields: Optional[ExtractedFields]
    intention: Union[intentionEnum, Literal[''], None]

# summarizeTitle generate by summarize llm
class SummarizeTitle(BaseModel):
    title: str

    