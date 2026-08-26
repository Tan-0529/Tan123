from pydantic import BaseModel, Field


class Chunk(BaseModel):
    id: str
    doc_id: str
    text: str
    chunk_type: str
    priority: int = 5
    attributes: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)
