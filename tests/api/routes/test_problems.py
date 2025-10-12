# ruff: noqa: ARG001
from datetime import datetime, timezone

from faker import Faker
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.commons import Prioridad
from app.models.config_items import ItemConfiguracion
from app.models.problems import EstadoProblema
from app.models.users import Usuario
from app.utils.config import settings

BASE_URL = f"{settings.API_V1_STR}/problems"

Faker.seed(0)
fake = Faker()


def test_get_all_problemas(client: TestClient, session: Session) -> None:
    # Given some problemas
    # Check db_seed.py to see them

    # When the user gets all problemas
    r = client.get(f"{BASE_URL}")

    # Then it returns a list of problemas
    assert 200 <= r.status_code < 300

    problemas = r.json()

    assert len(problemas) == 3


def test_get_problemas_by_titulo(client: TestClient, session: Session) -> None:
    # Given some problemas
    # Check db_seed.py to see them
    titulo = "webcam"

    # When the user gets them by titulo
    r = client.get(f"{BASE_URL}", params={"titulo": titulo})

    # Then it returns a list of problemas
    assert 200 <= r.status_code < 300

    problemas = r.json()

    assert len(problemas) == 1

    for problema in problemas:
        assert problema["titulo"].lower().find(titulo)


def test_get_problema_by_prioridad(client: TestClient, session: Session) -> None:
    # Given some problemas
    # Check db_seed.py to see them
    prioridad = "ALTA"

    # When the user gets them by prioridad
    r = client.get(f"{BASE_URL}", params={"prioridad": prioridad})

    # Then it returns a list of config item
    assert 200 <= r.status_code < 300

    problemas = r.json()

    assert len(problemas) == 1

    for problema in problemas:
        assert problema["prioridad"].lower().find(prioridad)


def test_get_problema_by_estado_en_analisis(
    client: TestClient, session: Session
) -> None:
    # Given some problemas
    # Check db_seed.py to see them
    estado = "EN_ANALISIS"

    # When the user gets them by estado
    r = client.get(f"{BASE_URL}", params={"estado": estado})

    # Then it returns a list of problemas
    assert 200 <= r.status_code < 300

    problemas = r.json()

    assert len(problemas) == 3

    for problema in problemas:
        assert problema["estado"] == estado


def test_get_problema_by_estado_cerrado(client: TestClient, session: Session) -> None:
    # Given some problemas
    # Check db_seed.py to see them
    estado = "CERRADO"

    # When the user gets them by estado
    r = client.get(f"{BASE_URL}", params={"estado": estado})

    # Then it returns a list of problemas
    assert 200 <= r.status_code < 300

    problemas = r.json()

    assert len(problemas) == 0


def test_get_problema_by_id(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # First we need the id of an item
    config_items = client.get(f"{settings.API_V1_STR}/config-items")

    config_item = config_items.json()[0]

    # Given a new problema
    titulo = "Cache falla"
    descripcion = "Redis falla al traer artículos nuevos"
    prioridad = Prioridad.MEDIA
    id_config_items = [config_item["id"]]

    now = datetime.now(timezone.utc)

    data = {
        "titulo": titulo,
        "descripcion": descripcion,
        "prioridad": prioridad,
        "id_config_items": id_config_items,
    }

    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)
    problema_id = r.json()["id"]

    # When the user gets it by id
    r = client.get(f"{BASE_URL}/{problema_id}")

    # Then it returns the same config item
    assert 200 <= r.status_code < 300

    problema = r.json()

    assert problema
    assert problema["titulo"] == titulo
    assert problema["descripcion"] == descripcion
    assert problema["prioridad"] == prioridad
    assert problema["fecha_creacion"] > str(now)
    assert problema["estado"] == EstadoProblema.EN_ANALISIS
    # Just check that `owner_id` is present, maybe if a get user
    # is implemented we can check if it's equal
    assert problema["owner_id"]
    assert problema["responsable_id"] is None
    assert len(problema["config_items"]) == len(id_config_items)
    for c in problema["config_items"]:
        assert any(c["id"] == config_item for config_item in id_config_items)


def test_create_new_problema(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a 'problema'
    titulo = "BSOD"
    descripcion = (
        "Cuando quiero conectarme a la VPN en Windows me salta la pantalla azul"
    )
    prioridad = Prioridad.MEDIA

    id_config_item = session.exec(
        select(ItemConfiguracion).where(ItemConfiguracion.nombre == "Windows")
    ).first()

    # Make sure the config item exists
    assert id_config_item

    id_config_items = [str(id_config_item.id)]

    now = datetime.now(timezone.utc)

    data = {
        "titulo": titulo,
        "descripcion": descripcion,
        "prioridad": prioridad,
        "id_config_items": id_config_items,
    }

    # When user tries to create the 'problema'
    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)

    assert 200 <= r.status_code < 300

    problema = r.json()

    assert problema
    assert problema["titulo"] == titulo
    assert problema["descripcion"] == descripcion
    assert problema["prioridad"] == prioridad
    assert problema["fecha_creacion"] > str(now)
    assert problema["estado"] == EstadoProblema.EN_ANALISIS
    # Just check that `owner_id` is present, maybe if a get user
    # is implemented we can check if it's equal
    assert problema["owner_id"]
    assert problema["responsable_id"] is None
    # And it includes the items linked
    assert len(problema["config_items"]) == len(id_config_items)
    for c in problema["config_items"]:
        assert any(c["id"] == config_item for config_item in id_config_items)


def test_create_problema_with_empty_title_returns_error(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a 'problema' with empty 'titulo'
    titulo = ""
    descripcion = (
        "Cuando quiero conectarme a la VPN en Windows me salta la pantalla azul"
    )
    prioridad = Prioridad.URGENTE

    data = {"titulo": titulo, "descripcion": descripcion, "prioridad": prioridad}

    # When user tries to create a 'problema'
    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)

    # Then it fails returning an error
    assert 400 <= r.status_code < 500

    details = r.json()["details"][0]
    assert details
    assert details["message"] == "String should have at least 1 character"
    assert details["field"] == "titulo"


def test_create_problema_with_titulo_too_long_returns_error(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a 'problema' with too long 'titulo' (256 characters)
    titulo = "This is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is"
    descripcion = (
        "Cuando quiero conectarme a la VPN en Windows me salta la pantalla azul"
    )
    prioridad = Prioridad.URGENTE

    data = {"titulo": titulo, "descripcion": descripcion, "prioridad": prioridad}

    # When user tries to create a 'problema'
    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)

    # Then it fails returning an error
    assert 400 <= r.status_code < 500

    details = r.json()["details"][0]
    assert details
    assert details["message"] == "String should have at most 255 characters"
    assert details["field"] == "titulo"


def test_create_problema_with_empty_description_returns_error(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a 'problema' with empty 'descripcion'
    titulo = "BSOD"
    descripcion = ""
    prioridad = Prioridad.URGENTE

    data = {"titulo": titulo, "descripcion": descripcion, "prioridad": prioridad}

    # When user tries to create a 'problema'
    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)

    # Then it fails returning an error
    assert 400 <= r.status_code < 500

    details = r.json()["details"][0]
    assert details
    assert details["message"] == "String should have at least 1 character"
    assert details["field"] == "descripcion"


def create_random_problem(client: TestClient, token_headers: dict[str, str]) -> dict:
    config_items = client.get(f"{settings.API_V1_STR}/config-items")
    config_item = config_items.json()[0]

    titulo = fake.word()
    descripcion = fake.text(max_nb_chars=100)
    prioridad = Prioridad.BAJA
    id_config_items = [config_item["id"]]

    data = {
        "titulo": titulo,
        "descripcion": descripcion,
        "prioridad": prioridad,
        "id_config_items": id_config_items,
    }

    r = client.post(BASE_URL, json=data, headers=token_headers)
    return r.json()


def test_update_problema_titulo(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given an problem
    problema_created = create_random_problem(client, empleado_token_headers)

    data = {"titulo": "Nuevo titulo"}

    # When the user edits it
    r = client.patch(
        f"{BASE_URL}/{problema_created['id']}",
        json=data,
        headers=empleado_token_headers,
    )

    # Then the cambio is persisted
    assert 200 <= r.status_code < 300

    problem = r.json()

    assert problem
    assert problem["titulo"] != problema_created["titulo"]
    assert problem["descripcion"] == problema_created["descripcion"]
    assert problem["prioridad"] == problema_created["prioridad"]
    assert problem["fecha_creacion"] == problema_created["fecha_creacion"]
    assert problem["owner_id"] == problema_created["owner_id"]
    assert problem["config_items"][0]["id"] == problema_created["config_items"][0]["id"]


def test_update_problema_descripcion(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given an problem
    problem_created = create_random_problem(client, empleado_token_headers)

    data = {"descripcion": "Nueva descripcion"}

    # When the user edits it
    r = client.patch(
        f"{BASE_URL}/{problem_created['id']}", json=data, headers=empleado_token_headers
    )

    # Then the cambio is persisted
    assert 200 <= r.status_code < 300

    problem = r.json()

    assert problem
    assert problem["titulo"] == problem_created["titulo"]
    assert problem["descripcion"] != problem_created["descripcion"]
    assert problem["prioridad"] == problem_created["prioridad"]
    assert problem["fecha_creacion"] == problem_created["fecha_creacion"]
    assert problem["owner_id"] == problem_created["owner_id"]
    assert problem["responsable_id"] == problem_created["responsable_id"]
    assert problem["config_items"][0]["id"] == problem_created["config_items"][0]["id"]


def test_update_problema_estado(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given an problem
    problem_created = create_random_problem(client, empleado_token_headers)

    data = {"estado": EstadoProblema.RESUELTO}

    # When the user edits it
    r = client.patch(
        f"{BASE_URL}/{problem_created['id']}", json=data, headers=empleado_token_headers
    )

    # Then the cambio is persisted
    assert 200 <= r.status_code < 300

    problem = r.json()

    # Newly created problem has no employee assigned to it
    assert problem["responsable_id"] is None

    assert problem
    assert problem["titulo"] == problem_created["titulo"]
    assert problem["descripcion"] == problem_created["descripcion"]
    assert problem["prioridad"] == problem_created["prioridad"]
    assert problem["fecha_creacion"] == problem_created["fecha_creacion"]
    assert problem["estado"] != problem_created["estado"]
    assert problem["owner_id"] == problem_created["owner_id"]
    assert problem["config_items"][0]["id"] == problem_created["config_items"][0]["id"]


def test_update_problema_responsable(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Get any user
    usuario = session.exec(select(Usuario)).first()

    # Given an problem
    problem_created = create_random_problem(client, empleado_token_headers)

    data = {"responsable_id": str(usuario.id)}

    # When the user edits it
    r = client.patch(
        f"{BASE_URL}/{problem_created['id']}", json=data, headers=empleado_token_headers
    )

    # Then the cambio is persisted
    assert 200 <= r.status_code < 300

    problem = r.json()

    assert problem["responsable_id"] is not None
    assert problem["responsable_id"] != problem_created["responsable_id"]

    assert problem
    assert problem["titulo"] == problem_created["titulo"]
    assert problem["descripcion"] == problem_created["descripcion"]
    assert problem["prioridad"] == problem_created["prioridad"]
    assert problem["fecha_creacion"] == problem_created["fecha_creacion"]
    assert problem["estado"] == problem_created["estado"]
    assert problem["owner_id"] == problem_created["owner_id"]
    assert problem["config_items"][0]["id"] == problem_created["config_items"][0]["id"]


def test_update_problema_prioridad(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given an problem
    problem_created = create_random_problem(client, empleado_token_headers)

    data = {"prioridad": Prioridad.URGENTE}

    # When the user edits it
    r = client.patch(
        f"{BASE_URL}/{problem_created['id']}", json=data, headers=empleado_token_headers
    )

    # Then the cambio is persisted
    assert 200 <= r.status_code < 300

    problem = r.json()

    assert problem
    assert problem["titulo"] == problem_created["titulo"]
    assert problem["descripcion"] == problem_created["descripcion"]
    assert problem["prioridad"] != problem_created["prioridad"]
    assert problem["fecha_creacion"] == problem_created["fecha_creacion"]
    assert problem["owner_id"] == problem_created["owner_id"]
    assert problem["config_items"][0]["id"] == problem_created["config_items"][0]["id"]
