from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import UUID, DateTime, Enum, ForeignKey, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.common.enums import (
    PaymentStatus,
    ServerUserRole,
    SubscriptionLevel,
    SubscriptionStatus,
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str | None]
    email_confirmed: Mapped[bool] = mapped_column(default=False)
    password_hash: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    server_users: Mapped[list["ServerUser"]] = relationship(back_populates="user")


class ServerUser(Base):
    __tablename__ = "server_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    server_id: Mapped[int] = mapped_column(ForeignKey("servers.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    role: Mapped[ServerUserRole] = mapped_column(
        Enum(ServerUserRole, name="server_user_role_enum"),
        default=ServerUserRole.VIEWER,
    )
    display_name: Mapped[str]
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="server_users")
    server: Mapped["Server"] = relationship(back_populates="server_users")


class Server(Base):
    __tablename__ = "servers"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, default=uuid.uuid4
    )
    daemon_key_hash: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    server_users: Mapped[list["ServerUser"]] = relationship(back_populates="server")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    level: Mapped[SubscriptionLevel] = mapped_column(
        Enum(SubscriptionLevel, name="subscription_level_enum"),
        default=SubscriptionLevel.FREE,
    )
    status: Mapped[SubscriptionStatus] = mapped_column(
        Enum(SubscriptionStatus, name="subscription_status_enum"),
        default=SubscriptionStatus.PENDING,
    )
    start_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    end_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    payments: Mapped[list["Payment"]] = relationship(back_populates="subscription")

    __table_args__ = (
        Index(
            "uq_idx_active_subscription_per_user",
            "user_id",
            unique=True,
            postgresql_where=(status == SubscriptionStatus.ACTIVE),
        ),
    )


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    subscription_id: Mapped[int | None] = mapped_column(
        ForeignKey("subscriptions.id", ondelete="SET NULL")
    )
    provider: Mapped[str]
    external_payment_id: Mapped[str]
    amount: Mapped[int]
    currency: Mapped[str]
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, name="payment_status_enum"), default=PaymentStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    subscription: Mapped["Subscription"] = relationship(back_populates="payments")
