from sqlalchemy.orm import Session
from flow_definitions import FLOW_STEPS
from models import Contract
from services.tools.hubspot import create_deal, update_phone
from validators import VALIDATORS

def handle_flow(db: Session, chat_session, message: str):
    steps = FLOW_STEPS[chat_session.action]

    current_index = next(
        (i for i, step in enumerate(steps) if step[0] == chat_session.step),
        None
    )
    if chat_session.data is None:
        chat_session.data = {}
    current_step = chat_session.step
    if current_step in VALIDATORS:
        is_valid, error_message = VALIDATORS[current_step](message)
        if not is_valid:
            return error_message
    chat_session.data[chat_session.step.lower()] = message
    db.commit()

    if current_index == len(steps) - 1:
        return finalize_action(db, chat_session)

    next_step, prompt = steps[current_index + 1]
    chat_session.step = next_step
    db.commit()
    return prompt


def finalize_action(db: Session, chat_session):
    data = chat_session.data if chat_session.data else {}
    action = chat_session.action
    response = "Something went wrong"

    try:
        if action == "START_CONTRACT":
            contract = Contract(
                session=chat_session,
                email=data.get("email", ""),
                name=data.get("name", ""),
                phone=data.get("phone", ""),
                address=data.get("address", ""),
                status="PENDING"
            )
            db.add(contract)
            db.commit()
            db.refresh(contract)

            deal_response=create_deal(data)
            contract.status = "COMPLETED"
            db.commit()

            response = {
                "message":"Contract started successfully",
                "deal_id":deal_response["deal_id"]
            }

        elif action == "UPDATE_PHONE":
            contract_id_str = data.get("contract_id")
            phone = data.get("phone")
            
            if not contract_id_str:
                return "Contract ID is missing"
            
            contract_id = int(contract_id_str)

            contract = db.query(Contract).filter_by(id=contract_id).first()
            if not contract:
                chat_session.step = "CONTRACT_ID"
                db.commit()
                return "Contract not found. Try again."

            contract.phone = phone
            db.commit()
            update_phone(contract_id, phone)

            response = "Phone updated successfully"

        chat_session.action = None
        chat_session.step = None
        chat_session.data = {}
        db.commit()

    except Exception as e:
        chat_session.action = None
        chat_session.step = None
        chat_session.data = {}
        db.commit()
        response = f"Error: {str(e)}"

    return response