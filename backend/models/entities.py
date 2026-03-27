from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, BIGINT, UUID, Boolean, CheckConstraint, DateTime, ForeignKey, Integer, LargeBinary, String, Text, text
from sqlalchemy.dialects.postgresql import ARRAY, INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))


class AppUser(TimestampMixin, Base):
    __tablename__ = "app_users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    username: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    full_name: Mapped[str | None] = mapped_column(String(150))
    email: Mapped[str | None] = mapped_column(String(150), unique=True)
    master_password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    password_hint: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("TRUE"))
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    vault_credentials: Mapped[list["VaultCredential"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    sessions: Mapped[list["UserSession"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class UserSession(Base):
    __tablename__ = "user_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("app_users.id", ondelete="CASCADE"), nullable=False)
    session_token_hash: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    ip_address: Mapped[str | None] = mapped_column(INET)
    user_agent: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("TRUE"))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["AppUser"] = relationship(back_populates="sessions")


class HostingProvider(TimestampMixin, Base):
    __tablename__ = "hosting_providers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("app_users.id", ondelete="CASCADE"), nullable=False)
    provider_name: Mapped[str] = mapped_column(String(120), nullable=False)
    access_url: Mapped[str] = mapped_column(Text, nullable=False)
    account_username: Mapped[str] = mapped_column(String(150), nullable=False)
    account_email: Mapped[str | None] = mapped_column(String(150))
    encrypted_password: Mapped[bytes | None] = mapped_column(LargeBinary)
    notes: Mapped[str | None] = mapped_column(Text)
    is_favorite: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("FALSE"))
    last_accessed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class VaultCredential(TimestampMixin, Base):
    __tablename__ = "vault_credentials"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("app_users.id", ondelete="CASCADE"), nullable=False)
    service_name: Mapped[str] = mapped_column(String(150), nullable=False)
    login_username: Mapped[str] = mapped_column(String(150), nullable=False)
    login_url: Mapped[str | None] = mapped_column(Text)
    encrypted_password: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    encrypted_notes: Mapped[bytes | None] = mapped_column(LargeBinary)
    category: Mapped[str | None] = mapped_column(String(80))
    is_favorite: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("FALSE"))
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["AppUser"] = relationship(back_populates="vault_credentials")


class TechnicalDocument(TimestampMixin, Base):
    __tablename__ = "technical_documents"
    __table_args__ = (
        CheckConstraint("document_type IN ('PDF', 'TXT', 'NOTE')", name="technical_documents_type_chk"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("app_users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    document_type: Mapped[str] = mapped_column(String(20), nullable=False)
    file_path: Mapped[str | None] = mapped_column(Text)
    file_name: Mapped[str | None] = mapped_column(String(255))
    mime_type: Mapped[str | None] = mapped_column(String(120))
    file_size_bytes: Mapped[int | None] = mapped_column(BIGINT)
    content_text: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, server_default=text("ARRAY[]::TEXT[]"))
    last_opened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        CheckConstraint("severity IN ('info', 'warning', 'critical')", name="notifications_severity_chk"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("app_users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'info'"))
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("FALSE"))
    related_entity_type: Mapped[str | None] = mapped_column(String(50))
    related_entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class AccessLog(Base):
    __tablename__ = "access_logs"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("app_users.id", ondelete="SET NULL"))
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    details: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))


class UserSettings(TimestampMixin, Base):
    __tablename__ = "user_settings"
    __table_args__ = (
        CheckConstraint("session_timeout_minutes BETWEEN 1 AND 240", name="user_settings_timeout_chk"),
        CheckConstraint("clipboard_clear_seconds BETWEEN 5 AND 300", name="user_settings_clipboard_chk"),
        CheckConstraint("theme IN ('dark', 'light')", name="user_settings_theme_chk"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("app_users.id", ondelete="CASCADE"), nullable=False)
    session_timeout_minutes: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("10"))
    theme: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'dark'"))
    locale: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'es_MX'"))
    api_base_url: Mapped[str | None] = mapped_column(Text)
    auto_lock_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("TRUE"))
    clipboard_clear_seconds: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("30"))
