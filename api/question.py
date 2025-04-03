from fastapi import APIRouter
from config import settings
from llm import LLMClient, ExtractorLLM, LLMClient, RAGLLM

# models
from model import QuestionRequest
from model import MinecraftModKeywords

router = APIRouter()

def mock_retrieve_context(keywords, topic_name):
    # Mock function to simulate database retrieval
    return [
        {
            "desciption": "这是涉及:**击败顺序**的参考资料",
            "content": "玩家应当依次击败娜迦，巫妖，米诺菇，九头蛇，幻影骑士，暮色恶魂，雪怪首领，冰雪女王，洞穴巨魔，巨人，最终来到荆棘城堡"
        },
        {
            "descirption": "这是涉及:**注意事项**的参考资料",
            "content": "最终荆棘城堡中没有boss，这个mod未完待续"
        }
    ]

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
        topic_name=topic_name)

    # return the response
    return {
        "response": response
    }


    



