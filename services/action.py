def detect_action(message: str):
    msg = message.lower()
    if "start contract" in msg:
        return "START_CONTRACT"
    if "update phone" in msg:
        return "UPDATE_PHONE"
    return None
