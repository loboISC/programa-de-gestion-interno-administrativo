from __future__ import annotations

import hashlib
import secrets
from typing import Tuple

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash, VerificationError, VerifyMismatchError

password_hasher = PasswordHasher()


def hash_master_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_master_password(password: str, password_hash: str) -> bool:
    try:
        return password_hasher.verify(password_hash, password)
    except (VerifyMismatchError, InvalidHash, VerificationError):
        return False


def hash_session_token(raw_token: str | None = None) -> Tuple[str, str]:
    token = raw_token or secrets.token_urlsafe(32)
    return token, hashlib.sha256(token.encode("utf-8")).hexdigest()
