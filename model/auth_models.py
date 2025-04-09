from pydantic import BaseModel, EmailStr
from typing import Optional

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class ConversationCreate(BaseModel):
    user_id: str
    title: str

class ChatMessage(BaseModel):
    conversation_id: str
    user_message: str
    assistant_message: str
