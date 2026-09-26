from typing import Optional
from mcp.server.fastmcp import FastMCP
from app.mcp.tools import crear_producto_tool, ajustar_stock_tool, listar_productos_tool

mcp = FastMCP("Inventario MCP Server")


@mcp.tool()
def crear_producto(nombre: str, cantidad: int, cantidad_minima: int, token: Optional[str] = None) -> dict:
    """Registra un nuevo producto en el catálogo del usuario autenticado."""
    return crear_producto_tool(nombre=nombre, cantidad=cantidad, cantidad_minima=cantidad_minima, token=token)


@mcp.tool()
def ajustar_stock(producto_id: int, ajuste: int, token: Optional[str] = None) -> dict:
    """Ajusta las existencias de un producto propio (+ o -) asegurando que no baje del mínimo permitido."""
    return ajustar_stock_tool(producto_id=producto_id, ajuste=ajuste, token=token)


@mcp.tool()
def listar_productos(skip: int = 0, limit: int = 20, token: Optional[str] = None) -> dict:
    """Obtiene la lista de productos pertenecientes al usuario actual con paginación."""
    return listar_productos_tool(skip=skip, limit=limit, token=token)


if __name__ == "__main__":
    mcp.run()
