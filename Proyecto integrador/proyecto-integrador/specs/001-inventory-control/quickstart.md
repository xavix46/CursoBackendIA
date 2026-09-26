# Guía de Inicio Rápido y Validación: Control de Inventario

Esta guía describe los pasos para instalar dependencias, levantar los servicios (API REST y servidor MCP) y ejecutar los escenarios de prueba automatizada y validación manual de extremo a extremo.

---

## 1. Prerrequisitos y Configuración Inicial

- **Python**: 3.12 o superior (compatible con Python 3.14).
- **Gestor de paquetes**: `uv` (recomendado) o `pip`.

### Paso 1: Configurar variables de entorno
Copiar `.env.example` a `.env`:
```bash
cp .env.example .env
```

Variables clave requeridas en `.env`:
```ini
DATABASE_URL=sqlite:///./inventario.db
SECRET_KEY=clave_secreta_super_segura_para_jwt
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
MCP_DEMO_USER_EMAIL=usuario_demo@ejemplo.com
```

### Paso 2: Instalar dependencias
```bash
uv sync
```
*(o alternativamente: `pip install -e .`)*

---

## 2. Ejecución de Servicios

### 2.1. Iniciar la API REST
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- Documentación interactiva Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
- Especificación OpenAPI: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

### 2.2. Iniciar el Servidor MCP

- **Modo Local (stdio)**:
  ```bash
  python -m app.mcp.server
  ```
- **Inspección Interactiva con MCP Inspector**:
  ```bash
  npx @modelcontextprotocol/inspector uv run python -m app.mcp.server
  ```

---

## 3. Ejecución de Pruebas Automatizadas

Ejecutar la suite completa con cobertura y detalle:
```bash
pytest -v
```

Verificar que se ejecuten y aprueben los 5 casos de error críticos:
```bash
pytest tests/test_productos.py -k "error" -v
```

---

## 4. Escenario de Validación Extremo a Extremo (REST)

### Escenario 1: Registro y Obtención de Token
```bash
# 1. Registrar usuario A
curl -X POST http://localhost:8000/usuarios/ \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@ejemplo.com", "password": "Password123!"}'

# 2. Iniciar sesión y obtener token
TOKEN_ALICE=$(curl -s -X POST http://localhost:8000/usuarios/token \
  -d "username=alice@ejemplo.com&password=Password123!" | jq -r .access_token)
```

### Escenario 2: Crear Producto Válido vs Rechazo por Debajo del Mínimo
```bash
# Aprobado: Crear con cantidad >= cantidad_minima (10 >= 5) -> 201 Created
curl -i -X POST http://localhost:8000/productos/ \
  -H "Authorization: Bearer $TOKEN_ALICE" \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Teclado Mecánico", "cantidad": 10, "cantidad_minima": 5}'

# Caso de Error 1: Crear con cantidad < cantidad_minima (3 < 5) -> 400 Bad Request
curl -i -X POST http://localhost:8000/productos/ \
  -H "Authorization: Bearer $TOKEN_ALICE" \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Mouse Gamer", "cantidad": 3, "cantidad_minima": 5}'
```

### Escenario 3: Ajuste de Stock Válido vs Rechazo por Romper Umbral
```bash
# Aprobado: Reducir stock (-3 unidades, de 10 a 7, >= 5) -> 200 OK
curl -i -X PATCH http://localhost:8000/productos/1/ajustar \
  -H "Authorization: Bearer $TOKEN_ALICE" \
  -H "Content-Type: application/json" \
  -d '{"ajuste": -3}'

# Caso de Error 2: Reducción excesiva (-4 unidades, de 7 a 3, < 5) -> 400 Bad Request
curl -i -X PATCH http://localhost:8000/productos/1/ajustar \
  -H "Authorization: Bearer $TOKEN_ALICE" \
  -H "Content-Type: application/json" \
  -d '{"ajuste": -4}'
```

### Escenario 4: Aislamiento Multi-usuario (Caso de Error 5)
```bash
# 1. Registrar y autenticar usuario B
curl -X POST http://localhost:8000/usuarios/ \
  -H "Content-Type: application/json" \
  -d '{"email": "bob@ejemplo.com", "password": "Password123!"}'

TOKEN_BOB=$(curl -s -X POST http://localhost:8000/usuarios/token \
  -d "username=bob@ejemplo.com&password=Password123!" | jq -r .access_token)

# Intentar modificar el producto de Alice (ID 1) usando el token de Bob -> 403 Forbidden
curl -i -X PATCH http://localhost:8000/productos/1/ajustar \
  -H "Authorization: Bearer $TOKEN_BOB" \
  -H "Content-Type: application/json" \
  -d '{"ajuste": 5}'
```
