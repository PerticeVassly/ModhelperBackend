import chromadb
import logging
from typing import List, Dict, Any
from .base import BaseVectorDB
from config import settings
from pathlib import Path
from .embedding import gen_embedding, split_text

logger = logging.getLogger("database")

class ChromaVectorDB(BaseVectorDB):
    def __init__(self):
        db_path = Path(settings.CHROMA_DB_PATH)
        db_path.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=str(db_path))
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION
        )
        
        logger.info(f"Initialized ChromaDB at {db_path}, collection: {settings.CHROMA_COLLECTION}")
    
    def add(self, name: str, text: str) -> bool:
        chunks = split_text(text)
        embeddings = []
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            embedding = gen_embedding(f"{name}: {chunk}")
            if embedding is not None:
                embeddings.append(embedding)
                metadatas.append({"chunk_id": i, "name": name})
        
        if embeddings:
            try:
                self.collection.add(
                    ids=[f"{name}_{i}" for i in range(len(embeddings))],
                    documents=chunks,
                    embeddings=embeddings,
                    metadatas=metadatas
                )
                logger.info(f"Document {name} added successfully.")
                return True
            except Exception as e:
                logger.error(f"Error adding document {name}: {e}")
                return False
        
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        query_embedding = gen_embedding(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )     
        return [
            {"id": id, "text": doc, "score": score}
            for id, doc, score in zip(
                results["ids"][0], 
                results["documents"][0], 
                results["distances"][0]
            )
        ]
    
    def __del__(self):
        logger.info("ChromaVectorDB instance deleted.")
    

vectorDB = ChromaVectorDB()