from pydantic import BaseModel, EmailStr
from .domain_models import Reference, ModVO
from .db_models import Mod

# auth
class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class RegisterResponse(BaseModel):
    message: str

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str

# question
class QuestionRequest(BaseModel):
    conversation_id: str
    question: str

class QuestionResponse(BaseModel):
    response: str
    reference: list[Reference]
        
class CreateConversationRequest(BaseModel):
    title: str

class CreateConversationResponse(BaseModel):
    id: str
    title: str 

class GetConversationMessagesResponseItem(BaseModel):
    user: str
    reference: list[Reference]
    assistant: str
    time: str
    
class DeleteConversationResponse(BaseModel):
    message: str

class GetAllConversationsResponseItem(BaseModel):
    id: str
    title: str

# mod
class GetModResponse(BaseModel):
    mods: list[ModVO] = []

class AddModRequest(BaseModel):
    mod: Mod

class AddModResponse(BaseModel):
    message: str

class DeleteModResponse(BaseModel):
    message: str

class ToggleFavoriteModResponse(BaseModel):
    message: str