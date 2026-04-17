import os

# For demonstration/testing purposes, we store the current session's retailer phone.
# In a real app, this would be set during authentication or per-request context.
_current_retailer_number = "+919900000001"

def get_current_retailer_number() -> str:
    return os.getenv("CURRENT_RETAILER_NUMBER", _current_retailer_number)

def set_current_retailer_number(phone: str):
    global _current_retailer_number
    _current_retailer_number = phone
