from sqlalchemy.orm import Session
from services.memory import get_or_create_session
from services.action import detect_action
from services.flow import handle_flow
from flow_definitions import FLOW_STEPS

def process_message(db: Session, session_id: str, message: str):
    chat_session = get_or_create_session(db, session_id)

    if chat_session.action and chat_session.step:
        return handle_flow(db, chat_session, message)

    action = detect_action(message)
    if not action:
        return "I can help with company-related services only."

    chat_session.action = action
    chat_session.step = FLOW_STEPS[action][0][0]
    db.commit()

    return FLOW_STEPS[action][0][1]
