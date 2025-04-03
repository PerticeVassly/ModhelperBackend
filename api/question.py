from fastapi import APIRouter
from config import settings
from llm import LLMClient, ExtractorLLM, LLMClient, RAGLLM

# models
from model import QuestionRequest
from model import MinecraftModKeywords

from test.mock import mock_retrieve_context

router = APIRouter()

@router.post("/question")
async def handle_ask(questionRequest: QuestionRequest):
    # todo() identify which game the user want to ask
    topic_name = "Minecraft Mod"

    # extract keywords from the question
    keywords = MinecraftModKeywords;
    extractor = ExtractorLLM(
        llm_client = LLMClient(api_key=settings.LLM_API_KEY))
    keypoints = extractor.extract(questionRequest.question, keywords, topic_name)

    # retrieve context from database
    context = mock_retrieve_context(keypoints, topic_name)

    # use LLM to generate response
    rag = RAGLLM(
        llm_client = LLMClient(api_key=settings.LLM_API_KEY))
    response = rag.generate_response(
        question=questionRequest.question,
        context=context,
        topic_name=topic_name
    )

    # return the response
    return {
        "response": response
    }


    



