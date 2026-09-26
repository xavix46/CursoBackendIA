# Contrato de API REST: Control de Inventario

Especificación formal de endpoints, contratos de entrada/salida y códigos de estado HTTP.

---

## 1. Resumen de Endpoints

| Método | Ruta | Autenticación | Request Body | Código Éxito | Códigos de Error |
|---|---|---|---|---|---|
| `POST` | `/usuarios/` | No requerida | JSON: `UserCreate` | `201 Created` | `400 Bad Request`, `422 Unprocessable Entity` |
| `POST` | `/usuarios/token` | No requerida | Form URL-encoded: `OAuth2PasswordRequestForm` | `200 OK` | `401 Unauthorized`, `422 Unprocessable Entity` |
| `POST` | `/productos/` | Requerida (Bearer) | JSON: `ProductoCreate` | `201 Created` | `400 Bad Request`, `401 Unauthorized`, `422 Unprocessable Entity` |
| `GET` | `/productos/` | Requerida (Bearer) | Query params: `skip`, `limit` | `200 OK` | `401 Unauthorized`, `422 Unprocessable Entity` |
| `PATCH` | `/productos/{id}/ajustar` | Requerida (Bearer) | JSON: `StockAjusteRequest` | `200 OK` | `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `422 Unprocessable Entity` |

---

## 2. Definición Detallada de Endpoints

### 2.1. `POST /usuarios/`
Registra un nuevo usuario en la plataforma.

- **Headers**: `Content-Type: application/json`
- **Request Body (`UserCreate`)**:
  ```json
  {
    "email": "usuario@ejemplo.com",
    "password": "Password123!"
  }
  ```
- **Respuestas**:
  - **`201 Created` (`UserResponse`)**:
    ```json
    {
      "id": 1,
      "email": "usuario@ejemplo.com",
      "created_at": "2026-09-26T16:00:00Z"
    }
    ```
    *Nota*: La contraseña nunca se incluye en la respuesta.
  - **`400 Bad Request`**: Si el correo ya existe.
    ```json
    { "detail": "El correo electrónico ya se encuentra registrado." }
    ```
  - **`422 Unprocessable Entity`**: Formato de correo inválido o contraseña vacía.

---

### 2.2. `POST /usuarios/token`
Autentica al usuario y devuelve un token de acceso JWT.

- **Headers**: `Content-Type: application/x-www-form-urlencoded`
- **Request Body (OAuth2)**:
  ```text
  username=usuario@ejemplo.com&password=Password123!
  ```
- **Respuestas**:
  - **`200 OK` (`TokenResponse`)**:
    ```json
    {
      "access_token": "eyJhbGciOi...",
      "token_type": "bearer"
    }
    ```
  - **`401 Unauthorized`**:
    ```json
    { "detail": "Credenciales inválidas." }
    ```

---

### 2.3. `POST /productos/`
Crea un nuevo producto en el catálogo del usuario autenticado.

- **Headers**:
  - `Authorization: Bearer <token>`
  - `Content-Type: application/json`
- **Request Body (`ProductoCreate`)**:
  ```json
  {
    "nombre": "Teclado Mecánico",
    "cantidad": 15,
    "cantidad_minima": 5
  }
  ```
- **Respuestas**:
  - **`201 Created` (`ProductoResponse`)**:
    ```json
    {
      "id": 10,
      "usuario_id": 1,
      "nombre": "Teclado Mecánico",
      "cantidad": 15,
      "cantidad_minima": 5,
      "created_at": "2026-09-26T16:00:00Z",
      "updated_at": "2026-09-26T16:00:00Z"
    }
    ```
  - **`400 Bad Request`**:
    - Si `cantidad < cantidad_minima`:
      ```json
      { "detail": "La cantidad inicial (3) no puede ser menor a la cantidad mínima (5)." }
      ```
    - Si el nombre ya existe para este usuario:
      ```json
      { "detail": "Ya existe un producto con el nombre 'Teclado Mecánico' para este usuario." }
      ```
  - **`401 Unauthorized`**: Token ausente o inválido.
  - **`422 Unprocessable Entity`**: Valores negativos (`cantidad < 0` o `cantidad_minima < 0`).

---

### 2.4. `GET /productos/`
Obtiene la lista paginada de productos pertenecientes exclusivamente al usuario autenticado.

- **Headers**: `Authorization: Bearer <token>`
- **Query Parameters**:
  - `skip` (int, default=0, ge=0)
  - `limit` (int, default=20, ge=1, le=100)
- **Respuestas**:
  - **`200 OK` (`list[ProductoResponse]`)**:
    ```json
    [
      {
        "id": 10,
        "usuario_id": 1,
        "nombre": "Teclado Mecánico",
        "cantidad": 15,
        "cantidad_minima": 5,
        "created_at": "2026-09-26T16:00:00Z",
        "updated_at": "2026-09-26T16:00:00Z"
      }
    ]
    ```
  - **`401 Unauthorized`**: Token ausente o expirado.

---

### 2.5. `PATCH /productos/{id}/ajustar`
Ajusta incremental o decrementalmente el stock de un producto propio.

- **Headers**:
  - `Authorization: Bearer <token>`
  - `Content-Type: application/json`
- **Path Parameters**: `id` (int, ID del producto)
- **Request Body (`StockAjusteRequest`)**:
  ```json
  {
    "ajuste": -5
  }
  ```
- **Respuestas**:
  - **`200 OK` (`ProductoResponse`)**:
    ```json
    {
      "id": 10,
      "usuario_id": 1,
      "nombre": "Teclado Mecánico",
      "cantidad": 10,
      "cantidad_minima": 5,
      "created_at": "2026-09-26T16:00:00Z",
      "updated_at": "2026-09-26T16:05:00Z"
    }
    ```
  - **`400 Bad Request`**: Si el ajuste deja el stock por debajo del umbral mínimo:
    ```json
    { "detail": "La cantidad resultante (4) no puede quedar por debajo de la cantidad mínima (5)." }
    ```
  - **`401 Unauthorized`**: Petición sin token o token expirado.
  - **`403 Forbidden`**: Si el producto con ID `{id}` pertenece a otro usuario.
    ```json
    { "detail": "No tiene permisos para modificar este producto." }
    ```
  - **`404 Not Found`**: Si el ID no existe en el sistema.
  - **`422 Unprocessable Entity`**: Parámetro `ajuste` no entero o mal formateado.
