from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class FeedbackRequest(BaseModel):
    conversation_id: str
    message_id: str
    rating: str
    comment: str = ""


@router.post("/feedback")
def feedback(req: FeedbackRequest, request: Request):
    service = request.app.state.feedback
    service.add(req.conversation_id, req.message_id, req.rating, req.comment)
    return {"ok": True}
