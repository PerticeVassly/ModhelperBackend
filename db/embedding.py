import requests
import json
import logging
from typing import List
from config import settings

logger = logging.getLogger("embedding")

def gen_embedding(input: str) -> List[float]:
    url = settings.EMBEDDING_URL
    
    payload = json.dumps({
        "input": [
            input
        ]
    }, ensure_ascii=False)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {settings.EMBEDDING_API_KEY}'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload.encode("utf-8"))
    
    if response.status_code != 200:
        logger.error(f"Embedding response error, status_code: [{response.status_code}]")
        # todo: should raise an exception ;(
        return []
    
    data = response.json()['data']
    
    embedding = data[0]['embedding']
    
    return embedding
    