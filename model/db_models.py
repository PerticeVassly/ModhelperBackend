from pydantic import BaseModel, EmailStr, ConfigDict
from pydantic import Field
from typing import Optional
from bson import ObjectId
from datetime import datetime

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
    assistant_message : str
    timestamp : datetime

    model_config = ConfigDict(arbitrary_types_allowed=True)