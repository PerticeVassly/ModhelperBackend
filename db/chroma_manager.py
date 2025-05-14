import chromadb
import logging
from typing import List, Dict, Any, Optional
from config import settings
from pathlib import Path
from .embedding import gen_embedding, split_text
from model import DocumentMetadata

logger = logging.getLogger("database")

class ChromaVectorDB:
    def __init__(self):
        db_path = Path(settings.CHROMA_DB_PATH)
        db_path.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=str(db_path))
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION
        )
        
        logger.info(f"Initialized ChromaDB at {db_path}, collection: {settings.CHROMA_COLLECTION}")

    def add(self, raw_text : str, metadata : DocumentMetadata, overwrite = False) -> bool:
        # check if the article has been added
        existing_docs = self.collection.query(
            query_embeddings=[gen_embedding(metadata.document_name)],
            n_results=1,
            where={
                "document_name": metadata.document_name,
            }
        )
        if existing_docs["documents"][0] and not overwrite:
            logger.info(f"Document {metadata.document_name} already exists in the database.")
            return
        summary =  metadata.document_name # TODO other way to generate summary
        chunks = split_text(raw_text)
        embedded_chunks = [gen_embedding(summary + chunk) for chunk in chunks]    
        if embedded_chunks:
            try:
                self.collection.add(
                    documents=chunks,
                    embeddings=embedded_chunks,
                    metadatas=[DocumentMetadata(
                        id=  metadata.mod_name +  metadata.document_name + str(i),
                        document_name=metadata.document_name,
                        url=metadata.url,
                        type=metadata.type,
                        mod_name=metadata.mod_name,
                        chunk_index=i,
                        total_chunks=len(chunks),
                    ).model_dump() for i in range(len(chunks))],
                )
                return True
            except Exception as e:
                logger.error(f"Error adding document {metadata.document_name}: {e}")
                return False
        
    def search(self, query: str, required_mod_names : Optional[list[str]], required_article_type : Optional[str], top_k: int = 5) -> List[Dict[str, Any]]:
        query_embedding = gen_embedding(query)

        query_params = {
            "query_embeddings": [query_embedding],
            "n_results": top_k,
        }
        where = {}
        if required_mod_names and len(required_mod_names) != 0:
            where["mod_name"] = {"$in": required_mod_names}
        # TODO chromadb竟然不支持多where查询...
        # if required_article_type:
        #     where["type"] = required_article_type
        if where:
            query_params["where"] = where
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