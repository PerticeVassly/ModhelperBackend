from abc import ABC, abstractclassmethod
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum

class ModPlatform(Enum):
    JAVA = "java"
    BEDROCK = "bedrock"
    CROSS = "cross-platform"
    
@dataclass
class ModMetadata:
    name: str
    tags: List[str]
    description: str
    support_platform: ModPlatform
    download_url: Optional[str]
    

class ModRelationType(Enum):
    dependency = "depends-on"
    interaction = "interacts-with"
    confliction = "conflicts-with"

@dataclass
class ModRelation:
    source_mod: str
    target_mod: str
    relationship_type: ModRelationType

class BaseMetadataDB(ABC):
    @abstractclassmethod
    def add(self, mod: ModMetadata) -> bool: ...
    
    @abstractclassmethod
    def get(self, name: str) -> Optional[ModMetadata]: ...
    
    @abstractclassmethod
    def search(self, keyword: str) -> List[ModMetadata]: ...

class BaseVectorDB(ABC):
    @abstractclassmethod
    def add(self, mod_name: str, text: str) -> bool: ...
    
    @abstractclassmethod
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]: ...

class BaseGraphDB(ABC):
    @abstractclassmethod
    def add(self, relaton: ModRelation) -> bool: ...
    
    @abstractclassmethod
    def search_related(self, mod_name: str) -> List[ModRelation]: ...
    
    @abstractclassmethod
    def check_conflict(self, mod_name1: str, mod_name2: str) -> bool: ...


