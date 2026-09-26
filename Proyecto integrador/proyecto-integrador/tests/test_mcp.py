import pytest
from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.auth import create_access_token


def test_mcp_crear_producto_exitoso(db_session: Session):
    """Verifica que la herramienta MCP crear_producto registre el producto con éxito."""
    from app.mcp.tools import crear_producto_tool
    
    # Usuario registrado
    usuario = Usuario(email="mcp_user@test.com", password_hash="hash")
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)

    token = create_access_token({"sub": usuario.email, "user_id": usuario.id})

    res = crear_producto_tool(
        nombre="Scanner Láser",
        cantidad=10,
        cantidad_minima=3,
        token=token,
        db=db_session,
    )
    assert res["status"] == "success"
    assert res["data"]["nombre"] == "Scanner Láser"
    assert res["data"]["cantidad"] == 10
    assert res["data"]["cantidad_minima"] == 3


def test_mcp_crear_producto_error_minimo(db_session: Session):
    """Verifica que crear_producto rechace cuando cantidad < cantidad_minima con error estructurado."""
    from app.mcp.tools import crear_producto_tool

    usuario = Usuario(email="mcp_user2@test.com", password_hash="hash")
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)

    token = create_access_token({"sub": usuario.email, "user_id": usuario.id})

    res = crear_producto_tool(
        nombre="Router WiFi",
        cantidad=1,
        cantidad_minima=5,
        token=token,
        db=db_session,
    )
    assert res["status"] == "error"
    assert "menor" in res["detail"].lower() or "mínima" in res["detail"].lower()


def test_mcp_ajustar_stock_exitoso_y_error_minimo(db_session: Session):
    """Verifica ajuste de stock y rechazo cuando deja el stock por debajo del mínimo."""
    from app.mcp.tools import crear_producto_tool, ajustar_stock_tool

    usuario = Usuario(email="mcp_user3@test.com", password_hash="hash")
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)

    token = create_access_token({"sub": usuario.email, "user_id": usuario.id})

    # Crear producto inicial: 10 unidades, mín 5
    creado = crear_producto_tool(nombre="Impresora 3D", cantidad=10, cantidad_minima=5, token=token, db=db_session)
    prod_id = creado["data"]["id"]

    # Ajuste exitoso (-3 -> queda en 7, >= 5)
    ajuste_ok = ajustar_stock_tool(producto_id=prod_id, ajuste=-3, token=token, db=db_session)
    assert ajuste_ok["status"] == "success"
    assert ajuste_ok["data"]["cantidad"] == 7

    # Ajuste que baja del mínimo (-4 dejaría 3, < 5) -> Debe responder con error estructurado
    ajuste_err = ajustar_stock_tool(producto_id=prod_id, ajuste=-4, token=token, db=db_session)
    assert ajuste_err["status"] == "error"
    assert "mínima" in ajuste_err["detail"].lower() or "debajo" in ajuste_err["detail"].lower()


def test_mcp_listar_productos(db_session: Session):
    """Verifica listado de productos vía MCP."""
    from app.mcp.tools import crear_producto_tool, listar_productos_tool

    usuario = Usuario(email="mcp_user4@test.com", password_hash="hash")
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)

    token = create_access_token({"sub": usuario.email, "user_id": usuario.id})

    crear_producto_tool(nombre="Item A", cantidad=5, cantidad_minima=1, token=token, db=db_session)
    crear_producto_tool(nombre="Item B", cantidad=15, cantidad_minima=2, token=token, db=db_session)

    res = listar_productos_tool(skip=0, limit=10, token=token, db=db_session)
    assert res["status"] == "success"
    assert res["count"] == 2
    nombres = {p["nombre"] for p in res["data"]}
    assert nombres == {"Item A", "Item B"}


def test_mcp_fallback_usuario_demo(db_session: Session):
    """Verifica que sin token (modo stdio), MCP resuelva y use al usuario demo configurado."""
    from app.mcp.tools import crear_producto_tool, listar_productos_tool

    # Invocación sin token (simulando transporte stdio)
    res = crear_producto_tool(nombre="Herramienta Demo", cantidad=8, cantidad_minima=2, token=None, db=db_session)
    assert res["status"] == "success"

    lista = listar_productos_tool(token=None, db=db_session)
    assert lista["status"] == "success"
    assert any(p["nombre"] == "Herramienta Demo" for p in lista["data"])
