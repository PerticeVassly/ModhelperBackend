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
    reference: list[dict[str, str]]
    assistant_message : str
    timestamp : datetime

    model_config = ConfigDict(arbitrary_types_allowed=True)

class Guide(BaseModel):
    guide_page_url : str
    guide_name : str
    content : str

class Boime(BaseModel):
    classification : str
    name : str
    biome_url : str
    description : str

class Item(BaseModel):
    classification : str
    name : str
    item_url : str
    description : str

class Entity(BaseModel):
    classification : str
    name : str
    entity_url : str
    description : str

class Structure(BaseModel):
    classification : str
    name : str
    structure_url : str
    description : str

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
    items : list[Item] = []
    biomes : list[Boime] = []
    entities : list[Entity] = []
    structures : list[Structure] = []

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