import os
from typing import List
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
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # Embedding 配置
    EMBEDDING_URL: str = Field(default="https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/embeddings/embedding-v1", env="EMBEDDING_URL")
    EMBEDDING_API_KEY: str = Field(..., env="EMBEDDING_API_KEY")
    
    # 向量数据库
    CHROMA_DB_PATH: str = os.path.join(DATA_DIR, "chromadb_store")
    CHROMA_COLLECTION: str = "mod_docs"
    
    # 关系数据库
    SQLITE_DB_PATH: str = Field(default=os.path.join(DATA_DIR, "mod_metadata.db"), env="SQLITE_DB_PATH")
    SQLITE_DB_URL: str = Field(default=f"sqlite:///{SQLITE_DB_PATH}", env="SQLITE_DB_URL")
    
    # 图数据库
    NEO4J_URL: str = Field(default="bolt://localhost:7687", env="NEO4J_URL")
    NEO4J_USER: str = Field(default="neo4j", env="NEO4J_USER")
    NEO4J_PASSWORD: str = Field(..., env="NEO4J_PASSWORD")

    # MongoDB
    MONGO_URL: str = Field(default="mongodb://localhost:27017", env="MONGO_URL")
    
    # CORS 配置
    ALLOW_ORIGINS: List[str] = Field(default=["http://localhost:5173", "http://172.29.4.206:80", "http://172.29.4.206"], env="ALLOW_ORIGINS")  # Frontend URL
    ALLOW_HEADERS: List[str] = Field(default=["*"], env="ALLOW_HEADERS")
    ALLOW_METHODS: List[str] = Field(default=["*"], env="ALLOW_METHODS")
    ALLOW_CREDENTIALS: bool = Field(default=True, env="ALLOW_CREDENTIALS")

    # LLM 配置
    LLM_API_KEY: str = Field(..., env="LLM_API_KEY")
    LLM_MODEL_NAME: str = Field(default="deepseek-chat", env="LLM_MODEL_NAME")  
    LLM_BASE_URL: str = Field(default = "https://api.deepseek.com",env="LLM_BASE_URL") 
    LLM_TEMPERATURE: float = Field(default=0.7, env="LLM_TEMPERATURE")
    LLM_MAX_TOKENS: int = Field(default=1000, env="LLM_MAX_TOKENS")

    # JWT 配置
    JWT_SECRET_KEY : str = Field(default="JWT_KEY", env="JWT_SECRET_KEY")
    JWT_ALGORITHM : str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES : str = Field(default="3600000", env ="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")

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