import logging
import uuid
from datetime import timedelta, timezone, datetime
from typing import Optional

import bcrypt
import jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import JWT_AUDIENCE, JWT_EXPIRE_HOURS, JWT_ISSUER, JWT_KEY
from ..database import EmailConfirmationToken, User, utcnow
from ..schemas import AuthResponse, LoginRequest, RegisterRequest, UserProfileDto

logger = logging.getLogger("smarttravel.email")


def send_activation_email(recipient_email: str, activation_token: str, base_url: str) -> None:
    """Symulowana wysyłka e-maila (log w konsoli) – odpowiednik EmailService."""
    url = f"{base_url.rstrip('/')}/api/auth/confirm-email?token={activation_token}"
    logger.info("=" * 66)
    logger.info("[EMAIL ACTIVATION SIMULATION] Do: %s", recipient_email)
    logger.info("Link Aktywacyjny: %s", url)
    logger.info("=" * 66)


def register(db: Session, request: RegisterRequest, base_url: str) -> AuthResponse:
    if not request.email.strip() or not request.password.strip():
        return AuthResponse(success=False, message="Email i hasło są wymagane.")

    email = request.email.strip().lower()
    if db.scalar(select(User).where(User.email == email)):
        return AuthResponse(success=False, message="Użytkownik o podanym adresie e-mail już istnieje.")

    password_hash = bcrypt.hashpw(request.password.encode(), bcrypt.gensalt()).decode()
    user = User(email=email, password_hash=password_hash, is_email_confirmed=False, created_at=utcnow())
    db.add(user)
    db.commit()

    token_str = uuid.uuid4().hex + uuid.uuid4().hex
    db.add(EmailConfirmationToken(
        user_id=user.id, token=token_str, expires_at=utcnow() + timedelta(hours=24),
        is_used=False, created_at=utcnow(),
    ))
    db.commit()

    send_activation_email(user.email, token_str, base_url)
    link = f"{base_url.rstrip('/')}/api/auth/confirm-email?token={token_str}"
    return AuthResponse(
        success=True,
        message="Rejestracja powiodła się! Na podany adres e-mail został wysłany link aktywacyjny.",
        email=user.email, activation_link=link,
    )


def confirm_email(db: Session, token: Optional[str]) -> AuthResponse:
    if not token or not token.strip():
        return AuthResponse(success=False, message="Nieprawidłowy token aktywacyjny.")

    ct = db.scalar(select(EmailConfirmationToken).where(EmailConfirmationToken.token == token))
    if ct is None:
        return AuthResponse(success=False, message="Token aktywacyjny nie istnieje w systemie.")
    if ct.is_used:
        return AuthResponse(success=False, message="Ten token aktywacyjny został już wcześniej wykorzystany.")
    if ct.expires_at < utcnow():
        return AuthResponse(success=False, message="Token aktywacyjny wygasł. Proszę zarejestrować się ponownie.")

    ct.is_used = True
    if ct.user:
        ct.user.is_email_confirmed = True
    db.commit()

    return AuthResponse(
        success=True, message="Konto zostało pomyślnie aktywowane! Możesz się teraz zalogować.",
        email=ct.user.email if ct.user else None,
    )


def login(db: Session, request: LoginRequest) -> AuthResponse:
    if not request.email.strip() or not request.password.strip():
        return AuthResponse(success=False, message="Proszę podać e-mail oraz hasło.")

    email = request.email.strip().lower()
    user = db.scalar(select(User).where(User.email == email))
    bad = AuthResponse(success=False, message="Nieprawidłowy e-mail lub hasło.")
    if user is None:
        return bad
    try:
        ok = bcrypt.checkpw(request.password.encode(), user.password_hash.encode())
    except ValueError:
        ok = False
    if not ok:
        return bad

    if not user.is_email_confirmed:
        return AuthResponse(
            success=False,
            message="Konto nie zostało jeszcze aktywowane. Proszę kliknąć w link aktywacyjny przesłany na adres e-mail.",
        )

    return AuthResponse(success=True, message="Logowanie udane!", token=generate_jwt(user), email=user.email)


def get_user_profile(db: Session, user_id: int) -> Optional[UserProfileDto]:
    user = db.get(User, user_id)
    if user is None:
        return None
    return UserProfileDto(
        id=user.id, email=user.email, is_email_confirmed=user.is_email_confirmed, created_at=user.created_at,
    )


def generate_jwt(user: User) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "jti": str(uuid.uuid4()),
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": now,
        "exp": now + timedelta(hours=JWT_EXPIRE_HOURS),
    }
    return jwt.encode(payload, JWT_KEY, algorithm="HS256")
