import random

from faker import Faker

from app.models.changes import CambioCrear, ImpactoCambio
from app.models.commons import Prioridad
from app.models.config_items import CategoriaItem, ItemConfiguracionCrear
from app.models.incidents import CategoriaIncidente, IncidenteCrear
from app.models.problems import ProblemaCrear

PRIORIDADES = [Prioridad.BAJA, Prioridad.MEDIA, Prioridad.ALTA, Prioridad.URGENTE]
MAX_DESCRIPTION = 100
GENERATE_RANDOM = 50

Faker.seed(0)
fake = Faker()


def generate_random_config_item() -> list[ItemConfiguracionCrear]:
    config_items: list[ItemConfiguracionCrear] = []

    for _ in range(GENERATE_RANDOM):
        config_items.append(
            ItemConfiguracionCrear(
                nombre=fake.file_name(extension="").capitalize(),
                descripcion=fake.text(max_nb_chars=MAX_DESCRIPTION),
                version=fake.numerify(text="#.%.%"),
                categoria=random.choice(
                    [
                        CategoriaItem.DOCUMENTACION,
                        CategoriaItem.HARDWARE,
                        CategoriaItem.SOFTWARE,
                    ]
                ),
            )
        )

    return config_items


def generate_random_incidentes() -> list[IncidenteCrear]:
    incidentes: list[IncidenteCrear] = []

    for _ in range(GENERATE_RANDOM):
        incidentes.append(
            IncidenteCrear(
                titulo=fake.catch_phrase(),
                descripcion=fake.text(max_nb_chars=MAX_DESCRIPTION),
                prioridad=random.choice(PRIORIDADES),
                categoria=random.choice(
                    [
                        CategoriaIncidente.HARDWARE,
                        CategoriaIncidente.SOFTWARE,
                        CategoriaIncidente.SEGURIDAD,
                        CategoriaIncidente.SOLICITUD_DE_SERVICIO,
                    ]
                ),
                id_config_items=[],
            ),
        )

    return incidentes


def generate_random_problemas() -> list[ProblemaCrear]:
    problemas: list[ProblemaCrear] = []

    for _ in range(GENERATE_RANDOM):
        problemas.append(
            ProblemaCrear(
                titulo=fake.catch_phrase(),
                descripcion=fake.text(max_nb_chars=MAX_DESCRIPTION),
                prioridad=random.choice(PRIORIDADES),
                id_config_items=[],
                id_incidentes=[],
            ),
        )

    return problemas


def generate_random_cambios() -> list[CambioCrear]:
    cambios: list[CambioCrear] = []

    for _ in range(GENERATE_RANDOM):
        cambios.append(
            CambioCrear(
                titulo=fake.catch_phrase(),
                descripcion=fake.text(max_nb_chars=MAX_DESCRIPTION),
                prioridad=random.choice(PRIORIDADES),
                impacto=fake.enum(ImpactoCambio),
                id_config_items=[],
            )
        )

    return cambios
