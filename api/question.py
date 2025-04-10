from fastapi import APIRouter, Depends
from model import QuestionRequest, CreateConversationRequest, UserInfo
from service import handle_rag_question, handle_create_conversation, handle_get_conversation_messages, get_current_user, handle_delete_conversation

router = APIRouter()

@router.post("/question")
def question(request: QuestionRequest,
                   userInfo: UserInfo = Depends(get_current_user)):
    response = handle_rag_question(request, userInfo)
    return response

@router.post("/conversation")
def create_conversation(request: CreateConversationRequest,
                        userInfo: UserInfo = Depends(get_current_user)):
    response = handle_create_conversation(request, userInfo)
    return response

@router.get("/conversation/{conversation_id}")
def get_conversation_messages(conversation_id: str,
                              userInfo: UserInfo = Depends(get_current_user)):
    response = handle_get_conversation_messages(conversation_id, userInfo)
    return response

@router.delete("/conversation/{conversation_id}")
def delete_conversation(conversation_id: str,
                        userInfo: UserInfo = Depends(get_current_user)):
    response = handle_delete_conversation(conversation_id, userInfo)
    return response

    



