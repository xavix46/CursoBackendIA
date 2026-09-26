from typing import Optional
from sqlalchemy.orm import Session
from app.config import get_settings
from app.auth import decode_access_token, hash_password
from app.models.usuario import Usuario
from app.repositories.usuario_repo import UsuarioRepository

settings = get_settings()


def get_mcp_user(db: Session, token: Optional[str] = None) -> Usuario:
    repo = UsuarioRepository(db)

    # 1. Si se provee token (ej. streamable-http / Authorization Bearer)
    if token:
        # Remover prefijo Bearer si viene incluido
        if token.lower().startswith("bearer "):
            token = token[7:].strip()
        payload = decode_access_token(token)
        if payload:
            user_id = payload.get("user_id")
            email = payload.get("sub")
            usuario = None
            if user_id:
                usuario = repo.buscar_por_id(user_id)
            elif email:
                usuario = repo.buscar_por_email(email)
            if usuario:
                return usuario
        raise ValueError("Token de sesión MCP inválido o expirado.")

    # 2. Fallback para transporte local stdio: resolver o auto-crear usuario demo
    demo_email = settings.MCP_DEMO_USER_EMAIL
    usuario = repo.buscar_por_email(demo_email)
    if not usuario:
        demo_user = Usuario(
            email=demo_email,
            password_hash=hash_password("DemoPassword123!"),
        )
        usuario = repo.crear(demo_user)

    return usuario
