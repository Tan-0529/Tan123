from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_retriever
from app.rag.retriever import Retriever

router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    filters: dict | None = None


@router.post("/search")
def search(req: SearchRequest, retriever: Retriever = Depends(get_retriever)):
    results = retriever.retrieve(req.query, top_k=req.top_k, filters=req.filters)
    return {"results": results}
