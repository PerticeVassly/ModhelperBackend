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

    def add(self, article_name : str, article_type : str, url : str, content : str, mod_name : str) -> bool:
        # check if the article has been added
        existing_docs = self.collection.query(
            query_embeddings=[gen_embedding(article_name)],
            n_results=1,
            where={
                "article_name": article_name
            }
        )
        if existing_docs["documents"][0]:
            logger.info(f"Document {article_name} already exists in the database.")
            return
        summary = article_name # TODO other way to generate summary
        chunks = split_text(content)
        embedded_chunks = [gen_embedding(summary + chunk) for chunk in chunks]    
        if embedded_chunks:
            try:
                self.collection.add(
                    documents=chunks,
                    metadatas=[{
                        "article_name": article_name,
                        "url": url,
                        "type": article_type,
                        "mod_name": mod_name,
                        "chunk_index": i,
                        "total_chunk": len(chunks)
                    } for i in range(len(chunks))],
                    ids=[f"{article_name}_{i}" for i in range(len(chunks))],
                    embeddings=embedded_chunks
                )
                return True
            except Exception as e:
                logger.error(f"Error adding document {article_name}: {e}")
                return False
        
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        query_embedding = gen_embedding(query)

        query_params = {
            "query_embeddings": [query_embedding],
            "n_results": top_k,
        }
        results = self.collection.query(**query_params)    
        return [
            {"id": id, "document": doc, "metadata": meta, "score": score}
            for id, doc, meta, score in zip(
                results["ids"][0], 
                results["documents"][0], 
                results["metadatas"][0], 
                results["distances"][0]
            )
        ]
    
    def __del__(self):
        logger.info("ChromaVectorDB instance deleted.")
    

vectorDB = ChromaVectorDB()