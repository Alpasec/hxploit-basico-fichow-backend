# Fichow API

## Contexto del proyecto

Fichow es una tienda educativa de chaufa con usuarios, login, JWT en cookie, wallet, productos, carrito, cupones, ordenes, transacciones y panel admin.

La aplicacion esta preparada para talleres de seguridad web. Los endpoints son rutas reales de una tienda y varias vulnerabilidades estan introducidas de forma intencional para que puedan descubrirse con Burp Suite, DevTools o requests manuales.

## Stack

- Python 3.11+
- FastAPI
- SQLAlchemy
- PostgreSQL
- psycopg2-binary
- Pydantic
- pydantic-settings
- python-jose
- passlib/bcrypt
- Uvicorn

## Estructura principal

```txt
app/
  main.py
  config.py
  database.py
  security.py
  startup.py
  seed.py
  models/
  schemas/
  routers/
  services/
  dependencies/
sql/
  schema.sql
  insert.sql
run.py
requirements.txt
render.yaml
```

## Requisitos locales

- Python 3.11+
- PostgreSQL local
- Navegador
- Burp Suite opcional para interceptar requests

## Configuracion local

Crear entorno e instalar dependencias:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Crear `.env`:

```bash
copy .env.example .env
```

Editar en `.env`:

```txt
DATABASE_URL=postgresql+psycopg2://postgres:TU_PASSWORD@localhost:5432/fichow_db
JWT_SECRET_KEY=un_secreto_largo_local
```

Valores utiles para local:

```txt
APP_ENV=development
DEBUG=true
FRONTEND_URL=http://localhost:5173
ALLOWED_ORIGINS=*
AUTO_CREATE_DATABASE=true
AUTO_CREATE_TABLES=true
AUTO_SEED_DATA=true
JWT_COOKIE_SECURE=false
JWT_COOKIE_SAMESITE=lax
```

Levantar backend:

```bash
python run.py
```

Al iniciar, si las flags estan activas, la aplicacion crea la base, tablas y datos iniciales. El usuario de PostgreSQL debe tener permiso para crear bases si `AUTO_CREATE_DATABASE=true`.

URLs locales:

```txt
API: http://localhost:8000/api/v1
Health: http://localhost:8000/api/v1/health
Swagger: http://localhost:8000/docs
```

## Frontend local

Desde la carpeta del frontend:

```bash
copy .env.example .env
python run.py
```

URL:

```txt
http://localhost:5173
```

Variable principal del frontend:

```txt
FICHOW_API_BASE_URL=http://localhost:8000/api/v1
```

## Usuarios iniciales

Todos usan password:

```txt
Admin123
```

Cuentas:

```txt
admin@fichow.test
ana@fichow.test
luis@fichow.test
maria@fichow.test
```

## Autenticacion

El login devuelve el JWT en una cookie `HttpOnly`:

```txt
fichow_access_token
```

El frontend no guarda el JWT en `localStorage`; solo guarda datos basicos del usuario para pintar la interfaz. Las peticiones usan cookies con `credentials: include`.

Para produccion con Vercel + Render:

```txt
JWT_COOKIE_SECURE=true
JWT_COOKIE_SAMESITE=none
ALLOWED_ORIGINS=https://front.com
FRONTEND_URL=https://front.com
```

## Vulnerabilidades intencionales

### 1. IDOR en wallet

Endpoint:

```txt
GET /api/v1/wallets/{wallet_id}
```

Flujo:

1. Iniciar sesion como `ana@fichow.test`.
2. Entrar a Wallet.
3. Interceptar `GET /api/v1/wallets/{wallet_id}`.
4. Cambiar `wallet_id` por `1`, `3`, `4`, etc.
5. Observar saldo, moneda y relacion `user_id` de otra wallet.

Impacto:

- Filtracion de saldo.
- Filtracion de moneda.
- Filtracion de relacion usuario-wallet.

Linea vulnerable:

```txt
app/routers/wallets.py:20
app/routers/wallets.py:22
```

La ruta recibe `current_user`, pero no valida que `wallet.user_id == current_user.id`.

Correccion esperada:

```python
if current_user.role.value != "ADMIN" and wallet.user_id != current_user.id:
    raise forbidden()
```

### 2. IDOR en transacciones

Endpoint:

```txt
GET /api/v1/transactions/{transaction_id}
```

Flujo:

1. Iniciar sesion como usuario CUSTOMER.
2. Entrar a Wallet.
3. Abrir detalle de una transaccion con el boton `View`.
4. Interceptar `GET /api/v1/transactions/{transaction_id}`.
5. Cambiar `transaction_id` por una transaccion ajena.

Impacto:

- Exposicion de recargas.
- Exposicion de compras.
- Exposicion de reembolsos.
- Exposicion de `balance_before` y `balance_after`.

Linea vulnerable:

```txt
app/routers/transactions.py:20
app/routers/transactions.py:22
```

La ruta devuelve cualquier transaccion por ID sin comprobar ownership.

Correccion esperada:

```python
if current_user.role.value != "ADMIN" and transaction.user_id != current_user.id:
    raise forbidden()
```

### 3. Broken Access Control en panel admin

Endpoints:

```txt
GET /api/v1/admin/summary
GET /api/v1/users
GET /api/v1/orders
GET /api/v1/transactions
```

Flujo:

1. Iniciar sesion como `ana@fichow.test`.
2. El frontend no muestra acceso al panel admin.
3. En Burp Repeater o curl, llamar manualmente endpoints admin.
4. Observar informacion reservada.

Impacto:

- Un CUSTOMER puede ver resumen administrativo.
- Un CUSTOMER puede listar usuarios.
- Un CUSTOMER puede listar ordenes.
- Un CUSTOMER puede listar transacciones.

Lineas vulnerables:

```txt
app/routers/admin.py:16
app/routers/admin.py:37
app/routers/admin.py:43
app/routers/admin.py:49
app/routers/users.py:16
app/routers/orders.py:32
app/routers/transactions.py:25
```

Las rutas usan `Depends(get_current_user)` en vez de `Depends(get_admin_user)`.

Correccion esperada:

```python
admin: User = Depends(get_admin_user)
```

### 4. Mass assignment en perfil de usuario

Endpoint:

```txt
PATCH /api/v1/users/{user_id}
```

Flujo normal:

```json
{
  "full_name": "Nuevo Nombre"
}
```

Payload manipulado:

```json
{
  "full_name": "Nuevo Nombre",
  "role": "ADMIN",
  "is_active": true,
  "deleted_at": null
}
```

Flujo:

1. Iniciar sesion como CUSTOMER.
2. Entrar a Dashboard.
3. Editar perfil.
4. Interceptar `PATCH /api/v1/users/{own_id}`.
5. Agregar campos internos al JSON.
6. Enviar.
7. Refrescar sesion o volver a login si la UI no actualiza todo inmediatamente.

Impacto:

- Escalada de rol a ADMIN.
- Reactivacion de usuarios.
- Modificacion de campos internos.

Lineas vulnerables:

```txt
app/schemas/user_schema.py:23
app/services/user_service.py:15
app/services/user_service.py:20
```

`UserUpdate` permite campos extra y el servicio aplica cualquier atributo existente del modelo.

Correccion esperada:

- Usar schema estricto.
- Ignorar campos no permitidos.
- Actualizar solo `full_name` y/o `email`.

### 5. Quantity tampering

Endpoints:

```txt
POST /api/v1/cart/items
PATCH /api/v1/cart/items/{cart_item_id}
POST /api/v1/orders
```

Payloads interesantes:

```json
{"product_id":1,"quantity":-1}
```

```json
{"quantity":0}
```

```json
{"quantity":999999}
```

```json
{"quantity":1.5}
```

```json
{"quantity":"abc"}
```

Flujo:

1. Iniciar sesion como CUSTOMER.
2. Agregar producto al carrito.
3. Interceptar `POST /api/v1/cart/items` o `PATCH /api/v1/cart/items/{cart_item_id}`.
4. Modificar `quantity`.
5. Validar carrito o crear orden.

Impacto:

- Cantidades negativas alteran subtotal.
- Cantidades extremas alteran stock.
- Tipos no esperados pueden causar errores o inconsistencias.

Lineas vulnerables:

```txt
app/schemas/cart_schema.py:9
app/schemas/cart_schema.py:12
app/services/cart_service.py:11
app/services/cart_service.py:31
app/services/cart_service.py:70
app/services/order_service.py:71
```

`quantity` acepta `Any`, no hay validacion de rango, y la orden descuenta stock con el valor recibido.

Correccion esperada:

```python
quantity: int = Field(gt=0)
```

Y validar:

```python
if quantity > product.stock:
    raise insufficient_stock()
```

### 6. User enumeration en login

Endpoint:

```txt
POST /api/v1/auth/login
```

Payload usuario inexistente:

```json
{
  "email": "noexiste@fichow.test",
  "password": "Admin123"
}
```

Respuesta vulnerable:

```json
{
  "success": false,
  "message": "User not found",
  "error": "USER_NOT_FOUND"
}
```

Payload password incorrecto para usuario existente:

```json
{
  "email": "ana@fichow.test",
  "password": "wrongpass"
}
```

Respuesta vulnerable:

```json
{
  "success": false,
  "message": "Invalid password",
  "error": "INVALID_PASSWORD"
}
```

Impacto:

- Enumeracion de usuarios registrados.
- Preparacion de ataques dirigidos a cuentas existentes.

Lineas vulnerables:

```txt
app/services/auth_service.py:42
app/services/auth_service.py:45
app/services/auth_service.py:48
```

Correccion esperada:

Usar la misma respuesta para usuario inexistente y password incorrecto:

```txt
INVALID_CREDENTIALS
```

### 7. Cancelacion de orden ajena

Endpoint:

```txt
POST /api/v1/orders/{order_id}/cancel
```

Flujo:

1. Iniciar sesion como CUSTOMER.
2. Ver una orden propia.
3. Interceptar `POST /api/v1/orders/{order_id}/cancel`.
4. Cambiar `order_id` por una orden de otro usuario.
5. Enviar request.

Impacto:

- Cancelacion de compras ajenas.
- Posible reembolso sobre ordenes no propias.
- Desorden financiero y operacional.

Lineas vulnerables:

```txt
app/routers/orders.py:42
app/services/order_service.py:146
```

`cancel_order` recibe `user_id`, pero no comprueba que `order.user_id == user_id`.

Correccion esperada:

```python
if not is_admin and order.user_id != user_id:
    raise forbidden()
```

### 8. Refund abuse

Endpoint:

```txt
POST /api/v1/orders/{order_id}/refund
```

Flujo:

1. Iniciar sesion como CUSTOMER.
2. Enviar manualmente `POST /api/v1/orders/{order_id}/refund`.
3. Probar con orden propia o ajena.
4. Observar cambio de estado, saldo y transaccion REFUND.

Impacto:

- Reembolsos no autorizados.
- Aumento indebido de saldo.
- Transacciones falsas.

Lineas vulnerables:

```txt
app/routers/orders.py:47
app/routers/orders.py:48
app/services/order_service.py:184
```

La ruta de refund usa `Depends(get_current_user)` y llama al servicio sin exigir ADMIN.

Correccion esperada:

```python
admin: User = Depends(get_admin_user)
```

## Funcionalidades que se mantienen mas restringidas

Estas operaciones siguen pensadas como administrativas, salvo que se explote mass assignment para subir a ADMIN:

- Crear productos.
- Editar productos.
- Activar/desactivar productos.
- Crear cupones.
- Editar cupones.
- Ajustar wallet manualmente.
- Cambiar rol desde endpoint dedicado.
- Cambiar estado de usuario desde endpoint dedicado.

## Notas para pruebas con Burp

- Configurar el navegador para usar el proxy de Burp.
- Iniciar sesion normalmente desde el frontend.
- El JWT esta en cookie `HttpOnly`; no aparece en `localStorage`.
- Las peticiones autenticadas deben conservar la cookie `fichow_access_token`.
- Para repetir requests en Repeater, copiar tambien la cabecera `Cookie`.

## Reset rapido de datos

En local, para reconstruir desde cero:

1. Detener backend.
2. Eliminar la base `fichow_db` en PostgreSQL.
3. Dejar en `.env`:

```txt
AUTO_CREATE_DATABASE=true
AUTO_CREATE_TABLES=true
AUTO_SEED_DATA=true
```

4. Ejecutar:

```bash
python run.py
```
