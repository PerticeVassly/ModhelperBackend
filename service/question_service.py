from llm import *
from db import conversationsRepository, messagesRepository, metaInfosRepository, vectorDB, all_mod_names, all_item_names, all_entity_names, all_structure_names, all_biome_names
from model import *
from bson import ObjectId
from datetime import datetime
from config import settings
from fastapi import HTTPException
import logging
import asyncio
from rapidfuzz import fuzz, process
from typing import Callable, Awaitable

logger = logging.getLogger("service")

async def preProcess(question: str) -> PreProcessResult:
    # async get all require response from llm
    classify_llm = ClassifyLLM(
        llm_client = LLMClient(api_key=settings.LLM_API_KEY))
    extract_llm = ExtractLLM(
        llm_client = LLMClient(api_key=settings.LLM_API_KEY))
    intention_analyze_llm = IntentionAnalyzeLLM(
        llm_client = LLMClient(api_key=settings.LLM_API_KEY))
    hyde_llm = HyDELLM(
        llm_client = LLMClient(api_key=settings.LLM_API_KEY))
    set_back_llm = SetBackLLM(
        llm_client = LLMClient(api_key=settings.LLM_API_KEY))
    
    tasks = [
        classify_llm.classify(question=question),
        extract_llm.extract(input=question),
        intention_analyze_llm.analyze_intention(question=question),
        hyde_llm.hyde(question=question),
        set_back_llm.set_back(question=question)
    ]

    results = await asyncio.gather(*(task() for task in tasks))

    return PreProcessResult(
        is_mc=results[0].is_mc,
        extracted_fields=results[1].extraction_fields,
        intention=results[2].intention,
        hyde_answer=results[3].hyde_answer,
        step_back_question=results[4].step_back_question,
        step_back_answer=results[4].step_back_answer
    )

async def handle_question(questionRequest : QuestionRequest, userInfo : UserInfo) -> QuestionResponse:
    preProcessResult = await preProcess(question=questionRequest.question)
    logger.info(f"preProcessResult: {preProcessResult}")
    if preProcess.is_mc: 
        return await __handle_rag_question(questionRequest=questionRequest, userInfo=userInfo, preProcessResult=preProcessResult)
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

async def __handle_rag_question(questionRequest : QuestionRequest, userInfo: UserInfo, preProcessResult : PreProcessResult) -> QuestionResponse:
     # check if the user do has this conversation
    __check_do_have_conversation(userInfo, questionRequest.conversation_id)
    # fetch history
    messages = messagesRepository.find_all_by_conversation_id(conversation_id=ObjectId(questionRequest.conversation_id))
    # retrieve context based on extracted info
    if preProcessResult.intention == "mod_recommendation" or preProcessResult.intention == "pack_customization":
        context = []
        categorizer = CategorizeLLM(
            llm_client = LLMClient(api_key=settings.LLM_API_KEY, messages=messages))
        categoryInfo = categorizer.categorize(
            text=questionRequest.question,
        )
        logger.info(f"categoryInfo: {categoryInfo}")
        filtered_mod_brief_introductions = metaInfosRepository.filter_mods(
            categories=categoryInfo.categories,
        )
        logger.info(f"filtered_mod_names: {[mod.mod_name for mod in filtered_mod_brief_introductions]}")
        recommender = ModRecommendLLM(
            llm_client = LLMClient(api_key=settings.LLM_API_KEY, messages=messages))
        response = recommender.recommend(
            text=questionRequest.question,
            mods=filtered_mod_brief_introductions
        )
    else:
        # chat with llm
        context = __retrieve(
            preProcessResult=preProcessResult,
            text=questionRequest.question)
        rag = RAGLLM(
            llm_client = LLMClient(api_key=settings.LLM_API_KEY, messages=messages))
        response = rag.chat(
            question=questionRequest.question,
            context=context)
        
    logger.info(f"contexts: {[ref.description for ref in context]}")
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
    return DeleteConversationResponse(
        message="Conversation deleted successfully"
    )

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

def __retrieve(preProcessResult : PreProcessResult, text : str) -> list[Reference]:
    searched_entries = vectorDB.search(query=text.strip() + preProcessResult.answer, top_k=3)
    stepback_searched_entries = vectorDB.search(query=preProcessResult.stepBackQuestion + preProcessResult.stepBackQuestionAnswer, top_k=3)
    all_entries = searched_entries + stepback_searched_entries
    all_refs = __generate_references(all_entries, preProcessResult)
    # logger.info(f"rerank and expand entries: {searched_entries}")
    return all_refs

def __generate_references(entries : list[Entry], preProcessResult : PreProcessResult) -> list[Reference]:
    std_mod_names = [
        match for mod_name in preProcessResult.extraction_fields.mods
        if (match := __fuzzy_match(query=mod_name, candidates=all_mod_names, threshold=80)) is not None
    ]
    std_item_names = [
        match for item_name in preProcessResult.extraction_fields.items
        if (match := __fuzzy_match(query=item_name, candidates=all_item_names, threshold=90)) is not None
    ]
    std_boime_names = [
        match for boime_name in preProcessResult.extraction_fields.biomes
        if (match := __fuzzy_match(query=boime_name, candidates=all_biome_names, threshold=90)) is not None
    ]
    std_entity_names = [
        match for entity_name in preProcessResult.extraction_fields.entities
        if (match := __fuzzy_match(query=entity_name, candidates=all_entity_names, threshold=90)) is not None
    ]
    std_structure_names = [
        match for structure_name in preProcessResult.extraction_fields.structures
        if (match := __fuzzy_match(query=structure_name, candidates=all_structure_names, threshold=90)) is not None
    ]
    logger.info(f"std_names_matched: mod={std_mod_names}, item={std_item_names}, biome={std_boime_names}, entity={std_entity_names}, structure={std_structure_names}")

    def __adjust_score(entry: Entry) -> float:
        base_score = entry.distance
        rule_socre = 0.0
        if entry.metadata.mod_name in std_mod_names:
            rule_socre += 1
        if (entry.metadata.type == "introduction" and preProcessResult.intention == "basic_info") or \
            (entry.metadata.type == "guide" and preProcessResult.intention == "gameplay_guide") :
            rule_socre += 1
        rule_score = min(rule_socre, 1.0)
        alpha = 0.2
        return float(base_score * (1 - alpha) + rule_score * alpha)
     
    # TODO 如果没有模组名称匹配，使用投票法选择所有个entry中出现最多的模组名称作为模组名称
    if not std_mod_names:
        mod_name_count = {}
        for entry in entries:
            if entry.metadata.mod_name not in mod_name_count:
                mod_name_count[entry.metadata.mod_name] = 0
            mod_name_count[entry.metadata.mod_name] += 1
        # sort by count
        std_mod_names = sorted(mod_name_count.items(), key=lambda x: x[1], reverse=True)
        std_mod_names = [mod_name for mod_name, _ in std_mod_names[:1]]

    # 如果已经确定了模组名称，那么所有entry必须是关于这个模组的    
    if std_mod_names:
        entries = [entry for entry in entries if entry.metadata.mod_name in std_mod_names]
    # rerank
    entries = sorted(entries, key=lambda x: __adjust_score(x), reverse = True)
   
    logger.info(f"rerank entries names: {[entry.metadata.document_name for entry in entries]}")
    references : list[Reference] = []

    # if there is no std_name matched use the retrieved entries
    num_extra = 2
    entries = entries[:num_extra]
    full_documents_map = {}
    for entry in entries:
        full_document = metaInfosRepository.find_full_document_by_metadata(metadata=entry.metadata)
        full_documents_map[entry.metadata.document_name] = full_document
    for key, value in full_documents_map.items():
        references.append(Reference(
            description=key,
            content=value
        ))
    
    # expand
    for item_name in std_item_names:
        item, mod_belonging = metaInfosRepository.find_item_by_name(item_name)
        if item and item.description and (mod_belonging in std_mod_names or not std_mod_names):
            # insert at the beginning
            references.insert(0, Reference(
                description=item.name,
                content=item.description
            ))
    for boime_name in std_boime_names:
        boime, mod_belonging = metaInfosRepository.find_biome_by_name(boime_name)
        if boime and boime.description and (mod_belonging in std_mod_names or not std_mod_names):
            references.insert(0, Reference(
                description=boime.name,
                content=boime.description
            ))
    for entity_name in std_entity_names:
        entity, mod_belonging = metaInfosRepository.find_entity_by_name(entity_name)
        if entity and entity.description and (mod_belonging in std_mod_names or not std_mod_names):
            references.insert(0, Reference(
                description=entity.name,
                content=entity.description
            ))
    for structure_name in std_structure_names:
        structure, mod_belonging = metaInfosRepository.find_structure_by_name(structure_name)
        if structure and structure.description and (mod_belonging in std_mod_names or not std_mod_names):
            references.insert(0, Reference(
                description=structure.name,
                content=structure.description
            ))
    return references

def __fuzzy_match(query: str, candidates: list[str], threshold: int) -> list[str]:
    matches = process.extract(query, candidates, scorer=fuzz.partial_ratio)
    return ([match for match, score, _ in matches if score >= threshold][:1] or [None])[0]


