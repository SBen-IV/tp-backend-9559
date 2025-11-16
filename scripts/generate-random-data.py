import requests

BASE_URL = "http://localhost:8000/api/v1"
USERS_URL = f"{BASE_URL}/users"
LOGIN_URL = f"{BASE_URL}/login/access-token"


def get_headers():
    r = requests.post(
        LOGIN_URL, data={"username": "john@company.com", "password": "12345678"}
    )

    token = r.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


headers = get_headers()

r = requests.get(USERS_URL, headers=headers)

empleados = []

for user in r.json():
    if user["rol"] == "EMPLEADO":
        empleados.append(user)

print(empleados)
