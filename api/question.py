from fastapi import APIRouter, Depends
from model import QuestionRequest, CreateConversationRequest, ChatRequest, UserInfo
from service import handle_rag_question, handle_create_conversation, handle_add_message, handle_get_conversation_messages, get_current_user

router = APIRouter()

@router.post("/question")
async def question(request: QuestionRequest,
                   userInfo: UserInfo = Depends(get_current_user)):
    response = handle_rag_question(request, userInfo)
    return response

@router.post("/conversation")
async def create_conversation(request: CreateConversationRequest,
                        userInfo: UserInfo = Depends(get_current_user)):
    response = handle_create_conversation(request, userInfo)
    return response

@router.post("/message")
async def add_message(request: ChatRequest,
                userInfo: UserInfo = Depends(get_current_user)):
    response = handle_add_message(request, userInfo)
    return response

@router.get("/conversation/{conversation_id}")
async def get_conversation_messages(conversation_id: str,
                              userInfo: UserInfo = Depends(get_current_user)):
    response = handle_get_conversation_messages(conversation_id, userInfo)
    return response

    



