# ruff: noqa: ARG001
from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.changes import EstadoCambio, Prioridad
from app.utils.config import settings

BASE_URL = f"{settings.API_V1_STR}/changes"


def test_create_new_cambio(
    client: TestClient, session: Session, empleado_token_headers: dict[str, str]
) -> None:
    titulo = "Upgrade CPU of server"
    descripcion = "Change old 2 cores CPU to brand new 32 cores CPU"
    prioridad = Prioridad.URGENTE

    now = datetime.now(timezone.utc)

    data = {"titulo": titulo, "descripcion": descripcion, "prioridad": prioridad}

    r = client.post(BASE_URL, json=data, headers=empleado_token_headers)

    assert 200 <= r.status_code < 300

    cambio = r.json()

    assert cambio
    assert cambio["titulo"] == titulo
    assert cambio["descripcion"] == descripcion
    assert cambio["prioridad"] == prioridad
    assert cambio["fecha_creacion"] > str(now)
    assert cambio["estado"] == EstadoCambio.RECIBIDO
    # Just check that `owner_id` is present, maybe if a get user
    # is implemented we can check if it's equal
    assert cambio["owner_id"]
