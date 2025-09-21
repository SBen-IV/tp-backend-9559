import os

from app.models.users import UsuarioRegistrar

seed_usuarios = []


if os.getenv("TESTS", None):
    seed_usuarios = [
        UsuarioRegistrar(
            nombre="Alice",
            apellido="Smith",
            email="alice@company.com",
            rol="EMPLEADO",
            contraseña="12345678",
        )
    ]
