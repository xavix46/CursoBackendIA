from app.repositories import gastos as gastos_repository
from app.utils.validadores import categoria_valida

LIMITE_POR_CATEGORIA = 500.0


class CategoriaInvalidaError(Exception):
    pass


class LimiteExcedidoError(Exception):
    pass


# SRP: esta función SOLO valida. No decide reglas de negocio, no persiste.
def _validar_gasto(descripcion: str, monto: float, categoria: str) -> None:
    if not descripcion or not descripcion.strip():
        raise ValueError("La descripción no puede estar vacía")

    if monto <= 0:
        raise ValueError("El monto debe ser mayor a cero")

    if not categoria_valida(categoria):
        raise CategoriaInvalidaError(f"'{categoria}' no es una categoría válida")


# SRP: esta función SOLO orquesta (valida -> revisa regla de negocio -> persiste).
# DIP: recibe "repo" como parámetro en vez de usar gastos_repository fijo dentro del
# cuerpo de la función -> se puede sustituir por cualquier objeto con el mismo contrato.
def registrar_gasto(
    db,
    usuario_id: int,
    descripcion: str,
    monto: float,
    categoria: str,
    repo=gastos_repository,
) -> dict:
    _validar_gasto(descripcion, monto, categoria)

    total_actual = repo.total_por_categoria(db, usuario_id, categoria)
    if total_actual + monto > LIMITE_POR_CATEGORIA:
        raise LimiteExcedidoError(
            f"Este gasto supera el límite de {LIMITE_POR_CATEGORIA} para la categoría '{categoria}'"
        )

    return repo.guardar(db, usuario_id, descripcion, monto, categoria)


def listar_gastos(db, usuario_id: int, skip: int = 0, limit: int = 20, repo=gastos_repository) -> list[dict]:
    return repo.listar(db, usuario_id, skip, limit)
