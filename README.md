# Elecciones DB API

API REST para consultar resultados electorales españoles.  
Desarrollada con **FastAPI** + **SQLAlchemy** + **PostgreSQL**.

---

## Estructura del proyecto

```
app/
├── main.py                  # Punto de entrada FastAPI
├── config.py                # Configuración por variables de entorno
├── database.py              # Engine SQLAlchemy, sesión, dependency get_db
├── crud.py                  # Funciones de acceso a datos (solo lectura)
├── api/
│   ├── routes_health.py     # GET /health
│   ├── routes_elecciones.py # Elecciones + tipos + totales territorio por elección
│   ├── routes_territorios.py# Territorios + jerarquía (hijos)
│   ├── routes_partidos.py   # Partidos + agrupaciones (recode)
│   └── routes_resultados.py # Totales territorio, votos partido, combinados
├── models/
│   └── models.py            # Modelos SQLAlchemy (9 tablas + 1 ENUM)
└── schemas/
    ├── pagination.py        # Paginación reutilizable
    ├── health.py
    ├── elecciones.py
    ├── territorios.py
    ├── partidos.py
    └── resultados.py
tests/
Dockerfile
docker-compose.yml
```

---

## Endpoints (15 en total)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Estado de la app + check BD |
| GET | `/api/v1/tipos-eleccion` | Catálogo de tipos de elección |
| GET | `/api/v1/tipos-eleccion/{codigo}` | Detalle de un tipo de elección |
| GET | `/api/v1/elecciones` | Lista paginada de las elecciones disponibles |
| GET | `/api/v1/elecciones/{id}` | Detalle con atributo tipo expandido |
| GET | `/api/v1/elecciones/{id}/totales-territorio` | Totales territorio de una elección |
| GET | `/api/v1/elecciones/{id}/totales-territorio/{territorio_id}` | Totales territorio + votos por partido |
| GET | `/api/v1/territorios` | Lista con filtros (tipo, CCAA, nombre) |
| GET | `/api/v1/territorios/{id}` | Detalle con todos los códigos |
| GET | `/api/v1/territorios/{id}/hijos` | Hijos directos (jerarquía) |
| GET | `/api/v1/partidos` | Lista con filtro por siglas |
| GET | `/api/v1/partidos/{id}` | Detalle con recode expandido |
| GET | `/api/v1/partidos-recode` | Agrupaciones de partidos |
| GET | `/api/v1/partidos-recode/{id}` | Detalle con partidos asociados |
| GET | `/api/v1/resultados/totales-territorio` | Totales territorio |
| GET | `/api/v1/resultados/votos-partido` | Votos por partido/territorio |

Todos los listados soportan paginación: `?skip=0&limit=50` (máx 500).

---

## Configuración

Copia `.env.example` a `.env` y ajusta los valores:

```bash
cp .env.example .env
```

### Variables de entorno

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DB_HOST` | Host de PostgreSQL | `localhost` |
| `DB_PORT` | Puerto | `5432` |
| `DB_NAME` | Nombre de la base de datos | `eleccionesdb` |
| `DB_USER` | Usuario | `eleccionesdb_api` |
| `DB_PASSWORD` | Contraseña | `changeme` |
| `DB_SCHEMA` | Esquema (vacío = public) | `` |
| `APP_ENV` | Entorno | `development` / `production` |
| `ROOT_PATH` | Prefijo para reverse proxy | `` / `/api` |

### Configurar `DB_HOST` según el escenario

| Escenario | Valor de `DB_HOST` |
|-----------|-------------------|
| Local sin Docker | `localhost` |
| Docker en **Windows/Mac** (BD en el host) | `host.docker.internal` |
| Docker en **Linux** (BD en el host) | `172.17.0.1` (IP del bridge docker0) |
| BD en otra máquina | IP o hostname del servidor |

> **`host.docker.internal`** funciona de forma nativa en Docker Desktop (Windows/Mac).  
> En Linux, funciona gracias a `extra_hosts` en `docker-compose.yml`.

---

## Ejecución

### 1. Local sin Docker (desarrollo)

```bash
# Crear entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Configurar .env (DB_HOST=localhost si la BD está en local)

# Arrancar con recarga automática
uvicorn app.main:app --reload
```

Abrir: http://localhost:8000/docs

### 2. Local con Docker

```bash
# Ajustar DB_HOST en .env:
#   Windows/Mac: host.docker.internal
#   Linux:       172.17.0.1

docker compose up --build
```

Abrir: http://localhost:8000/docs

### 3. Producción (Ubuntu con Docker Compose)

```bash
# Ajustar .env:
#   DB_HOST=<ip-del-servidor-de-bd>
#   APP_ENV=production
#   ROOT_PATH=/api   (si va detrás de Nginx en /api)

docker compose up -d --build
```

### Nginx reverse proxy (ejemplo)

Si la API se sirve en `https://midominio.com/api`:

```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

Y en `.env`: `ROOT_PATH=/api`

---

## Tests

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```

---

## Notas de diseño

- **`requirements.txt`** sobre `pyproject.toml`: Es una aplicación desplegable, no una librería. `requirements.txt` es más simple para Docker y universalmente entendido.
- **Multi-stage Docker build**: Imagen final sin `gcc` ni headers de desarrollo (~150 MB).
- **`psycopg2-binary`**: Simplifica el build Docker. Suficiente para producción.
- **Schema dinámico**: Si `DB_SCHEMA` tiene valor, se ejecuta `SET search_path TO <schema>, public` en cada conexión. Si está vacío, usa `public` por defecto.
- **`root_path`**: FastAPI lo soporta nativamente para funcionar detrás de un reverse proxy.
- **No hay `metadata.create_all()`**: La BD se gestiona por separado (`db_schema.sql`).
- **ENUM `territorio_tipo`** mapeado con `create_type=False`: El tipo ya existe en PostgreSQL.

---

## CI/CD

El repositorio tiene dos GitHub Actions que se ejecutan automáticamente al hacer push a `main`:

### GitHub Pages (documentación)

El sitio de documentación (Quarto) se publica en **GitHub Pages** automáticamente cuando hay cambios en `docs/`.

**Configuración necesaria:**

1. Ir a **Settings → Pages → Build and deployment**.
2. En **Source**, seleccionar **GitHub Actions**.

### Despliegue de la API en VPS

La API se despliega automáticamente en el VPS cuando hay cambios en el código (cualquier archivo excepto `docs/`). El workflow conecta por SSH, hace `git pull` y reconstruye los contenedores Docker.

**Secrets necesarios** (Settings → Secrets and variables → Actions):

| Secret | Descripción | Ejemplo |
|---|---|---|
| `VPS_HOST` | IP o hostname del servidor | `203.0.113.10` |
| `VPS_USER` | Usuario SSH | `deploy` |
| `VPS_SSH_KEY` | Clave privada SSH | (contenido de `~/.ssh/id_ed25519`) |
| `VPS_DEPLOY_PATH` | Ruta del proyecto en el servidor | `/opt/eleccionesdb-api` |
