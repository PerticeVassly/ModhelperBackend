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
    
    try:
        response = requests.request("POST", url, headers=headers, data=payload.encode("utf-8"))
        response.raise_for_status()
        data = response.json()    
        
        if "error_code" in data:
            raise ValueError(f"Embedding API Error: {data['error_msg']} (code: {data['error_code']})")
        return data['data'][0]['embedding']
    
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        return []

def split_text(text: str, max_length: int = 500) -> List[str]:
    words = text.strip().splitlines()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 <= max_length:
            current_chunk.append(word)
            current_length += len(word) + 1
        else:
            chunks.append("\n".join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
    
    if current_chunk:
        chunks.append("\n".join(current_chunk))

    return chunks
   