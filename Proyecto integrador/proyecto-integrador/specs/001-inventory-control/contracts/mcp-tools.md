# Contrato de Herramientas MCP: Control de Inventario

Especificación formal de las herramientas MCP (Model Context Protocol) expuestas para agentes de Inteligencia Artificial.

---

## 1. Contexto de Autenticación y Sesión MCP

Todas las herramientas operan bajo el contexto del usuario autenticado:
- **Transporte `streamable-http` (o HTTP/SSE)**: La identidad se extrae y verifica desde el token Bearer incluido en los encabezados HTTP de la solicitud o sesión.
- **Transporte `stdio`**: Se resuelve la identidad a través de la variable de entorno `MCP_DEMO_USER_EMAIL` definida en la configuración del entorno local.
- Si no es posible autenticar al usuario, las herramientas retornan:
  ```json
  {
    "status": "error",
    "detail": "Sesión no autenticada o token no provisto."
  }
  ```

---

## 2. Herramientas Disponibles

### 2.1. Herramienta: `crear_producto`

Registra un nuevo producto en el catálogo del usuario autenticado.

- **Nombre**: `crear_producto`
- **Descripción**: `Registra un nuevo producto en el inventario con su nombre, cantidad inicial y umbral de cantidad mínima.`
- **Parámetros de entrada**:
  ```json
  {
    "type": "object",
    "properties": {
      "nombre": {
        "type": "string",
        "description": "Nombre identificador del producto (único para el usuario)"
      },
      "cantidad": {
        "type": "integer",
        "minimum": 0,
        "description": "Existencias iniciales en stock (debe ser >= cantidad_minima)"
      },
      "cantidad_minima": {
        "type": "integer",
        "minimum": 0,
        "description": "Cantidad mínima permitida de seguridad en inventario"
      }
    },
    "required": ["nombre", "cantidad", "cantidad_minima"]
  }
  ```
- **Respuesta de Éxito**:
  ```json
  {
    "status": "success",
    "data": {
      "id": 1,
      "usuario_id": 1,
      "nombre": "Mouse Inalámbrico",
      "cantidad": 20,
      "cantidad_minima": 5,
      "created_at": "2026-09-26T16:00:00Z"
    }
  }
  ```
- **Respuesta de Error de Negocio**:
  ```json
  {
    "status": "error",
    "detail": "La cantidad inicial (3) no puede ser menor a la cantidad mínima (5)."
  }
  ```

---

### 2.2. Herramienta: `ajustar_stock`

Modifica las existencias de un producto propio sumando o restando unidades.

- **Nombre**: `ajustar_stock`
- **Descripción**: `Ajusta el inventario de un producto propio mediante un valor entero positivo o negativo, garantizando que el stock resultante no quede por debajo de su cantidad mínima.`
- **Parámetros de entrada**:
  ```json
  {
    "type": "object",
    "properties": {
      "producto_id": {
        "type": "integer",
        "description": "Identificador único del producto a modificar"
      },
      "ajuste": {
        "type": "integer",
        "description": "Número de unidades a incrementar (positivo) o decrementar (negativo), ej. -5 o +10"
      }
    },
    "required": ["producto_id", "ajuste"]
  }
  ```
- **Respuesta de Éxito**:
  ```json
  {
    "status": "success",
    "data": {
      "id": 1,
      "usuario_id": 1,
      "nombre": "Mouse Inalámbrico",
      "cantidad": 15,
      "cantidad_minima": 5,
      "updated_at": "2026-09-26T16:10:00Z"
    }
  }
  ```
- **Respuestas de Error de Negocio**:
  - *Violación de cantidad mínima*:
    ```json
    {
      "status": "error",
      "detail": "Operación rechazada: La cantidad resultante (3) quedaría por debajo del mínimo permitido (5)."
    }
    ```
  - *Producto ajeno o no existente*:
    ```json
    {
      "status": "error",
      "detail": "No tiene permisos para modificar este producto o no existe."
    }
    ```

---

### 2.3. Herramienta: `listar_productos`

Consulta los productos pertenecientes al usuario actual de forma paginada.

- **Nombre**: `listar_productos`
- **Descripción**: `Obtiene la lista de productos pertenecientes al usuario autenticado actual con paginación.`
- **Parámetros de entrada**:
  ```json
  {
    "type": "object",
    "properties": {
      "skip": {
        "type": "integer",
        "default": 0,
        "minimum": 0,
        "description": "Número de registros a omitir para paginación"
      },
      "limit": {
        "type": "integer",
        "default": 20,
        "minimum": 1,
        "maximum": 100,
        "description": "Cantidad máxima de productos a retornar"
      }
    }
  }
  ```
- **Respuesta de Éxito**:
  ```json
  {
    "status": "success",
    "count": 1,
    "data": [
      {
        "id": 1,
        "usuario_id": 1,
        "nombre": "Mouse Inalámbrico",
        "cantidad": 15,
        "cantidad_minima": 5,
        "created_at": "2026-09-26T16:00:00Z"
      }
    ]
  }
  ```
