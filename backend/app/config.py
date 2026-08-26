from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_base_url: str = "https://api.openai.com/v1"
    openai_api_key: str = ""
    embedding_model: str = "BAAI/bge-small-zh-v1.5"
    embedding_dim: int = 512
    llm_model: str = "gpt-5.5"
    milvus_uri: str = ""
    milvus_db_path: str = "milvus.db"
    milvus_collection: str = "product"
