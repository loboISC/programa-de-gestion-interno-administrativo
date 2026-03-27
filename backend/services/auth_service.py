from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from backend.models.entities import AppUser, UserSession
from core.auth import hash_session_token, verify_master_password
from database.connection import session_scope


class AuthenticationError(Exception):
    pass


@dataclass
class AuthService:
    default_username: str
    session_timeout_minutes: int

    def login(self, master_password: str, ip_address: str | None, user_agent: str | None) -> dict:
        if not master_password:
            raise AuthenticationError("La contraseña maestra es obligatoria.")

        with session_scope() as session:
            user = session.scalar(select(AppUser).where(AppUser.username == self.default_username, AppUser.is_active.is_(True)))
            if not user:
                raise AuthenticationError("No existe un usuario interno configurado para el login.")

            if not verify_master_password(master_password, user.master_password_hash):
                raise AuthenticationError("Credenciales inválidas.")

            raw_token, token_hash = hash_session_token()
            expires_at = datetime.now(UTC) + timedelta(minutes=self.session_timeout_minutes)

            db_session = UserSession(
                user_id=user.id,
                session_token_hash=token_hash,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=expires_at,
            )
            user.last_login_at = datetime.now(UTC)
            session.add(db_session)
            session.flush()

            return {
                "token": raw_token,
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "full_name": user.full_name,
                },
                "expires_at": expires_at.isoformat(),
            }

    def validate_session(self, raw_token: str) -> dict | None:
        if not raw_token:
            return None

        with session_scope() as session:
            token_hash = hash_session_token(raw_token=raw_token)[1]
            db_session = session.scalar(
                select(UserSession).where(
                    UserSession.session_token_hash == token_hash,
                    UserSession.is_active.is_(True),
                    UserSession.expires_at > datetime.now(UTC),
                )
            )
            if not db_session:
                return None

            user = session.get(AppUser, db_session.user_id)
            if not user or not user.is_active:
                return None
            db_session.last_activity_at = datetime.now(UTC)
            return {
                "id": str(user.id),
                "username": user.username,
                "full_name": user.full_name,
            }
