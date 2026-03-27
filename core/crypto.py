from __future__ import annotations

from cryptography.fernet import Fernet

from backend.config import settings


def _get_fernet() -> Fernet:
    if settings.encryption_key:
        return Fernet(settings.encryption_key.encode("utf-8"))
    raise RuntimeError(
        "APP_ENCRYPTION_KEY no está configurada. Genera una llave con generate_encryption_key() y guárdala en .env."
    )


def generate_encryption_key() -> str:
    return Fernet.generate_key().decode("utf-8")


def encrypt_value(value: str) -> bytes:
    return _get_fernet().encrypt(value.encode("utf-8"))


def decrypt_value(value: bytes) -> str:
    return _get_fernet().decrypt(value).decode("utf-8")
