from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas import ChatRequest, ChatResponse
from database import get_db
from services.brain import process_message

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    reply = process_message(db, request.session_id, request.message)
    return {"reply": reply}
