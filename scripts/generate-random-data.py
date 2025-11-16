import random

import requests
from faker import Faker

from app.models.commons import Prioridad
from app.models.config_items import EstadoItem
from app.models.incidents import EstadoIncidente

fake = Faker()

BASE_URL = "http://localhost:8000/api/v1"
USERS_URL = f"{BASE_URL}/users"
LOGIN_URL = f"{BASE_URL}/login/access-token"
CONFIG_ITEMS_URL = f"{BASE_URL}/config-items"
CHANGES_URL = f"{BASE_URL}/changes"
PROBLEMS_URL = f"{BASE_URL}/problems"
INCIDENTS_URL = f"{BASE_URL}/incidents"

RANDOM_CHANGES = 100
MAX_DESCRIPTION = 100


def get_headers():
    r = requests.post(
        LOGIN_URL, data={"username": "john@company.com", "password": "12345678"}
    )

    token = r.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def get_empleados(headers: dict):
    r = requests.get(USERS_URL, headers=headers)

    empleados = []

    for user in r.json():
        if user["rol"] == "EMPLEADO":
            empleados.append(user)

    return empleados


def get_config_items():
    r = requests.get(CONFIG_ITEMS_URL)

    return r.json()


def get_changes():
    r = requests.get(CHANGES_URL)

    return r.json()


def get_problems():
    r = requests.get(PROBLEMS_URL)

    return r.json()


def get_incidents():
    r = requests.get(INCIDENTS_URL)

    return r.json()


### CHAOS
def chaos_config_items(config_items, headers):
    for _ in range(RANDOM_CHANGES):
        config_item = random.choice(config_items)
        config_item_id = config_item["id"]
        data = {}

        if random.random() < 0.3:
            data["descripcion"] = fake.text(max_nb_chars=MAX_DESCRIPTION)

        if random.random() < 0.5:
            data["estado"] = fake.enum(EstadoItem).value

        # Skip if there's no update
        if len(data.keys()) == 0:
            continue

        requests.patch(
            f"{CONFIG_ITEMS_URL}/{config_item_id}", json=data, headers=headers
        )


def chaos_incidents(incidents, config_items_id, empleados_id, headers):
    for _ in range(RANDOM_CHANGES):
        incident = random.choice(incidents)
        incident_id = incident["id"]
        data = {}

        if random.random() < 0.3:
            data["descripcion"] = fake.text(max_nb_chars=MAX_DESCRIPTION)

        if random.random() < 0.5:
            data["prioridad"] = fake.enum(Prioridad).value

        if random.random() < 0.5:
            data["estado"] = fake.enum(EstadoIncidente).value

        if random.random() < 0.7:
            data["responsable_id"] = random.choice(empleados_id)

        if random.random() < 0.4:
            k = random.randint(1, 4)
            data["id_config_items"] = random.choices(config_items_id, k=k)

        requests.patch(f"{INCIDENTS_URL}/{incident_id}", json=data, headers=headers)


def main():
    headers = get_headers()
    empleados = get_empleados(headers=headers)
    config_items = get_config_items()
    incidents = get_incidents()
    changes = get_changes()
    problems = get_problems()

    chaos_config_items(config_items, headers)

    empleados_id = [empleado["id"] for empleado in empleados]
    config_items_id = [config_item["id"] for config_item in config_items]

    chaos_incidents(incidents, config_items_id, empleados_id, headers)


main()
