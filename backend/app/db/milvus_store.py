from pymilvus import MilvusClient

from app.config import Settings
from app.db.vector_store import SearchHit, VectorStore
from app.models.chunk import Chunk


class MilvusStore(VectorStore):
    def __init__(self, settings: Settings):
        uri = settings.milvus_uri or settings.milvus_db_path
        self._client = MilvusClient(uri)
        self._collection = settings.milvus_collection
        self._dim = settings.embedding_dim
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        if self._client.has_collection(self._collection):
            return
        self._client.create_collection(
            collection_name=self._collection, dimension=self._dim
        )

    def insert(self, chunks: list[Chunk]) -> None:
        data = [{
            "id": c.id,
            "vector": c.metadata.get("vector", [0.0] * self._dim),
            "text": c.text,
            "doc_id": c.doc_id,
            "chunk_type": c.chunk_type,
            "priority": c.priority,
            "price": c.metadata.get("price", 0.0),
            "category": c.metadata.get("category", ""),
            "brand": c.metadata.get("brand", ""),
            "sku": c.metadata.get("sku", ""),
        } for c in chunks]
        self._client.insert(collection_name=self._collection, data=data)

    def search(self, vector, top_k=50, expr=None):
        resp = self._client.search(
            collection_name=self._collection, data=[vector], limit=top_k,
            filter=expr or "", output_fields=["text", "doc_id", "chunk_type",
                                              "priority", "price", "category",
                                              "brand", "sku"],
        )
        hits = []
        for item in resp[0]:
            f = item.get("entity", {})
            hits.append(SearchHit(id=str(item["id"]), score=item["distance"], fields=f))
        return hits

    def close(self) -> None:
        self._client.close()
