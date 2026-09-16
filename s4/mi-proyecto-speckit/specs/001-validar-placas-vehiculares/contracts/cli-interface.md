# Contract: CLI Interface (`validador-placa`)

**Feature**: `001-validar-placas-vehiculares`  
**Date**: 2026-09-16  
**Status**: Formal Contract  

---

## 1. Propósito

Permitir que operadores o scripts de automatización validen placas vehiculares directamente desde la terminal utilizando el intérprete de Python gestionado por `uv`.

---

## 2. Invocación y Parámetros

```bash
uv run python -m validador_placa [PLACAS...] [--json]
```

### Argumentos Posicionales
- `PLACAS` (cero o más argumentos): Lista de placas vehiculares a validar separadas por espacio.
  - Si no se proporcionan argumentos, se ejecuta una demostración con un conjunto de placas de prueba predefinidas (casos válidos, casos inválidos y casos borde).

### Opciones y Flags
- `--json`: (Opcional) Si se especifica, la salida en `stdout` se emite como un arreglo de objetos JSON estructurados para consumo por otras herramientas.

---

## 3. Formato de Salida

### 3.1 Salida Estándar (Modo Humano / Texto)

```text
=================================================================
  VALIDADOR DE PLACAS VEHICULARES (ANT - ECUADOR)  
=================================================================

Entrada: 'PBX-1234'
[VÁLIDA] Placa válida para la provincia de Pichincha (Particular / Privado).
  - Placa normalizada: PBX-1234
  - Provincia: Pichincha
  - Tipo de servicio: Particular / Privado
-----------------------------------------------------------------
```

### 3.2 Salida Estructurada (Modo `--json`)

```json
[
  {
    "es_valida": true,
    "placa_original": "PBX-1234",
    "placa_normalizada": "PBX-1234",
    "provincia": "Pichincha",
    "tipo_servicio": "Particular / Privado",
    "mensaje": "Placa válida para la provincia de Pichincha (Particular / Privado).",
    "detalles": {
      "provincia": "Pichincha",
      "codigo_provincia": "P",
      "segunda_letra": "B",
      "tercera_letra": "X",
      "correlativo_numerico": "1234",
      "servicio": "Particular / Privado"
    }
  }
]
```

---

## 4. Códigos de Salida del Proceso (`Exit Codes`)

- `0`: Todas las placas procesadas fueron evaluadas correctamente (independientemente de si individualmente resultaron válidas o inválidas según negocio).
- `1`: Error fatal de ejecución (error interno no controlado).
