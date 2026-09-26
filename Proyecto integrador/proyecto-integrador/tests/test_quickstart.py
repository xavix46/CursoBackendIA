"""Pruebas de integración de extremo a extremo (E2E) basadas en quickstart.md.

Ejecuta el flujo secuencial de los escenarios 1 a 4 detallados en quickstart.md:
1. Registro y login de Alice con obtención de JWT.
2. Creación de producto válido (10 >= 5) y rechazo por debajo del mínimo (3 < 5).
3. Reducción válida de stock (-3) y rechazo por romper umbral mínimo (-4).
4. Registro/login de Bob e intento denegado (403) de modificar producto ajeno.
"""

from fastapi.testclient import TestClient


def test_quickstart_e2e_scenarios(client: TestClient):
    # =========================================================================
    # Escenario 1: Registro y Obtención de Token (Alice)
    # =========================================================================
    alice_email = "alice@ejemplo.com"
    alice_password = "Password123!"

    # 1. Registrar usuario Alice
    res_reg_alice = client.post(
        "/usuarios/",
        json={"email": alice_email, "password": alice_password},
    )
    assert res_reg_alice.status_code == 201
    alice_data = res_reg_alice.json()
    assert alice_data["email"] == alice_email
    assert "id" in alice_data
    assert "password" not in alice_data
    assert "password_hash" not in alice_data

    # 2. Iniciar sesión y obtener token
    res_token_alice = client.post(
        "/usuarios/token",
        data={"username": alice_email, "password": alice_password},
    )
    assert res_token_alice.status_code == 200
    token_alice = res_token_alice.json()["access_token"]
    headers_alice = {"Authorization": f"Bearer {token_alice}"}

    # =========================================================================
    # Escenario 2: Crear Producto Válido vs Rechazo por Debajo del Mínimo
    # =========================================================================
    # Aprobado: Crear con cantidad >= cantidad_minima (10 >= 5) -> 201 Created
    res_prod_ok = client.post(
        "/productos/",
        headers=headers_alice,
        json={"nombre": "Teclado Mecánico", "cantidad": 10, "cantidad_minima": 5},
    )
    assert res_prod_ok.status_code == 201
    prod_data = res_prod_ok.json()
    assert prod_data["nombre"] == "Teclado Mecánico"
    assert prod_data["cantidad"] == 10
    assert prod_data["cantidad_minima"] == 5
    producto_alice_id = prod_data["id"]

    # Caso de Error 1: Crear con cantidad < cantidad_minima (3 < 5) -> 400 Bad Request
    res_prod_err = client.post(
        "/productos/",
        headers=headers_alice,
        json={"nombre": "Mouse Gamer", "cantidad": 3, "cantidad_minima": 5},
    )
    assert res_prod_err.status_code == 400
    assert "no puede ser menor" in res_prod_err.json()["detail"].lower()

    # =========================================================================
    # Escenario 3: Ajuste de Stock Válido vs Rechazo por Romper Umbral
    # =========================================================================
    # Aprobado: Reducir stock (-3 unidades, de 10 a 7, >= 5) -> 200 OK
    res_ajuste_ok = client.patch(
        f"/productos/{producto_alice_id}/ajustar",
        headers=headers_alice,
        json={"ajuste": -3},
    )
    assert res_ajuste_ok.status_code == 200
    assert res_ajuste_ok.json()["cantidad"] == 7

    # Caso de Error 2: Reducción excesiva (-4 unidades, de 7 a 3, < 5) -> 400 Bad Request
    res_ajuste_err = client.patch(
        f"/productos/{producto_alice_id}/ajustar",
        headers=headers_alice,
        json={"ajuste": -4},
    )
    assert res_ajuste_err.status_code == 400
    assert "por debajo" in res_ajuste_err.json()["detail"].lower()

    # Verificar que el stock no fue alterado tras el error rechazado
    res_list_alice = client.get("/productos/", headers=headers_alice)
    assert res_list_alice.status_code == 200
    alice_prods = res_list_alice.json()
    assert len(alice_prods) == 1
    assert alice_prods[0]["cantidad"] == 7

    # =========================================================================
    # Escenario 4: Aislamiento Multi-usuario (Caso de Error 5)
    # =========================================================================
    bob_email = "bob@ejemplo.com"
    bob_password = "Password123!"

    # 1. Registrar y autenticar usuario Bob
    res_reg_bob = client.post(
        "/usuarios/",
        json={"email": bob_email, "password": bob_password},
    )
    assert res_reg_bob.status_code == 201

    res_token_bob = client.post(
        "/usuarios/token",
        data={"username": bob_email, "password": bob_password},
    )
    assert res_token_bob.status_code == 200
    token_bob = res_token_bob.json()["access_token"]
    headers_bob = {"Authorization": f"Bearer {token_bob}"}

    # Intentar modificar el producto de Alice usando el token de Bob -> 403 Forbidden
    res_ajuste_bob = client.patch(
        f"/productos/{producto_alice_id}/ajustar",
        headers=headers_bob,
        json={"ajuste": 5},
    )
    assert res_ajuste_bob.status_code == 403
    assert "no tiene permisos" in res_ajuste_bob.json()["detail"].lower()

    # Bob lista sus productos y no ve el de Alice
    res_list_bob = client.get("/productos/", headers=headers_bob)
    assert res_list_bob.status_code == 200
    assert len(res_list_bob.json()) == 0
