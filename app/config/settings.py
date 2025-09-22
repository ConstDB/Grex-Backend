from pydantic_settings import BaseSettings
import os

# instead of accessing the env values directly, we will use Settings to access env
class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str

    PGADMIN_DEFAULT_EMAIL:str
    PGADMIN_DEFAULT_PASSWORD:str
 
    POSTGRES_USER: str 
    POSTGRES_PASSWORD:str 
    POSTGRES_DB: str 

    JWT_REFRESH_SECRET: str 
    JWT_ACCESS_SECRET: str 
    JWT_ALGORITHM: str 

    GOOGLE_CLIENT_ID:str
    GOOGLE_CLIENT_SECRET: str

    SESSION_SECRET: str 
    SECRET_PASSWORD: str

    CLOUD_NAME: str
    CLOUD_API_KEY: str
    CLOUD_SECRET_KEY: str
    CLOUDINARY_URL: str

    GEMINI_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()