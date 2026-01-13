from services.memory import get_or_create_session
from services.action import detect_action
from services.flow import handle_flow
from services.filter_builder import build_filter
from flow_definitions import FLOW_STEPS
from context_definitions import list_available_contexts

def process_message(db, session_id, message, context=None):
    session = get_or_create_session(db, session_id)

    # Continue existing flows FIRST
    if session.action and session.step:
        return handle_flow(db, session, message)

    decision = detect_action(message)

    # NEW: SQL FILTERS
    if decision == "CREATE_FILTER":
        if not context:
            return {
                "message": "Please specify data context",
                "available_contexts": list_available_contexts()
            }
        return build_filter(context, message)

    # EXISTING FLOWS (UNCHANGED)
    if decision in FLOW_STEPS:
        session.action = decision
        session.step = FLOW_STEPS[decision][0][0]
        db.commit()
        return FLOW_STEPS[decision][0][1]

    return "I can help start a contract, update phone, or create data filters."
