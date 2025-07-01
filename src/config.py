import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./hr.db"
    DEBUG: bool = True

settings = Settings()