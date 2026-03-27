from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload

from backend.models.entities import AccessLog, AppUser, HostingDomain, HostingMailbox, HostingProvider, UserSession
from core.auth import hash_session_token
from core.crypto import decrypt_value, encrypt_value
from database.connection import session_scope


class HostingServiceError(Exception):
    pass


class HostingService:
    def list_providers(self, raw_token: str, query: str = "") -> list[dict]:
        user_id = self._get_authenticated_user_id(raw_token)
        with session_scope() as session:
            statement = (
                select(HostingProvider)
                .options(
                    selectinload(HostingProvider.domains),
                    selectinload(HostingProvider.mailboxes),
                )
                .where(HostingProvider.user_id == user_id)
                .order_by(HostingProvider.provider_name.asc())
            )
            if query:
                like_query = f"%{query.strip()}%"
                statement = statement.where(
                    or_(
                        HostingProvider.provider_name.ilike(like_query),
                        HostingProvider.account_username.ilike(like_query),
                        HostingProvider.access_url.ilike(like_query),
                    )
                )
            providers = session.scalars(statement).all()
            return [self._serialize_provider(provider) for provider in providers]

    def create_provider(self, raw_token: str, payload: dict) -> dict:
        user_id = self._get_authenticated_user_id(raw_token)
        provider_name = (payload.get("provider_name") or "").strip()
        access_url = (payload.get("access_url") or "").strip()
        account_username = (payload.get("account_username") or "").strip()
        account_password = payload.get("account_password") or ""

        if not provider_name or not access_url or not account_username or not account_password:
            raise HostingServiceError("Proveedor, URL, usuario y contraseña son obligatorios.")

        with session_scope() as session:
            provider = HostingProvider(
                user_id=user_id,
                provider_name=provider_name,
                access_url=access_url,
                account_username=account_username,
                encrypted_password=encrypt_value(account_password),
                notes=(payload.get("notes") or "").strip() or None,
            )
            session.add(provider)
            session.flush()

            for domain_payload in payload.get("domains", []):
                domain_name = (domain_payload.get("domain_name") or "").strip()
                if not domain_name:
                    continue
                session.add(
                    HostingDomain(
                        provider_id=provider.id,
                        domain_name=domain_name,
                        domain_url=(domain_payload.get("domain_url") or "").strip() or None,
                        expiration_date=self._parse_date(domain_payload.get("expiration_date")),
                        last_payment_date=self._parse_date(domain_payload.get("last_payment_date")),
                        notes=(domain_payload.get("notes") or "").strip() or None,
                    )
                )

            for mailbox_payload in payload.get("mailboxes", []):
                email_address = (mailbox_payload.get("email_address") or "").strip()
                if not email_address:
                    continue
                session.add(
                    HostingMailbox(
                        provider_id=provider.id,
                        email_address=email_address,
                        encrypted_password=encrypt_value(mailbox_payload.get("password") or "")
                        if mailbox_payload.get("password")
                        else None,
                        owner_name=(mailbox_payload.get("owner_name") or "").strip() or None,
                        notes=(mailbox_payload.get("notes") or "").strip() or None,
                    )
                )

            session.flush()
            provider = session.scalar(
                select(HostingProvider)
                .options(
                    selectinload(HostingProvider.domains),
                    selectinload(HostingProvider.mailboxes),
                )
                .where(HostingProvider.id == provider.id)
            )
            self._log(session, user_id, "hosting_providers", provider.id, "create")
            return self._serialize_provider(provider)

    def delete_provider(self, raw_token: str, provider_id: UUID) -> None:
        user_id = self._get_authenticated_user_id(raw_token)
        with session_scope() as session:
            provider = session.scalar(
                select(HostingProvider).where(HostingProvider.id == provider_id, HostingProvider.user_id == user_id)
            )
            if not provider:
                raise HostingServiceError("Proveedor no encontrado.")
            session.delete(provider)
            self._log(session, user_id, "hosting_providers", provider_id, "delete")

    def _get_authenticated_user_id(self, raw_token: str) -> UUID:
        if not raw_token:
            raise HostingServiceError("Falta el token de sesión.")

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
                raise HostingServiceError("Sesión inválida o expirada.")
            user = session.get(AppUser, db_session.user_id)
            if not user or not user.is_active:
                raise HostingServiceError("Usuario no disponible.")
            db_session.last_activity_at = datetime.now(UTC)
            session.flush()
            return user.id

    def _serialize_provider(self, provider: HostingProvider) -> dict:
        return {
            "id": str(provider.id),
            "provider_name": provider.provider_name,
            "access_url": provider.access_url,
            "account_username": provider.account_username,
            "account_password": decrypt_value(provider.encrypted_password) if provider.encrypted_password else "",
            "notes": provider.notes,
            "created_at": provider.created_at.isoformat() if provider.created_at else None,
            "domains": [
                {
                    "id": str(domain.id),
                    "domain_name": domain.domain_name,
                    "domain_url": domain.domain_url,
                    "expiration_date": domain.expiration_date.date().isoformat() if domain.expiration_date else "",
                    "last_payment_date": domain.last_payment_date.date().isoformat() if domain.last_payment_date else "",
                    "notes": domain.notes,
                }
                for domain in sorted(provider.domains, key=lambda item: item.domain_name.lower())
            ],
            "mailboxes": [
                {
                    "id": str(mailbox.id),
                    "email_address": mailbox.email_address,
                    "password": decrypt_value(mailbox.encrypted_password) if mailbox.encrypted_password else "",
                    "owner_name": mailbox.owner_name,
                    "notes": mailbox.notes,
                }
                for mailbox in sorted(provider.mailboxes, key=lambda item: item.email_address.lower())
            ],
        }

    def _parse_date(self, value: str | None):
        if not value:
            return None
        try:
            return datetime.fromisoformat(value).replace(tzinfo=UTC)
        except ValueError as exc:
            raise HostingServiceError(f"Fecha inválida: {value}") from exc

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
