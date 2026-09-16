# Quickstart: Validador de Formato de Placa Vehicular (ANT Ecuador)

**Feature**: `001-validar-placas-vehiculares`  
**Date**: 2026-09-16  
**Status**: Ready for Validation  

Esta guía describe cómo validar de extremo a extremo que el validador de placas cumple con todas las especificaciones y contratos definidos.

---

## 1. Requisitos Previos

- Python >= 3.14 instalado en el sistema.
- Gestor de paquetes y entornos `uv` instalado y disponible en el `PATH`.
- Terminal abierta en el directorio de trabajo del proyecto o en la raíz del repositorio.

Verificar el entorno con:
```bash
uv --version
python --version
```

---

## 2. Ejecución de la Suite de Pruebas Unitarias

Para comprobar exhaustivamente todos los requerimientos funcionales (FR-001 a FR-011) y casos borde descritos en [spec.md](./spec.md):

```bash
uv run python -m unittest tests/unit/test_validador_placa.py -v
```

### Resultado Esperado
- Ejecución de todas las pruebas unitarias sin fallos (`Ran X tests in ... OK`).
- Casos validados:
  1. Placas estándar con guion, sin separador y con espacios.
  2. Detección precisa de las 24 provincias reconocidas por la ANT.
  3. Detección de categorías de servicio (público, comercial, gubernamental, GAD, oficial, particular).
  4. Rechazo controlado de formato antiguo de 3 números.
  5. Rechazo de letras no provinciales (como `D` y `F`).
  6. Manejo seguro de entradas vacías, `None` y caracteres especiales.

---

## 3. Demostración en Línea de Comandos (CLI)

### 3.1 Ejecución Interactiva con Placas Específicas

Validar una placa particular, una pública y una con error:

```bash
uv run python -m src.validador_placa PBX-1234 GYA-4567 DFG-1234
```

### Salida Esperada:
- `PBX-1234`: Válida | Pichincha | Particular / Privado.
- `GYA-4567`: Válida | Guayas | Público / Comercial.
- `DFG-1234`: Inválida | Informa que la letra 'D' no corresponde a una provincia de la ANT.

### 3.2 Ejecución en Modo Demostración por Defecto

```bash
uv run python -m src.validador_placa
```

Ejecutará una batería completa de pruebas interactivas en consola demostrando las distintas ramas de validación.

---

## 4. Uso Programático como Librería Python

Consumo dentro de cualquier servicio del backend:

```python
from src.validador_placa import validar_placa

resultado = validar_placa("pbx 1234")

if resultado.es_valida:
    print(f"Placa válida: {resultado.placa_normalizada} ({resultado.provincia})")
else:
    print(f"Rechazada: {resultado.mensaje}")
```

Para mayor detalle de tipos y estructuras, consultar:
- [Data Model](./data-model.md)
- [Python API Contract](./contracts/python-api.md)
- [CLI Contract](./contracts/cli-interface.md)
