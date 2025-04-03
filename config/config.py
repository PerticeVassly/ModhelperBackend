from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):

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
        env_file = ".env"  # load .env in the root directory
        env_file_encoding = "utf-8"

settings = Settings()
