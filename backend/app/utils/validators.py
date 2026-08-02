"""AttritionIQ — Data Validation Utility"""

import re
from typing import List, Tuple


def validate_email(email: str) -> bool:
    """Regex validation for email addresses."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email))


def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
    """Validate password rules: length >= 8, uppercase, digit."""
    errors = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter")
    if not re.search(r"\d", password):
        errors.append("Password must contain at least one digit")
    return len(errors) == 0, errors
