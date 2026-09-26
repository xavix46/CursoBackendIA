# Research & Technical Decisions: Sistema de Control de Inventario

Este documento consolida las decisiones de arquitectura, diseño técnico y mejores prácticas evaluadas para la implementación del sistema de inventario.

---

## 1. Framework Web y Servidor HTTP

- **Decisión**: Utilizar **FastAPI** montado sobre **Uvicorn** como servidor ASGI.
- **Justificación**:
  - Excelente rendimiento asíncrono y soporte nativo para esquemas de validación mediante Pydantic v2.
  - Generación automática de especificaciones OpenAPI y documentación Swagger interactiva.
  - Facilidad para definir dependencias inyectables (`Depends`) para autenticación y sesiones de base de datos.
- **Alternativas consideradas**:
  - *Flask*: Descartado por requerir múltiples extensiones de terceros para validación, async y OpenAPI.
  - *Django / DRF*: Descartado por excesiva sobrecarga arquitectónica para un servicio enfocado y ligero.

---

## 2. Persistencia y Manejo de Concurrencia en Stock

- **Decisión**: **SQLAlchemy 2.0** con base de datos relacional (SQLite por defecto para desarrollo/testing, configurable a PostgreSQL vía `.env`).
- **Justificación**:
  - La restricción de unicidad compuesta `(usuario_id, nombre)` y las comprobaciones `cantidad >= cantidad_minima >= 0` se garantizan tanto a nivel de modelo como mediante `CheckConstraint` y `UniqueConstraint` en DDL.
  - Para ajustes de stock concurrentes, se utiliza una actualización atómica en SQL o una transacción aislada:
    ```sql
    UPDATE productos
    SET cantidad = cantidad + :ajuste
    WHERE id = :id AND usuario_id = :usuario_id AND (cantidad + :ajuste) >= cantidad_minima
    ```
    Si el número de filas afectadas es 0, se evalúa si el producto no existe/no pertenece al usuario (403 Forbidden) o si el ajuste violaba la cantidad mínima (400 Bad Request).
- **Alternativas consideradas**:
  - *Ajuste en memoria (leer -> sumar/restar en Python -> guardar)*: Descartado porque es propenso a condiciones de carrera (race conditions) bajo solicitudes simultáneas.
  - *Bloqueo optimista con columna de versión*: Descartado en v1 por agregar complejidad sin aportar ventajas sobre el `UPDATE` atómico condicional.

---

## 3. Autenticación, Seguridad y Aislamiento Multi-usuario

- **Decisión**: Autenticación basada en **JWT (JSON Web Tokens)** mediante `PyJWT`, hashing de contraseñas con `bcrypt` (o `passlib[bcrypt]`), y esquema `OAuth2PasswordBearer`.
- **Justificación**:
  - Estándar de la industria, sin estado (stateless), ideal para APIs REST y sesiones HTTP en MCP.
  - Las contraseñas nunca se persisten en texto plano ni se incluyen en los esquemas de respuesta Pydantic (`exclude=True` / schema dedicado `UserRead`).
  - Todas las consultas y mutaciones de productos filtran estrictamente por `usuario_id = current_user.id`.
  - Intentos de acceder o modificar IDs que pertenezcan a otros usuarios responden determinísticamente con `403 Forbidden`.
- **Alternativas consideradas**:
  - *Sesiones con cookies*: Descartado por ser menos amigable para clientes API móviles y agentes de IA MCP.
  - *API Keys estáticas*: Descartado para usuarios finales; no permite autenticación multi-usuario dinámica con login de formulario.

---

## 4. Arquitectura del Servidor MCP (Model Context Protocol)

- **Decisión**: Implementar el servidor MCP utilizando el SDK oficial **`mcp`** para Python (utilizando `FastMCP` o servidor estándar `mcp.server`).
- **Justificación**:
  - Soporta transporte dual: `streamable-http` (o HTTP/SSE) para clientes remotos y `stdio` para ejecución local por asistentes de línea de comandos.
  - En `streamable-http`, el contexto de usuario se resuelve inspeccionando los headers de autorización de la conexión o solicitud.
  - En `stdio`, se utiliza un usuario fallback configurado mediante la variable de entorno `MCP_DEMO_USER_EMAIL` asegurando operatividad inmediata en desarrollo.
  - Las herramientas invocan la misma capa de servicios de dominio que los endpoints REST, garantizando paridad total de reglas de negocio.
- **Alternativas consideradas**:
  - *Crear un script independiente de herramientas*: Descartado para evitar duplicar lógica de negocio y divergencias en validaciones.

---

## 5. Formato y Estrategia de Manejo de Errores

- **Decisión**:
  - **REST API**: Retorno de códigos de estado HTTP estándar (201, 200, 400, 401, 403, 422) con cuerpo `{ "detail": "<mensaje descriptivo>" }`.
  - **MCP Tools**: Retorno de payload JSON estructurado `{ "status": "error", "detail": "<mensaje descriptivo>" }` dentro del contenido de texto de la respuesta sin interrumpir la sesión MCP.
- **Justificación**:
  - Alineado con la decisión de clarificación aceptada en `/speckit-clarify` (Opción B para MCP y código 403 para violaciones de tenencia).
  - Permite a los agentes de IA recibir feedback comprensible y ejecutar correcciones en su flujo de razonamiento.
- **Alternativas consideradas**:
  - *Levantar excepciones no controladas en MCP*: Descartado porque rompe el flujo conversacional del asistente.

---

## 6. Estrategia de Pruebas Automatizadas

- **Decisión**: Suite de pruebas con **pytest** y **httpx.AsyncClient / TestClient**.
- **Justificación**:
  - Pruebas unitarias de modelos y servicios de dominio.
  - Pruebas de integración sobre los endpoints REST cubriendo obligatoriamente los 5 casos de error críticos definidos en los requisitos:
    1. Creación con cantidad inicial menor a mínima.
    2. Ajuste restando stock por debajo de cantidad mínima.
    3. Creación o ajuste con valores negativos inválidos.
    4. Acceso no autenticado (401).
    5. Ajuste sobre producto ajeno (403).
  - Pruebas funcionales sobre las herramientas MCP invocadas programáticamente.
