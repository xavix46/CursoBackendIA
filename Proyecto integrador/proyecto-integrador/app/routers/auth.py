from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import oauth2_scheme, create_access_token, decode_access_token
from app.models.usuario import Usuario
from app.schemas.usuario import UserCreate, UserResponse, TokenResponse
from app.repositories.usuario_repo import UsuarioRepository
from app.services.usuario_service import UsuarioService

router = APIRouter(prefix="/usuarios", tags=["Usuarios y Autenticación"])


def get_usuario_repo(db: Annotated[Session, Depends(get_db)]) -> UsuarioRepository:
    return UsuarioRepository(db)


def get_usuario_service(
    repo: Annotated[UsuarioRepository, Depends(get_usuario_repo)]
) -> UsuarioService:
    return UsuarioService(repo)


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    repo: Annotated[UsuarioRepository, Depends(get_usuario_repo)],
) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales de autenticación inválidas o expiradas.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    email: str = payload.get("sub")
    user_id: int = payload.get("user_id")
    if email is None and user_id is None:
        raise credentials_exception

    usuario = None
    if user_id is not None:
        usuario = repo.buscar_por_id(user_id)
    elif email is not None:
        usuario = repo.buscar_por_email(email)

    if usuario is None:
        raise credentials_exception
    return usuario


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario",
    description="Crea un nuevo usuario en el sistema con correo electrónico único y contraseña encriptada.",
)
def registrar_usuario(
    user_in: UserCreate,
    service: Annotated[UsuarioService, Depends(get_usuario_service)],
) -> UserResponse:
    """Registra un nuevo usuario en la base de datos verificando unicidad de correo."""
    return service.crear_usuario(user_in)


@router.post(
    "/token",
    response_model=TokenResponse,
    summary="Iniciar sesión y obtener token JWT",
    description="Autentica las credenciales del usuario y genera un token JWT Bearer de acceso.",
)
def login_para_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: Annotated[UsuarioService, Depends(get_usuario_service)],
) -> TokenResponse:
    """Verifica credenciales del usuario y emite un token de acceso JWT."""
    usuario = service.autenticar_usuario(form_data.username, form_data.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": usuario.email, "user_id": usuario.id}
    )
    return TokenResponse(access_token=access_token, token_type="bearer")
