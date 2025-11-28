import random
from collections.abc import Callable

import requests
from faker import Faker

from app.models.changes import EstadoCambio, ImpactoCambio
from app.models.commons import Prioridad
from app.models.config_items import EstadoItem
from app.models.incidents import EstadoIncidente
from app.models.problems import EstadoProblema

fake = Faker()

BASE_URL = "http://localhost:8000/api/v1"
USERS_URL = f"{BASE_URL}/users"
LOGIN_URL = f"{BASE_URL}/login/access-token"
CONFIG_ITEMS_URL = f"{BASE_URL}/config-items"
CHANGES_URL = f"{BASE_URL}/changes"
PROBLEMS_URL = f"{BASE_URL}/problems"
INCIDENTS_URL = f"{BASE_URL}/incidents"

MAX_UPDATES = 100
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


def random_apply(data: dict, key: str, randomizer: Callable, chances: float = 0.5):
    if random.random() < chances:
        data[key] = randomizer()


def random_descripcion(data: dict):
    # 0.3 chances because it should be unlikely to change a description
    random_apply(
        data=data,
        key="descripcion",
        randomizer=lambda: fake.text(max_nb_chars=MAX_DESCRIPTION),
        chances=0.3,
    )


def random_prioridad(data: dict):
    random_apply(
        data=data, key="prioridad", randomizer=lambda: fake.enum(Prioridad).value
    )


def random_responsable(data: dict, empleados_id: dict):
    # 0.7 chances to make it likely to set a responsable_id
    random_apply(
        data=data,
        key="responsable_id",
        randomizer=lambda: random.choice(empleados_id),
        chances=0.7,
    )


def generate_random_id_choices(data_id: dict, min_rand: int = 1, max_rand: int = 4):
    k = random.randint(min_rand, max_rand)
    return random.choices(data_id, k=k)


def random_config_items(data: dict, config_items_id: dict):
    random_apply(
        data=data,
        key="id_config_items",
        randomizer=lambda: generate_random_id_choices(config_items_id),
    )


def random_problemas(data: dict, problems_id: dict):
    random_apply(
        data=data,
        key="id_problemas",
        randomizer=lambda: generate_random_id_choices(problems_id, max_rand=2),
    )


def random_incidentes(data: dict, incidents_id: dict):
    random_apply(
        data=data,
        key="id_incidentes",
        randomizer=lambda: generate_random_id_choices(incidents_id, max_rand=2),
    )


def chaos_config_items(config_items, headers):
    for _ in range(MAX_UPDATES):
        config_item = random.choice(config_items)
        config_item_id = config_item["id"]
        data = {}

        random_descripcion(data)
        random_apply(data, "estado", lambda: fake.enum(EstadoItem).value)

        # Skip if there's no update
        if len(data.keys()) == 0:
            continue

        r = requests.patch(
            f"{CONFIG_ITEMS_URL}/{config_item_id}", json=data, headers=headers
        )

        if r.status_code >= 400:
            print("[config items] ", r.json())


def chaos_incidents(incidents, config_items_id, empleados_id, headers):
    for _ in range(MAX_UPDATES):
        incident = random.choice(incidents)
        incident_id = incident["id"]
        data = {}

        random_descripcion(data)
        random_prioridad(data)
        random_apply(data, "estado", lambda: fake.enum(EstadoIncidente).value)
        random_responsable(data, empleados_id)
        random_config_items(data, config_items_id)

        # Skip if there's no update
        if len(data.keys()) == 0:
            continue

        r = requests.patch(f"{INCIDENTS_URL}/{incident_id}", json=data, headers=headers)

        if r.status_code >= 400:
            print("[incidents]: ", r.json())


def chaos_changes(
    changes, incidents_id, problems_id, config_items_id, empleados_id, headers
):
    for _ in range(MAX_UPDATES):
        change = random.choice(changes)
        change_id = change["id"]
        data = {}

        random_descripcion(data)
        random_prioridad(data)
        random_apply(data, "impacto", lambda: fake.enum(ImpactoCambio).value)
        random_apply(data, "estado", lambda: fake.enum(EstadoCambio).value)
        random_config_items(data, config_items_id)
        random_problemas(data, problems_id)
        random_incidentes(data, incidents_id)
        random_responsable(data, empleados_id)

        # Skip if there's no update
        if len(data.keys()) == 0:
            continue

        r = requests.patch(f"{CHANGES_URL}/{change_id}", json=data, headers=headers)

        if r.status_code >= 400:
            print("[changes] ", r.json())


def chaos_problems(problems, incidents_id, config_items_id, empleados_id, headers):
    for _ in range(MAX_UPDATES):
        problem = random.choice(problems)
        problem_id = problem["id"]
        data = {}

        random_descripcion(data)
        random_prioridad(data)
        random_apply(data, "estado", lambda: fake.enum(EstadoProblema).value)
        random_responsable(data, empleados_id)
        # random_apply(data, "id_incidentes", lambda: random.choice(incidents_id))
        random_incidentes(data, incidents_id)
        random_config_items(data, config_items_id)

        # Skip if there's no update
        if len(data.keys()) == 0:
            continue

        r = requests.patch(f"{PROBLEMS_URL}/{problem_id}", json=data, headers=headers)

        if r.status_code >= 400:
            print("[problems] ", r.json())


def main():
    headers = get_headers()
    empleados = get_empleados(headers=headers)
    config_items = get_config_items()
    incidents = get_incidents()
    changes = get_changes()
    problems = get_problems()

    chaos_config_items(config_items=config_items, headers=headers)

    empleados_id = [empleado["id"] for empleado in empleados]
    config_items_id = [config_item["id"] for config_item in config_items]

    chaos_incidents(
        incidents=incidents,
        config_items_id=config_items_id,
        empleados_id=empleados_id,
        headers=headers,
    )

    incidents_id = [incident["id"] for incident in incidents]

    chaos_problems(
        problems=problems,
        incidents_id=incidents_id,
        config_items_id=config_items_id,
        empleados_id=empleados_id,
        headers=headers,
    )

    problems_id = [problem["id"] for problem in problems]

    chaos_changes(
        changes=changes,
        incidents_id=incidents_id,
        problems_id=problems_id,
        config_items_id=config_items_id,
        empleados_id=empleados_id,
        headers=headers,
    )


main()
