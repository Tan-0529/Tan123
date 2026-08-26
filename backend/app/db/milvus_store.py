from pymilvus import DataType, MilvusClient

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
        if not self._client.has_collection(self._collection):
            schema = self._client.create_schema(auto_id=False, enable_dynamic_field=False)
            schema.add_field(field_name="id", datatype=DataType.VARCHAR,
                             is_primary=True, max_length=128)
            schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=self._dim)
            schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=4096)
            schema.add_field(field_name="doc_id", datatype=DataType.VARCHAR, max_length=128)
            schema.add_field(field_name="chunk_type", datatype=DataType.VARCHAR, max_length=32)
            schema.add_field(field_name="priority", datatype=DataType.INT64)
            schema.add_field(field_name="price", datatype=DataType.DOUBLE)
            schema.add_field(field_name="rating", datatype=DataType.DOUBLE)
            schema.add_field(field_name="category", datatype=DataType.VARCHAR, max_length=64)
            schema.add_field(field_name="brand", datatype=DataType.VARCHAR, max_length=64)
            schema.add_field(field_name="sku", datatype=DataType.VARCHAR, max_length=64)
            schema.add_field(field_name="title", datatype=DataType.VARCHAR, max_length=256)
            schema.add_field(field_name="image_url", datatype=DataType.VARCHAR, max_length=512)
            schema.add_field(field_name="product_url", datatype=DataType.VARCHAR, max_length=512)

            index_params = self._client.prepare_index_params()
            index_params.add_index(field_name="vector", index_type="HNSW",
                                   metric_type="COSINE", params={"M": 16, "efConstruction": 256})
            self._client.create_collection(collection_name=self._collection,
                                           schema=schema, index_params=index_params)
        self._client.load_collection(self._collection)

    def insert(self, chunks: list[Chunk]) -> None:
        data = [{
            "id": c.id,
            "vector": c.metadata.get("vector", [0.0] * self._dim),
            "text": c.text,
            "doc_id": c.doc_id,
            "chunk_type": c.chunk_type,
            "priority": c.priority,
            "price": c.metadata.get("price", 0.0),
            "rating": c.metadata.get("rating", 0.0),
            "category": c.metadata.get("category", ""),
            "brand": c.metadata.get("brand", ""),
            "sku": c.metadata.get("sku", ""),
            "title": c.metadata.get("title", ""),
            "image_url": c.metadata.get("image_url", ""),
            "product_url": c.metadata.get("product_url", ""),
        } for c in chunks]
        self._client.insert(collection_name=self._collection, data=data)

    def search(self, vector, top_k=50, expr=None):
        resp = self._client.search(
            collection_name=self._collection, data=[vector], limit=top_k,
            filter=expr or "", output_fields=["text", "doc_id", "chunk_type",
                                              "priority", "price", "rating", "category",
                                              "brand", "sku", "title", "image_url",
                                              "product_url"],
        )
        hits = []
        for item in resp[0]:
            f = item.get("entity", {})
            hits.append(SearchHit(id=str(item["id"]), score=item["distance"], fields=f))
        return hits

    def close(self) -> None:
        self._client.close()
