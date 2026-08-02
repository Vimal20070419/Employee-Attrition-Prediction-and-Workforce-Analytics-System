"""Integration tests for FastAPI endpoints"""
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
