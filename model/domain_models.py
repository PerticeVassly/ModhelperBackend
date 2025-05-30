from pydantic import BaseModel
from enum import Enum
from typing import Literal
from typing import Optional
from typing import Union
from .db_models import Mod

# retrieved reference
class Reference(BaseModel):
    description: str
    content: str

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
    mods : list[str] = []
    items : list[str] = []
    entities : list[str] = []
    biomes : list[str] = []
    structures : list[str] = []

class ExtractedInfo(BaseModel):
    is_mc: Literal[0, 1]
    extraction_fields: Optional[ExtractedFields]
    intention: Union[intentionEnum, Literal[''], None]
    answer: Optional[str] = None
    stepBackQuestion: Optional[str] = None
    stepBackQuestionAnswer: Optional[str] = None

# summarizeTitle generate by summarize llm
class SummarizedTitleInfo(BaseModel):
    title: str

# categoryInfo generate by category llm
class CategoryInfo(BaseModel):
    categories : list[str] = []

class RecommendationItem(BaseModel):
    name: str
    url: str
    reason: str

# ModRecommendationInfo generate by mod recommendation llm
class ModRecommendationInfo(BaseModel):
    recommendations: list[RecommendationItem] = []

# 暂无作者信息
class ModVO(Mod):
    id: str
    isFavorite: bool

    



    