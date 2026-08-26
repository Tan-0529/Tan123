from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_pipeline
from app.rag.ingestion.pipeline import IngestionPipeline

router = APIRouter()


class IngestRequest(BaseModel):
    doc_id: str
    source_type: str = "text"
    title: str = ""
    content: str
    metadata: dict = {}
    attributes: dict = {}


@router.post("/ingest")
def ingest(req: IngestRequest, pipeline: IngestionPipeline = Depends(get_pipeline)):
    n = pipeline.ingest(req.content, {
        "doc_id": req.doc_id, "source_type": req.source_type, "title": req.title,
        "metadata": req.metadata, "attributes": req.attributes,
    })
    return {"doc_id": req.doc_id, "chunks": n}
