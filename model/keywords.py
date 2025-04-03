from pydantic import BaseModel, Field
from abc import ABC, abstractmethod
from typing import List

# todo() how to classify which game the user is talking about ?
class Keywords(ABC, BaseModel):
    """
    Keyword model

    Contains only the game name
    """
    game_name: str

    class Config:
      min_anystr_length = 1
      anystr_strip_whitespace = True
    
    def __init__(self,  game_name: str):
      self.game_name = game_name

    def get_game_name(self):
      return self.game_name
    

# todo() how to support multi mods in one question ?
class MinecraftModKeywords(Keywords):
    """
    The key points when understand a MC Mod related question
    """
    mod_names: str = Field(default=None)
    versions: str = Field(default=None)
    item_names: List[str] = Field(default=None)
    block_names: List[str] = Field(default=None)
    world_name: List[str] = Field(default=None)

    