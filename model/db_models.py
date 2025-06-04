from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional
from bson import ObjectId
from datetime import datetime
from enum import Enum

class UserInfo(BaseModel):
    id : Optional[ObjectId] = Field(default=None, alias="_id")
    username: str
    email : EmailStr
    password : str
    favorite_mods : list[str] = []

    model_config = ConfigDict(arbitrary_types_allowed=True)

class ConversationInfo(BaseModel):
    id : Optional[ObjectId] = Field(default=None, alias="_id")
    user_id : ObjectId
    title: str

    model_config = ConfigDict(arbitrary_types_allowed=True)

class MessageInfo(BaseModel):
    id : Optional[ObjectId] = Field(default=None, alias="_id")
    conversation_id : ObjectId
    user_message : str
    reference: list[dict[str, str]] = []
    assistant_message : str
    timestamp : datetime

    model_config = ConfigDict(arbitrary_types_allowed=True)

class AdminInfo(BaseModel):
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    user_id: ObjectId
    username: str

    model_config = ConfigDict(arbitrary_types_allowed=True)

class Guide(BaseModel):
    guide_page_url : str
    guide_name : str
    content : str

class GeneralItem(BaseModel):
    name : str
    url : str
    description : str

class Guide(BaseModel):
    guide_page_url : str
    guide_name : str
    content : str

class Mod(BaseModel):
    mod_name : str
    support_platforms : list[str] = []
    run_methods : list[str] = []
    run_environments : list[str] = []
    categories : list[str] = []
    tags : list[str] = []
    related_links : list[str] = []
    detail_page_url : str
    introduction : str
    guides : list[Guide] = []
    items : list[GeneralItem] = []
    biomes : list[GeneralItem] = []
    entities : list[GeneralItem] = []
    structures : list[GeneralItem] = []


class DocumentEnum(str, Enum):
    introduction = "introduction"
    guide = "guide"
    generalItem = "generalItem"
    other = "other"

class DocumentMetadata(BaseModel):
    id : Optional[str] = None
    document_name: str
    url: str
    type: DocumentEnum
    mod_name: str
    chunk_index: Optional[int] = None
    total_chunks: Optional[int] = None
    
class ModRelationType(Enum):
    dependency = "depends-on"
    interaction = "interacts-with"
    confliction = "conflicts-with"

class ModRelation(BaseModel):
    source_mod: str
    target_mod: str
    relationship_type: ModRelationType

class ModPlatform(Enum):
    JAVA = "java"
    BEDROCK = "bedrock"
    CROSS = "cross-platform"

class Entry(BaseModel):
    id: str
    document: str
    metadata: DocumentMetadata
    distance: float
    score : float

from enum import Enum

class Category(Enum):
    TECH = "科技"
    MAGIC = "魔法"
    ADVENTURE = "冒险"
    FARMING = "农业"
    DECORATION = "装饰"
    SECURITY = "安全"
    TIB = "TIB"
    RESOURCE = "资源"
    WORLD = "世界"
    BIOMES = "群系"
    CREATURE = "生物"
    ENERGY = "能源"
    STORAGE = "存储"
    LOGISTICS = "物流"
    ITEM = "道具"
    REDSTONE = "红石"
    FOOD = "食物"
    MODEL = "模型"
    GUIDE = "指南"
    DESTRUCTION = "破坏"
    OVERHAUL = "魔改"
    MEME = "meme"
    UTILITY = "实用"
    SUPPORT = "辅助"
    CHINESE_STYLE = "中式"
    JAPANESE_STYLE = "日式"
    WESTERN_STYLE = "西式"
    HORROR = "恐怖"
    BUILDING = "建材"
    SURVIVAL = "生存"
    COMMAND = "指令"
    OPTIMIZATION = "优化"
    CHINA_ORIGIN = "国创"
    LEVEL = "关卡"
    STRUCTURE = "结构"

class ModBriefIntroduction(BaseModel):
    mod_name: str
    categories: list[str] = []
    introduction: str
    detail_page_url : str

def str_to_category(value: str) -> Category:
    for category in Category:
        if category.value == value:
            return category
    return ""

def category_to_str(category: Category) -> str:
    if not isinstance(category, Category):
        return ""
    return category.value

def all_category_names() -> list[str]:
    return [c.value for c in Category]

