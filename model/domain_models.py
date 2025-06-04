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
    url : str = ""

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

# ExtractLLMResponse generate by extract llm
class ExtractedFields(BaseModel):
    mods : list[str] = []
    items : list[str] = []
    entities : list[str] = []
    biomes : list[str] = []
    structures : list[str] = []

class ExtractLLMResponse(BaseModel):
    extracted_fields: Optional[ExtractedFields]
    
# ClassifyLLMResponse generate by classify llm
class ClassifyLLMResponse(BaseModel):
    is_mc: Literal[0, 1] = 0

# IntentionAnalyzeLLMResponse generate by intention analyze llm
class IntentionAnalyzeLLMResponse(BaseModel):
    intention: Union[intentionEnum, Literal[''], None] = None

# HyDELLMResponse generate by hyde llm
class HyDELLMResponse(BaseModel):
    hyde_answer: Optional[str] = None

# SetBackLLMResponse generate by set back llm
class SetBackLLMResponse(BaseModel):
    step_back_question: Optional[str] = None
    step_back_answer: Optional[str] = None

# summarizeLLMResponse generate by summarize llm
class SummarizeLLMResponse(BaseModel):
    title: str

# categorizeLLMResponse generate by categorize llm
class CategorizeLLMResponse(BaseModel):
    categories : list[str] = []

# modRecommendLLMResponse generate by mod recommend llm
class RecommendationItem(BaseModel):
    name: str
    url: str
    reason: str

class ModRecommendLLMResponse(BaseModel):
    recommendations: list[RecommendationItem] = []


class ModVO(Mod):
    id: str
    isFavorite: bool

class PreProcessResult(BaseModel):
    is_mc: Optional[Literal[0, 1]] = None
    extracted_fields: Optional[ExtractedFields] = None
    intention: Optional[intentionEnum] = None
    hyde_answer: Optional[str] = None
    step_back_question: Optional[str] = None
    step_back_answer: Optional[str] = None

    



    