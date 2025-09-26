# ruff: noqa: ARG001
from fastapi.testclient import TestClient

from app.utils.config import settings

BASE_URL = f"{settings.API_V1_STR}/login"


def test_get_access_token(client: TestClient) -> None:
    login_data = {"username": "alice@company.com", "password": "12345678"}

    r = client.post(f"{BASE_URL}/access-token", data=login_data)

    assert r.status_code == 200

    tokens = r.json()

    assert "access_token" in tokens
    assert tokens["access_token"]


def test_get_access_token_incorrect_password(client: TestClient) -> None:
    login_data = {
        "username": "alice@company.com",
        "password": "not-my-password",
    }

    r = client.post(f"{BASE_URL}/access-token", data=login_data)

    assert r.status_code == 400


def test_get_access_token_user_not_exists(client: TestClient) -> None:
    login_data = {
        "username": "not_a_real_user@fake.com",
        "password": "super-secret-password",
    }

    r = client.post(f"{BASE_URL}/access-token", data=login_data)

    assert r.status_code == 400
