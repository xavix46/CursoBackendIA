from mcp.server.fastmcp import FastMCP
from app.config import settings
from app.database import SessionLocal
from app.repositories import usuarios as usuarios_repository
from app.services import gastos as gastos_service
from app.security import hash_password


def _obtener_o_crear_usuario_demo(db):
    """
    Simplificación intencional de esta práctica: MCP todavía no propaga
    identidad (JWT) como sí lo hace REST desde la Sesión 7. En un proyecto
    real, este usuario vendría del contexto de la sesión MCP, no hardcodeado.

    El email/password del usuario demo vienen de Settings (.env), no quemados
    en el código -- mismo patrón que SECRET_KEY/DATABASE_URL desde la S7.
    """
    usuario = usuarios_repository.obtener_por_email(db, settings.mcp_demo_email)
    if usuario is None:
        usuario = usuarios_repository.guardar(
            db, settings.mcp_demo_email, hash_password(settings.mcp_demo_password)
        )
    return usuario


def register(mcp: FastMCP) -> None:
    """Registra los tools de gastos sobre la instancia de FastMCP que le pasa server.py."""

    @mcp.tool()
    def registrar_gasto(descripcion: str, monto: float, categoria: str) -> dict:
        """Registra un nuevo gasto. Usar cuando el usuario mencione una compra o pago que quiere trackear."""
        db = SessionLocal()
        try:
            usuario = _obtener_o_crear_usuario_demo(db)
            return gastos_service.registrar_gasto(db, usuario.id, descripcion, monto, categoria)
        except (ValueError, gastos_service.CategoriaInvalidaError, gastos_service.LimiteExcedidoError) as e:
            # Manejo de errores en tools: se devuelve texto claro, no una excepción sin control
            return {"error": str(e)}
        finally:
            db.close()

    @mcp.tool()
    def listar_gastos() -> list[dict]:
        """Lista todos los gastos registrados del usuario. Usar cuando pregunten por sus gastos o quieran un resumen."""
        db = SessionLocal()
        try:
            usuario = _obtener_o_crear_usuario_demo(db)
            return gastos_service.listar_gastos(db, usuario.id)
        finally:
            db.close()

