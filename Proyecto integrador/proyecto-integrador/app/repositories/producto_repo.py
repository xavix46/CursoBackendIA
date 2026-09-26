from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.producto import Producto


class ProductoRepository:
    def __init__(self, db: Session):
        self.db = db

    def buscar_por_id(self, producto_id: int) -> Optional[Producto]:
        stmt = select(Producto).where(Producto.id == producto_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def buscar_por_nombre_y_usuario(self, usuario_id: int, nombre: str) -> Optional[Producto]:
        stmt = select(Producto).where(
            Producto.usuario_id == usuario_id,
            Producto.nombre == nombre,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def crear(self, producto: Producto) -> Producto:
        self.db.add(producto)
        self.db.commit()
        self.db.refresh(producto)
        return producto

    def listar_por_usuario(self, usuario_id: int, skip: int = 0, limit: int = 20) -> list[Producto]:
        stmt = (
            select(Producto)
            .where(Producto.usuario_id == usuario_id)
            .order_by(Producto.id.asc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def guardar_ajuste(self, producto: Producto, nueva_cantidad: int) -> Producto:
        producto.cantidad = nueva_cantidad
        producto.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(producto)
        return producto
