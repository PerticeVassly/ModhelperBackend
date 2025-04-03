from fastapi import APIRouter
from pydantic import BaseModel
from openai import OpenAI
from config import settings

from model.ask_request import AskRequest

router = APIRouter()

@router.post("/ask")
async def handle_ask(ask_request: AskRequest):

    # todo()

    # process the request get the keywords

    # retrieve the related context from the database with the keywords

    # fetch the chating history from the database

    # compose the prompt with the context history and the question

    # interact with the LLM 

    # save and return the response 

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


