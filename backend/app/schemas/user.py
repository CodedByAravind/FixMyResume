from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_byte_length(cls, value: str) -> str:
        # bcrypt operates on the first 72 bytes of the password. Enforce that
        # limit at the schema boundary (by UTF-8 byte length, not char count)
        # so an oversized password returns a clean 422 instead of a 500.
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 bytes (UTF-8).")
        return value


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)



class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    is_active: bool
    created_at: Optional[datetime] = None


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut


class TokenRefresh(BaseModel):
    refresh_token: str
