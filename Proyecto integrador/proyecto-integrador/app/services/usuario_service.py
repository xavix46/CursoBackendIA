from typing import Optional
from fastapi import HTTPException, status
from app.models.usuario import Usuario
from app.schemas.usuario import UserCreate
from app.repositories.usuario_repo import UsuarioRepository
from app.auth import hash_password, verify_password


class UsuarioService:
    def __init__(self, usuario_repo: UsuarioRepository):
        self.usuario_repo = usuario_repo

    def crear_usuario(self, user_in: UserCreate) -> Usuario:
        existente = self.usuario_repo.buscar_por_email(user_in.email)
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya se encuentra registrado.",
            )

        hashed = hash_password(user_in.password)
        nuevo_usuario = Usuario(
            email=user_in.email,
            password_hash=hashed,
        )
        return self.usuario_repo.crear(nuevo_usuario)

    def autenticar_usuario(self, email: str, password: str) -> Optional[Usuario]:
        usuario = self.usuario_repo.buscar_por_email(email)
        if not usuario:
            return None
        if not verify_password(password, usuario.password_hash):
            return None
        return usuario
