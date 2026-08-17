from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core import security
from app.models.user import User
from app.repositories import user_repository, refresh_token_repository


def _issue_token_pair(db: Session, user: User) -> dict:
    """Generate an access JWT and an opaque refresh token (stored only as a hash)."""
    access_token = security.create_access_token(user.id)

    raw_refresh_token = security.generate_refresh_token()
    token_hash = security.hash_refresh_token(raw_refresh_token)
    expires_at = security.refresh_token_expiry()

    refresh_token_repository.create_refresh_token(
        db,
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    return {
        "access_token": access_token,
        "refresh_token": raw_refresh_token,
    }


def build_token_pair(db: Session, user: User) -> dict:
    return _issue_token_pair(db, user)


def register_user(db: Session, *, name: str, email: str, password: str) -> dict:
    """Create a user and automatically log them in (returns token pair + user)."""
    existing = user_repository.get_user_by_email(db, email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    hashed_password = security.hash_password(password)
    user = user_repository.create_user(
        db,
        name=name,
        email=email,
        hashed_password=hashed_password,
    )

    tokens = _issue_token_pair(db, user)
    return {**tokens, "user": user}


def authenticate_user(db: Session, *, email: str, password: str) -> dict:
    user = user_repository.get_user_by_email(db, email)
    # Generic error message to avoid user enumeration.
    if not user or not security.verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is inactive.",
        )

    tokens = _issue_token_pair(db, user)
    return {**tokens, "user": user}


def refresh_tokens(db: Session, *, refresh_token: str) -> dict:
    token_hash = security.hash_refresh_token(refresh_token)
    stored = refresh_token_repository.get_refresh_token_by_hash(db, token_hash)

    if not stored or not refresh_token_repository.is_refresh_token_valid(stored):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
        )

    user = user_repository.get_user_by_id(db, stored.user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
        )

    # Rotate: revoke old token, issue a new pair.
    refresh_token_repository.revoke_refresh_token(db, stored)
    tokens = _issue_token_pair(db, user)
    return {**tokens, "user": user}


def logout(db: Session, *, refresh_token: str) -> None:
    token_hash = security.hash_refresh_token(refresh_token)
    stored = refresh_token_repository.get_refresh_token_by_hash(db, token_hash)
    if stored:
        refresh_token_repository.revoke_refresh_token(db, stored)
