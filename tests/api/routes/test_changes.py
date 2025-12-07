# ruff: noqa: ARG001
from datetime import datetime, timezone

from faker import Faker
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.changes import EstadoCambio, ImpactoCambio, Prioridad
from app.models.commons import Operacion, TipoEntidad
from app.models.config_items import ItemConfiguracion
from app.models.incidents import Incidente
from app.models.problems import Problema
from app.models.users import Usuario
from app.utils.config import settings

Faker.seed(0)
fake = Faker()

BASE_URL = f"{settings.API_V1_STR}/changes"


def test_create_new_cambio(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    titulo = "Upgrade CPU of server"
    descripcion = "Change old 2 cores CPU to brand new 32 cores CPU"
    prioridad = Prioridad.URGENTE
    impacto = ImpactoCambio.SIGNIFICATIVO

    now = datetime.now(timezone.utc)

    config_items = session.exec(select(ItemConfiguracion))
    id_config_items = [str(config_item.id) for config_item in config_items]

    incidentes = list(session.exec(select(Incidente)))
    id_incidentes = [str(incidente.id) for incidente in incidentes]

    problemas = list(session.exec(select(Problema)))
    id_problemas = [str(problema.id) for problema in problemas]

    data = {
        "titulo": titulo,
        "descripcion": descripcion,
        "prioridad": prioridad,
        "impacto": impacto,
        "id_config_items": id_config_items,
        "id_incidentes": id_incidentes,
        "id_problemas": id_problemas,
    }

    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)

    assert 200 <= r.status_code < 300

    cambio = r.json()

    assert cambio
    assert cambio["titulo"] == titulo
    assert cambio["descripcion"] == descripcion
    assert cambio["prioridad"] == prioridad
    assert cambio["impacto"] == impacto
    assert cambio["fecha_creacion"] > str(now)
    assert cambio["estado"] == EstadoCambio.RECIBIDO
    # Just check that `owner_id` is present, maybe if a get user
    # is implemented we can check if it's equal
    assert cambio["owner_id"]
    assert cambio["incidentes"]
    assert len(cambio["incidentes"]) == len(incidentes)
    for incidente in cambio["incidentes"]:
        assert incidente["id"] in id_incidentes
    assert cambio["problemas"]
    assert len(cambio["problemas"]) == len(problemas)
    for problema in cambio["problemas"]:
        assert problema["id"] in id_problemas


def test_create_cambio_with_empty_title_returns_error(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a 'cambio' with empty 'titulo'
    titulo = ""
    descripcion = "Change old 2 cores CPU to brand new 32 cores CPU"
    prioridad = Prioridad.URGENTE
    impacto = ImpactoCambio.SIGNIFICATIVO

    data = {
        "titulo": titulo,
        "descripcion": descripcion,
        "prioridad": prioridad,
        "impacto": impacto,
    }

    # When user tries to create a 'cambio'
    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)

    # Then it fails returning an error
    assert 400 <= r.status_code < 500

    details = r.json()["details"][0]
    assert details
    assert details["message"] == "String should have at least 1 character"
    assert details["field"] == "titulo"


def test_create_cambio_with_titulo_too_long_returns_error(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a 'cambio' with too long 'titulo' (256 characters)
    titulo = "This is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is a very long titleThis is"
    descripcion = "Change old 2 cores CPU to brand new 32 cores CPU"
    prioridad = Prioridad.URGENTE
    impacto = ImpactoCambio.SIGNIFICATIVO

    data = {
        "titulo": titulo,
        "descripcion": descripcion,
        "prioridad": prioridad,
        "impacto": impacto,
    }

    # When user tries to create a 'cambio'
    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)

    # Then it fails returning an error
    assert 400 <= r.status_code < 500

    details = r.json()["details"][0]
    assert details
    assert details["message"] == "String should have at most 255 characters"
    assert details["field"] == "titulo"


def test_create_cambio_with_empty_description_returns_error(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a 'cambio' with empty 'descripcion'
    titulo = "Windows update"
    descripcion = ""
    prioridad = Prioridad.URGENTE
    impacto = ImpactoCambio.SIGNIFICATIVO

    data = {
        "titulo": titulo,
        "descripcion": descripcion,
        "prioridad": prioridad,
        "impacto": impacto,
    }

    # When user tries to create a 'cambio'
    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)

    # Then it fails returning an error
    assert 400 <= r.status_code < 500

    details = r.json()["details"][0]
    assert details
    assert details["message"] == "String should have at least 1 character"
    assert details["field"] == "descripcion"


def test_get_change_by_titulo(client: TestClient, session: Session) -> None:
    # Given some changes
    # Check db_seed.py to see them
    titulo = "Nueva television"

    # When the user gets them by titulo
    r = client.get(f"{BASE_URL}", params={"titulo": titulo})

    # Then it returns a list of changes
    assert 200 <= r.status_code < 300

    cambios = r.json()

    assert len(cambios) == 1

    for cambio in cambios:
        assert cambio["titulo"].lower().find(titulo)


def test_get_change_by_descripcion(client: TestClient, session: Session) -> None:
    # Given some changes
    # Check db_seed.py to see them
    descripcion = "Cambiar la television manual"

    # When the user gets them by description
    r = client.get(f"{BASE_URL}", params={"descripcion": descripcion})

    # Then it returns a list of changes
    assert 200 <= r.status_code < 300

    cambios = r.json()

    assert len(cambios) == 1

    for cambio in cambios:
        assert cambio["descripcion"].lower().find(descripcion)


def test_get_change_returns_items(client: TestClient, session: Session) -> None:
    # Given some changes
    # Check db_seed.py to see them

    config_items = client.get(f"{settings.API_V1_STR}/config-items")

    # The change from the seed should have this item linked
    config_item = config_items.json()[0]

    titulo = "Nueva television"

    # When the user gets them
    r = client.get(f"{BASE_URL}", params={"titulo": titulo})

    # Then it returns a list of changes
    assert 200 <= r.status_code < 300

    cambios = r.json()

    assert len(cambios) == 1

    # And it includes the items linked
    for cambio in cambios:
        item_from_change = cambio["config_items"][0]
        assert cambio["descripcion"].lower().find(titulo)
        assert config_item["nombre"] == item_from_change["nombre"]
        assert config_item["owner_id"] == item_from_change["owner_id"]


def test_get_change_by_id(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # First we need the id of an item
    config_items = client.get(f"{settings.API_V1_STR}/config-items")

    # The change from the seed should have this item linked
    config_item = config_items.json()[0]

    # Given a new change
    titulo = "Impresora"
    descripcion = "Reemplazar la impresora"
    prioridad = Prioridad.BAJA
    impacto = ImpactoCambio.MENOR
    id_config_items = [config_item["id"]]

    now = datetime.now(timezone.utc)

    data = {
        "titulo": titulo,
        "descripcion": descripcion,
        "prioridad": prioridad,
        "impacto": impacto,
        "id_config_items": id_config_items,
    }

    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)
    change_id = r.json()["id"]

    # When the user gets it by id
    r = client.get(f"{BASE_URL}/{change_id}")

    # Then it returns the same change
    assert 200 <= r.status_code < 300

    cambio = r.json()

    assert cambio
    assert cambio["titulo"] == titulo
    assert cambio["descripcion"] == descripcion
    assert cambio["prioridad"] == prioridad
    assert cambio["impacto"] == impacto
    assert cambio["fecha_creacion"] > str(now)
    # Just check that `owner_id` is present, maybe if a get user
    # is implemented we can check if it's equal
    assert cambio["owner_id"]
    assert cambio["config_items"][0]["id"] == config_item["id"]


def create_random_cambio(client: TestClient, token_headers: dict[str, str]) -> dict:
    config_items = client.get(f"{settings.API_V1_STR}/config-items")
    config_item = config_items.json()[0]

    incidentes = client.get(f"{settings.API_V1_STR}/incidents")
    incidente = incidentes.json()[0]

    problemas = client.get(f"{settings.API_V1_STR}/problems")
    problema = problemas.json()[0]

    titulo = fake.word()
    descripcion = fake.text(max_nb_chars=100)
    prioridad = Prioridad.BAJA
    impacto = ImpactoCambio.MENOR
    id_config_items = [config_item["id"]]
    id_incidentes = [incidente["id"]]
    id_problemas = [problema["id"]]

    data = {
        "titulo": titulo,
        "descripcion": descripcion,
        "prioridad": prioridad,
        "impacto": impacto,
        "id_config_items": id_config_items,
        "id_incidentes": id_incidentes,
        "id_problemas": id_problemas,
    }

    r = client.post(BASE_URL, json=data, headers=token_headers)
    return r.json()


def test_update_change_titulo(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a cambio
    cambio_created = create_random_cambio(client, empleado_token_headers)

    data = {"titulo": "Nuevo titulo"}

    # When the user edits it
    r = client.patch(
        f"{BASE_URL}/{cambio_created['id']}", json=data, headers=empleado_token_headers
    )

    # Then the cambio is persisted
    assert 200 <= r.status_code < 300

    cambio = r.json()

    assert cambio
    assert cambio["titulo"] != cambio_created["titulo"]
    assert cambio["descripcion"] == cambio_created["descripcion"]
    assert cambio["prioridad"] == cambio_created["prioridad"]
    assert cambio["impacto"] == cambio_created["impacto"]
    assert cambio["fecha_creacion"] == cambio_created["fecha_creacion"]
    assert cambio["owner_id"] == cambio_created["owner_id"]
    assert cambio["config_items"][0]["id"] == cambio_created["config_items"][0]["id"]
    assert cambio["incidentes"][0]["id"] == cambio_created["incidentes"][0]["id"]
    assert cambio["problemas"][0]["id"] == cambio_created["problemas"][0]["id"]


def test_update_change_descripcion(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a cambio
    cambio_created = create_random_cambio(client, empleado_token_headers)

    data = {"descripcion": "Nueva descripción"}

    # When the user edits it
    r = client.patch(
        f"{BASE_URL}/{cambio_created['id']}", json=data, headers=empleado_token_headers
    )

    # Then the cambio is persisted
    assert 200 <= r.status_code < 300

    cambio = r.json()

    assert cambio
    assert cambio["titulo"] == cambio_created["titulo"]
    assert cambio["descripcion"] != cambio_created["descripcion"]
    assert cambio["prioridad"] == cambio_created["prioridad"]
    assert cambio["impacto"] == cambio_created["impacto"]
    assert cambio["fecha_creacion"] == cambio_created["fecha_creacion"]
    assert cambio["owner_id"] == cambio_created["owner_id"]
    assert cambio["config_items"][0]["id"] == cambio_created["config_items"][0]["id"]
    assert cambio["incidentes"][0]["id"] == cambio_created["incidentes"][0]["id"]


def test_update_change_prioridad(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a cambio
    cambio_created = create_random_cambio(client, empleado_token_headers)

    data = {"prioridad": "ALTA"}

    # When the user edits it
    r = client.patch(
        f"{BASE_URL}/{cambio_created['id']}", json=data, headers=empleado_token_headers
    )

    # Then the cambio is persisted
    assert 200 <= r.status_code < 300

    cambio = r.json()

    assert cambio
    assert cambio["titulo"] == cambio_created["titulo"]
    assert cambio["descripcion"] == cambio_created["descripcion"]
    assert cambio["prioridad"] != cambio_created["prioridad"]
    assert cambio["impacto"] == cambio_created["impacto"]
    assert cambio["fecha_creacion"] == cambio_created["fecha_creacion"]
    assert cambio["owner_id"] == cambio_created["owner_id"]
    assert cambio["config_items"][0]["id"] == cambio_created["config_items"][0]["id"]
    assert cambio["incidentes"][0]["id"] == cambio_created["incidentes"][0]["id"]


def test_update_change_estado(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a cambio
    cambio_created = create_random_cambio(client, empleado_token_headers)

    data = {"estado": "CERRADO"}

    # When the user edits it
    r = client.patch(
        f"{BASE_URL}/{cambio_created['id']}", json=data, headers=empleado_token_headers
    )

    # Then the cambio is persisted
    assert 200 <= r.status_code < 300

    cambio = r.json()

    assert cambio
    assert cambio["titulo"] == cambio_created["titulo"]
    assert cambio["descripcion"] == cambio_created["descripcion"]
    assert cambio["prioridad"] == cambio_created["prioridad"]
    assert cambio["impacto"] == cambio_created["impacto"]
    assert cambio["estado"] != cambio_created["estado"]
    assert cambio["fecha_creacion"] == cambio_created["fecha_creacion"]
    assert cambio["owner_id"] == cambio_created["owner_id"]
    assert cambio["config_items"][0]["id"] == cambio_created["config_items"][0]["id"]
    assert cambio["incidentes"][0]["id"] == cambio_created["incidentes"][0]["id"]


def test_update_change_config_items(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a cambio
    cambio_created = create_random_cambio(client, empleado_token_headers)

    r = client.get(f"{settings.API_V1_STR}/config-items")

    # Pick the last one so that it's different from the original attached
    config_item = r.json()[-1]

    id_config_items = [str(config_item["id"])]

    data = {"id_config_items": id_config_items}

    # When the user edits it
    r = client.patch(
        f"{BASE_URL}/{cambio_created['id']}", json=data, headers=empleado_token_headers
    )

    # Then the cambio is persisted
    assert 200 <= r.status_code < 300

    change = r.json()

    assert change
    assert change["titulo"] == cambio_created["titulo"]
    assert change["descripcion"] == cambio_created["descripcion"]
    assert change["prioridad"] == cambio_created["prioridad"]
    assert change["impacto"] == cambio_created["impacto"]
    assert change["fecha_creacion"] == cambio_created["fecha_creacion"]
    assert change["owner_id"] == cambio_created["owner_id"]
    assert change["config_items"][0]["id"] != cambio_created["config_items"][0]["id"]
    assert change["config_items"][0]["id"] == id_config_items[0]
    assert change["incidentes"][0]["id"] == cambio_created["incidentes"][0]["id"]


def test_update_change_problems(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a cambio
    cambio_created = create_random_cambio(client, empleado_token_headers)

    r = client.get(f"{settings.API_V1_STR}/problems")

    # Pick the last one so that it's different from the original attached
    problemas = r.json()[-1]

    id_problemas = [str(problemas["id"])]

    data = {"id_problemas": id_problemas}

    # When the user edits it
    r = client.patch(
        f"{BASE_URL}/{cambio_created['id']}", json=data, headers=empleado_token_headers
    )

    # Then the cambio is persisted
    assert 200 <= r.status_code < 300

    change = r.json()

    assert change
    assert change["titulo"] == cambio_created["titulo"]
    assert change["descripcion"] == cambio_created["descripcion"]
    assert change["prioridad"] == cambio_created["prioridad"]
    assert change["impacto"] == cambio_created["impacto"]
    assert change["fecha_creacion"] == cambio_created["fecha_creacion"]
    assert change["owner_id"] == cambio_created["owner_id"]
    assert change["incidentes"][0]["id"] == cambio_created["incidentes"][0]["id"]
    assert change["config_items"][0]["id"] == cambio_created["config_items"][0]["id"]
    assert change["problemas"][0]["id"] != cambio_created["problemas"][0]["id"]
    assert change["problemas"][0]["id"] == problemas["id"]


def test_update_change_incidents(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a cambio
    cambio_created = create_random_cambio(client, empleado_token_headers)

    r = client.get(f"{settings.API_V1_STR}/incidents")

    # Pick the last one so that it's different from the original attached
    incidentes = r.json()[-1]

    id_incidentes = [str(incidentes["id"])]

    data = {"id_incidentes": id_incidentes}

    # When the user edits it
    r = client.patch(
        f"{BASE_URL}/{cambio_created['id']}", json=data, headers=empleado_token_headers
    )

    # Then the cambio is persisted
    assert 200 <= r.status_code < 300

    change = r.json()

    assert change
    assert change["titulo"] == cambio_created["titulo"]
    assert change["descripcion"] == cambio_created["descripcion"]
    assert change["prioridad"] == cambio_created["prioridad"]
    assert change["impacto"] == cambio_created["impacto"]
    assert change["fecha_creacion"] == cambio_created["fecha_creacion"]
    assert change["owner_id"] == cambio_created["owner_id"]
    assert change["incidentes"][0]["id"] != cambio_created["incidentes"][0]["id"]
    assert change["incidentes"][0]["id"] == incidentes["id"]
    assert change["config_items"][0]["id"] == cambio_created["config_items"][0]["id"]


def test_update_change_impacto(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a cambio
    cambio_created = create_random_cambio(client, empleado_token_headers)

    data = {"impacto": "MAYOR"}

    # When the user edits it
    r = client.patch(
        f"{BASE_URL}/{cambio_created['id']}", json=data, headers=empleado_token_headers
    )

    # Then the cambio is persisted
    assert 200 <= r.status_code < 300

    cambio = r.json()

    assert cambio
    assert cambio["titulo"] == cambio_created["titulo"]
    assert cambio["descripcion"] == cambio_created["descripcion"]
    assert cambio["prioridad"] == cambio_created["prioridad"]
    assert cambio["impacto"] != cambio_created["impacto"]
    assert cambio["impacto"] == data["impacto"]
    assert cambio["estado"] == cambio_created["estado"]
    assert cambio["fecha_creacion"] == cambio_created["fecha_creacion"]
    assert cambio["owner_id"] == cambio_created["owner_id"]
    assert cambio["config_items"][0]["id"] == cambio_created["config_items"][0]["id"]


def test_update_change_responsable_id(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Get any user
    usuario = session.exec(select(Usuario)).first()

    # Given a cambio
    cambio_created = create_random_cambio(client, empleado_token_headers)

    data = {"responsable_id": str(usuario.id)}

    # When the user edits it
    r = client.patch(
        f"{BASE_URL}/{cambio_created['id']}", json=data, headers=empleado_token_headers
    )

    # Then the cambio is persisted
    assert 200 <= r.status_code < 300

    cambio = r.json()

    assert cambio
    assert cambio["titulo"] == cambio_created["titulo"]
    assert cambio["descripcion"] == cambio_created["descripcion"]
    assert cambio["prioridad"] == cambio_created["prioridad"]
    assert cambio["impacto"] == cambio_created["impacto"]
    assert cambio["estado"] == cambio_created["estado"]
    assert cambio["fecha_creacion"] == cambio_created["fecha_creacion"]
    assert cambio["owner_id"] == cambio_created["owner_id"]
    assert cambio["config_items"][0]["id"] == cambio_created["config_items"][0]["id"]
    assert cambio["responsable_id"] is not None
    assert cambio["responsable_id"] != cambio_created["responsable_id"]


def test_delete_change(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a cambio
    cambio_created = create_random_cambio(client, empleado_token_headers)

    # When the user deletes it
    r = client.delete(
        f"{BASE_URL}/{cambio_created['id']}", headers=empleado_token_headers
    )

    # Then the cambio is deleted and returned
    assert 200 <= r.status_code < 300

    cambio = r.json()

    assert cambio
    assert cambio["titulo"] == cambio_created["titulo"]
    assert cambio["descripcion"] == cambio_created["descripcion"]
    assert cambio["prioridad"] == cambio_created["prioridad"]
    assert cambio["impacto"] == cambio_created["impacto"]
    assert cambio["estado"] == cambio_created["estado"]
    assert cambio["fecha_creacion"] == cambio_created["fecha_creacion"]
    assert cambio["owner_id"] == cambio_created["owner_id"]
    assert cambio["config_items"][0]["id"] == cambio_created["config_items"][0]["id"]

    r = client.get(f"{BASE_URL}/{cambio['id']}", headers=empleado_token_headers)

    assert r.status_code == 404


def test_delete_change_invalid_uuid(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a uuid that's not linked to any change
    id_change = "1c6f2b84-25f2-4032-b37b-eabca65a4fb3"

    # When the user uses it to delete a change
    r = client.delete(f"{BASE_URL}/{id_change}", headers=empleado_token_headers)

    # Then not found is returned
    assert r.status_code == 404


def test_delete_change_invalid_if_not_empleado(
    client: TestClient,
    session: Session,
    empleado_token_headers: dict[str, str],
    cliente_token_headers: dict[str, str],
) -> None:
    # Given a cambio
    cambio_created = create_random_cambio(client, empleado_token_headers)

    # When the cliente deletes it
    r = client.delete(
        f"{BASE_URL}/{cambio_created['id']}", headers=cliente_token_headers
    )

    # Then the cambio is not deleted and an error is returned
    assert 400 <= r.status_code < 500
    assert r.json()["detail"] == "Sólo empleados pueden eliminar un cambio"

    r = client.get(f"{BASE_URL}/{cambio_created['id']}", headers=empleado_token_headers)

    assert 200 <= r.status_code < 300

    cambio = r.json()

    assert cambio
    assert cambio["titulo"] == cambio_created["titulo"]
    assert cambio["descripcion"] == cambio_created["descripcion"]
    assert cambio["prioridad"] == cambio_created["prioridad"]
    assert cambio["impacto"] == cambio_created["impacto"]
    assert cambio["estado"] == cambio_created["estado"]
    assert cambio["fecha_creacion"] == cambio_created["fecha_creacion"]
    assert cambio["owner_id"] == cambio_created["owner_id"]
    assert cambio["config_items"][0]["id"] == cambio_created["config_items"][0]["id"]


def test_closing_change_sets_closing_date(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a change
    cambio_created = create_random_cambio(client, empleado_token_headers)

    assert cambio_created["fecha_cierre"] is None

    data = {"estado": EstadoCambio.CERRADO}

    # When the user edits it
    r = client.patch(
        f"{BASE_URL}/{cambio_created['id']}",
        json=data,
        headers=empleado_token_headers,
    )

    # Then the cambio is persisted
    assert 200 <= r.status_code < 300

    cambio = r.json()

    assert cambio
    assert cambio["descripcion"] == cambio_created["descripcion"]
    assert cambio["prioridad"] == cambio_created["prioridad"]
    assert cambio["impacto"] == cambio_created["impacto"]
    assert cambio["fecha_creacion"] == cambio_created["fecha_creacion"]
    assert cambio["owner_id"] == cambio_created["owner_id"]
    assert cambio["config_items"][0]["id"] == cambio_created["config_items"][0]["id"]
    assert cambio["fecha_cierre"] is not None


def test_get_change_history_returns_audits(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a change
    cambio_created = create_random_cambio(client, empleado_token_headers)

    # When the user gets the change history
    r = client.get(
        f"{BASE_URL}/{cambio_created['id']}/history", headers=empleado_token_headers
    )

    assert 200 <= r.status_code < 300

    history = r.json()

    # The history should contain at least the CREAR audit
    assert len(history) >= 1
    assert history[0]["tipo_entidad"] == TipoEntidad.CAMBIO
    assert history[0]["estado_nuevo"]["id"] == cambio_created["id"]


def test_rollback_change_to_creation(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a change
    cambio_created = create_random_cambio(client, empleado_token_headers)

    data = {"titulo": "Nuevo titulo"}

    # And the user edits it
    r = client.patch(
        f"{BASE_URL}/{cambio_created['id']}",
        json=data,
        headers=empleado_token_headers,
    )

    assert 200 <= r.status_code < 300

    cambio_actualizado = r.json()

    assert cambio_actualizado
    assert cambio_actualizado["titulo"] != cambio_created["titulo"]
    assert cambio_actualizado["titulo"] == data["titulo"]

    # And the user gets the change history
    r = client.get(
        f"{BASE_URL}/{cambio_created['id']}/history", headers=empleado_token_headers
    )

    assert 200 <= r.status_code < 300

    auditorias = r.json()
    assert auditorias

    # It should return the CREAR and ACTUALIZAR audits
    assert len(auditorias) == 2

    # CREAR audit should be the last since audits are returned from most to least recent
    auditoria_actualizar_uno = auditorias[1]

    assert auditoria_actualizar_uno["operacion"] == Operacion.CREAR

    # When the user rollbacks the change to when it was created
    r = client.post(
        f"{BASE_URL}/{cambio_created['id']}/rollback",
        params={"id_auditoria": auditoria_actualizar_uno["id"]},
        headers=empleado_token_headers,
    )

    assert 200 <= r.status_code < 300

    cambio_rollback = r.json()

    # It should return to its original state
    assert cambio_rollback
    assert cambio_rollback["id"] == cambio_created["id"]
    assert cambio_rollback["titulo"] == cambio_created["titulo"]
    assert cambio_rollback["titulo"] != cambio_actualizado["titulo"]


def test_rollback_change_to_patched_version(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Given a change
    cambio_created = create_random_cambio(client, empleado_token_headers)

    update_uno = {"titulo": "Primer nuevo titulo"}
    update_dos = {"titulo": "Segundo nuevo titulo"}

    # And the user edits it
    r = client.patch(
        f"{BASE_URL}/{cambio_created['id']}",
        json=update_uno,
        headers=empleado_token_headers,
    )

    assert 200 <= r.status_code < 300

    cambio_actualizado = r.json()

    assert cambio_actualizado
    assert cambio_actualizado["titulo"] != cambio_created["titulo"]
    assert cambio_actualizado["titulo"] == update_uno["titulo"]

    # If the user edits it again
    r = client.patch(
        f"{BASE_URL}/{cambio_created['id']}",
        json=update_dos,
        headers=empleado_token_headers,
    )

    assert 200 <= r.status_code < 300

    cambio_actualizado = r.json()

    assert cambio_actualizado
    assert cambio_actualizado["titulo"] != cambio_created["titulo"]
    assert cambio_actualizado["titulo"] != update_uno["titulo"]
    assert cambio_actualizado["titulo"] == update_dos["titulo"]

    # When the user gets the change history
    r = client.get(
        f"{BASE_URL}/{cambio_created['id']}/history", headers=empleado_token_headers
    )

    assert 200 <= r.status_code < 300

    auditorias = r.json()
    assert auditorias

    # It should return the CREAR and 2 ACTUALIZAR audits
    assert len(auditorias) == 3

    # We pick the first update done
    auditoria_actualizar_uno = auditorias[1]

    assert auditoria_actualizar_uno["operacion"] == Operacion.ACTUALIZAR

    # When the user rollbacks the change to when it was first updated
    r = client.post(
        f"{BASE_URL}/{cambio_created['id']}/rollback",
        params={"id_auditoria": auditoria_actualizar_uno["id"]},
        headers=empleado_token_headers,
    )

    assert 200 <= r.status_code < 300

    cambio_rollback = r.json()

    # It should return to the state of its first update
    assert cambio_rollback
    assert cambio_rollback["id"] == cambio_created["id"]
    assert cambio_rollback["titulo"] != cambio_created["titulo"]
    assert cambio_rollback["titulo"] == update_uno["titulo"]
    assert cambio_rollback["titulo"] != update_dos["titulo"]


def test_rollback_change_responsable_id(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    # Get any user
    usuario = session.exec(select(Usuario)).first()

    # Given a change
    cambio_created = create_random_cambio(client, empleado_token_headers)

    update = {"responsable_id": str(usuario.id)}

    r = client.patch(
        f"{BASE_URL}/{cambio_created['id']}",
        json=update,
        headers=empleado_token_headers,
    )

    assert 200 <= r.status_code < 300

    # When the user gets the change history
    r = client.get(
        f"{BASE_URL}/{cambio_created['id']}/history", headers=empleado_token_headers
    )

    assert 200 <= r.status_code < 300

    auditorias = r.json()
    assert auditorias

    # It should return the CREAR and ACTUALIZAR audits
    assert len(auditorias) == 2

    # We pick the first update done
    auditoria_crear = auditorias[1]

    assert auditoria_crear["operacion"] == Operacion.CREAR

    # When the user rollbacks the change to when it was first updated
    r = client.post(
        f"{BASE_URL}/{cambio_created['id']}/rollback",
        params={"id_auditoria": auditoria_crear["id"]},
        headers=empleado_token_headers,
    )

    assert 200 <= r.status_code < 300

    cambio_rollback = r.json()

    # It should return to the state of its first update
    assert cambio_rollback
    assert cambio_rollback["id"] == cambio_created["id"]
    assert cambio_rollback["responsable_id"] is None
    assert cambio_rollback["responsable_id"] == cambio_created["responsable_id"]
