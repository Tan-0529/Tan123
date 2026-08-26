from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_base_url: str = "https://api.openai.com/v1"
    openai_api_key: str = ""
    embedding_model: str = "text-embedding-3-large"
    embedding_dim: int = 1024
    milvus_uri: str = ""
    milvus_db_path: str = "milvus.db"
    milvus_collection: str = "product"
