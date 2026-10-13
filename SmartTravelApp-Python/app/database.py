from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

from .config import DATABASE_URL


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "Users"

    id: Mapped[int] = mapped_column("Id", Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column("Email", String(256), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column("PasswordHash", String, nullable=False)
    is_email_confirmed: Mapped[bool] = mapped_column("IsEmailConfirmed", Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column("CreatedAt", DateTime, default=utcnow)

    confirmation_tokens = relationship("EmailConfirmationToken", back_populates="user", cascade="all, delete-orphan")
    search_logs = relationship("UserSearchLog", back_populates="user", cascade="all, delete-orphan")


class EmailConfirmationToken(Base):
    __tablename__ = "EmailConfirmationTokens"

    id: Mapped[int] = mapped_column("Id", Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column("UserId", ForeignKey("Users.Id", ondelete="CASCADE"))
    token: Mapped[str] = mapped_column("Token", String(128), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column("ExpiresAt", DateTime, nullable=False)
    is_used: Mapped[bool] = mapped_column("IsUsed", Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column("CreatedAt", DateTime, default=utcnow)

    user = relationship("User", back_populates="confirmation_tokens")


class UserSearchLog(Base):
    __tablename__ = "UserSearchLogs"

    id: Mapped[int] = mapped_column("Id", Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column("UserId", ForeignKey("Users.Id", ondelete="CASCADE"))
    query: Mapped[str] = mapped_column("Query", String(100), nullable=False)
    searched_at: Mapped[datetime] = mapped_column("SearchedAt", DateTime, default=utcnow)

    user = relationship("User", back_populates="search_logs")


connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
