from typing import Optional, Any
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.producto import ProductoCreate
from app.repositories.producto_repo import ProductoRepository
from app.services.producto_service import ProductoService
from app.mcp.auth import get_mcp_user


def _serializar_producto(p) -> dict[str, Any]:
    return {
        "id": p.id,
        "usuario_id": p.usuario_id,
        "nombre": p.nombre,
        "cantidad": p.cantidad,
        "cantidad_minima": p.cantidad_minima,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }


def crear_producto_tool(
    nombre: str,
    cantidad: int,
    cantidad_minima: int,
    token: Optional[str] = None,
    db: Optional[Session] = None,
) -> dict[str, Any]:
    """Herramienta MCP: Registra un nuevo producto en el inventario."""
    own_session = False
    if db is None:
        db = SessionLocal()
        own_session = True

    try:
        usuario = get_mcp_user(db, token)
        repo = ProductoRepository(db)
        service = ProductoService(repo)
        prod_in = ProductoCreate(
            nombre=nombre,
            cantidad=cantidad,
            cantidad_minima=cantidad_minima,
        )
        producto = service.crear_producto(usuario_id=usuario.id, prod_in=prod_in)
        return {
            "status": "success",
            "data": _serializar_producto(producto),
        }
    except HTTPException as e:
        return {"status": "error", "detail": e.detail}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
    finally:
        if own_session:
            db.close()


def ajustar_stock_tool(
    producto_id: int,
    ajuste: int,
    token: Optional[str] = None,
    db: Optional[Session] = None,
) -> dict[str, Any]:
    """Herramienta MCP: Modifica las existencias de un producto propio."""
    own_session = False
    if db is None:
        db = SessionLocal()
        own_session = True

    try:
        usuario = get_mcp_user(db, token)
        repo = ProductoRepository(db)
        service = ProductoService(repo)
        producto = service.ajustar_stock(
            usuario_id=usuario.id,
            producto_id=producto_id,
            ajuste=ajuste,
        )
        return {
            "status": "success",
            "data": _serializar_producto(producto),
        }
    except HTTPException as e:
        return {"status": "error", "detail": e.detail}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
    finally:
        if own_session:
            db.close()


def listar_productos_tool(
    skip: int = 0,
    limit: int = 20,
    token: Optional[str] = None,
    db: Optional[Session] = None,
) -> dict[str, Any]:
    """Herramienta MCP: Consulta los productos del usuario autenticado."""
    own_session = False
    if db is None:
        db = SessionLocal()
        own_session = True

    try:
        usuario = get_mcp_user(db, token)
        repo = ProductoRepository(db)
        service = ProductoService(repo)
        productos = service.listar_productos(
            usuario_id=usuario.id,
            skip=skip,
            limit=limit,
        )
        return {
            "status": "success",
            "count": len(productos),
            "data": [_serializar_producto(p) for p in productos],
        }
    except HTTPException as e:
        return {"status": "error", "detail": e.detail}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
    finally:
        if own_session:
            db.close()
