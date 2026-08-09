from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UUID
from datetime import datetime, timezone
import uuid

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password_hash = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    server_users = relationship("ServerUser", back_populates="user")

class ServerUser(Base):
    __tablename__ = "server_users"

    id = Column(Integer, primary_key=True)
    server_id = Column(Integer, ForeignKey("servers.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    role = Column(String)
    display_name = Column(String)
    joined_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="server_users")
    server = relationship("Server", back_populates="server_users")

class Server(Base):
    __tablename__ = "servers"

    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    daemon_keys = relationship("DaemonKey", back_populates="server")
    server_users = relationship("ServerUser", back_populates="server")

class DaemonKey(Base):
    __tablename__ = "daemon_keys"

    id = Column(Integer, primary_key=True)
    server_id = Column(Integer, ForeignKey("servers.id", ondelete="CASCADE"))
    key_hash = Column(String)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    server = relationship("Server", back_populates="daemon_keys")

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    level = Column(String)
    status = Column(String)
    start_at = Column(DateTime(timezone=True))
    end_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    payments = relationship("Payment", back_populates="subscription")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="SET NULL"))
    provider = Column(String)
    external_payment_id = Column(String)
    amount = Column(Integer)
    currency = Column(String)
    status = Column(String)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True))

    subscription = relationship("Subscription", back_populates="payments")
