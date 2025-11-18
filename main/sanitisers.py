from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re

# --- VALIDATION FUNCTIONS ---

def is_valid_email(email: str) -> bool:
    try:
        validate_email(email.strip().lower())
        return True
    except ValidationError:
        return False
    
def is_valid_phone(phone: str) -> bool:
    """
    Validate international phone numbers in E.164 format.
    Accepts: +441234567890 or +1-202-555-0173 (after cleaning).
    """
    # Remove spaces, dashes, parentheses
    clean_phone = re.sub(r'[^\d+]', '', phone.strip())

    # Basic E.164 check: + followed by 10–15 digits
    return bool(re.fullmatch(r'^\+\d{10,15}$', clean_phone))

def validate_passwords(password: str, password_confirm: str) -> bool:
    if password != password_confirm:
        return False
    return re.match(
        r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#^])[A-Za-z\d@$!%*?&#^]{8,}$',
        password
    ) is not None


# --- TRIMMING / CLEANING FUNCTIONS ---

def trim_whitespace(value: str) -> str:
    """Strip leading/trailing whitespace and reduce internal multiple spaces to one."""
    return re.sub(r'\s+', ' ', value.strip())


def trim_name(value: str) -> str:
    """Trim and capitalise name-like inputs (e.g. ' john  SMITH ' → 'John Smith')."""
    cleaned = trim_whitespace(value)
    return ' '.join(part.capitalize() for part in cleaned.split())


def clean_email(email: str) -> str:
    """Lowercase and trim email."""
    return email.strip().lower()


def clean_phone(phone: str) -> str:
    """Trim and clean phone number into E.164-compatible format (non-validating)."""
    return re.sub(r'[^\d+]', '', phone.strip())