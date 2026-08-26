from fastapi import FastAPI

from app.ai.embedding import Embedder, LocalEmbedder
from app.ai.llm import LLM, OpenAILLM
from app.config import Settings
from app.core.memory import InMemoryMemory
from app.core.orchestrator import Orchestrator
from app.db.vector_store import VectorStore
from app.db.milvus_store import MilvusStore
from app.rag.ingestion.pipeline import IngestionPipeline
from app.rag.retriever import Retriever


def build_embedder(settings: Settings) -> Embedder:
    return LocalEmbedder(settings.embedding_model)


def build_store(settings: Settings) -> VectorStore:
    return MilvusStore(settings)


def build_llm(settings: Settings) -> LLM:
    return OpenAILLM(settings)


def create_app() -> FastAPI:
    settings = Settings()
    store = build_store(settings)
    embedder = build_embedder(settings)
    llm = build_llm(settings)
    pipeline = IngestionPipeline(store, embedder)
    retriever = Retriever(store, embedder)
    memory = InMemoryMemory()
    orchestrator = Orchestrator(retriever, llm, memory)

    app = FastAPI(title="SmartShop AI")
    app.state.pipeline = pipeline
    app.state.retriever = retriever
    app.state.orchestrator = orchestrator

    from app.api.routes.ingest import router as ingest_router
    from app.api.routes.search import router as search_router
    from app.api.routes.chat import router as chat_router
    app.include_router(ingest_router)
    app.include_router(search_router)
    app.include_router(chat_router)
    return app


app = create_app()
