from llm import LLMClient, RAGLLM, NonRAGLLM, LLMClient, ExtractorLLM, SummarizeLLM
from db import conversationsCollection, messagesCollection, vectorDB
from model import CreateConversationRequest, MinecraftModKeywords, QuestionRequest, UserInfo, ConversationInfo, MessageInfo
from bson import ObjectId
from datetime import datetime
from config import settings
from fastapi import HTTPException
import logging
import asyncio

logger = logging.getLogger("service")

async def handle_question(questionRequest : QuestionRequest, userInfo : UserInfo):
    # check if the user do has this conversation
    __check_do_have_conversation(userInfo, questionRequest.conversation_id)
    # fetch history
    history = messagesCollection.find_all_by_conversation_id(conversation_id=ObjectId(questionRequest.conversation_id))
    # chat with llm
    non_rag = NonRAGLLM(
        llm_client = LLMClient(api_key=settings.LLM_API_KEY, messages=history))
    response = non_rag.generate_response(question=questionRequest.question)
    # save message
    new_message = MessageInfo(
        conversation_id=ObjectId(questionRequest.conversation_id),
        user_message=questionRequest.question,
        reference=[],
        assistant_message=response,
        timestamp=datetime.now()
    )
    messagesCollection.insert_one(message=new_message)
    # async summarize
    history.append(new_message)
    if not len(history) > 3:
        asyncio.create_task(__summarize(messages=history, concersation_id=questionRequest.conversation_id))
    return {
        "response": response,
        "reference": []
    }

async def handle_rag_question(questionRequest : QuestionRequest, userInfo: UserInfo):
     # check if the user do has this conversation
    __check_do_have_conversation(userInfo, questionRequest.conversation_id)
    # fetch history
    history = messagesCollection.find_all_by_conversation_id(conversation_id=ObjectId(questionRequest.conversation_id))
    # classify the question topic
    topic_name = __classify(questionRequest.question)
    # extract keypoints {key : value}
    keypoints = __extract(
        text=questionRequest.question,
        topic_name=topic_name)
    # retrieve context
    context = __retrieve(
        keypoints=keypoints, 
        topic_name=topic_name, 
        text=questionRequest.question)
    # chat with llm
    rag = RAGLLM(
        llm_client = LLMClient(api_key=settings.LLM_API_KEY, messages=history))
    response = rag.generate_response(
        question=questionRequest.question,
        context=context,
        topic_name=topic_name)
    # save message
    new_message = MessageInfo(
        conversation_id=ObjectId(questionRequest.conversation_id),
        user_message=questionRequest.question,
        reference=context,
        assistant_message=response,
        timestamp=datetime.now()
    )
    messagesCollection.insert_one(message=new_message)
    # async summarize
    history.append(new_message)
    if not len(history) > 3:
        asyncio.create_task(__summarize(messages=history, concersation_id=questionRequest.conversation_id))
    return {
        "response": response,
        "reference": context
    }

def handle_create_conversation(request: CreateConversationRequest, userInfo : UserInfo):
    result = conversationsCollection.insert_one(conversation=ConversationInfo(
        user_id=ObjectId(userInfo.id),
        title=request.title,
        created_at=datetime.now()
    ))
    logger.info(f"Conversation created with id: {result.inserted_id}")
    return {"id" : str(result.inserted_id), "title" : request.title}

def handle_delete_conversation(conversation_id : str, userInfo: UserInfo):
    # check if the user do has this conversation
    __check_do_have_conversation(userInfo, conversation_id)
    # delete conversation
    conversationsCollection.delete_one(ObjectId(conversation_id))
    messagesCollection.delete_many_by_conversation_id(conversation_id=ObjectId(conversation_id))

def handle_get_conversation_messages(conversation_id: str, userInfo: UserInfo):
    # check if the user do has this conversation
    __check_do_have_conversation(userInfo, conversation_id)
    # fetch history
    msgs = messagesCollection.find_all_by_conversation_id(conversation_id=ObjectId(conversation_id))
    result = []
    for msg in msgs:
        result.append({
            "user": msg.user_message,
            "reference": msg.reference,
            "assistant": msg.assistant_message,
            "time": msg.timestamp
        })
    return result

def handle_get_all_conversations(userInfo: UserInfo):
    conversations = conversationsCollection.find_all_by_user_id(user_id=ObjectId(userInfo.id))
    result = []
    for conv in conversations:
        result.append({
            "id": str(conv.id),
            "title": conv.title,
        })
    return result

async def __summarize(messages : list[MessageInfo], concersation_id : str):
    # chat with llm 
    conversation = conversationsCollection.find_one(ObjectId(concersation_id))
    llm = SummarizeLLM(
        llm_client = LLMClient(api_key=settings.LLM_API_KEY))
    json_response = llm.summarize(messages=messages, old_name=conversation.title)
    new_title = json_response["title"][0]
    # save new title
    conversationsCollection.update_ones_title(
        conversation_id=ObjectId(concersation_id),
        new_title=new_title
    )        


def __classify(text : str) -> str: 
  # TODO wait for more type of mod
  return "Minecraft Mod"

def __get_keywords(topic_name : str) -> list:
    if topic_name == "Minecraft Mod":
        return MinecraftModKeywords
    else:
        raise ValueError(f"Unsupported topic name: {topic_name}")
        return []

def __extract(text : str, topic_name : str) -> list[dict]:
    keywords = __get_keywords(topic_name)
    # extractor = ExtractorLLM(
    #     llm_client = LLMClient(api_key=settings.LLM_API_KEY))
    # keypoints = extractor.extract(text, keywords, topic_name)
    # TODO for efficiency now only return {key : []}
    keypoints = {key: [] for key in keywords }
    return keypoints

def __check_do_have_conversation(userInfo: UserInfo, conversation_id: str) -> bool:
    # check if the user do has this conversation
    conversation = conversationsCollection.find_one(ObjectId(conversation_id))
    if not conversation or conversation.user_id != userInfo.id:
        raise HTTPException(status_code=400, detail="Conversation not found or user not matching")
        return False
    return True

def __retrieve(keypoints : dict, text : str, topic_name) -> list[dict[str, str]]:
    context = [] # { description : str, content : str }
    # TODO now just retrieve the user direct input
    searched_entries = vectorDB.search(query=text.strip(), top_k=3)
    for entry in searched_entries:
        context.append({
            "description": entry["id"],
            "content": entry["text"],
        })
    return context


