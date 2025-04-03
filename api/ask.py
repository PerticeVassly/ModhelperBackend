from fastapi import APIRouter
from config import settings
from llm import LLMClient, ExtractorLLM, LLMClient, RAGLLM

# models
from model import QuestionRequest

from test.mock import mock_retrieve_context
router = APIRouter()

@router.post("/ask")
async def handle_ask(questionRequest: QuestionRequest):
    # extract keywords from the question
    extractor = ExtractorLLM(
        llm_client = LLMClient(api_key=settings.LLM_API_KEY))
    keywords = extractor.extract(questionRequest.question)
    # retrieve context from database
    context = mock_retrieve_context(keywords)

    # use LLM to generate response
    rag = RAGLLM(
        llm_client = LLMClient(
            api_key=settings.LLM_API_KEY,
        ),
        context=context
    )
    response = rag.generate_response(
        question=questionRequest.question,
        context=context
    )

    # return the response
    return {
        "response": response
    }


    



