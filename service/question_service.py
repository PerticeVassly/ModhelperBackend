from llm import LLMClient, RAGLLM, NonRAGLLM, LLMClient, ExtractorLLM
from db import conversationsCollection, messagesCollection, vectorDB
from model import CreateConversationRequest, MinecraftModKeywords, QuestionRequest, UserInfo, ConversationInfo, MessageInfo
from bson import ObjectId
from datetime import datetime
from config import settings
from fastapi import HTTPException

def handle_question(questionRequest : QuestionRequest, userInfo : UserInfo):
    # check if the user do has this conversation
    conversation = conversationsCollection.find_one(questionRequest.conversation_id)
    if not conversation or conversation.user_id != userInfo.id:
        raise HTTPException(status_code=400, detail="Conversation not found or user not matching")
    # use LLM to generate response
    history = messagesCollection.find({"conversation_id": ObjectId(questionRequest.conversation_id)}).sort("timestamp", 1)
    non_rag = NonRAGLLM(
        llm_client = LLMClient(api_key=settings.LLM_API_KEY, messages=history))
    response = non_rag.generate_response(
        question=questionRequest.question)
    # store 
    messagesCollection.insert_one(message=MessageInfo(
        conversation_id=ObjectId(questionRequest.conversation_id),
        user_message=questionRequest.question,
        assistant_message=response,
        timestamp=datetime.now()
    ))
    return response

def handle_rag_question(questionRequest : QuestionRequest, userInfo: UserInfo):
     # check if the user do has this conversation
    conversation = conversationsCollection.find_one(ObjectId(questionRequest.conversation_id))
    if not conversation or conversation.user_id != userInfo.id:
        raise HTTPException(status_code=400, detail="Conversation not found or user not matching")
    history = messagesCollection.find_all_by_conversation_id(
        conversation_id=ObjectId(questionRequest.conversation_id))
    topic_name = classify(questionRequest.question)
    keypoints = extract(
        text=questionRequest.question,
        topic_name=topic_name)
    context = retrieve(
        keypoints=keypoints, 
        topic_name=topic_name, text=questionRequest.question)
    # use LLM to generate response
    rag = RAGLLM(
        llm_client = LLMClient(api_key=settings.LLM_API_KEY, messages=history))
    response = rag.generate_response(
        question=questionRequest.question,
        context=context,
        topic_name=topic_name)
    messagesCollection.insert_one(message=MessageInfo(
        conversation_id=ObjectId(questionRequest.conversation_id),
        user_message=questionRequest.question,
        assistant_message=response,
        timestamp=datetime.now()
    ))
    return response

def handle_create_conversation(conv: CreateConversationRequest, userInfo : UserInfo):
    result = conversationsCollection.insert_one(conversation=ConversationInfo(
        user_id=ObjectId(userInfo.id),
        title=conv.title,
        created_at=datetime.now()
    ))
    return {str(result.inserted_id)}

def handle_delete_conversation(conversation_id : str, userInfo: UserInfo):
    # check if the user do has this conversation
    conversation = conversationsCollection.find_one(ObjectId(conversation_id))
    if not conversation or conversation.user_id != userInfo.id:
        raise HTTPException(status_code=400, detail="Conversation not found or user not matching")
    conversationsCollection.delete_one(ObjectId(conversation_id))
    messagesCollection.delete_many_by_conversation_id(conversation_id=ObjectId(conversation_id))

def handle_get_conversation_messages(conversation_id: str, userInfo: UserInfo):
    # check if the user do has this conversation
    conversation = conversationsCollection.find_one(ObjectId(conversation_id))
    if not conversation or conversation.user_id != userInfo.id:
        raise HTTPException(status_code=400, detail="Conversation not found or user not matching")
    msg_cursor = messagesCollection.find_all_by_conversation_id(conversation_id=ObjectId(conversation_id))
    result = []
    for msg in msg_cursor:
        result.append({
            "user": msg["user_message"],
            "assistant": msg["assistant_message"],
            "time": msg["timestamp"]
        })
    return result

def handle_get_all_conversations(userInfo: UserInfo):
    conversations = conversationsCollection.find_all_by_user_id(user_id=ObjectId(userInfo.id))
    result = []
    for conv in conversations:
        result.append({
            "id": str(conv["id"]),
            "title": conv["title"],
        })
    return result

def classify(text : str) -> str: 
  # TODO wait for more type of mod
  return "Minecraft Mod"

def get_keywords(topic_name : str) -> list:
    if topic_name == "Minecraft Mod":
        return MinecraftModKeywords
    else:
        raise ValueError(f"Unsupported topic name: {topic_name}")
        return []

def extract(text : str, topic_name : str) -> list[dict]:
    keywords = get_keywords(topic_name)
    extractor = ExtractorLLM(
        llm_client = LLMClient(api_key=settings.LLM_API_KEY))
    keypoints = extractor.extract(text, keywords, topic_name)
    return keypoints

def retrieve(keypoints : dict, text : str, topic_name) -> list[dict[str, str]]:
    context = [] # { description : str, content : str }
    # TODO more retrieval methods now only doc
    # for k, v in keypoints.items():
    #     if len(v) == 0:
    #         continue
    #     for each in v:
    #         searched_entries = vectorDB.search(query=each.strip(), top_k=5)
    #         for entry in searched_entries:
    #             # TODO more retrieval methods now only doc
    #             context.append({
    #                 "description": entry["id"],
    #                 "content": entry["text"],
    #             })
    # 用户问题直接匹配
    searched_entries = vectorDB.search(query=text.strip(), top_k=3)
    for entry in searched_entries:
        # TODO more retrieval methods now only doc
        context.append({
            "description": entry["id"],
            "content": entry["text"],
        })
    return context


