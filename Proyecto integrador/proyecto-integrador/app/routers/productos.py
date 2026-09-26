from typing import Annotated
from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.models.producto import Producto
from app.schemas.producto import ProductoCreate, ProductoResponse, StockAjusteRequest
from app.repositories.producto_repo import ProductoRepository
from app.services.producto_service import ProductoService
from app.routers.auth import get_current_user

router = APIRouter(prefix="/productos", tags=["Productos e Inventario"])


def get_producto_repo(db: Annotated[Session, Depends(get_db)]) -> ProductoRepository:
    return ProductoRepository(db)


def get_producto_service(
    repo: Annotated[ProductoRepository, Depends(get_producto_repo)]
) -> ProductoService:
    return ProductoService(repo)


@router.post(
    "/",
    response_model=ProductoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo producto",
    description="Registra un producto en el inventario propio del usuario autenticado, verificando que cantidad >= cantidad_minima >= 0.",
)
def crear_producto(
    prod_in: ProductoCreate,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    service: Annotated[ProductoService, Depends(get_producto_service)],
) -> ProductoResponse:
    """Crea un nuevo producto asociado al usuario autenticado."""
    return service.crear_producto(usuario_id=current_user.id, prod_in=prod_in)


@router.get(
    "/",
    response_model=list[ProductoResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar productos del usuario",
    description="Obtiene el catálogo de productos pertenecientes exclusivamente al usuario autenticado, soportando paginación.",
)
def listar_productos(
    current_user: Annotated[Usuario, Depends(get_current_user)],
    service: Annotated[ProductoService, Depends(get_producto_service)],
    skip: Annotated[int, Query(ge=0, description="Cantidad de registros a omitir")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Cantidad máxima de registros a retornar")] = 20,
) -> list[ProductoResponse]:
    """Lista los productos del usuario con paginación."""
    return service.listar_productos(usuario_id=current_user.id, skip=skip, limit=limit)


@router.patch(
    "/{id}/ajustar",
    response_model=ProductoResponse,
    status_code=status.HTTP_200_OK,
    summary="Ajustar stock de un producto",
    description="Ajusta la cantidad disponible (positiva o negativamente) validando propiedad (403) y que la cantidad resultante no caiga por debajo de la cantidad mínima configurada.",
)
def ajustar_stock(
    id: Annotated[int, Path(description="ID del producto a ajustar", ge=1)],
    ajuste_in: StockAjusteRequest,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    service: Annotated[ProductoService, Depends(get_producto_service)],
) -> ProductoResponse:
    """Ajusta el stock de un producto perteneciente al usuario autenticado."""
    return service.ajustar_stock(usuario_id=current_user.id, producto_id=id, ajuste=ajuste_in.ajuste)
