# Constitución — Proyecto Integrador: Control de Inventario

## Artículo I — Arquitectura en capas
1. `routers/` reciben la solicitud HTTP, delegan al service correspondiente y traducen su resultado (o excepción) a una respuesta HTTP. Un router NUNCA valida reglas de negocio — esa lógica vive en `services/`.
2. `services/` contienen toda la lógica de negocio. Un service NUNCA importa SQLAlchemy, `Session`, ni ningún detalle de persistencia directamente.
3. `repositories/` son la única capa autorizada a leer o escribir en la base de datos. Un repository no contiene reglas de negocio, solo operaciones de persistencia.
4. `utils/` son funciones puras (mismo input → mismo output, sin efectos secundarios), sin importar nada de `services/`, `routers/` ni `repositories/`.
5. `mcp/tools/` NUNCA reimplementan lógica de `services/`. Si una tool de MCP y un router necesitan la misma regla, ambos llaman al mismo service.

## Artículo II — SOLID aplicado (no teórico)
1. **SRP**: cada función de `services/` hace una sola cosa. La validación está separada de la orquestación.
2. **OCP**: agregar una regla nueva se hace agregando un valor a una constante o `Enum`, nunca reescribiendo un `if` ya existente.
3. **DIP**: todo service que necesite un repository lo recibe como parámetro con un valor por defecto (`def ajustar_stock(..., repo=productos_repo)`), nunca lo importa fijo dentro del cuerpo de la función. Esto es innegociable.
4. No se fuerza LSP ni ISP si el proyecto no tiene jerarquías de clases ni interfaces formales.

## Artículo III — Persistencia
1. SQLAlchemy como ORM, Alembic para migraciones. Ninguna sentencia SQL cruda concatenada con strings.
2. SQLite en desarrollo; el código de `database.py` debe funcionar contra Postgres sin tocar `services/` ni `routers/` (usar `connect_args` condicional solo para SQLite).
3. Cada modelo con datos de usuario incluye `usuario_id` como FK. Ninguna consulta de datos de Producto puede omitir el filtro por `usuario_id`.

## Artículo IV — Seguridad (no negociable)
1. Contraseñas: hash con `passlib[bcrypt]`. Nunca se guarda ni se loguea una contraseña en texto plano.
2. Autenticación: OAuth2 password flow + JWT firmado con HS256. `ACCESS_TOKEN_EXPIRE_MINUTES` configurable, nunca infinito.
3. `SECRET_KEY` y `DATABASE_URL` viven solo en `.env` (nunca versionado). `.env.example` documenta las variables necesarias sin valores reales.
4. Autorización: el `usuario_id` para filtrar, crear o modificar un Producto SIEMPRE sale del token JWT decodificado (`get_current_user`), NUNCA de un parámetro de la URL, del body, ni de un query param. 
5. Un error no controlado (`Exception` genérica) devuelve `500` con `{"detail": "Error interno del servidor"}`.
6. Toda entrada de usuario se valida con schemas Pydantic antes de llegar a `services/`.

## Artículo V — Diseño de endpoints REST
1. Convención de verbos y códigos: `POST` crea (`201`), `GET` lista/lee (`200`), fallo de autenticación (`401`), recurso no encontrado (`404`), error de validación de schema (`422`), error de regla de negocio conocido (`400`). `403` se reserva para cuando el recurso pertenece a otro usuario y se identifica por `id`.
2. Toda lista paginada expone `skip` y `limit` como query params.
3. Los schemas de entrada y salida son distintos — nunca se expone el modelo de SQLAlchemy directamente.

## Artículo VI — MCP: tools y reutilización
1. Cada tool de MCP llama a una función de `services/`, punto. Ejemplo con Inventario: `ajustar_stock` (tool) y `POST /productos/{id}/ajustar` (router) llaman a la misma función `services/productos.py::ajustar_stock()`.
2. La descripción de cada tool es específica y accionable, nunca genérica.
3. Errores de negocio se devuelven como una estructura clara (`{"error": "..."}`).
4. Si el transporte es `streamable-http` y hay un token verificado, la tool DEBE usar la identidad de ese token.
5. Cualquier tool con efecto destructivo (ej. eliminar un producto) debe pedir confirmación explícita gestionada por el servidor, nunca depender de que el modelo decida preguntar por su cuenta.

## Artículo VII — Testing y cobertura
1. Pirámide de pruebas obligatoria: unitarias (mayoría) → integración → API/E2E (minoría).
2. Tests unitarios de `services/` inyectan un repositorio falso como parámetro — está PROHIBIDO usar `unittest.mock` para esto.
3. Cobertura mínima exigida:
   - 100% de las reglas de negocio explícitas de `spec.md` cubiertas por al menos un test unitario cada una.
   - Cobertura de líneas de `services/` ≥ 90%.
   - Cobertura de líneas del conjunto `services/ + repositories/ + routers/ + utils/` ≥ 70%, medida con `pytest --cov=app --cov-report=term-missing`.
4. Tests de integración corren contra una base de datos real (SQLite en memoria como mínimo).
5. Tests de API usan `app.dependency_overrides` de FastAPI.
6. Toda tool de MCP tiene al menos dos tests: un caso exitoso y un caso de error de negocio.
7. Ninguna tarea de `tasks.md` se considera terminada sin su test correspondiente en verde.

## Artículo VIII — Compatibilidad con el proyecto de referencia
1. `repositories/productos.py` y `repositories/usuarios.py` son módulos con funciones sueltas, no clases. Un repository devuelve estructuras simples (`dict`, o el objeto de dominio ya existente), nunca expone el objeto de sesión de SQLAlchemy al llamador.

## Gobernanza
Esta constitución tiene prioridad sobre cualquier decisión tomada durante `/speckit-implement`. Si el agente necesita desviarse de un artículo, debe señalarlo explícitamente y esperar aprobación antes de continuar, no decidir en silencio.