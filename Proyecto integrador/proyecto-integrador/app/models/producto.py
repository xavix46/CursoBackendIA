from datetime import datetime, timezone
from sqlalchemy import Integer, String, DateTime, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Producto(Base):
    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    cantidad_minima: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relación con Usuario
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="productos")

    __table_args__ = (
        UniqueConstraint("usuario_id", "nombre", name="uq_usuario_producto_nombre"),
        CheckConstraint("cantidad >= 0", name="ck_producto_cantidad_no_negativa"),
        CheckConstraint("cantidad_minima >= 0", name="ck_producto_cantidad_minima_no_negativa"),
        CheckConstraint("cantidad >= cantidad_minima", name="ck_producto_stock_minimo_valido"),
    )
