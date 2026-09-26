from typing import Optional
from fastapi import HTTPException, status
from app.models.producto import Producto
from app.schemas.producto import ProductoCreate
from app.repositories.producto_repo import ProductoRepository


class ProductoService:
    def __init__(self, producto_repo: ProductoRepository):
        self.producto_repo = producto_repo

    def crear_producto(self, usuario_id: int, prod_in: ProductoCreate) -> Producto:
        # Validación: cantidad inicial no puede ser menor a cantidad mínima
        if prod_in.cantidad < prod_in.cantidad_minima:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La cantidad inicial ({prod_in.cantidad}) no puede ser menor a la cantidad mínima ({prod_in.cantidad_minima}).",
            )

        # Validación: valores negativos
        if prod_in.cantidad < 0 or prod_in.cantidad_minima < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La cantidad y la cantidad mínima deben ser números enteros mayores o iguales a cero.",
            )

        # Validación: unicidad del nombre dentro del catálogo del mismo usuario
        existente = self.producto_repo.buscar_por_nombre_y_usuario(usuario_id, prod_in.nombre)
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un producto con el nombre '{prod_in.nombre}' en su catálogo.",
            )

        nuevo_producto = Producto(
            usuario_id=usuario_id,
            nombre=prod_in.nombre,
            cantidad=prod_in.cantidad,
            cantidad_minima=prod_in.cantidad_minima,
        )
        return self.producto_repo.crear(nuevo_producto)

    def ajustar_stock(self, usuario_id: int, producto_id: int, ajuste: int) -> Producto:
        producto = self.producto_repo.buscar_por_id(producto_id)
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado.",
            )

        # Aislamiento estricto: 403 Forbidden si el producto pertenece a otro usuario
        if producto.usuario_id != usuario_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para modificar este producto.",
            )

        nueva_cantidad = producto.cantidad + ajuste

        # Validación de negocio: la cantidad resultante no puede bajar del mínimo ni ser negativa
        if nueva_cantidad < 0 or nueva_cantidad < producto.cantidad_minima:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La cantidad resultante ({nueva_cantidad}) no puede quedar por debajo de la cantidad mínima configurada ({producto.cantidad_minima}).",
            )

        return self.producto_repo.guardar_ajuste(producto, nueva_cantidad)

    def listar_productos(self, usuario_id: int, skip: int = 0, limit: int = 20) -> list[Producto]:
        if skip < 0 or limit <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Los parámetros de paginación deben ser positivos (skip >= 0, limit > 0).",
            )
        return self.producto_repo.listar_por_usuario(usuario_id, skip=skip, limit=limit)
