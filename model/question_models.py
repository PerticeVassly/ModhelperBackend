from pydantic import BaseModel

class QuestionRequest(BaseModel):
    conversation_id: str
    question: str

class CreateConversationRequest(BaseModel):
    title: str

class ChatRequest(BaseModel):
    conversation_id: str
    user_message: str
    assistant_message: str

# TODO add response models