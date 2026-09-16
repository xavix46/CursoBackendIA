# Research & Technical Decisions: Validador de Formato de Placa Vehicular (ANT Ecuador)

**Feature**: `001-validar-placas-vehiculares`  
**Date**: 2026-09-16  
**Status**: Completed  

---

## 1. Runtime Environment & Package Management

### Decision
Utilizar **Python >= 3.14** gestionado a través de **`uv`**, integrándose armoniosamente con la configuración del proyecto raíz (`pyproject.toml`).

### Rationale
- `uv` proporciona una ejecución de herramientas y resolución de entornos ultrarrápida en entornos de desarrollo modernos.
- El repositorio raíz ya define `requires-python = ">=3.14"` y utiliza `uv_build` / `.venv`, garantizando compatibilidad directa sin configurar intérpretes aislados ni redundantes.
- Ejecución determinista mediante comandos directos (`uv run ...`).

### Alternatives Considered
- *Pipenv / Poetry*: Descartados por requerir herramientas adicionales y no ser el estándar configurado en el repositorio.
- *Entorno virtual manual con `venv` nativo*: Funcional, pero `uv` simplifica la reproducibilidad y sincronización de dependencias de todo el proyecto.

---

## 2. Pila Tecnológica del Módulo (Dependencias y Librerías)

### Decision
Implementar el validador como una librería en **Python puro utilizando exclusivamente la biblioteca estándar** (`re`, `dataclasses`, `typing`, `enum`, `sys`), complementada opcionalmente con `argparse` para la interfaz de línea de comandos (CLI).

### Rationale
- **Cero dependencias externas en tiempo de ejecución**: El parsing de texto, validación de patrones y extracción de metadatos de placas ANT no requiere paquetes de terceros.
- **Portabilidad máxima**: Puede integrarse en cualquier servicio backend (FastAPI, Flask, Django, Azure Functions, microservicios) sin conflictos de versiones.
- **Rendimiento**: Expresiones regulares compiladas (`re.compile`) con estructuras en memoria (`dict`, `set`) ofrecen validaciones en menos de 0.05 milisegundos por placa.

### Alternatives Considered
- *Pydantic / Marshmallow*: Útiles para APIs web, pero añaden overhead innecesario para un validador unitario de formato de placa. Un validador liviano con `@dataclass` permite a los consumidores integrarlo directamente en sus modelos Pydantic o esquemas preferidos sin forzar dependencias.
- *Librerías externas de validación de cadenas (e.g. `validator`)*: No tienen conocimiento de las reglas específicas de la ANT Ecuador (24 provincias, servicios público/gubernamental).

---

## 3. Estrategia de Expresiones Regulares y Normalización

### Decision
Adoptar un flujo de dos fases:
1. **Fase de Sanitización y Normalización**: Limpieza de espacios circundantes (`strip()`), conversión a mayúsculas (`upper()`).
2. **Fase de Análisis y Diagnóstico**:
   - Detección de formato antiguo (3 letras + 3 dígitos) con patrón `^([A-Z]{3})[\s\-]?(\d{3})$` para emitir mensaje informativo diferenciado.
   - Validación del patrón vigente (3 letras + 4 dígitos) con `^([A-Z]{3})[\s\-]?(\d{4})$`.
   - Diagnóstico detallado para entradas que fallen el patrón (conteo de letras vs dígitos, verificación de caracteres extraños).

### Rationale
- Brinda tolerancia a entradas habituales de usuarios (minúsculas, guiones, espacios o cadenas continuas).
- Cumple el criterio de negocio de diferenciar claramente una placa con formato antiguo de un valor completamente erróneo.

### Alternatives Considered
- *Regex única y compleja*: Dificulta dar mensajes de error específicos y amigables al usuario (diferenciar longitud, caracteres ilegales o provincia inválida).

---

## 4. Estructura de Datos para Provincias y Servicios de la ANT

### Decision
Modelar las 24 provincias y los tipos de servicio como diccionarios/mapeos inmutables constantes:
- `PROVINCIAS_ECUADOR: dict[str, str]`: Mapeo O(1) de la primera letra a la provincia oficial (A -> Azuay ... Z -> Zamora Chinchipe). Letras como `D` y `F` no existen en este mapeo.
- `SERVICIOS_SEGUNDA_LETRA: dict[str, str]`: Mapeo de la segunda letra a su categoría (A, U, Z -> Comercial/Público; E -> Gubernamental; M -> GAD; X -> Uso Oficial).

### Rationale
- Acceso en tiempo constante $O(1)$.
- Mantenimiento claro y legible de la normativa de la ANT.

---

## 5. Estrategia de Pruebas Automatizadas

### Decision
Emplear `unittest` (módulo nativo de Python) complementado con soporte para `pytest` vía `uv run pytest` o `uv run python -m unittest`.

### Rationale
- `unittest` no requiere instalar dependencias adicionales y permite ejecutar pruebas en cualquier entorno de CI/CD de inmediato.
- Compatibilidad total con la suite de pruebas exhaustiva que cubre casos normales, los 24 códigos provinciales, casos de servicio, casos borde de la spec y entradas inválidas/maliciosas.
