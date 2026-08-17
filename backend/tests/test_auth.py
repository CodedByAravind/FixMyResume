import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database.db import get_db
from app.main import app

# Use an isolated temporary SQLite database for tests so we never touch the
# development database (fixmyresume.db).
_tmp = tempfile.NamedTemporaryFile(delete=False)
TEST_DB_PATH = _tmp.name
_tmp.close()

_test_engine = create_engine(f"sqlite:///{TEST_DB_PATH}", connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=_test_engine)

_TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)


def override_get_db():
    db = _TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def _clean_tables():
    # Reset tables between tests so they are independent.
    Base.metadata.drop_all(bind=_test_engine)
    Base.metadata.create_all(bind=_test_engine)
    yield


@pytest.fixture()
def registered_user():
    return {
        "name": "Test User",
        "email": "test@example.com",
        "password": "strongpassword",
    }


def test_register_success(registered_user):
    resp = client.post("/api/v1/auth/register", json=registered_user)
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test@example.com"
    assert "password" not in data["user"]

    # Verify the password is stored as a bcrypt hash, not plaintext.
    db = _TestingSessionLocal()
    from app.models.user import User
    user = db.query(User).filter(User.email == "test@example.com").first()
    assert user is not None
    assert user.password != "strongpassword"
    assert user.password.startswith("$2")
    db.close()


def test_register_duplicate_email(registered_user):
    client.post("/api/v1/auth/register", json=registered_user)
    resp = client.post("/api/v1/auth/register", json=registered_user)
    assert resp.status_code == 409


def test_register_invalid_email(registered_user):
    payload = {**registered_user, "email": "not-an-email"}
    resp = client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 422


def test_register_short_password(registered_user):
    payload = {**registered_user, "password": "short"}
    resp = client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 422


def test_register_oversized_password_returns_422(registered_user):
    # 73 ASCII bytes -> exceeds bcrypt's 72-byte limit -> clean 422, not 500.
    payload = {**registered_user, "password": "a" * 73}
    resp = client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 422


def test_register_72_byte_password_succeeds(registered_user):
    # Exactly 72 ASCII bytes is allowed.
    payload = {**registered_user, "password": "a" * 72}
    resp = client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201


def test_register_multibyte_password_byte_length(registered_user):
    # Use an emoji (4 UTF-8 bytes each). 18 emoji = 72 bytes -> allowed.
    ok_payload = {**registered_user, "password": "z" * 8 + "😀" * 16}  # 8 + 64 = 72 bytes
    resp = client.post("/api/v1/auth/register", json=ok_payload)
    assert resp.status_code == 201

    # 19 emoji = 76 bytes -> exceeds 72 -> 422.
    too_long_payload = {**registered_user, "email": "multi2@example.com", "password": "z" * 8 + "😀" * 19}
    resp = client.post("/api/v1/auth/register", json=too_long_payload)
    assert resp.status_code == 422



def test_login_success(registered_user):
    client.post("/api/v1/auth/register", json=registered_user)
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "strongpassword"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_wrong_password(registered_user):
    client.post("/api/v1/auth/register", json=registered_user)
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "wrongpassword"},
    )
    assert resp.status_code == 401


def test_login_nonexistent_user():
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "strongpassword"},
    )
    assert resp.status_code == 401


def test_me_with_valid_token(registered_user):
    client.post("/api/v1/auth/register", json=registered_user)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "strongpassword"},
    ).json()
    access = login["access_token"]
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@example.com"


def test_me_without_token():
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_me_with_invalid_token():
    resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert resp.status_code == 401


def test_refresh_rotates_token(registered_user):
    client.post("/api/v1/auth/register", json=registered_user)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "strongpassword"},
    ).json()
    old_refresh = login["refresh_token"]

    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert resp.status_code == 200
    data = resp.json()
    assert data["access_token"]

    # The old refresh token must be revoked after rotation.
    resp2 = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert resp2.status_code == 401


def test_refresh_with_invalid_token():
    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": "garbage"})
    assert resp.status_code == 401


def test_logout_revokes_token(registered_user):
    client.post("/api/v1/auth/register", json=registered_user)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "strongpassword"},
    ).json()
    refresh = login["refresh_token"]

    resp = client.post("/api/v1/auth/logout", json={"refresh_token": refresh})
    assert resp.status_code == 204

    # Refresh token must be revoked after logout.
    resp2 = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert resp2.status_code == 401


@pytest.fixture(scope="session", autouse=True)
def _cleanup():
    yield
    try:
        os.unlink(TEST_DB_PATH)
    except OSError:
        pass
