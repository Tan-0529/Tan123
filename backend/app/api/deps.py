from fastapi import Request

from app.rag.ingestion.pipeline import IngestionPipeline
from app.rag.retriever import Retriever


def get_pipeline(request: Request) -> IngestionPipeline:
    return request.app.state.pipeline


def get_retriever(request: Request) -> Retriever:
    return request.app.state.retriever
