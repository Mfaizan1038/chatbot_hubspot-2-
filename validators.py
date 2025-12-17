import re

def validate_email(email: str) -> tuple[bool, str]:
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(email_pattern, email.strip()):
        return True, ""
    return False, "Invalid email format. Please provide a valid email (e.g., example@gmail.com)"

def validate_phone(phone: str) -> tuple[bool, str]:
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    
    phone_pattern = r'^\+?[0-9]{10,15}$'
    if re.match(phone_pattern, cleaned):
        return True, ""
    return False, "Invalid phone number. Please provide a valid phone number (10-15 digits, optional + prefix)"

def validate_name(name: str) -> tuple[bool, str]:
    """Validate name format"""
    name = name.strip()
    if len(name) >= 2 and re.match(r'^[a-zA-Z\s]+$', name):
        return True, ""
    return False, "Invalid name. Please provide a valid name (at least 2 characters, letters only)"

def validate_address(address: str) -> tuple[bool, str]:
    address = address.strip()
    if len(address) >= 5:
        return True, ""
    return False, "Invalid address. Please provide a complete address (at least 5 characters)"

def validate_contract_id(contract_id: str) -> tuple[bool, str]:
    if contract_id.strip().isdigit():
        return True, ""
    return False, "Invalid Contract ID. Please provide a numeric ID"

VALIDATORS = {
    "EMAIL": validate_email,
    "NAME": validate_name,
    "PHONE": validate_phone,
    "ADDRESS": validate_address,
    "CONTRACT_ID": validate_contract_id,
}