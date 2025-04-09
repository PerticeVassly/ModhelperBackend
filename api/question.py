from fastapi import APIRouter, Depends
from model import QuestionRequest, ConversationCreate, ChatMessage, UserInfo
from service import handle_rag_question, handle_create_conversation, handle_add_message, handle_get_conversation_messages, get_current_user

router = APIRouter()

@router.post("/question")
async def question(questionRequest: QuestionRequest,
                   userInfo: UserInfo = Depends(get_current_user)):
    response = handle_rag_question(questionRequest, userInfo)
    return response

@router.post("/conversation")
def create_conversation(conv: ConversationCreate,
                        userInfo: UserInfo = Depends(get_current_user)):
    response = handle_create_conversation(conv, userInfo)
    return response

@router.post("/message")
def add_message(chat: ChatMessage,
                userInfo: UserInfo = Depends(get_current_user)):
    response = handle_add_message(chat, userInfo)
    return response

@router.get("/conversation/{conversation_id}")
def get_conversation_messages(conversation_id: str,
                              userInfo: UserInfo = Depends(get_current_user)):
    response = handle_get_conversation_messages(conversation_id, userInfo)
    return response

    



