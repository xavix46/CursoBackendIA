Sistema de control de inventario simple.

## Entidades
- Usuario: email (único), contraseña (nunca expuesta en respuestas).
- Producto: nombre, cantidad (entero, >= 0), cantidad_minima (entero, >= 0), pertenece a un usuario.

## Reglas de negocio
- La cantidad de un producto nunca puede ser negativa.
- Al registrar o ajustar un producto (por ejemplo, al restar stock por una venta), la cantidad resultante NO puede quedar por debajo de la `cantidad_minima` definida para ese producto. Si se intenta, la operación debe ser rechazada con un error de negocio claro.
- Un usuario solo puede ver, crear o modificar productos propios; nunca los de otro usuario, sin importar qué identificador se pase en la solicitud.

## Contrato de la API (REST)

| Método | Ruta | Auth | Request | Éxito | Errores esperados |
|---|---|---|---|---|---|
| POST | /usuarios/ | No | email, password | 201 Usuario | 400 email duplicado, 422 validación |
| POST | /usuarios/token | No | username, password (form) | 200 token JWT | 401 credenciales inválidas |
| POST | /productos/ | Sí | nombre, cantidad, cantidad_minima | 201 Producto | 400 cantidad menor a mínima, 401, 422 |
| GET | /productos/ | Sí | query: skip, limit | 200 lista | 401, 422 |
| PATCH | /productos/{id}/ajustar | Sí | ajuste (entero, ej. -5 o +10) | 200 Producto | 400 baja del mínimo definido, 401, 403 o 404 si no es dueño, 422 |

## Contrato equivalente por MCP
- Tool `crear_producto(nombre, cantidad, cantidad_minima)`: mismo comportamiento y reglas que POST /productos/.
- Tool `ajustar_stock(producto_id, ajuste)`: mismo comportamiento y reglas que PATCH /productos/{id}/ajustar, devolviendo el producto actualizado o un error de negocio estructurado si baja del mínimo.
- Tool `listar_productos(skip=0, limit=20)`: mismo comportamiento que GET /productos/.
- Todas las tools operan siempre sobre el usuario autenticado de la sesión MCP (identidad resuelta desde el token verificado cuando el transporte es streamable-http; usuario demo de .env solo como fallback para stdio).

## Casos de error explícitos que deben tener test
1. Crear un producto donde la cantidad inicial es menor a la cantidad mínima.
2. Ajustar el stock restando una cantidad que deje el total por debajo de la cantidad mínima definida para ese producto.
3. Crear un producto o ajustar stock con valores negativos no permitidos (ej. cantidad_minima < 0).
4. Listar, crear o ajustar productos sin token → 401.
5. Intentar ajustar el stock de un producto de otro usuario pasando su ID manualmente → debe devolver 403 o 404, nunca actualizarlo.