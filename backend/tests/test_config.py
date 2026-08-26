from app.config import Settings


def _clean_env(monkeypatch):
    for k in ["LLM_MODEL", "EMBEDDING_DIM", "EMBEDDING_MODEL",
              "OPENAI_API_KEY", "OPENAI_BASE_URL"]:
        monkeypatch.delenv(k, raising=False)


def test_settings_defaults(monkeypatch):
    _clean_env(monkeypatch)
    settings = Settings(_env_file=None)
    assert settings.embedding_dim == 512
    assert settings.embedding_model == "BAAI/bge-small-zh-v1.5"
    assert settings.milvus_db_path.endswith("milvus.db")


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("EMBEDDING_DIM", "768")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    settings = Settings(_env_file=None)
    assert settings.embedding_dim == 768
    assert settings.openai_api_key == "sk-test"


def test_settings_llm_model_default(monkeypatch):
    _clean_env(monkeypatch)
    settings = Settings(_env_file=None)
    assert settings.llm_model == "gpt-5.5"
