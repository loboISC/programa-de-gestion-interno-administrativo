from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import or_, select

from backend.models.entities import AccessLog, AppUser, UserSession, VaultCredential
from core.auth import hash_session_token
from core.crypto import decrypt_value, encrypt_value
from database.connection import session_scope


class VaultServiceError(Exception):
    pass


class VaultService:
    def list_credentials(self, raw_token: str, query: str = "") -> list[dict]:
        user = self._get_authenticated_user(raw_token)
        with session_scope() as session:
            statement = select(VaultCredential).where(VaultCredential.user_id == user.id)
            if query:
                like_query = f"%{query.strip()}%"
                statement = statement.where(
                    or_(
                        VaultCredential.service_name.ilike(like_query),
                        VaultCredential.login_username.ilike(like_query),
                    )
                )
            statement = statement.order_by(VaultCredential.service_name.asc())
            items = session.scalars(statement).all()
            return [self._serialize(item, include_password=True) for item in items]

    def create_credential(self, raw_token: str, payload: dict) -> dict:
        user = self._get_authenticated_user(raw_token)
        service_name = (payload.get("service_name") or "").strip()
        login_username = (payload.get("login_username") or "").strip()
        password = payload.get("password") or ""

        if not service_name or not login_username or not password:
            raise VaultServiceError("Servicio, usuario y contraseña son obligatorios.")

        with session_scope() as session:
            credential = VaultCredential(
                user_id=user.id,
                service_name=service_name,
                login_username=login_username,
                login_url=(payload.get("login_url") or "").strip() or None,
                encrypted_password=encrypt_value(password),
                encrypted_notes=encrypt_value(payload["notes"]) if payload.get("notes") else None,
                category=(payload.get("category") or "").strip() or None,
                is_favorite=bool(payload.get("is_favorite", False)),
            )
            session.add(credential)
            session.flush()
            self._log(session, user.id, "vault_credentials", credential.id, "create")
            return self._serialize(credential, include_password=True)

    def update_credential(self, raw_token: str, credential_id: UUID, payload: dict) -> dict:
        user = self._get_authenticated_user(raw_token)
        with session_scope() as session:
            credential = session.scalar(
                select(VaultCredential).where(VaultCredential.id == credential_id, VaultCredential.user_id == user.id)
            )
            if not credential:
                raise VaultServiceError("Credencial no encontrada.")

            if payload.get("service_name") is not None:
                credential.service_name = payload["service_name"].strip()
            if payload.get("login_username") is not None:
                credential.login_username = payload["login_username"].strip()
            if payload.get("login_url") is not None:
                credential.login_url = payload["login_url"].strip() or None
            if payload.get("password"):
                credential.encrypted_password = encrypt_value(payload["password"])
            if "notes" in payload:
                credential.encrypted_notes = encrypt_value(payload["notes"]) if payload.get("notes") else None
            if "category" in payload:
                credential.category = payload["category"].strip() or None
            if "is_favorite" in payload:
                credential.is_favorite = bool(payload["is_favorite"])
            credential.last_used_at = datetime.now(UTC)
            session.flush()
            self._log(session, user.id, "vault_credentials", credential.id, "update")
            return self._serialize(credential, include_password=True)

    def delete_credential(self, raw_token: str, credential_id: UUID) -> None:
        user = self._get_authenticated_user(raw_token)
        with session_scope() as session:
            credential = session.scalar(
                select(VaultCredential).where(VaultCredential.id == credential_id, VaultCredential.user_id == user.id)
            )
            if not credential:
                raise VaultServiceError("Credencial no encontrada.")
            session.delete(credential)
            self._log(session, user.id, "vault_credentials", credential_id, "delete")

    def _get_authenticated_user(self, raw_token: str) -> AppUser:
        if not raw_token:
            raise VaultServiceError("Falta el token de sesión.")

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
                raise VaultServiceError("Sesión inválida o expirada.")
            user = session.get(AppUser, db_session.user_id)
            if not user or not user.is_active:
                raise VaultServiceError("Usuario no disponible.")
            db_session.last_activity_at = datetime.now(UTC)
            session.flush()
            return user

    def _serialize(self, credential: VaultCredential, include_password: bool) -> dict:
        payload = {
            "id": str(credential.id),
            "service_name": credential.service_name,
            "login_username": credential.login_username,
            "login_url": credential.login_url,
            "category": credential.category,
            "is_favorite": credential.is_favorite,
            "created_at": credential.created_at.isoformat() if credential.created_at else None,
            "updated_at": credential.updated_at.isoformat() if credential.updated_at else None,
        }
        if include_password:
            payload["password"] = decrypt_value(credential.encrypted_password)
            payload["notes"] = decrypt_value(credential.encrypted_notes) if credential.encrypted_notes else None
        return payload

    def _log(self, session, user_id: UUID, entity_type: str, entity_id: UUID, action: str) -> None:
        session.add(
            AccessLog(
                user_id=user_id,
                entity_type=entity_type,
                entity_id=entity_id,
                action=action,
                details={},
            )
        )
