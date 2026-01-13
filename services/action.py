def detect_action(message: str):
    msg = message.lower().strip()

    if any(k in msg for k in ["start contract", "new contract", "create contract"]):
        return "START_CONTRACT"

    if any(k in msg for k in ["update phone", "change phone"]):
        return "UPDATE_PHONE"

    if any(k in msg for k in [
        "filter", "query", "max", "min", "count",
        "greater", "less", "show", "list"
    ]):
        return "CREATE_FILTER"

    return "REJECT"
