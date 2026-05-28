import sqlite3
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app
from app.db import get_db

SCHEMA_PATH = Path(__file__).parent.parent / "schema.sql"


@pytest.fixture()
def db():
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA_PATH.read_text())
    conn.commit()
    yield conn
    conn.close()


@pytest.fixture()
def client(db):
    def override():
        yield db

    app.dependency_overrides[get_db] = override
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()
