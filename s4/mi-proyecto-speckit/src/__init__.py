"""Módulo principal del validador de placas vehiculares (ANT Ecuador)."""

from typing import Any


def __getattr__(name: str) -> Any:
    if name in ("validar_placa", "ResultadoValidacion", "PROVINCIAS_ECUADOR", "SERVICIOS_SEGUNDA_LETRA"):
        from . import validador_placa
        return getattr(validador_placa, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "validar_placa",
    "ResultadoValidacion",
    "PROVINCIAS_ECUADOR",
    "SERVICIOS_SEGUNDA_LETRA",
]
