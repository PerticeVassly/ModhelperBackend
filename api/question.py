from fastapi import APIRouter, Depends, Request
from model import *
from service import *

router = APIRouter()

@router.post("/question", response_model = QuestionResponse)
async def question(request: QuestionRequest,
                   rawRequest : Request , 
                   userInfo: UserInfo = Depends(get_current_user)) -> QuestionResponse:
    plain = rawRequest.query_params.get("key") == "plain"
    response = await handle_question(request, userInfo, plainQues=plain)
    return response

@router.post("/conversation", response_model = CreateConversationResponse)
def create_conversation(request: CreateConversationRequest,
                        userInfo: UserInfo = Depends(get_current_user)) -> CreateConversationResponse:
    response = handle_create_conversation(request, userInfo)
    return response

@router.get("/conversation/{conversation_id}", response_model = list[GetConversationMessagesResponseItem])
def get_conversation_messages(conversation_id: str,
                              userInfo: UserInfo = Depends(get_current_user)) -> list[GetConversationMessagesResponseItem]:
    response = handle_get_conversation_messages(conversation_id, userInfo)
    return response

@router.delete("/conversation/{conversation_id}", response_model = DeleteConversationResponse)
def delete_conversation(conversation_id: str,
                        userInfo: UserInfo = Depends(get_current_user)) -> DeleteConversationResponse:
    response = handle_delete_conversation(conversation_id, userInfo)
    return response

@router.get("/conversations", response_model = list[GetAllConversationsResponseItem])
def get_all_conversations(userInfo: UserInfo = Depends(get_current_user)) -> list[GetAllConversationsResponseItem]:
    response = handle_get_all_conversations(userInfo)
    return response

    



