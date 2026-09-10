import pytest
from app.services import gastos as gastos_service
from app.services.gastos import LimiteExcedidoError, CategoriaInvalidaError


class RepositorioFalso:
    """Test double: mismo contrato que app/repositories/gastos.py, sin persistencia real."""

    def __init__(self, total_inicial_por_categoria: float = 0.0):
        self._gastos: list[dict] = []
        self._total_inicial = total_inicial_por_categoria

    def guardar(self, descripcion: str, monto: float, categoria: str) -> dict:
        gasto = {"id": len(self._gastos) + 1,
         "descripcion": descripcion,
          "monto": monto,
            "categoria": categoria}
        self._gastos.append(gasto)
        return gasto

    def listar(self) -> list[dict]:
        return self._gastos

    def total_por_categoria(self, categoria: str) -> float:
        return self._total_inicial + sum(g["monto"] for g in self._gastos if g["categoria"] == categoria)


# Gracias a DIP: se inyecta un repositorio falso, no se necesita unittest.mock.
def test_registrar_gasto_exitoso():
    repo = RepositorioFalso()

    resultado = gastos_service.registrar_gasto("Almuerzo", 12.50, "comida", repo=repo)

    assert resultado["descripcion"] == "Almuerzo"
    assert repo.listar() == [resultado]


def test_registrar_gasto_monto_invalido_lanza_error():
    with pytest.raises(ValueError):
        gastos_service.registrar_gasto("Café", -5.0, "comida", repo=RepositorioFalso())


def test_registrar_gasto_categoria_invalida_lanza_error():
    with pytest.raises(CategoriaInvalidaError):
        gastos_service.registrar_gasto("Cine", 20.0, "categoria-inventada", repo=RepositorioFalso())


def test_registrar_gasto_excede_limite_categoria_lanza_error():
    repo = RepositorioFalso(total_inicial_por_categoria=490.0)

    with pytest.raises(LimiteExcedidoError):
        gastos_service.registrar_gasto("Cena cara", 50.0, "comida", repo=repo)
