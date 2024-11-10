from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    DATABASE_URL: str = "postgresql://admin:changeme111@postgres_db/mydb"

    ES_HOST: str = 'https://es01:9200'
    ES_USER: str = 'elastic'
    ES_PASS: str = 'adminadmin'
    ca_cert: str = "/app/certs/ca/ca.crt"
    ES_index_name: str = "item_embeddings"


    # class Config:
    #     env_file = ".env"

settings = Settings()
