from pydantic_settings import BaseSettings

DATABASE_URL = "postgresql://admin:changeme111@postgres_db/mydb"

class Settings(BaseSettings):
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # class Config:
    #     env_file = ".env"

settings = Settings()
