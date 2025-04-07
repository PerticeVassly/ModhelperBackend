from fastapi import APIRouter

# models
from model import QuestionRequest

# service
from service import handle_question, handle_rag_question

router = APIRouter()

@router.post("/question")
async def question(questionRequest: QuestionRequest):
    # TODO rag-key
    response = handle_rag_question(questionRequest)
    return response


    



