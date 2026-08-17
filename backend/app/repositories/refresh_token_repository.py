from datetime import datetime

from sqlalchemy.orm import Session

from app.models.token import RefreshToken


def create_refresh_token(
    db: Session,
    *,
    user_id: int,
    token_hash: str,
    expires_at: datetime,
) -> RefreshToken:
    refresh_token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)
    return refresh_token


def get_refresh_token_by_hash(db: Session, token_hash: str) -> RefreshToken | None:
    return db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()


def revoke_refresh_token(db: Session, refresh_token: RefreshToken) -> None:
    refresh_token.revoked = True
    db.commit()


def is_refresh_token_valid(refresh_token: RefreshToken, now: datetime | None = None) -> bool:
    now = now or datetime.utcnow()
    return not refresh_token.revoked and refresh_token.expires_at > now
