# chat.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas import ChatRequest, ChatResponse
from services.filter_builder import build_filter  # import your FilterBuilder wrapper

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    message = request.message
    context = request.context

    # Use FilterBuilder to parse the message
    try:
        filter_result = build_filter(context, message)
        if "error" in filter_result:
            reply = f"Error: {filter_result['error']}"
        else:
            reply = {"supabase_query": filter_result["supabase_query"]}
    except Exception as e:
        reply = f"Error: {str(e)}"

    return {"reply": reply}
