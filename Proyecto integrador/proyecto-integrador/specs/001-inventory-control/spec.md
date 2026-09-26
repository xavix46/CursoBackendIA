# Feature Specification: Sistema de Control de Inventario Simple

**Feature Branch**: `001-inventory-control`

**Created**: 2026-09-26

**Status**: Draft

**Input**: User description: "Sistema de control de inventario simple. Entidades: Usuario (email único, contraseña nunca expuesta), Producto (nombre, cantidad >= 0, cantidad_minima >= 0, pertenece a usuario). Reglas: cantidad nunca negativa, cantidad resultante nunca menor a cantidad_minima, aislamiento estricto por usuario. Contrato REST y MCP con herramientas crear_producto, ajustar_stock y listar_productos. Casos de error explícitos testeados."

## Clarifications

### Session 2026-09-26

- Q: ¿Qué código de estado HTTP exacto debe responder la API cuando un usuario autenticado intenta acceder o modificar un producto que pertenece a otro usuario? → A: Código 403 Forbidden (indica explícitamente que no tiene permisos sobre el producto ajeno existente).
- Q: ¿Debe ser único el nombre de un producto dentro del catálogo de un mismo usuario, o se permiten nombres duplicados diferenciados solo por ID? → A: Único por usuario (el nombre no puede repetirse dentro de la cuenta del mismo usuario; si se intenta crear con un nombre existente, se rechaza con código 400).
- Q: ¿Cómo deben las herramientas MCP reportar los errores de negocio (como intentar un ajuste que deje el stock por debajo del mínimo)? → A: Respuesta JSON estructurada (retornar un objeto JSON estructurado `{ "status": "error", "detail": "<mensaje>" }` informando el error de negocio).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Registro y autenticación de usuarios (Priority: P1)

Como nuevo usuario del sistema, quiero registrar una cuenta con mi correo electrónico y contraseña, e iniciar sesión para obtener un token de acceso seguro que me permita gestionar mi inventario privado.

**Why this priority**: Es la base del aislamiento y seguridad del sistema. Sin autenticación y gestión de identidad, no es posible garantizar que cada usuario acceda exclusivamente a su propio inventario.

**Independent Test**: Puede probarse registrando un usuario con credenciales válidas, verificando que la contraseña no se exponga en la respuesta, y realizando login para obtener un token de acceso utilizable.

**Acceptance Scenarios**:

1. **Given** un correo electrónico no registrado previamente y una contraseña válida, **When** el usuario solicita el registro de su cuenta, **Then** el sistema crea la cuenta con éxito, devuelve código 201 y los datos del usuario sin revelar la contraseña.
2. **Given** un correo electrónico que ya existe en el sistema, **When** se intenta registrar nuevamente, **Then** el sistema rechaza la solicitud devolviendo código 400 informando duplicidad de correo.
3. **Given** credenciales correctas de un usuario registrado, **When** solicita inicio de sesión, **Then** el sistema emite un token de acceso válido con código 200.
4. **Given** credenciales incorrectas o inexistentes, **When** solicita inicio de sesión, **Then** el sistema deniega el acceso devolviendo código 401.

---

### User Story 2 - Creación y registro de productos con control de umbral mínimo (Priority: P1)

Como usuario autenticado, quiero registrar nuevos productos en mi inventario indicando su nombre, cantidad inicial y una cantidad mínima de seguridad, garantizando que el stock inicial cumpla con dicho umbral y que no existan nombres duplicados en mi catálogo.

**Why this priority**: Permite poblar el catálogo de productos con sus políticas de inventario mínimas, salvaguardando la integridad de los datos desde el momento de su alta.

**Independent Test**: Puede probarse creando productos con cantidades válidas y verificando su persistencia asociada al usuario, así como intentando crear productos con cantidad inicial menor a la mínima o con nombres duplicados para verificar su rechazo.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado y datos válidos donde la cantidad inicial es mayor o igual a la cantidad mínima y el nombre no existe aún en su catálogo, **When** solicita crear un nuevo producto, **Then** el sistema registra el producto asociado al usuario y devuelve el producto creado con código 201.
2. **Given** un usuario autenticado y una solicitud donde la cantidad inicial es estrictamente menor a la cantidad mínima definida, **When** intenta crear el producto, **Then** el sistema rechaza la operación con código 400 y un mensaje de negocio claro.
3. **Given** un usuario autenticado que ya tiene un producto registrado con un nombre específico, **When** intenta crear otro producto con ese mismo nombre, **Then** el sistema rechaza la solicitud con código 400 indicando nombre duplicado.
4. **Given** datos con valores numéricos negativos (ej. cantidad_minima < 0 o cantidad < 0), **When** el usuario intenta crear el producto, **Then** el sistema rechaza la solicitud indicando error de validación (código 422 o 400).
5. **Given** una solicitud sin token de autenticación o con token inválido, **When** intenta crear un producto, **Then** el sistema deniega el acceso con código 401.

---

### User Story 3 - Ajuste de stock con validación de umbral mínimo y aislamiento (Priority: P1)

Como usuario autenticado, quiero ajustar las existencias de un producto propio (sumando o restando unidades) asegurando que el stock resultante nunca quede por debajo de la cantidad mínima configurada ni sea negativo.

**Why this priority**: Es la operación central del control de inventario (ventas, reposiciones, mermas). Debe prevenir automáticamente el desabastecimiento por debajo del umbral pactado.

**Independent Test**: Puede probarse ejecutando ajustes positivos (aumento) y ajustes negativos (reducción que respete el mínimo), y comprobando que reducciones excesivas sean abortadas sin alterar el stock.

**Acceptance Scenarios**:

1. **Given** un producto existente con cantidad 20 y cantidad mínima 5 perteneciente al usuario autenticado, **When** el usuario aplica un ajuste de -10, **Then** el sistema actualiza la cantidad a 10 y devuelve el producto actualizado con código 200.
2. **Given** un producto con cantidad 10 y cantidad mínima 5 perteneciente al usuario autenticado, **When** el usuario intenta aplicar un ajuste de -8 (resultando en 2, menor al mínimo), **Then** el sistema rechaza el ajuste con código 400, no modifica el stock y devuelve un error explicativo.
3. **Given** un producto perteneciente al usuario A, **When** el usuario B intenta ajustar el stock pasando el identificador del producto de A, **Then** el sistema rechaza la operación con código 403 Forbidden, impidiendo cualquier modificación.
4. **Given** una solicitud de ajuste sin credenciales de autenticación válidas, **When** se envía la petición, **Then** el sistema devuelve código 401.

---

### User Story 4 - Consulta paginada del catálogo de inventario propio (Priority: P2)

Como usuario autenticado, quiero consultar la lista de mis productos de forma paginada para supervisar el estado de mi inventario sin interferir con los productos de otros usuarios.

**Why this priority**: Ofrece visibilidad operativa del inventario para la toma de decisiones, garantizando el aislamiento de datos por usuario.

**Independent Test**: Puede probarse creando productos con dos usuarios distintos y validando que cada uno únicamente liste sus propios ítems, respetando los parámetros de paginación (`skip` y `limit`).

**Acceptance Scenarios**:

1. **Given** un usuario autenticado con productos registrados, **When** solicita el listado de productos con parámetros de paginación, **Then** el sistema devuelve la lista correspondiente a su cuenta con código 200.
2. **Given** múltiples usuarios en la plataforma con productos creados, **When** cualquiera de ellos solicita el listado, **Then** la respuesta contiene únicamente productos creados por dicho usuario solicitante.
3. **Given** una solicitud de listado sin token de autenticación, **When** se efectúa la petición, **Then** el sistema responde con código 401.

---

### User Story 5 - Operaciones de inventario mediante herramientas MCP (Priority: P2)

Como asistente inteligente o agente de IA conectado vía el protocolo Model Context Protocol (MCP), quiero invocar herramientas estructuradas para crear productos, ajustar stock y listar productos bajo el contexto del usuario autenticado.

**Why this priority**: Expone las capacidades del sistema a flujos agenticos y de automatización IA mediante un protocolo estándar de interoperabilidad.

**Independent Test**: Puede probarse conectando un cliente MCP y ejecutando las herramientas `crear_producto`, `ajustar_stock` y `listar_productos`, verificando que se apliquen las mismas validaciones de negocio y resolución de identidad.

**Acceptance Scenarios**:

1. **Given** una sesión MCP con autenticación resuelta (vía token en streamable-http o usuario configurado en stdio), **When** el asistente invoca la herramienta `crear_producto(nombre, cantidad, cantidad_minima)`, **Then** se crea el producto aplicando las mismas reglas de negocio que la API REST y se retorna el resultado.
2. **Given** una herramienta `ajustar_stock(producto_id, ajuste)` invocada con un ajuste que dejaría el stock por debajo del mínimo, **When** se ejecuta la llamada, **Then** la herramienta retorna una respuesta JSON estructurada `{ "status": "error", "detail": "<mensaje>" }` informando el rechazo de la operación sin alterar el stock.
3. **Given** una llamada a `listar_productos(skip, limit)`, **When** se ejecuta, **Then** devuelve únicamente los productos del usuario de la sesión MCP.

---

### Edge Cases

- **Cantidad inicial menor al mínimo**: Intentar crear un producto donde `cantidad < cantidad_minima` debe abortar la transacción inmediatamente con código 400.
- **Nombre de producto duplicado por usuario**: Si un usuario intenta crear un producto cuyo nombre ya existe en su catálogo personal, la operación debe ser rechazada con código 400.
- **Ajuste negativo excesivo**: Al restar stock mediante ajuste (`ajuste < 0`), si `cantidad_actual + ajuste < cantidad_minima`, la operación debe ser rechazada sin aplicar cambios parciales.
- **Valores negativos en atributos no permitidos**: Enviar valores negativos en `cantidad`, `cantidad_minima` al crear, o solicitar parámetros de paginación inválidos (`limit <= 0` o `skip < 0`), debe ser rechazado con error de validación (422 o 400).
- **Acceso no autenticado**: Cualquier intento de invocar endpoints o herramientas que requieran autenticación sin token o con credenciales expiradas debe responder unívocamente con 401 Unauthorized.
- **Violación de tenencia / Aislamiento cruzado**: Intentar consultar o modificar un producto especificando el ID de un producto perteneciente a otro usuario debe retornar error de acceso prohibido (código 403 Forbidden), garantizando que no se permita mutación no autorizada.
- **Ajustes simultáneos (Concurrencia)**: Si ocurren dos ajustes simultáneos sobre el mismo producto, cada uno debe validar el stock resultante sobre el estado actualizado para evitar que condiciones de carrera lleven el inventario por debajo del mínimo permitido.
- **Resolución de contexto en MCP**: Si el transporte es streamable-http, la identidad debe provenir obligatoriamente del token validado; el modo fallback local (stdio) solo opera con el usuario demo configurado en el entorno.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE permitir el registro de usuarios mediante dirección de correo electrónico única y contraseña.
- **FR-002**: El sistema DEBE almacenar las contraseñas de forma irreversible y segura, garantizando que nunca sean expuestas en respuestas o registros.
- **FR-003**: El sistema DEBE autenticar usuarios mediante credenciales válidas y emitir un token de acceso estándar (JWT) para autorizar solicitudes subsecuentes.
- **FR-004**: El sistema DEBE restringir todos los endpoints y herramientas de inventario exclusivamente a usuarios con autenticación verificada, respondiendo con código 401 ante solicitudes no autorizadas.
- **FR-005**: El sistema DEBE permitir a un usuario autenticado registrar productos definiendo: nombre (único dentro de la cuenta del usuario), cantidad (entero >= 0) y cantidad mínima (entero >= 0). Si el nombre ya existe para ese usuario, DEBE rechazar la creación con código 400.
- **FR-006**: El sistema DEBE validar obligatoriamente que, al crear un producto, la `cantidad` inicial sea mayor o igual que la `cantidad_minima`; de lo contrario, DEBE rechazar la creación con código 400.
- **FR-007**: El sistema DEBE permitir al usuario autenticado consultar su lista de productos con soporte de paginación (parámetros `skip` y `limit`).
- **FR-008**: El sistema DEBE garantizar el aislamiento total de datos: los usuarios solo pueden visualizar, crear y modificar sus propios productos. Intentos de acceder o modificar recursos ajenos DEBEN responder inequívocamente con código 403 Forbidden.
- **FR-009**: El sistema DEBE permitir ajustar las existencias de un producto propio mediante un valor entero de ajuste (positivo para sumar stock, negativo para restar stock).
- **FR-010**: El sistema DEBE validar en cada operación de ajuste que la cantidad resultante (`cantidad_actual + ajuste`) sea mayor o igual a la `cantidad_minima` configurada para el producto. Si la cantidad resultante fuera inferior al mínimo o resultara negativa, la operación DEBE ser rechazada con código 400 sin modificar los datos.
- **FR-011**: El sistema DEBE exponer herramientas de protocolo MCP (`crear_producto`, `ajustar_stock`, `listar_productos`) que apliquen exactamente las mismas reglas de negocio, validaciones y aislamiento por usuario que los endpoints REST, reportando cualquier error de negocio mediante un payload JSON estructurado `{ "status": "error", "detail": "<mensaje>" }`.
- **FR-012**: El servidor MCP DEBE resolver la identidad del usuario a partir del token verificado cuando el transporte sea streamable-http, y admitir un usuario demo configurado en variables de entorno únicamente como fallback para transporte stdio.

### Key Entities *(include if feature involves data)*

- **Usuario**: Representa la identidad de un operador o cliente en el sistema.
  - Atributos clave: Identificador único, correo electrónico (único en el sistema), credencial segura (hash de contraseña), fecha de registro.
  - Relaciones: Posee cero o más Productos en su catálogo personal.
- **Producto**: Representa un artículo inventariado perteneciente a un usuario específico.
  - Atributos clave: Identificador único, nombre descriptivo (único por usuario), cantidad en existencia (entero >= 0), cantidad mínima de seguridad (entero >= 0), referencia al usuario propietario.
  - Restricciones: El par `(usuario_id, nombre)` es único en el sistema; `cantidad >= cantidad_minima >= 0` en todo momento.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% de las solicitudes que intenten dejar el inventario por debajo de la `cantidad_minima` (tanto en creación como en ajuste de stock) son bloqueadas con mensajes de error explícitos.
- **SC-002**: 100% de aislamiento verificado entre usuarios: ninguna prueba de acceso cruzado entre cuentas permite leer o modificar productos de otro usuario.
- **SC-003**: 100% de las pruebas automatizadas para los 5 casos de error críticos definidos en los requisitos pasan satisfactoriamente.
- **SC-004**: Los usuarios reciben respuesta a sus operaciones de consulta, creación y ajuste en menos de 200 milisegundos en el 95% de los casos bajo carga estándar.
- **SC-005**: 100% de paridad funcional entre la API REST y las herramientas MCP en cuanto a validación de reglas de negocio y restricciones de stock.

## Assumptions

- Las credenciales de acceso se transmiten mediante protocolos de transporte cifrados y seguros.
- Las solicitudes a la API REST autenticadas proporcionan el token de acceso mediante el encabezado estándar `Authorization: Bearer <token>`.
- Las modificaciones a otros atributos del producto (como renombrar o modificar el umbral de `cantidad_minima`) quedan fuera del alcance de esta versión inicial, centrándose exclusivamente en la gestión y ajuste de existencias.
- Las herramientas MCP interactúan con la misma capa de lógica de dominio y persistencia que los controladores REST para garantizar consistencia absoluta.
- En despliegues locales sin servidor HTTP (stdio), se utiliza una variable de entorno para identificar al usuario por defecto con fines de prueba y depuración.
