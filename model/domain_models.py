from pydantic import BaseModel
from enum import Enum
from typing import Literal
from typing import Optional
from typing import Union

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

class ExtractorLLMResponse(BaseModel):
    extraction_fields: Optional[ExtractedFields]

# classifyLLMResponse generate by classify llm
class ClassifyLLMResponse(BaseModel):
    is_mc: Literal[0, 1] = 0

class IntentionAnalyzeLLMResponse(BaseModel):
    intention: Union[intentionEnum, Literal[''], None] = None

class HyDELLMResponse(BaseModel):
    hyde_answer: Optional[str] = None

class SetBackLLMResponse(BaseModel):
    step_back_question: Optional[str] = None
    step_back_answer: Optional[str] = None


# summarizeTitle generate by summarize llm
class SummarizeLLMResponse(BaseModel):
    title: str

# categoryInfo generate by category llm
class CategorizeLLMResponse(BaseModel):
    categories : list[str] = []

class RecommendationItem(BaseModel):
    name: str
    url: str
    reason: str

# ModRecommendationInfo generate by mod recommendation llm
class ModRecommendLLMResponse(BaseModel):
    recommendations: list[RecommendationItem] = []


    



    