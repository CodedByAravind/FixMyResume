from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.database.db import get_db
from app.models.user import User
from app.schemas.user import TokenPair, TokenRefresh, UserCreate, UserLogin, UserOut
from app.services import auth_service

router = APIRouter()


@router.post("/register", response_model=TokenPair, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    result = auth_service.register_user(
        db,
        name=payload.name,
        email=str(payload.email),
        password=payload.password,
    )
    return TokenPair(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        user=result["user"],
    )


@router.post("/login", response_model=TokenPair)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    result = auth_service.authenticate_user(
        db,
        email=str(payload.email),
        password=payload.password,
    )
    return TokenPair(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        user=result["user"],
    )


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: TokenRefresh, db: Session = Depends(get_db)):
    result = auth_service.refresh_tokens(db, refresh_token=payload.refresh_token)
    return TokenPair(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        user=result["user"],
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: TokenRefresh, db: Session = Depends(get_db)):
    auth_service.logout(db, refresh_token=payload.refresh_token)
    return None


@router.get("/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
