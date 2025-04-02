import os
from pydantic import Field, validator, BaseSettings

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
    SECRET_KEY: str = Field(default="change-me-in-prod", min_length=32)
    API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("*", pre=True)
    def create_dirs(cls, v, field):
        if field.name.endswith(("DIR", "PATH")):
            path = Path(v)
            if not path.exists():
                if field.name in ("UPLOAD_DIR", "DATA_DIR"):
                    path.mkdir(parents=True, exist_ok=True)
            return str(path.absolute())
        return v

settings = Settings()