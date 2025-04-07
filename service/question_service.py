from .util import *;
from llm import LLMClient, RAGLLM, NonRAGLLM

def handle_question(question):
    # use LLM to generate response
    non_rag = NonRAGLLM(
        llm_client = LLMClient(api_key=settings.LLM_API_KEY))
    response = non_rag.generate_response(
        question=question)
    return response

def handle_rag_question(question : str):
    topic_name = classify(question)
    keypoints = extract(
        text=question,
        topic_name=topic_name)
    context = retrieve(
        keypoints=keypoints, 
        topic_name=topic_name)

    # use LLM to generate response
    rag = RAGLLM(
        llm_client = LLMClient(api_key=settings.LLM_API_KEY))
    response = rag.generate_response(
        question=question,
        context=context,
        topic_name=topic_name)

    # return the response
    return response