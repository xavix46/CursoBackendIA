from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ProductoCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre único del producto para el usuario")
    cantidad: int = Field(..., ge=0, description="Stock inicial (debe ser >= cantidad_minima)")
    cantidad_minima: int = Field(..., ge=0, description="Cantidad mínima de seguridad")


class StockAjusteRequest(BaseModel):
    ajuste: int = Field(..., description="Unidades a sumar o restar del stock")


class ProductoResponse(BaseModel):
    id: int
    usuario_id: int
    nombre: str
    cantidad: int
    cantidad_minima: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
