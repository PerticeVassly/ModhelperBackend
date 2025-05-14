# from abc import ABC, abstractclassmethod
# from typing import List, Dict, Optional, Any
# from model import *
    
# @dataclass
# class ModMetadata:
#     name: str
#     tags: List[str]
#     description: str
#     support_platform: ModPlatform
#     download_url: Optional[str]
    
# class BaseMetadataDB(ABC):
#     @abstractclassmethod
#     def add(self, mod: ModMetadata) -> bool: ...
    
#     @abstractclassmethod
#     def get(self, name: str) -> Optional[ModMetadata]: ...
    
#     @abstractclassmethod
#     def search(self, keyword: str) -> List[ModMetadata]: ...

# TODO tobe formated add other db

# class BaseVectorDB(ABC):
#     @abstractclassmethod
#     def add(self, mod_name: str, text: str) -> bool: ...
    
#     @abstractclassmethod
#     def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]: ...

# class BaseGraphDB(ABC):
#     @abstractclassmethod
#     def add(self, relaton: ModRelation) -> bool: ...
    
#     @abstractclassmethod
#     def search_related(self, mod_name: str) -> List[ModRelation]: ...
    
#     @abstractclassmethod
#     def check_conflict(self, mod_name1: str, mod_name2: str) -> bool: ...


