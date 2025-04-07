from model import MinecraftModKeywords
from llm import LLMClient, ExtractorLLM
from config import settings
from db import vectorDB, relationDB, graphDB

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

def retrieve(keypoints : dict, topic_name) -> list[dict[str, str]]:
    context = [] # { description : str, content : str }
    # TODO more retrieval methods now only doc
    for k, v in keypoints.items():
        if len(v) == 0:
            continue
        for each in v:
            searched_entries = vectorDB.search(query=each.strip(), top_k=3)
            for entry in searched_entries:
                # TODO more retrieval methods now only doc
                context.append({
                    "description": entry["id"],
                    "content": entry["text"],
                })
    return context


