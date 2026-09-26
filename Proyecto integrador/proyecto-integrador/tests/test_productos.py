import pytest
from fastapi.testclient import TestClient


def crear_usuario_y_obtener_token(client: TestClient, email: str = "user@test.com") -> str:
    """Helper para registrar usuario y obtener token JWT."""
    client.post("/usuarios/", json={"email": email, "password": "Password123!"})
    res = client.post("/usuarios/token", data={"username": email, "password": "Password123!"})
    return res.json()["access_token"]


# =========================================================================
# User Story 2 Tests: Creación y registro de productos
# =========================================================================

def test_crear_producto_valido(client: TestClient):
    """Verifica creación válida de producto donde cantidad >= cantidad_minima (201)."""
    token = crear_usuario_y_obtener_token(client, "user_crear@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "nombre": "Monitor 27 pulgadas",
        "cantidad": 10,
        "cantidad_minima": 2
    }
    response = client.post("/productos/", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Monitor 27 pulgadas"
    assert data["cantidad"] == 10
    assert data["cantidad_minima"] == 2
    assert "id" in data
    assert "usuario_id" in data


def test_error_caso_1_crear_producto_cantidad_menor_a_minima(client: TestClient):
    """Caso de Error 1: Crear un producto donde la cantidad inicial es menor a la cantidad mínima -> 400."""
    token = crear_usuario_y_obtener_token(client, "user_error1@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "nombre": "Teclado RGB",
        "cantidad": 2,
        "cantidad_minima": 5
    }
    response = client.post("/productos/", json=payload, headers=headers)
    assert response.status_code == 400
    detail = response.json()["detail"].lower()
    assert "menor" in detail or "mínima" in detail or "minima" in detail


def test_error_caso_3_crear_producto_valores_negativos(client: TestClient):
    """Caso de Error 3: Crear un producto con valores negativos no permitidos (ej. cantidad_minima < 0 o cantidad < 0) -> 422 o 400."""
    token = crear_usuario_y_obtener_token(client, "user_error3@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    # cantidad negativa
    res1 = client.post("/productos/", json={"nombre": "Item 1", "cantidad": -5, "cantidad_minima": 0}, headers=headers)
    assert res1.status_code in (400, 422)

    # cantidad_minima negativa
    res2 = client.post("/productos/", json={"nombre": "Item 2", "cantidad": 5, "cantidad_minima": -2}, headers=headers)
    assert res2.status_code in (400, 422)


def test_crear_producto_nombre_duplicado_mismo_usuario(client: TestClient):
    """Verifica que un usuario no pueda registrar dos productos con el mismo nombre -> 400."""
    token = crear_usuario_y_obtener_token(client, "user_dup@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "nombre": "Mouse Inalámbrico",
        "cantidad": 10,
        "cantidad_minima": 5
    }
    res1 = client.post("/productos/", json=payload, headers=headers)
    assert res1.status_code == 201

    res2 = client.post("/productos/", json=payload, headers=headers)
    assert res2.status_code == 400
    assert "nombre" in res2.json()["detail"].lower() or "duplicado" in res2.json()["detail"].lower() or "existe" in res2.json()["detail"].lower()


def test_error_caso_4_crear_producto_sin_token(client: TestClient):
    """Caso de Error 4: Crear productos sin token -> 401 Unauthorized."""
    payload = {
        "nombre": "Sin Token",
        "cantidad": 10,
        "cantidad_minima": 5
    }
    response = client.post("/productos/", json=payload)
    assert response.status_code == 401


# =========================================================================
# User Story 3 Tests: Ajuste de stock con umbral mínimo y aislamiento
# =========================================================================

def test_ajustar_stock_positivo(client: TestClient):
    """Verifica ajuste positivo incrementando stock (200)."""
    token = crear_usuario_y_obtener_token(client, "user_ajuste_pos@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    p_res = client.post("/productos/", json={"nombre": "Audífonos", "cantidad": 10, "cantidad_minima": 5}, headers=headers)
    prod_id = p_res.json()["id"]

    res = client.patch(f"/productos/{prod_id}/ajustar", json={"ajuste": 5}, headers=headers)
    assert res.status_code == 200
    assert res.json()["cantidad"] == 15


def test_ajustar_stock_reduccion_valida(client: TestClient):
    """Verifica reducción válida de stock que respeta cantidad_minima (200)."""
    token = crear_usuario_y_obtener_token(client, "user_ajuste_val@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    p_res = client.post("/productos/", json={"nombre": "Webcam", "cantidad": 20, "cantidad_minima": 5}, headers=headers)
    prod_id = p_res.json()["id"]

    res = client.patch(f"/productos/{prod_id}/ajustar", json={"ajuste": -10}, headers=headers)
    assert res.status_code == 200
    assert res.json()["cantidad"] == 10


def test_error_caso_2_ajustar_stock_debajo_de_minimo(client: TestClient):
    """Caso de Error 2: Ajustar el stock restando una cantidad que deje el total por debajo de cantidad_minima -> 400 y no altera stock."""
    token = crear_usuario_y_obtener_token(client, "user_ajuste_error2@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    p_res = client.post("/productos/", json={"nombre": "Micrófono", "cantidad": 10, "cantidad_minima": 5}, headers=headers)
    prod_id = p_res.json()["id"]

    # Reducción de 6 dejaría 4, menor al mínimo 5 -> 400
    res = client.patch(f"/productos/{prod_id}/ajustar", json={"ajuste": -6}, headers=headers)
    assert res.status_code == 400
    detail = res.json()["detail"].lower()
    assert "mínima" in detail or "minima" in detail or "debajo" in detail

    # Verificar que el stock NO fue modificado
    lista = client.get("/productos/", headers=headers).json()
    item = next(p for p in lista if p["id"] == prod_id)
    assert item["cantidad"] == 10


def test_error_caso_5_ajustar_stock_producto_otro_usuario(client: TestClient):
    """Caso de Error 5: Intentar ajustar el stock de un producto de otro usuario pasando su ID manualmente -> debe devolver 403 Forbidden, nunca actualizarlo."""
    token_alice = crear_usuario_y_obtener_token(client, "alice@test.com")
    headers_alice = {"Authorization": f"Bearer {token_alice}"}
    p_res = client.post("/productos/", json={"nombre": "Tablet de Alice", "cantidad": 10, "cantidad_minima": 2}, headers=headers_alice)
    prod_id_alice = p_res.json()["id"]

    # Bob intenta modificar el producto de Alice
    token_bob = crear_usuario_y_obtener_token(client, "bob@test.com")
    headers_bob = {"Authorization": f"Bearer {token_bob}"}
    res = client.patch(f"/productos/{prod_id_alice}/ajustar", json={"ajuste": -2}, headers=headers_bob)

    # Debe ser inequívocamente 403 Forbidden
    assert res.status_code == 403
    assert "permisos" in res.json()["detail"].lower()

    # Comprobar que el producto de Alice sigue intacto
    alice_item = client.get("/productos/", headers=headers_alice).json()[0]
    assert alice_item["cantidad"] == 10


def test_ajustar_stock_producto_inexistente(client: TestClient):
    """Verifica que ajustar un producto que no existe devuelva 404 Not Found."""
    token = crear_usuario_y_obtener_token(client, "user_404@test.com")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.patch("/productos/99999/ajustar", json={"ajuste": 5}, headers=headers)
    assert res.status_code == 404


def test_error_caso_4_ajustar_stock_sin_token(client: TestClient):
    """Caso de Error 4: Ajustar productos sin token -> 401 Unauthorized."""
    res = client.patch("/productos/1/ajustar", json={"ajuste": 5})
    assert res.status_code == 401


# =========================================================================
# User Story 4 Tests: Consulta paginada y aislamiento de catálogo
# =========================================================================

def test_listar_productos_paginacion(client: TestClient):
    """Verifica que el listado responda con paginación respetando skip y limit (200)."""
    token = crear_usuario_y_obtener_token(client, "user_paginacion@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Crear 5 productos
    for i in range(1, 6):
        client.post(
            "/productos/",
            json={"nombre": f"Producto {i}", "cantidad": 10 * i, "cantidad_minima": 2},
            headers=headers,
        )

    # Página 1: limit 2, skip 0 -> 2 items (Producto 1, Producto 2)
    p1 = client.get("/productos/?skip=0&limit=2", headers=headers)
    assert p1.status_code == 200
    assert len(p1.json()) == 2
    assert p1.json()[0]["nombre"] == "Producto 1"
    assert p1.json()[1]["nombre"] == "Producto 2"

    # Página 2: limit 2, skip 2 -> 2 items (Producto 3, Producto 4)
    p2 = client.get("/productos/?skip=2&limit=2", headers=headers)
    assert p2.status_code == 200
    assert len(p2.json()) == 2
    assert p2.json()[0]["nombre"] == "Producto 3"
    assert p2.json()[1]["nombre"] == "Producto 4"

    # Página 3: limit 2, skip 4 -> 1 item (Producto 5)
    p3 = client.get("/productos/?skip=4&limit=2", headers=headers)
    assert p3.status_code == 200
    assert len(p3.json()) == 1
    assert p3.json()[0]["nombre"] == "Producto 5"


def test_listar_productos_aislamiento_entre_usuarios(client: TestClient):
    """Verifica que cada usuario vea única y exclusivamente sus propios productos."""
    token_user_a = crear_usuario_y_obtener_token(client, "alice_list@test.com")
    headers_a = {"Authorization": f"Bearer {token_user_a}"}

    token_user_b = crear_usuario_y_obtener_token(client, "bob_list@test.com")
    headers_b = {"Authorization": f"Bearer {token_user_b}"}

    # Alice crea 3 productos
    client.post("/productos/", json={"nombre": "Laptop Alice", "cantidad": 5, "cantidad_minima": 1}, headers=headers_a)
    client.post("/productos/", json={"nombre": "Mochila Alice", "cantidad": 8, "cantidad_minima": 2}, headers=headers_a)
    client.post("/productos/", json={"nombre": "Mousepad Alice", "cantidad": 12, "cantidad_minima": 3}, headers=headers_a)

    # Bob crea 2 productos
    client.post("/productos/", json={"nombre": "Monitor Bob", "cantidad": 4, "cantidad_minima": 1}, headers=headers_b)
    client.post("/productos/", json={"nombre": "Cable Bob", "cantidad": 20, "cantidad_minima": 5}, headers=headers_b)

    # Listado de Alice
    res_a = client.get("/productos/", headers=headers_a)
    assert res_a.status_code == 200
    productos_a = res_a.json()
    assert len(productos_a) == 3
    nombres_a = {p["nombre"] for p in productos_a}
    assert nombres_a == {"Laptop Alice", "Mochila Alice", "Mousepad Alice"}

    # Listado de Bob
    res_b = client.get("/productos/", headers=headers_b)
    assert res_b.status_code == 200
    productos_b = res_b.json()
    assert len(productos_b) == 2
    nombres_b = {p["nombre"] for p in productos_b}
    assert nombres_b == {"Monitor Bob", "Cable Bob"}


def test_error_caso_4_listar_productos_sin_token(client: TestClient):
    """Caso de Error 4: Listar productos sin token -> 401 Unauthorized."""
    res = client.get("/productos/")
    assert res.status_code == 401


