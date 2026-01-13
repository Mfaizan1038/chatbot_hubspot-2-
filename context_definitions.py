AVAILABLE_CONTEXTS = {
    "USERS": {
        "table_name": "users",
        "columns": {
            "id": {"type": "INTEGER"},
            "name": {"type": "STRING"},
            "email": {"type": "STRING"},
            "age": {"type": "INTEGER"},
            "status": {"type": "STRING"},
        }
    },
    "CONTRACTS": {
        "table_name": "contracts",
        "columns": {
            "id": {"type": "INTEGER"},
            "email": {"type": "STRING"},
            "name": {"type": "STRING"},
            "phone": {"type": "STRING"},
            "address": {"type": "STRING"},
            "status": {"type": "STRING"},
        }
    }
}

def get_context_info(key: str):
    return AVAILABLE_CONTEXTS.get(key.upper())

def list_available_contexts():
    return list(AVAILABLE_CONTEXTS.keys())
