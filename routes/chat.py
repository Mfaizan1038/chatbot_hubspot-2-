from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas import ChatRequest, ChatResponse
from database import get_db
from services.brain import process_message

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    reply = process_message(
        db,
        req.session_id,
        req.message,
        req.context
    )
    return {"reply": reply}
