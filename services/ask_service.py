from fastapi import APIRouter
from pydantic import BaseModel
from openai import OpenAI
from config import settings

router = APIRouter()

# 定义请求体模型
class AskRequest(BaseModel):
    ask: str

# 定义 API 端点
@router.post("/ask")
async def handle_ask(ask_request: AskRequest):
    # use langchain to process the ask_request
    client = OpenAI(
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL,
    )

    reponse = client.chat.completions.create(
        model=settings.LLM_MODEL_NAME,
        messages=[{"role": "user", "content": ask_request.ask}],
        temperature=settings.LLM_TEMPERATURE,
        max_tokens=settings.LLM_MAX_TOKENS,
        stream=False,
    )

    return {
        "ask": ask_request.ask,
        "response": reponse.choices[0].message.content,
    }


