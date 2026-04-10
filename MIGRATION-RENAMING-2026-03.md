# Migración: Renombrado de endpoints y schemas (marzo 2026)

Documento de referencia para actualizar el paquete de R que consume la API.

---

## Resumen del cambio

Se han renombrado los endpoints y schemas relacionados con las tablas `resumen_territorial` y `votos_territoriales` para que los nombres de la API sean más descriptivos:

| Concepto | Nombre anterior | Nombre nuevo |
|---|---|---|
| Datos de la tabla `resumen_territorial` | `resumen` | `totales_territorio` |
| Datos de la tabla `votos_territoriales` | `votos` | `votos_partido` |

---

## 1. Cambios en URLs de endpoints

### Endpoints independientes (bajo `/v1/resultados/`)

| Ruta anterior | Ruta nueva |
|---|---|
| `GET /v1/resultados/resumen` | `GET /v1/resultados/totales-territorio` |
| `GET /v1/resultados/votos` | `GET /v1/resultados/votos-partido` |

### Endpoints bajo `/v1/elecciones/{id}/`

| Ruta anterior | Ruta nueva |
|---|---|
| `GET /v1/elecciones/{id}/resultados` | `GET /v1/elecciones/{id}/totales-territorio` |
| `GET /v1/elecciones/{id}/resultados/{territorio_id}` | `GET /v1/elecciones/{id}/totales-territorio/{territorio_id}` |

### Endpoints SIN cambio

| Ruta | Nota |
|---|---|
| `GET /v1/resultados/combinados` | Sin cambios en URL ni en estructura |

---

## 2. Cambios en nombres de schemas (tipos de respuesta)

| Schema anterior | Schema nuevo |
|---|---|
| `ResumenTerritorialSchema` | `TotalTerritorioSchema` |
| `VotoTerritorialSchema` | `VotoPartidoSchema` |
| `VotoConPartidoSchema` | `VotoPartidoDetalleSchema` |

El schema `ResultadoCompletoSchema` y `ResultadoCombinadoSchema` **mantienen su nombre**, pero los campos internos de `ResultadoCompletoSchema` cambian (ver sección 3).

---

## 3. Cambios en campos de respuesta JSON

### Endpoint: `GET /v1/elecciones/{id}/totales-territorio/{territorio_id}`

**Antes:**
```json
{
  "resumen": {
    "id": 408788,
    "eleccion_id": 208,
    "territorio_id": 20,
    "censo_ine": 500556,
    ...
  },
  "votos": [
    {
      "id": 5732190,
      "eleccion_id": 208,
      "territorio_id": 20,
      "partido_id": 9451,
      "votos": 98924,
      "representantes": 2,
      "partido": { ... }
    }
  ]
}
```

**Después:**
```json
{
  "totales_territorio": {
    "id": 408788,
    "eleccion_id": 208,
    "territorio_id": 20,
    "censo_ine": 500556,
    ...
  },
  "votos_partido": [
    {
      "id": 5732190,
      "eleccion_id": 208,
      "territorio_id": 20,
      "partido_id": 9451,
      "votos": 98924,
      "representantes": 2,
      "partido": { ... }
    }
  ]
}
```

**Campos renombrados:**

| Campo anterior | Campo nuevo |
|---|---|
| `resumen` | `totales_territorio` |
| `votos` | `votos_partido` |

### Todos los demás endpoints

Los campos internos de los objetos individuales (`id`, `eleccion_id`, `territorio_id`, `censo_ine`, `votos_validos`, `votos`, `representantes`, etc.) **NO cambian**. Solo cambian:
- Las URLs de los endpoints
- Los nombres de los campos contenedores en `ResultadoCompleto`

---

## 4. Resumen de acciones para el paquete de R

### URLs a actualizar

```r
# ANTES → DESPUÉS

# Totales territorio (listado general)
"resultados/resumen"          → "resultados/totales-territorio"

# Votos partido (listado general)
"resultados/votos"            → "resultados/votos-partido"

# Totales territorio por elección
"elecciones/{id}/resultados"  → "elecciones/{id}/totales-territorio"

# Resultado completo (elección + territorio)
"elecciones/{id}/resultados/{territorio_id}" → "elecciones/{id}/totales-territorio/{territorio_id}"
```

### Campos JSON a actualizar en el parsing

```r
# En la respuesta de /elecciones/{id}/totales-territorio/{territorio_id}:
# ANTES                    → DESPUÉS
response$resumen           → response$totales_territorio
response$votos             → response$votos_partido
```

### Funciones R a renombrar (sugerencia)

| Función anterior (probable) | Función nueva (sugerida) |
|---|---|
| `get_resumen_territorial()` | `get_totales_territorio()` |
| `get_votos_territoriales()` | `get_votos_partido()` |
| `get_resultados_eleccion()` | `get_totales_territorio_eleccion()` |

---

## 5. Lo que NO cambia

- **Tablas de la base de datos**: `resumen_territorial` y `votos_territoriales` mantienen sus nombres en PostgreSQL.
- **Modelos SQLAlchemy internos**: `ResumenTerritorial` y `VotoTerritorial` en el código Python de la API.
- **Estructura interna de los objetos**: Los campos de cada registro individual (`censo_ine`, `votos_validos`, `abstenciones`, `votos`, `representantes`, etc.) no cambian.
- **Endpoint `/v1/resultados/combinados`**: Sin cambios.
- **Paginación**: La estructura `{ total, skip, limit, data }` no cambia.
- **Filtros query parameters**: Mismos nombres y comportamiento.
