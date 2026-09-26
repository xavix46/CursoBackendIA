import pytest
from fastapi.testclient import TestClient


def test_registrar_usuario_exitoso(client: TestClient):
    """Verifica el registro exitoso de un usuario (201) y que la contraseña no se exponga."""
    payload = {
        "email": "usuario1@test.com",
        "password": "Password123!"
    }
    response = client.post("/usuarios/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "usuario1@test.com"
    assert "id" in data
    assert "created_at" in data
    assert "password" not in data
    assert "password_hash" not in data


def test_registrar_usuario_email_duplicado(client: TestClient):
    """Verifica que intentar registrar un email ya existente devuelva 400."""
    payload = {
        "email": "duplicado@test.com",
        "password": "Password123!"
    }
    # Primer registro exitoso
    res1 = client.post("/usuarios/", json=payload)
    assert res1.status_code == 201

    # Segundo registro debe fallar con 400
    res2 = client.post("/usuarios/", json=payload)
    assert res2.status_code == 400
    assert "email" in res2.json()["detail"].lower() or "registrado" in res2.json()["detail"].lower() or "duplicado" in res2.json()["detail"].lower()


def test_login_exitoso(client: TestClient):
    """Verifica inicio de sesión exitoso devolviendo token JWT (200)."""
    # Crear usuario
    client.post("/usuarios/", json={"email": "login@test.com", "password": "Password123!"})

    # Login usando form URL-encoded (OAuth2PasswordRequestForm: username y password)
    login_data = {
        "username": "login@test.com",
        "password": "Password123!"
    }
    response = client.post("/usuarios/token", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_credenciales_invalidas(client: TestClient):
    """Verifica que login con contraseña incorrecta devuelva 401."""
    client.post("/usuarios/", json={"email": "login_fail@test.com", "password": "Password123!"})

    # Contraseña errónea
    response = client.post("/usuarios/token", data={"username": "login_fail@test.com", "password": "WrongPassword"})
    assert response.status_code == 401

    # Usuario no existente
    response2 = client.post("/usuarios/token", data={"username": "noexiste@test.com", "password": "Password123!"})
    assert response2.status_code == 401
