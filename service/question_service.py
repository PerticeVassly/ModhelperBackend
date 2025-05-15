from llm import LLMClient, RAGLLM, NonRAGLLM, LLMClient, ExtractorLLM, SummarizeLLM
from db import conversationsRepository, messagesRepository, metaInfosRepository, vectorDB, all_mod_names, all_item_names, all_entity_names, all_structure_names, all_biome_names
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
    context = [] 
    searched_entries = vectorDB.search(query=text.strip(), top_k=8)
    searched_entries = rerank_and_expand(searched_entries, extractedInfo)
    logger.info(f"rerank and expand entries: {searched_entries}")
    num_extra = 3
    for entry in searched_entries:
        if (num_extra <= 0):
            break
        if entry.score == 1:
            context.append(
                Reference(
                    description=entry.metadata.document_name,
                    content=entry.document
                )
            )
        elif entry.score > 0.6 and entry.score < 1:
            context.append(
                Reference(
                    description=entry.metadata.document_name,
                    content=entry.document
                )
            )
            num_extra -= 1
    return context

def rerank_and_expand(entries : list[Entry], extractedInfo : ExtractedInfo) -> list[Entry]:
    std_mod_names = [
        match for mod_name in extractedInfo.extraction_fields.mods
        if (match := __fuzzy_match(query=mod_name, candidates=all_mod_names, threshold=90)) is not None
    ]
    logger.info(f"std_mod_names: {std_mod_names}")
    std_item_names = [
        match for item_name in extractedInfo.extraction_fields.items
        if (match := __fuzzy_match(query=item_name, candidates=all_item_names, threshold=90)) is not None
    ]
    logger.info(f"std_item_names: {std_item_names}")
    std_boime_names = [
        match for boime_name in extractedInfo.extraction_fields.biomes
        if (match := __fuzzy_match(query=boime_name, candidates=all_biome_names, threshold=90)) is not None
    ]
    logger.info(f"std_boime_names: {std_boime_names}")
    std_entity_names = [
        match for entity_name in extractedInfo.extraction_fields.entities
        if (match := __fuzzy_match(query=entity_name, candidates=all_entity_names, threshold=90)) is not None
    ]
    logger.info(f"std_entity_names: {std_entity_names}")
    std_structure_names = [
        match for structure_name in extractedInfo.extraction_fields.structures
        if (match := __fuzzy_match(query=structure_name, candidates=all_structure_names, threshold=80)) is not None
    ]
    # based on extractedInfo
    

    def adjust_score(entry: Entry) -> int:
        base_score = entry.distance
        rule_socre = 0.0
        if entry.metadata.mod_name in std_mod_names:
            rule_socre += 1
        if (entry.metadata.type == "introduction" and extractedInfo.intention == "basic_info") or \
            (entry.metadata.type == "guide" and extractedInfo.intention == "gameplay_guide") :
            rule_socre += 1
        rule_score = min(rule_socre, 1.0)
        alpha = 0.8
        return int(base_score * (1 - alpha) + rule_score * alpha)
    
    # rerank
    entries = sorted(entries, key=lambda x: adjust_score(x), reverse=True)

    # expand
    for item_name in std_item_names:
        item = metaInfosRepository.find_item_by_name(item_name)
        if item:
            entries.insert(0,
                Entry(
                    id=str(item.name),
                    document=item.description,
                    metadata=DocumentMetadata(
                        id=str(item.name),
                        document_name=item.name,
                        url=item.item_url,
                        type=DocumentEnum.generalItem,
                        mod_name=""
                    ),
                    distance=1,
                    score = 1
                )
            )
    for boime_name in std_boime_names:
        boime = metaInfosRepository.find_biome_by_name(boime_name)
        if boime:
            entries.insert(0,
                Entry(
                    id=str(boime.name),
                    document=boime.description,
                    metadata=DocumentMetadata(
                        id=str(boime.name),
                        document_name=boime.name,
                        url=boime.biome_url,
                        type=DocumentEnum.generalItem,
                        mod_name=""
                    ),
                    distance=1,
                    score = 1
                )
            )

    for entity_name in std_entity_names:
        entity = metaInfosRepository.find_entity_by_name(entity_name)
        if entity:
            entries.insert(0,
                Entry(
                    id=str(entity.name),
                    document=entity.description,
                    metadata=DocumentMetadata(
                        id=str(entity.name),
                        document_name=entity.name,
                        url=entity.entity_url,
                        type=DocumentEnum.generalItem,
                        mod_name=""
                    ),
                    distance = 1,
                    score = 1
                )
            )
    
    for structure_name in std_structure_names:
        structure = metaInfosRepository.find_structure_by_name(structure_name)
        if structure:
            entries.insert(0,
                Entry(
                    id=str(structure.name),
                    document=structure.description,
                    metadata=DocumentMetadata(
                        id=str(structure.name),
                        document_name=structure.name,
                        url=structure.structure_url,
                        type=DocumentEnum.generalItem,
                        mod_name=""
                    ),
                    distance = 1,
                    score = 1
                )
            )

    return entries


def __fuzzy_match(query: str, candidates: list[str], threshold: int) -> list[str]:
    matches = process.extract(query, candidates, scorer=fuzz.partial_ratio)
    return ([match for match, score, _ in matches if score >= threshold][:1] or [None])[0]


