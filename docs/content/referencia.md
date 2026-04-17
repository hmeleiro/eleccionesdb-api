---
title: "Referencia de la API"
description: "Catálogo completo de endpoints, parámetros, filtros y estructura de respuestas."
---


<div style="background: #f1f5ff; border-left: 4px solid #2d5bff; padding: 1.5em 1.5em 1em 1.5em; border-radius: 8px; margin-bottom: 2em;">
  <strong style="color: #2d5bff; font-size: 1.1em;">Información general</strong>
  <ul style="font-size: 1.05rem; color: #1a1a2e; margin: 0.5em 0 0 0;">
    <li><b>Base URL:</b> <code>https://api.spainelectoralproject.com/v1</code></li>
    <li><b>Versión:</b> 1.0.0</li>
    <li><b>Especificación:</b> OpenAPI 3.1.0</li>
    <li><b>Métodos HTTP:</b> Solo <code>GET</code> (API de solo lectura)</li>
    <li><b>Autenticación:</b> API key (header <code>X-API-Key</code>)</li>
    <li><b>Formato respuesta:</b> JSON (<code>application/json</code>)</li>
  </ul>
</div>

<div style="background: #eaf1fb; border-left: 4px solid #2d5bff; padding: 1.2em 1.5em 1em 1.5em; border-radius: 8px; margin-bottom: 2em;">
  <strong style="color: #2d5bff; font-size: 1.1em;">Autenticación</strong><br>
  Todos los endpoints de <code>/v1/*</code> requieren autenticación mediante API key, excepto <code>/v1/auth/*</code> (registro, verificación, gestión de clave) y <code>/health</code>.<br><br>
  Obtén tu clave registrándote en <code>/v1/auth/register</code> y verificando tu email. Incluye el header <code>X-API-Key</code> en todas tus peticiones:
</div>

```bash
curl -H "X-API-Key: TU_API_KEY" https://api.spainelectoralproject.com/v1/elecciones
```

Si la clave es inválida, revocada o falta, la API responderá con:

```json
{
  "detail": "API key requerida"
}
```

o

```json
{
  "detail": "API key inválida o revocada"
}
```

<div style="color: #9ca3af; font-size: 0.98rem; text-align: center; margin-top: 2.5rem;">Spain Electoral Project &mdash; API</div>

---

## Endpoints

### Health

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/health` | Estado de la aplicación y conexión a la BD |

### Elecciones

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/v1/tipos-eleccion` | Catálogo de tipos de elección (array simple, sin paginación) |
| GET | `/v1/tipos-eleccion/{codigo}` | Detalle de un tipo de elección |
| GET | `/v1/elecciones` | Listado paginado de elecciones con filtros |
| GET | `/v1/elecciones/{id}` | Detalle de una elección con tipo expandido |
| GET | `/v1/elecciones/{id}/fuente` | Fuente oficial de los datos de una elección |
| GET | `/v1/elecciones/{id}/totales-territorio` | Totales territorio de una elección (paginado, con filtros) |
| GET | `/v1/elecciones/{id}/totales-territorio/{territorio_id}` | Resultado completo: totales + votos por partido |

### Territorios

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/v1/territorios` | Listado paginado de territorios con filtros |
| GET | `/v1/territorios/{id}` | Detalle con todos los códigos |
| GET | `/v1/territorios/{id}/hijos` | Hijos directos (navegación jerárquica) |

### Partidos

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/v1/partidos` | Listado paginado de partidos con filtros |
| GET | `/v1/partidos/{id}` | Detalle con agrupación (recode) expandida |
| GET | `/v1/partidos-recode` | Listado paginado de agrupaciones de partidos |
| GET | `/v1/partidos-recode/{id}` | Detalle de agrupación con lista de partidos asociados |

### Resultados

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/v1/resultados/totales-territorio` | Totales territorio filtrables por múltiples criterios |
| GET | `/v1/resultados/votos-partido` | Votos por partido filtrables |
| GET | `/v1/resultados/combinados` | Votos con partido, territorio y elección expandidos |

## Paginación

Todos los endpoints que devuelven listados (excepto `/v1/tipos-eleccion`) usan paginación.

### Parámetros

| Parámetro | Tipo | Default | Mín | Máx | Descripción |
|---|---|---|---|---|---|
| `skip` | int | 0 | 0 | — | Registros a saltar |
| `limit` | int | 50 | 1 | 500 | Registros por página |

### Estructura de respuesta paginada

```json
{
  "total": 254,
  "skip": 0,
  "limit": 50,
  "data": [...]
}
```

- `total`: número total de registros que cumplen los filtros.
- `skip` / `limit`: eco de los parámetros enviados.
- `data`: array con los registros de la página actual.

### Recorrido completo

Para recorrer todos los registros se incrementa `skip` en cada petición:

```
Página 1: ?skip=0&limit=100
Página 2: ?skip=100&limit=100
Página 3: ?skip=200&limit=100
...hasta que skip >= total
```

Cuando no hay coincidencias, la respuesta es `total=0` y `data=[]` (HTTP 200, no es error).

## Filtros

### Convenciones generales

- Todos los filtros son **opcionales**. Sin filtros se devuelven todos los registros.
- Los filtros de texto (`nombre`, `siglas`, `denominacion`, `agrupacion`) usan **búsqueda parcial case-insensitive** (ILIKE).
- Para filtrar por **múltiples valores**, se repite el parámetro: `?tipo_eleccion=G&tipo_eleccion=A`.

### Filtros por endpoint

#### `/v1/elecciones`

| Parámetro | Tipo | Ejemplo | Descripción |
|---|---|---|---|
| `tipo_eleccion` | str (repetible) | `G`, `A` | Código del tipo de elección |
| `year` | str (repetible) | `2019` | Año de la elección |
| `mes` | str (repetible) | `04` | Mes (con cero a la izquierda) |

#### `/v1/territorios`

| Parámetro | Tipo | Ejemplo | Descripción |
|---|---|---|---|
| `tipo` | str (repetible) | `ccaa`, `provincia` | Tipo de territorio |
| `codigo_ccaa` | str (repetible) | `01` | Código de comunidad autónoma |
| `codigo_provincia` | str (repetible) | `28` | Código de provincia |
| `nombre` | str | `madrid` | Búsqueda parcial por nombre |

#### `/v1/partidos`

| Parámetro | Tipo | Ejemplo | Descripción |
|---|---|---|---|
| `siglas` | str | `psoe` | Búsqueda parcial por siglas |
| `denominacion` | str | `socialista` | Búsqueda parcial por nombre completo |

#### `/v1/partidos-recode`

| Parámetro | Tipo | Ejemplo | Descripción |
|---|---|---|---|
| `agrupacion` | str | `PCE/IU` | Búsqueda parcial por agrupación |

#### `/v1/elecciones/{id}/totales-territorio`

| Parámetro | Tipo | Ejemplo | Descripción |
|---|---|---|---|
| `territorio_id` | int | `20` | ID de territorio específico |
| `tipo_territorio` | str (repetible) | `provincia` | Tipo de territorio |
| `codigo_ccaa` | str (repetible) | `01` | Código de comunidad autónoma |
| `codigo_provincia` | str (repetible) | `28` | Código de provincia |
| `codigo_municipio` | str (repetible) | `079` | Código de municipio |

#### `/v1/resultados/totales-territorio`

| Parámetro | Tipo | Ejemplo | Descripción |
|---|---|---|---|
| `eleccion_id` | int (repetible) | `208` | ID de elección |
| `territorio_id` | int (repetible) | `20` | ID de territorio |
| `year` | str (repetible) | `2019` | Año de la elección |
| `tipo_eleccion` | str (repetible) | `G` | Código del tipo |
| `tipo_territorio` | str (repetible) | `provincia` | Tipo de territorio |
| `codigo_ccaa` | str (repetible) | `01` | Código CCAA |
| `codigo_provincia` | str (repetible) | `28` | Código provincia |
| `codigo_municipio` | str (repetible) | `079` | Código municipio |

#### `/v1/resultados/votos-partido` y `/v1/resultados/combinados`

Los mismos filtros que `resultados/totales-territorio`, más:

| Parámetro | Tipo | Ejemplo | Descripción |
|---|---|---|---|
| `partido_id` | int (repetible) | `9451` | ID de partido |

## Errores

| Código HTTP | Significado | Ejemplo |
|---|---|---|
| 404 | Recurso no encontrado | `{"detail": "Elección no encontrada"}` |
| 422 | Error de validación | `{"detail": [{"type": "...", "loc": [...], "msg": "..."}]}` |
