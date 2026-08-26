from pydantic import BaseModel, Field


class Document(BaseModel):
    doc_id: str
    source_type: str
    title: str
    content: str
    metadata: dict = Field(default_factory=dict)
    attributes: dict = Field(default_factory=dict)
