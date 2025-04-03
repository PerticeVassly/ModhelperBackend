from fastapi import APIRouter
from pydantic import BaseModel
from openai import OpenAI
from config import settings
from llm import LLMClient, LLMExtractor, LLMClient, LLMRAG

router = APIRouter()

def mock_get_context_from_db(keywords):
    # Mock function to simulate database retrieval
    return [{
        "desciption": "这是涉及：“击败顺序” 的参考资料",
        "content": "玩家应当依次击败娜迦，巫妖，米诺菇，九头蛇，幻影骑士，暮色恶魂，雪怪首领，冰雪女王，洞穴巨魔，巨人，最终来到荆棘城堡（boss未完成）"
    }]

@router.post("/ask")
async def handle_ask(question: str):
    # extract keywords from the question
    extractor = LLMExtractor(
        llm_client = LLMClient(
            api_key=settings.LLM_API_KEY,
        )
    )
    keywords = extractor.extract(question)

    # retrieve context from database
    context = mock_get_context_from_db(keywords)

    # use LLM to generate response
    rag = LLMRAG(
        llm_client = LLMClient(
            api_key=settings.LLM_API_KEY,
        ),
        context=context
    )
    response = rag.generate_response(
        question=question,
        context=context
    )

    # return the response
    return {
        "response": response
    }


    



