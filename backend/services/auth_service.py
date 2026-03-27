from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import or_, select

from backend.models.entities import AppUser, UserSession, UserSettings
from core.auth import hash_master_password, hash_session_token, verify_master_password
from database.connection import session_scope


class AuthenticationError(Exception):
    pass


class RegistrationError(Exception):
    pass


@dataclass
class AuthService:
    default_username: str
    session_timeout_minutes: int

    def login(self, username: str, password: str, ip_address: str | None, user_agent: str | None) -> dict:
        if not username or not password:
            raise AuthenticationError("Usuario y contraseña son obligatorios.")

        with session_scope() as session:
            user = session.scalar(
                select(AppUser).where(AppUser.username == username.strip(), AppUser.is_active.is_(True))
            )
            if not user:
                raise AuthenticationError("Usuario o contraseña inválidos.")

            if not verify_master_password(password, user.master_password_hash):
                raise AuthenticationError("Usuario o contraseña inválidos.")

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

    def register_user(self, payload: dict) -> dict:
        username = (payload.get("username") or "").strip()
        full_name = (payload.get("full_name") or "").strip()
        email = (payload.get("email") or "").strip()
        password = payload.get("password") or ""

        if not username or not full_name or not password:
            raise RegistrationError("Usuario, nombre completo y contraseña son obligatorios.")

        with session_scope() as session:
            conditions = [AppUser.username == username]
            if email:
                conditions.append(AppUser.email == email)
            existing = session.scalar(select(AppUser).where(or_(*conditions)))
            if existing:
                raise RegistrationError("Ya existe un usuario con ese nombre o correo.")

            user = AppUser(
                username=username,
                full_name=full_name,
                email=email or None,
                master_password_hash=hash_master_password(password),
                password_hint=(payload.get("password_hint") or "").strip() or None,
            )
            session.add(user)
            session.flush()

            settings = UserSettings(user_id=user.id)
            session.add(settings)

            return {
                "id": str(user.id),
                "username": user.username,
                "full_name": user.full_name,
                "email": user.email,
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
