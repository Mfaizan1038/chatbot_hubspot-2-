def detect_action(message: str):
    msg = message.lower().strip()

    # ---------- CONTRACT FLOWS ----------
    if any(k in msg for k in ["start contract", "new contract", "create contract"]):
        return "START_CONTRACT"

    if any(k in msg for k in ["update phone", "change phone"]):
        return "UPDATE_PHONE"

    # ---------- FILTER / QUERY ----------
    if any(k in msg for k in [
        "filter",
        "query",
        "show",
        "list",
        "give me",
        "get",
        "find",
        "with",
        "where",
        "=",
        "equals",
        "is"
    ]):
        return "CREATE_FILTER"

    # ---------- UPDATE QUERY ----------
    if any(w in msg for w in ["update", "set", "change", "modify"]):
        return "UPDATE_FILTER"

    return "REJECT"
