# Fichow API

Backend de Fichow hecho con FastAPI, SQLAlchemy y PostgreSQL.

## Ejecutar local simple

1. Crea el entorno e instala dependencias una vez:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

2. Crea tu `.env`:

```bash
copy .env.example .env
```

3. Edita esto segun tu PostgreSQL local:

```txt
DATABASE_URL=postgresql+psycopg2://postgres:tu_password@localhost:5432/fichow_db
JWT_SECRET_KEY=un_secreto_largo_local
```

4. Levanta el backend:

```bash
python run.py
```

Al arrancar, el backend puede crear automaticamente:

```txt
AUTO_CREATE_DATABASE=true
AUTO_CREATE_TABLES=true
AUTO_SEED_DATA=true
```

Eso crea la base `fichow_db`, las tablas y datos iniciales si no existen. El usuario de PostgreSQL que pongas en `DATABASE_URL` debe tener permiso para crear bases si usas `AUTO_CREATE_DATABASE=true`.

## URLs locales

```txt
API: http://localhost:8000/api/v1
Health: http://localhost:8000/api/v1/health
Swagger: http://localhost:8000/docs
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

## Que es Uvicorn

FastAPI es la aplicacion, pero necesita un servidor ASGI para escuchar HTTP. Uvicorn es ese servidor. No tienes que recordarlo: `python run.py` lo ejecuta por dentro.

## Deploy en Render con PostgreSQL

Render tiene PostgreSQL gestionado. Crea primero la DB:

```txt
New + -> Postgres
Name: fichow-db
Database: fichow_db
User: fichow_user
Region: la misma que el backend
```

Cuando Render termine de crearla, copia la Internal Database URL. Se ve parecida a:

```txt
postgresql://USER:PASSWORD@INTERNAL_HOST:5432/fichow_db
```

Para SQLAlchemy usa:

```txt
postgresql+psycopg2://USER:PASSWORD@INTERNAL_HOST:5432/fichow_db
```

Variables recomendadas para el backend:

```txt
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@INTERNAL_HOST:5432/fichow_db
JWT_SECRET_KEY=un_secreto_largo_de_produccion
APP_ENV=production
DEBUG=false
API_PREFIX=/api/v1
ALLOWED_ORIGINS=https://tu-front.vercel.app
JWT_COOKIE_SECURE=true
JWT_COOKIE_SAMESITE=none
AUTO_CREATE_DATABASE=false
AUTO_CREATE_TABLES=true
AUTO_SEED_DATA=true
```

En local usa:

```txt
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
JWT_COOKIE_SECURE=false
JWT_COOKIE_SAMESITE=lax
```

Comandos Render:

```txt
Build Command: pip install -r requirements.txt
Start Command: python run.py
```

`python run.py` detecta automaticamente la variable `PORT` de Render.
