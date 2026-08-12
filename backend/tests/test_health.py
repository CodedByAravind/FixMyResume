from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["database"] == "ok"


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "FixMyResume Backend Running"


def test_db_endpoint():
    response = client.get("/test-db")
    assert response.status_code == 200
    assert response.json()["message"] == "Database connected successfully"