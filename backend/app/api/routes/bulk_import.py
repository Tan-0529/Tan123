from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class ProductItem(BaseModel):
    title: str
    content: str = ""
    price: float = 0
    rating: float = 0
    category: str = ""
    brand: str = ""
    sku: str = ""
    image_url: str = ""
    product_url: str = ""
    attributes: dict = {}


class ImportRequest(BaseModel):
    products: list[ProductItem]


@router.post("/import")
def import_products(req: ImportRequest, request: Request):
    pipeline = request.app.state.pipeline
    for i, p in enumerate(req.products):
        doc_id = f"import_{p.sku or i}_{i}"
        pipeline.ingest(p.content, {
            "doc_id": doc_id,
            "source_type": "text",
            "title": p.title,
            "metadata": {
                "price": p.price, "rating": p.rating, "category": p.category,
                "brand": p.brand, "sku": p.sku, "image_url": p.image_url,
                "product_url": p.product_url,
            },
            "attributes": p.attributes,
        })
    return {"imported": len(req.products)}
