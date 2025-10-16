from pydantic_settings import BaseSettings
from pydantic import AnyUrl

class Settings(BaseSettings):
    """
    App configuration loaded from .env
    """
    GROQ_API_KEY: str
    GROQ_API_URL: AnyUrl
    GROQ_MODEL: str
    DUMMYJSON_URL: AnyUrl
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
