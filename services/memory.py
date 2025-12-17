from sqlalchemy.orm import Session
from models import ChatSession

def get_or_create_session(db: Session, session_id: str):
    session = db.query(ChatSession).filter_by(session_id=session_id).first()
    if not session:
        session = ChatSession(session_id=session_id, data={})  
        db.add(session)
        db.commit()
        db.refresh(session)
    elif session.data is None:
        session.data = {}
        db.commit()
    return session