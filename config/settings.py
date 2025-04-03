import os
from pydantic import Field, validator, BaseSettings
from typing import List, Optional
import json
from pathlib import Path
from typing import Optional
from pathlib import Path
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)

class Settings(BaseSettings):
    # 应用配置
    PROJECT_NAME: str = "ModHelper-Backend"
    API_VERSION: str = "v1"
    
    # FastAPI 配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 向量数据库
    CHROMA_DB_PATH: str = os.path.join(DATA_DIR, "chromadb_store")
    CHROMA_COLLECTION: str = "mod_docs"
    
    # 关系数据库
    SQLITE_DB_PATH: str = os.path.join(DATA_DIR, "mod_metadata.db")
    SQLITE_DB_URL: str = f"sqlite:///{SQLITE_DB_PATH}"
    
    # 图数据库
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"
    
    # 模型配置
    EMBEDDING_MODEL: str = "BAAI/bge-small-zh"
    LLM_MODEL: str = "deepseek-chat"
    
    # 安全配置
    SECRET_KEY: str = Field(default="change-me-in-prod")
    API_KEY: Optional[str] = None

    # CORS settings
    ALLOW_ORIGINS: List[str] = Field(default=["localhost:5173"])  # Frontend URL
    ALLOW_HEADERS: List[str] = Field(default=["*"])
    ALLOW_METHODS: List[str] = Field(default=["*"])
    ALLOW_CREDENTIALS: bool = Field(default=True)

    # LLM settings
    LLM_API_KEY: str = Field(
        default=None, 
        env="LLM_API_KEY")
    LLM_MODEL_NAME: str = Field(
        default="deepseek-chat", 
        env="LLM_MODEL_NAME")  
    LLM_BASE_URL: str = Field(
        default = "https://api.deepseek.com",
        env="LLM_BASE_URL") 
    LLM_TEMPERATURE: float = Field(
        default=0.7, 
        env="LLM_TEMPERATURE")
    LLM_MAX_TOKENS: int = Field(
        default=1000, 
        env="LLM_MAX_TOKENS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @field_validator("*", mode="before")
    def create_dirs(cls, v, info):
        if info.field_name.endswith(("DIR", "PATH")):
            path = Path(v)
            if not path.exists():
                if info.field_name in ("UPLOAD_DIR", "DATA_DIR"):
                    path.mkdir(parents=True, exist_ok=True)
            return str(path.absolute())
        return v

settings = Settings()