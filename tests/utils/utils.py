from fastapi.testclient import TestClient

from app.utils.config import settings


def get_user_token_header(
    client: TestClient, login_data: dict[str, str]
) -> dict[str, str]:
    response = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)

    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def get_empleado_token_headers(client: TestClient) -> dict[str, str]:
    login_data = {"username": "alice@company.com", "password": "12345678"}

    return get_user_token_header(client, login_data)


def get_cliente_token_headers(client: TestClient) -> dict[str, str]:
    login_data = {"username": "carl@company.com", "password": "12345678"}

    return get_user_token_header(client, login_data)
