from pydantic import BaseModel

class QuestionRequest(BaseModel):
    conversation_id: str
    question: str

class ConversationCreate(BaseModel):
    title: str

class ChatMessage(BaseModel):
    conversation_id: str
    user_message: str
    assistant_message: str