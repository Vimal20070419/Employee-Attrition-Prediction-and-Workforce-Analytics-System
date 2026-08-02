"""
AttritionIQ — Backend Unit Tests (pytest)
===========================================
"""

import pytest
from app.auth.password import hash_password, verify_password
from app.auth.jwt_handler import create_access_token, decode_access_token


def test_password_hashing():
    raw_password = "SecretPassword123"
    hashed = hash_password(raw_password)
    assert hashed != raw_password
    assert verify_password(raw_password, hashed)
    assert not verify_password("WrongPassword", hashed)


def test_jwt_token_generation():
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    role = "hr_manager"
    token = create_access_token(user_id=user_id, role=role)

    payload = decode_access_token(token)
    assert payload["sub"] == user_id
    assert payload["role"] == role
    assert payload["type"] == "access"
