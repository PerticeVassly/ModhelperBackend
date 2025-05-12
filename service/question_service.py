from llm import LLMClient, RAGLLM, NonRAGLLM, LLMClient, ExtractorLLM, SummarizeLLM
from db import conversationsRepository, messagesRepository, vectorDB, all_mod_names
from model import *
from bson import ObjectId
from datetime import datetime
from config import settings
from fastapi import HTTPException
import logging
import asyncio
from rapidfuzz import fuzz, process

logger = logging.getLogger("service")

async def handle_question(questionRequest : QuestionRequest, userInfo : UserInfo) -> QuestionResponse:
    extractor = ExtractorLLM(
        llm_client = LLMClient(api_key=settings.LLM_API_KEY))
    extractedInfo = extractor.extract(input=questionRequest.question)
    # TODO: try deploy a small llm to do this to save time ?
    if extractedInfo.is_mc: 
        return await __handle_rag_question(questionRequest=questionRequest, userInfo=userInfo, extractedInfo=extractedInfo)
    else:
        return await __handle_non_rag_question(questionRequest=questionRequest, userInfo=userInfo) 
        
async def __handle_non_rag_question(questionRequest : QuestionRequest, userInfo : UserInfo) -> QuestionResponse:
    # check if the user do has this conversation
    __check_do_have_conversation(userInfo, questionRequest.conversation_id)
    # fetch history
    messages = messagesRepository.find_all_by_conversation_id(conversation_id=ObjectId(questionRequest.conversation_id))
    # chat with llm
    non_rag = NonRAGLLM(
        llm_client = LLMClient(api_key=settings.LLM_API_KEY, messages=messages))
    response = non_rag.chat(question=questionRequest.question)
    # save message
    new_message = MessageInfo(
        conversation_id=ObjectId(questionRequest.conversation_id),
        user_message=questionRequest.question,
        reference=[],
        assistant_message=response,
        timestamp=datetime.now()
    )
    messagesRepository.insert_one(message=new_message)
    # async summarize
    messages.append(new_message)
    if not len(messages) > 5:
        asyncio.create_task(__summarize(messages=messages, concersation_id=questionRequest.conversation_id))
    return QuestionResponse(
        response=response,
        reference=[]
    )

async def __handle_rag_question(questionRequest : QuestionRequest, userInfo: UserInfo, extractedInfo : ExtractedInfo) -> QuestionResponse:
     # check if the user do has this conversation
    __check_do_have_conversation(userInfo, questionRequest.conversation_id)
    # fetch history
    messages = messagesRepository.find_all_by_conversation_id(conversation_id=ObjectId(questionRequest.conversation_id))
    # retrieve context based on extracted info
    context = __retrieve(
        extractedInfo=extractedInfo,
        text=questionRequest.question)
    # chat with llm
    rag = RAGLLM(
        llm_client = LLMClient(api_key=settings.LLM_API_KEY, messages=messages))
    response = rag.chat(
        question=questionRequest.question,
        context=context)
    # save message
    new_message = MessageInfo(
        conversation_id=ObjectId(questionRequest.conversation_id),
        user_message=questionRequest.question,
        reference=[item.model_dump() for item in context],
        assistant_message=response,
        timestamp=datetime.now()
    )
    messagesRepository.insert_one(message=new_message)
    # async summarize
    messages.append(new_message)
    if not len(messages) > 3:
        asyncio.create_task(__summarize(messages=messages, concersation_id=questionRequest.conversation_id))
    return  QuestionResponse(
        response=response,
        reference=context
    )
def handle_create_conversation(request: CreateConversationRequest, userInfo : UserInfo) -> CreateConversationResponse:
    result = conversationsRepository.insert_one(conversation=ConversationInfo(
        user_id=ObjectId(userInfo.id),
        title=request.title,
        created_at=datetime.now()
    ))
    logger.info(f"Conversation created with id: {result.inserted_id}")
    return CreateConversationResponse(
        id=str(result.inserted_id),
        title=request.title
    )

def handle_delete_conversation(conversation_id : str, userInfo: UserInfo):
    # check if the user do has this conversation
    __check_do_have_conversation(userInfo, conversation_id)
    # delete conversation
    conversationsRepository.delete_one(ObjectId(conversation_id))
    messagesRepository.delete_many_by_conversation_id(conversation_id=ObjectId(conversation_id))

def handle_get_conversation_messages(conversation_id: str, userInfo: UserInfo) -> list[GetConversationMessagesResponseItem]:
    # check if the user do has this conversation
    __check_do_have_conversation(userInfo, conversation_id)
    # fetch history
    msgs = messagesRepository.find_all_by_conversation_id(conversation_id=ObjectId(conversation_id))
    result = []
    for msg in msgs:
        result.append(
            GetConversationMessagesResponseItem(
                user=msg.user_message,
                reference=msg.reference,
                assistant=msg.assistant_message,
                time=msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            )
        )
    return result

def handle_get_all_conversations(userInfo: UserInfo) -> list[GetAllConversationsResponseItem]:
    conversations = conversationsRepository.find_all_by_user_id(user_id=ObjectId(userInfo.id))
    result = []
    for conv in conversations:
        result.append(
            GetAllConversationsResponseItem(
                id=str(conv.id),
                title=conv.title
            )
        )
    return result

async def __summarize(messages : list[MessageInfo], concersation_id : str) -> None:
    # chat with llm 
    conversation = conversationsRepository.find_one(ObjectId(concersation_id))
    llm = SummarizeLLM(
        llm_client = LLMClient(api_key=settings.LLM_API_KEY))
    summarizeTitle = llm.summarize(messages=messages, old_name=conversation.title)
    new_title = summarizeTitle.title
    # save new title
    conversationsRepository.update_ones_title(
        conversation_id=ObjectId(concersation_id),
        new_title=new_title
    )        

def __check_do_have_conversation(userInfo: UserInfo, conversation_id: str) -> bool:
    # check if the user do has this conversation
    conversation = conversationsRepository.find_one(ObjectId(conversation_id))
    if not conversation or conversation.user_id != userInfo.id:
        raise HTTPException(status_code=400, detail="Conversation not found or user not matching")
    return True

def __retrieve(extractedInfo : ExtractedInfo, text : str) -> list[Reference]:
    context = [] # { description : str, content : str }
    # TODO now just retrieve the user direct input

    # use extractedInfo to filter
    mod_names = extractedInfo.extraction_fields.mod_name
    matched_names = []
    for name in mod_names:
        matches = __fuzzy_match(query = name, candidates=all_mod_names, threshold = 80)
        if matches:
            matched_names.append(matches[0])

    logger.info(f"Matched mod names: {matched_names} in {all_mod_names}")
    # if len == 0 required_mod_names = None
    required_mod_names = matched_names;
    required_article_type = None
    if extractedInfo.intention == intentionEnum.basic_info:
        required_article_type = "introduction"
    elif extractedInfo.intention == intentionEnum.gameplay_guide:
        required_article_type = "guide"

    # search
    searched_entries = vectorDB.search(query=text.strip(), required_article_type=required_article_type, required_mod_names=required_mod_names, top_k=3)
    for entry in searched_entries:
        logger.info(f"Found entry: {entry}")
        context.append(
            Reference(
                description=entry["id"],
                content=entry["document"],
            )
        )
    return context

def __fuzzy_match(query: str, candidates: list[str], threshold: int) -> list[str]:
    matches = process.extract(query, candidates, scorer=fuzz.partial_ratio)
    return [match for match, score, _ in matches if score >= threshold]

