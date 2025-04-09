from pydantic import BaseModel, EmailStr
from pydantic import Field
from typing import Optional
from bson import ObjectId

class UserInfo(BaseModel):
    id : Optional[ObjectId] = Field(alias="_id")
    username: str
    email : EmailStr
    password : str

class ConversationInfo(BaseModel):
    id : Optional[ObjectId] = Field(alias="_id")
    user_id : ObjectId
    title: str

class MessageInfo(BaseModel):
    id : Optional[ObjectId] = Field(alias="_id")
    conversation_id : ObjectId
    user_message : str
    assistant_message : str
    timestamp : str