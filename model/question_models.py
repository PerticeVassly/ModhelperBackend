from pydantic import BaseModel

class QuestionRequest(BaseModel):
    conversation_id: str
    question: str

class CreateConversationRequest(BaseModel):
    title: str