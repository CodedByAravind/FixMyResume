import os
import tempfile

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database.db import get_db
from app.main import app

# One isolated temporary SQLite database shared by all test modules so the
# global get_db override is consistent across the whole session.
_tmp = tempfile.NamedTemporaryFile(delete=False)
TEST_DB_PATH = _tmp.name
_tmp.close()

_test_engine = create_engine(
    f"sqlite:///{TEST_DB_PATH}",
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=_test_engine,
)

Base.metadata.create_all(bind=_test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def _clean_db():
    """Reset tables after every test so tests stay independent."""
    yield
    Base.metadata.drop_all(bind=_test_engine)
    Base.metadata.create_all(bind=_test_engine)


@pytest.fixture()
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def _cleanup():
    yield
    try:
        os.unlink(TEST_DB_PATH)
    except OSError:
        pass
