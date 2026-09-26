from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.usuario import Usuario


class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def buscar_por_email(self, email: str) -> Optional[Usuario]:
        stmt = select(Usuario).where(Usuario.email == email)
        return self.db.execute(stmt).scalar_one_or_none()

    def buscar_por_id(self, usuario_id: int) -> Optional[Usuario]:
        stmt = select(Usuario).where(Usuario.id == usuario_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def crear(self, usuario: Usuario) -> Usuario:
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario
