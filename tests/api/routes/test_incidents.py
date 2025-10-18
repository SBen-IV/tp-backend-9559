# ruff: noqa: ARG001
from datetime import datetime, timezone

from faker import Faker
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.commons import Prioridad
from app.models.config_items import ItemConfiguracion
from app.models.incidents import CategoriaIncidente, EstadoIncidente
from app.models.users import Usuario
from app.utils.config import settings

Faker.seed(0)
fake = Faker()

BASE_URL = f"{settings.API_V1_STR}/incidents"


def test_get_all_incidentes(client: TestClient, session: Session) -> None:
    # Given some incidentes
    # Check db_seed.py to see them

    # When the user gets all incidentes
    r = client.get(f"{BASE_URL}")

    # Then it returns a list of incidentes
    assert 200 <= r.status_code < 300

    incidentes = r.json()

    assert len(incidentes) == 6


def test_get_incidentes_by_titulo(client: TestClient, session: Session) -> None:
    # Given some incidentes
    # Check db_seed.py to see them
    titulo = "quemada"

    # When the user gets them by titulo
    r = client.get(f"{BASE_URL}", params={"titulo": titulo})

    # Then it returns a list of incidentes
    assert 200 <= r.status_code < 300

    incidentes = r.json()

    assert len(incidentes) == 1

    for incidente in incidentes:
        assert incidente["titulo"].lower().find(titulo)


def test_get_incidente_by_prioridad(client: TestClient, session: Session) -> None:
    # Given some incidentes
    # Check db_seed.py to see them
    prioridad = "URGENTE"

    # When the user gets them by prioridad
    r = client.get(f"{BASE_URL}", params={"prioridad": prioridad})

    # Then it returns a list of config item
    assert 200 <= r.status_code < 300

    incidentes = r.json()

    assert len(incidentes) == 1

    for incidente in incidentes:
        assert incidente["prioridad"].lower().find(prioridad)


def test_get_incidente_by_categoria(client: TestClient, session: Session) -> None:
    # Given some config items
    # Check db_seed.py to see them
    categoria = "SOLICITUD_DE_SERVICIO"

    # When the user gets them by categoria
    r = client.get(f"{BASE_URL}", params={"categoria": categoria})

    # Then it returns a list of config item
    assert 200 <= r.status_code < 300

    incidentes = r.json()

    assert len(incidentes) == 1

    for incidente in incidentes:
        assert incidente["categoria"] == categoria


def test_get_incidente_by_estado_nuevo(client: TestClient, session: Session) -> None:
    # Given some config items
    # Check db_seed.py to see them
    estado = "NUEVO"

    # When the user gets them by estado
    r = client.get(f"{BASE_URL}", params={"estado": estado})

    # Then it returns a list of config item
    assert 200 <= r.status_code < 300

    incidentes = r.json()

    assert len(incidentes) == 6

    for incidente in incidentes:
        assert incidente["estado"] == estado


def test_get_incidente_by_estado_resuelto(client: TestClient, session: Session) -> None:
    # Given some config items
    # Check db_seed.py to see them
    estado = "RESUELTO"

    # When the user gets them by estado
    r = client.get(f"{BASE_URL}", params={"estado": estado})

    # Then it returns a list of config item
    assert 200 <= r.status_code < 300

    incidentes = r.json()

    assert len(incidentes) == 0


def test_get_incidente_by_id(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # First we need the id of an item
    config_items = client.get(f"{settings.API_V1_STR}/config-items")

    config_item = config_items.json()[0]

    # Given a new incidente
    titulo = "Cache falla"
    descripcion = "Redis falla al traer artículos nuevos"
    prioridad = Prioridad.MEDIA
    categoria = CategoriaIncidente.SOFTWARE
    id_config_items = [config_item["id"]]

    now = datetime.now(timezone.utc)

    data = {
        "titulo": titulo,
        "descripcion": descripcion,
        "prioridad": prioridad,
        "categoria": categoria,
        "id_config_items": id_config_items,
    }

    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)
    incidente_id = r.json()["id"]

    # When the user gets it by id
    r = client.get(f"{BASE_URL}/{incidente_id}")

    # Then it returns the same config item
    assert 200 <= r.status_code < 300

    incidente = r.json()

    assert incidente
    assert incidente["titulo"] == titulo
    assert incidente["descripcion"] == descripcion
    assert incidente["categoria"] == categoria
    assert incidente["prioridad"] == prioridad
    assert incidente["fecha_creacion"] > str(now)
    assert incidente["estado"] == EstadoIncidente.NUEVO
    # Just check that `owner_id` is present, maybe if a get user
    # is implemented we can check if it's equal
    assert incidente["owner_id"]
    assert incidente["responsable_id"] is None
    # And it includes the items linked
    assert len(incidente["config_items"]) == len(id_config_items)
    for c in incidente["config_items"]:
        assert any(c["id"] == config_item for config_item in id_config_items)


def test_create_new_incidente(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a 'incidente'
    titulo = "Base de datos"
    descripcion = "Se cayó la base de datos y los clientes no pueden usar la página"
    categoria = CategoriaIncidente.SOFTWARE
    prioridad = Prioridad.URGENTE

    id_config_item = session.exec(select(ItemConfiguracion)).first()

    # Make sure the config item exists
    assert id_config_item

    id_config_items = [str(id_config_item.id)]

    now = datetime.now(timezone.utc)

    data = {
        "titulo": titulo,
        "descripcion": descripcion,
        "categoria": categoria,
        "prioridad": prioridad,
        "id_config_items": id_config_items,
    }

    # When user tries to create the 'incidente'
    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)

    assert 200 <= r.status_code < 300

    incidente = r.json()

    assert incidente
    assert incidente["titulo"] == titulo
    assert incidente["descripcion"] == descripcion
    assert incidente["categoria"] == categoria
    assert incidente["prioridad"] == prioridad
    assert incidente["fecha_creacion"] > str(now)
    assert incidente["estado"] == EstadoIncidente.NUEVO
    # Just check that `owner_id` is present, maybe if a get user
    # is implemented we can check if it's equal
    assert incidente["owner_id"]
    assert incidente["responsable_id"] is None
    # And it includes the items linked
    assert len(incidente["config_items"]) == len(id_config_items)
    for c in incidente["config_items"]:
        assert any(c["id"] == config_item for config_item in id_config_items)


def test_create_incidente_with_empty_title_returns_error(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a 'incidente' with empty 'titulo'
    titulo = ""
    descripcion = "Se cayó la base de datos y los clientes no pueden usar la página"
    categoria = CategoriaIncidente.SOFTWARE
    prioridad = Prioridad.URGENTE

    data = {
        "titulo": titulo,
        "descripcion": descripcion,
        "categoria": categoria,
        "prioridad": prioridad,
    }

    # When user tries to create a 'incidente'
    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)

    # Then it fails returning an error
    assert 400 <= r.status_code < 500

    details = r.json()["details"][0]
    assert details
    assert details["message"] == "String should have at least 1 character"
    assert details["field"] == "titulo"


def test_create_incidente_with_titulo_too_long_returns_error(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a 'incidente' with too long 'titulo' (256 characters)
    titulo = "This is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is"
    descripcion = "Se cayó la base de datos y los clientes no pueden usar la página"
    categoria = CategoriaIncidente.SOFTWARE
    prioridad = Prioridad.URGENTE

    data = {
        "titulo": titulo,
        "descripcion": descripcion,
        "categoria": categoria,
        "prioridad": prioridad,
    }

    # When user tries to create a 'incidente'
    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)

    # Then it fails returning an error
    assert 400 <= r.status_code < 500

    details = r.json()["details"][0]
    assert details
    assert details["message"] == "String should have at most 255 characters"
    assert details["field"] == "titulo"


def test_create_incidente_with_empty_description_returns_error(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a 'incidente' with empty 'descripcion'
    titulo = "Base de datos"
    descripcion = ""
    categoria = CategoriaIncidente.SOFTWARE
    prioridad = Prioridad.URGENTE

    data = {
        "titulo": titulo,
        "descripcion": descripcion,
        "categoria": categoria,
        "prioridad": prioridad,
    }

    # When user tries to create a 'incidente'
    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)

    # Then it fails returning an error
    assert 400 <= r.status_code < 500

    details = r.json()["details"][0]
    assert details
    assert details["message"] == "String should have at least 1 character"
    assert details["field"] == "descripcion"


def create_random_incident(client: TestClient, token_headers: dict[str, str]) -> dict:
    config_items = client.get(f"{settings.API_V1_STR}/config-items")
    config_item = config_items.json()[0]

    titulo = fake.word()
    descripcion = fake.text(max_nb_chars=100)
    prioridad = Prioridad.BAJA
    categoria = CategoriaIncidente.SOFTWARE
    id_config_items = [config_item["id"]]

    data = {
        "titulo": titulo,
        "descripcion": descripcion,
        "prioridad": prioridad,
        "categoria": categoria,
        "id_config_items": id_config_items,
    }

    r = client.post(BASE_URL, json=data, headers=token_headers)
    return r.json()


def test_update_incidente_titulo(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given an incident
    incidente_created = create_random_incident(client, empleado_token_headers)

    data = {"titulo": "Nuevo titulo"}

    # When the user edits it
    r = client.patch(
        f"{BASE_URL}/{incidente_created['id']}",
        json=data,
        headers=empleado_token_headers,
    )

    # Then the cambio is persisted
    assert 200 <= r.status_code < 300

    incident = r.json()

    assert incident
    assert incident["titulo"] != incidente_created["titulo"]
    assert incident["descripcion"] == incidente_created["descripcion"]
    assert incident["prioridad"] == incidente_created["prioridad"]
    assert incident["fecha_creacion"] == incidente_created["fecha_creacion"]
    assert incident["categoria"] == incidente_created["categoria"]
    assert incident["owner_id"] == incidente_created["owner_id"]
    assert (
        incident["config_items"][0]["id"] == incidente_created["config_items"][0]["id"]
    )


def test_update_incidente_descripcion(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given an incident
    incidente_created = create_random_incident(client, empleado_token_headers)

    data = {"descripcion": "Nueva descripcion"}

    # When the user edits it
    r = client.patch(
        f"{BASE_URL}/{incidente_created['id']}",
        json=data,
        headers=empleado_token_headers,
    )

    # Then the cambio is persisted
    assert 200 <= r.status_code < 300

    incident = r.json()

    assert incident
    assert incident["titulo"] == incidente_created["titulo"]
    assert incident["descripcion"] != incidente_created["descripcion"]
    assert incident["prioridad"] == incidente_created["prioridad"]
    assert incident["fecha_creacion"] == incidente_created["fecha_creacion"]
    assert incident["categoria"] == incidente_created["categoria"]
    assert incident["owner_id"] == incidente_created["owner_id"]
    assert incident["responsable_id"] == incidente_created["responsable_id"]
    assert (
        incident["config_items"][0]["id"] == incidente_created["config_items"][0]["id"]
    )


def test_update_incidente_categoria(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given an incident
    incidente_created = create_random_incident(client, empleado_token_headers)

    data = {"categoria": CategoriaIncidente.SOLICITUD_DE_SERVICIO}

    # When the user edits it
    r = client.patch(
        f"{BASE_URL}/{incidente_created['id']}",
        json=data,
        headers=empleado_token_headers,
    )

    # Then the cambio is persisted
    assert 200 <= r.status_code < 300

    incident = r.json()

    assert incident
    assert incident["titulo"] == incidente_created["titulo"]
    assert incident["descripcion"] == incidente_created["descripcion"]
    assert incident["prioridad"] == incidente_created["prioridad"]
    assert incident["fecha_creacion"] == incidente_created["fecha_creacion"]
    assert incident["categoria"] != incidente_created["categoria"]
    assert incident["owner_id"] == incidente_created["owner_id"]
    assert (
        incident["config_items"][0]["id"] == incidente_created["config_items"][0]["id"]
    )


def test_update_incidente_estado(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given an incident
    incidente_created = create_random_incident(client, empleado_token_headers)

    data = {"estado": EstadoIncidente.RESUELTO}

    # When the user edits it
    r = client.patch(
        f"{BASE_URL}/{incidente_created['id']}",
        json=data,
        headers=empleado_token_headers,
    )

    # Then the cambio is persisted
    assert 200 <= r.status_code < 300

    incident = r.json()

    # Newly created incident has no employee assigned to it
    assert incident["responsable_id"] is None

    assert incident
    assert incident["titulo"] == incidente_created["titulo"]
    assert incident["descripcion"] == incidente_created["descripcion"]
    assert incident["prioridad"] == incidente_created["prioridad"]
    assert incident["fecha_creacion"] == incidente_created["fecha_creacion"]
    assert incident["categoria"] == incidente_created["categoria"]
    assert incident["estado"] != incidente_created["estado"]
    assert incident["owner_id"] == incidente_created["owner_id"]
    assert (
        incident["config_items"][0]["id"] == incidente_created["config_items"][0]["id"]
    )


def test_update_incidente_prioridad(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given an incident
    incidente_created = create_random_incident(client, empleado_token_headers)

    data = {"prioridad": Prioridad.URGENTE}

    # When the user edits it
    r = client.patch(
        f"{BASE_URL}/{incidente_created['id']}",
        json=data,
        headers=empleado_token_headers,
    )

    # Then the cambio is persisted
    assert 200 <= r.status_code < 300

    incident = r.json()

    # Newly created incident has no employee assigned to it
    assert incident["responsable_id"] is None

    assert incident
    assert incident["titulo"] == incidente_created["titulo"]
    assert incident["descripcion"] == incidente_created["descripcion"]
    assert incident["fecha_creacion"] == incidente_created["fecha_creacion"]
    assert incident["categoria"] == incidente_created["categoria"]
    assert incident["estado"] == incidente_created["estado"]
    assert incident["prioridad"] != incidente_created["prioridad"]
    assert incident["owner_id"] == incidente_created["owner_id"]
    assert (
        incident["config_items"][0]["id"] == incidente_created["config_items"][0]["id"]
    )


def test_update_incidente_responsable(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Get any user
    usuario = session.exec(select(Usuario)).first()

    # Given an incident
    incidente_created = create_random_incident(client, empleado_token_headers)

    data = {"responsable_id": str(usuario.id)}

    # When the user edits it
    r = client.patch(
        f"{BASE_URL}/{incidente_created['id']}",
        json=data,
        headers=empleado_token_headers,
    )

    # Then the cambio is persisted
    assert 200 <= r.status_code < 300

    incident = r.json()

    assert incident["responsable_id"] is not None
    assert incident["responsable_id"] != incidente_created["responsable_id"]

    assert incident
    assert incident["titulo"] == incidente_created["titulo"]
    assert incident["descripcion"] == incidente_created["descripcion"]
    assert incident["prioridad"] == incidente_created["prioridad"]
    assert incident["fecha_creacion"] == incidente_created["fecha_creacion"]
    assert incident["categoria"] == incidente_created["categoria"]
    assert incident["estado"] == incidente_created["estado"]
    assert incident["owner_id"] == incidente_created["owner_id"]
    assert (
        incident["config_items"][0]["id"] == incidente_created["config_items"][0]["id"]
    )


def test_delete_incident(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a incidente
    incidente_created = create_random_incident(client, empleado_token_headers)

    # When the user deletes it
    r = client.delete(
        f"{BASE_URL}/{incidente_created['id']}", headers=empleado_token_headers
    )

    # Then the incidente is deleted and returned
    assert 200 <= r.status_code < 300

    incidente = r.json()

    assert incidente
    assert incidente["titulo"] == incidente_created["titulo"]
    assert incidente["descripcion"] == incidente_created["descripcion"]
    assert incidente["prioridad"] == incidente_created["prioridad"]
    assert incidente["fecha_creacion"] == incidente_created["fecha_creacion"]
    assert incidente["categoria"] == incidente_created["categoria"]
    assert incidente["estado"] == incidente_created["estado"]
    assert incidente["owner_id"] == incidente_created["owner_id"]
    assert (
        incidente["config_items"][0]["id"] == incidente_created["config_items"][0]["id"]
    )

    r = client.get(f"{BASE_URL}/{incidente['id']}", headers=empleado_token_headers)

    assert r.status_code == 404


def test_delete_incident_invalid_uuid(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a uuid that's not linked to any incident
    id_incident = "b9809f61-ba46-40ea-b7bc-5a7f67031e6b"

    # When the user uses it to delete a incident
    r = client.delete(f"{BASE_URL}/{id_incident}", headers=empleado_token_headers)

    # Then not found is returned
    assert r.status_code == 404


def test_delete_incident_invalid_if_not_empleado(
    client: TestClient,
    session: Session,
    empleado_token_headers: dict[str, str],
    cliente_token_headers: dict[str, str],
) -> None:
    # Given a incidente
    incidente_created = create_random_incident(client, empleado_token_headers)

    # When the cliente deletes it
    r = client.delete(
        f"{BASE_URL}/{incidente_created['id']}", headers=cliente_token_headers
    )

    # Then the incidente is not deleted and an error is returned
    assert 400 <= r.status_code < 500
    assert r.json()["detail"] == "Sólo empleados pueden eliminar un incidente"

    r = client.get(
        f"{BASE_URL}/{incidente_created['id']}", headers=empleado_token_headers
    )

    assert 200 <= r.status_code < 300

    incidente = r.json()

    assert incidente
    assert incidente["titulo"] == incidente_created["titulo"]
    assert incidente["descripcion"] == incidente_created["descripcion"]
    assert incidente["prioridad"] == incidente_created["prioridad"]
    assert incidente["estado"] == incidente_created["estado"]
    assert incidente["categoria"] == incidente_created["categoria"]
    assert incidente["fecha_creacion"] == incidente_created["fecha_creacion"]
    assert incidente["owner_id"] == incidente_created["owner_id"]
    assert (
        incidente["config_items"][0]["id"] == incidente_created["config_items"][0]["id"]
    )
