# fastapi
from fastapi import APIRouter

# models
from model import QuestionRequest, ConversationCreate, ChatMessage

# service
from service import handle_rag_question, handle_create_conversation, handle_add_message, handle_get_conversation_messages



router = APIRouter()

@router.post("/question")
async def question(questionRequest: QuestionRequest):
    response = handle_rag_question(questionRequest)
    return response

@router.post("/conversation")
def create_conversation(conv: ConversationCreate):
    response = handle_create_conversation(conv)
    return response

@router.post("/message")
def add_message(chat: ChatMessage):
    response = handle_add_message(chat)
    return response

@router.get("/conversation/{conversation_id}")
def get_conversation_messages(conversation_id: str):
    response = handle_get_conversation_messages(conversation_id)
    return response

    



