# Contract: Python Library API (`validar_placa`)

**Feature**: `001-validar-placas-vehiculares`  
**Date**: 2026-09-16  
**Status**: Formal Contract  

---

## 1. Módulo: `validador_placa`

El módulo expone la función principal y el tipo de dato devuelto para ser consumido por cualquier servicio backend o script en Python.

### 1.1 Firma de la Función Principal

```python
def validar_placa(placa: Any) -> ResultadoValidacion:
    """Valida si una placa vehicular cumple con el formato ANT Ecuador de 3 letras y 4 números.
    
    Args:
        placa (Any): Cadena de texto que contiene la placa vehicular a validar.
                     Se aceptan variaciones como 'PBX-1234', 'PBX 1234', 'PBX1234', 'pbx-1234'.
                     Si se pasa un tipo distinto de 'str' o 'None', se captura de forma controlada.
                     
    Returns:
        ResultadoValidacion: Instancia con los resultados de la validación, normalización,
                             provincia identificada, tipo de servicio y mensaje diagnóstico.
    """
```

---

## 2. Definición de Tipos y Clases

### 2.1 `ResultadoValidacion`

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class ResultadoValidacion:
    es_valida: bool
    placa_original: str
    placa_normalizada: str | None = None
    provincia: str | None = None
    tipo_servicio: str | None = None
    mensaje: str = ""
    detalles: dict[str, Any] | None = None

    def __str__(self) -> str:
        """Representación legible para consola/logs."""
        ...
```

---

## 3. Comportamientos Contractuales y Casos de Retorno

| Caso de Prueba / Entrada | `es_valida` | `placa_normalizada` | `provincia` | `tipo_servicio` | Contenido Clave en `mensaje` |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `"PBX-1234"` | `True` | `"PBX-1234"` | `"Pichincha"` | `"Particular / Privado"` | `"Placa válida para la provincia de Pichincha..."` |
| `"ABC1234"` | `True` | `"ABC-1234"` | `"Azuay"` | `"Particular / Privado"` | `"Placa válida para la provincia de Azuay..."` |
| `"gyb 4567"` | `True` | `"GYB-4567"` | `"Guayas"` | `"Particular / Privado"` | `"Placa válida para la provincia de Guayas..."` |
| `"PAA-1234"` | `True` | `"PAA-1234"` | `"Pichincha"` | `"Público / Comercial..."` | `"Placa válida para la provincia de Pichincha..."` |
| `"PEA-1234"` | `True` | `"PEA-1234"` | `"Pichincha"` | `"Gubernamental..."` | `"Placa válida para la provincia de Pichincha..."` |
| `"DFG-1234"` | `False` | `None` o `"DFG-1234"` | `None` | `None` | `"no corresponde a ninguna provincia del Ecuador"` |
| `"PBX-123"` | `False` | `"PBX-123"` | `None` | `None` | `"formato antiguo"` / `"3 letras y 4 números"` |
| `"PBX-12@4"` | `False` | `None` | `None` | `None` | `"caracteres especiales o símbolos"` |
| `""` o `"   "` | `False` | `None` | `None` | `None` | `"vacía"` |
| `None` | `False` | `None` | `None` | `None` | `"nula (None)"` |
| `1234567` | `False` | `None` | `None` | `None` | `"Tipo de dato no soportado"` |
