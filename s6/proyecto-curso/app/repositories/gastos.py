# Repository en memoria — se reemplazará por SQLAlchemy en la Sesión 7
# SRP: cada función hace UNA sola cosa (guardar, listar o sumar). Cero lógica de negocio aquí.
_gastos: list[dict] = []
_siguiente_id = 1


def guardar(descripcion: str, monto: float, categoria: str) -> dict:
    global _siguiente_id
    gasto = {
        "id": _siguiente_id,
        "descripcion": descripcion,
        "monto": monto,
        "categoria": categoria,
    }
    _gastos.append(gasto)
    _siguiente_id += 1
    return gasto


def listar() -> list[dict]:
    return _gastos


def total_por_categoria(categoria: str) -> float:
    return sum(g["monto"] for g in _gastos if g["categoria"] == categoria)
