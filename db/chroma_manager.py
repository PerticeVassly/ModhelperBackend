import chromadb
import logging
from typing import List, Dict, Any, Optional
from config import settings
from pathlib import Path
from .embedding import gen_embedding, split_text
from model import DocumentMetadata, Entry

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
                    ids = [metadata.mod_name + metadata.document_name + str(i) for i in range(len(chunks))],
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
                logger.info(f"Added document {metadata.document_name} to the database.")
                return True
            except Exception as e:
                logger.error(f"Error adding document {metadata.document_name}: {e}")
                return False
        
    def search(self, query: str, top_k: int = 5) -> list[Entry]:
        query_embedding = gen_embedding(query)

        query_params = {
            "query_embeddings": [query_embedding],
            "n_results": top_k,
        }
        results = self.collection.query(**query_params)    
        return [
            Entry(
                id=id,
                document=doc,
                metadata=DocumentMetadata(**meta),
                distance=score,
                score=score,
            )
            for id, doc, meta, score in zip(
                results["ids"][0], 
                results["documents"][0], 
                results["metadatas"][0], 
                results["distances"][0]
            )
        ]

    def delete_by_mod(self, mod_name: str) -> bool:
        try:
            mod_name = mod_name
            ids_to_delete = self.collection.get(where={"mod_name": mod_name})["ids"]
            if not ids_to_delete:
                logger.info(f"[ChromaDB] 未找到 mod_name={mod_name} 的任何分块，无需删除。")
                return True

            self.collection.delete(ids=ids_to_delete)
            logger.info(f"[ChromaDB] 已删除 mod_name={mod_name} 的 {len(ids_to_delete)} 个分块。")
            return True
        except Exception as e:
            logger.error(f"[ChromaDB] 删除 mod_name={mod_name} 相关分块时出错: {e}")
            return False

    
    def __del__(self):
        logger.info("ChromaVectorDB instance deleted.")
    

vectorDB = ChromaVectorDB()