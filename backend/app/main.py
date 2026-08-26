from fastapi import FastAPI

from app.ai.embedding import Embedder, OpenAIEmbedder
from app.config import Settings
from app.db.vector_store import VectorStore
from app.db.milvus_store import MilvusStore
from app.rag.ingestion.pipeline import IngestionPipeline
from app.rag.retriever import Retriever


def build_embedder(settings: Settings) -> Embedder:
    return OpenAIEmbedder(settings)


def build_store(settings: Settings) -> VectorStore:
    return MilvusStore(settings)


def create_app() -> FastAPI:
    settings = Settings()
    store = build_store(settings)
    embedder = build_embedder(settings)
    pipeline = IngestionPipeline(store, embedder)
    retriever = Retriever(store, embedder)

    app = FastAPI(title="SmartShop AI")
    app.state.pipeline = pipeline
    app.state.retriever = retriever

    from app.api.routes.ingest import router as ingest_router
    from app.api.routes.search import router as search_router
    app.include_router(ingest_router)
    app.include_router(search_router)
    return app


app = create_app()
