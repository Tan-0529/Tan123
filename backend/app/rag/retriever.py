from app.ai.embedding import Embedder
from app.db.vector_store import VectorStore


class Retriever:
    def __init__(self, store: VectorStore, embedder: Embedder):
        self._store = store
        self._embedder = embedder

    def retrieve(self, query: str, top_k: int = 5, filters: dict | None = None,
                 vision_vec: list[float] | None = None) -> list[dict]:
        vec = self._embedder.embed_query(query)
        expr = self._build_expr(filters)
        hits = self._store.search(vec, top_k=max(top_k * 4, 20), expr=expr)

        if vision_vec is not None:
            vhits = self._store.search(vision_vec, top_k=max(top_k * 4, 20),
                                       expr=expr, field="vision_embedding")
            hits = self._rrf_fuse(hits, vhits)

        scored = []
        for h in hits:
            priority = h.fields.get("priority", 5)
            scored.append((h.score * priority, h))
        scored.sort(key=lambda x: -x[0])
        return [{"text": h.fields.get("text", ""), "score": s, "metadata": h.fields}
                for s, h in scored[:top_k]]

    def _rrf_fuse(self, text_hits, vision_hits, k: int = 60):
        scores: dict[str, float] = {}
        hit_map: dict[str, object] = {}
        for hits in (text_hits, vision_hits):
            for rank, h in enumerate(hits):
                scores[h.id] = scores.get(h.id, 0.0) + 1.0 / (k + rank + 1)
                hit_map[h.id] = h
        ordered = sorted(scores.items(), key=lambda x: -x[1])
        return [hit_map[cid] for cid, _ in ordered]

    def _build_expr(self, filters: dict | None) -> str | None:
        if not filters:
            return None
        conds = []
        if "category" in filters:
            conds.append(f'category == "{filters["category"]}"')
        if "max_price" in filters:
            conds.append(f"price <= {filters['max_price']}")
        if "brand" in filters:
            conds.append(f'brand == "{filters["brand"]}"')
        return " and ".join(conds) if conds else None
