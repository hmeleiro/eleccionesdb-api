# EleccionesDB API — Reglas de uso funcionales

Documentación funcional para construir un paquete de R que consuma esta API.

## 1. Información general

| Propiedad | Valor |
|---|---|
| Base URL | `http://{host}:{port}` (por defecto `http://localhost:8000`) |
| Versión | 1.0.0 |
| Especificación | OpenAPI 3.1.0 |
| Métodos HTTP | Solo `GET` (API de solo lectura) |
| Autenticación | API key (header `X-API-Key`) |
| Rate limiting | Ninguno |
| Formato respuesta | JSON (`application/json`) |
| Idioma datos | Español (nombres de campos, mensajes de error, datos) |


## Autenticación

Todos los endpoints de `/v1/*` requieren autenticación mediante API key, excepto `/v1/auth/*` (registro, verificación, gestión de clave) y `/health`.

Obtén tu clave registrándote en `/v1/auth/register` y verificando tu email. Incluye el header `X-API-Key` en todas tus peticiones:

```r
httr2::request("https://api.spainelectoralproject.com/v1/elecciones") %>%
  req_headers(`X-API-Key` = "TU_API_KEY")
```

Si la clave es inválida, revocada o falta, la API responderá con:

```json
{"detail": "API key requerida"}
```

o

```json
{"detail": "API key inválida o revocada"}
```

---

## 2. Endpoints — Catálogo completo

### Health
| Método | Ruta | Respuesta | Descripción |
|---|---|---|---|
| GET | `/health` | `HealthResponse` | Estado de la aplicación y BD |

### Elecciones
| Método | Ruta | Respuesta | Descripción |
|---|---|---|---|
| GET | `/v1/tipos-eleccion` | `TipoEleccion[]` | Catálogo de tipos (array simple) |
| GET | `/v1/tipos-eleccion/{codigo}` | `TipoEleccion` | Detalle de un tipo |
| GET | `/v1/elecciones` | `PaginatedResponse[Eleccion]` | Listado paginado con filtros |
| GET | `/v1/elecciones/{id}` | `EleccionDetail` | Detalle con tipo expandido |

### Territorios
| Método | Ruta | Respuesta | Descripción |
|---|---|---|---|
| GET | `/v1/territorios` | `PaginatedResponse[Territorio]` | Listado paginado con filtros |
| GET | `/v1/territorios/{id}` | `TerritorioDetail` | Detalle con todos los códigos |
| GET | `/v1/territorios/{id}/hijos` | `PaginatedResponse[Territorio]` | Hijos directos (jerarquía) |

### Partidos
| Método | Ruta | Respuesta | Descripción |
|---|---|---|---|
| GET | `/v1/partidos` | `PaginatedResponse[Partido]` | Listado paginado con filtros |
| GET | `/v1/partidos/{id}` | `PartidoDetail` | Detalle con recode expandido |
| GET | `/v1/partidos-recode` | `PaginatedResponse[PartidoRecode]` | Listado de agrupaciones |
| GET | `/v1/partidos-recode/{id}` | `PartidoRecodeDetail` | Detalle con lista de partidos |

### Resultados
| Método | Ruta | Respuesta | Descripción |
|---|---|---|---|
| GET | `/v1/elecciones/{id}/totales-territorio` | `PaginatedResponse[TotalTerritorio]` | Totales territorio de una elección |
| GET | `/v1/elecciones/{id}/totales-territorio/{territorio_id}` | `ResultadoCompleto` | Totales territorio + votos por partido |
| GET | `/v1/resultados/totales-territorio` | `PaginatedResponse[TotalTerritorio]` | Totales territorio filtrable |
| GET | `/v1/resultados/votos-partido` | `PaginatedResponse[VotoPartido]` | Votos por partido filtrable |
| GET | `/v1/resultados/combinados` | `PaginatedResponse[ResultadoCombinado]` | Votos con todo expandido |

## 3. Paginación

Todos los endpoints que devuelven listas (excepto `/tipos-eleccion`) usan paginación genérica.

### Parámetros query

| Parámetro | Tipo | Default | Min | Max | Descripción |
|---|---|---|---|---|---|
| `skip` | int | 0 | 0 | — | Número de registros a saltar |
| `limit` | int | 50 | 1 | 500 | Número máximo de registros a devolver |

### Estructura de respuesta paginada

```json
{
  "total": 254,    // int: número total de registros que cumplen los filtros
  "skip": 0,       // int: registros saltados (echo del parámetro)
  "limit": 50,     // int: límite aplicado (echo del parámetro)
  "data": [...]    // array: registros de esta página
}
```

### Recorrido completo

Para recorrer todos los registros:
```
Página 1: ?skip=0&limit=100
Página 2: ?skip=100&limit=100
Página 3: ?skip=200&limit=100
...hasta que skip >= total
```

**Resultado vacío**: Cuando no hay coincidencias, `total=0` y `data=[]`. No es error, devuelve HTTP 200.

## 4. Filtros

### Convenciones generales
- Los filtros se pasan como **query parameters**.
- Todos los filtros son **opcionales** — sin filtros se devuelven todos los registros.
- Los filtros de texto (`nombre`, `siglas`, `agrupacion`) usan **búsqueda parcial case-insensitive** (ILIKE).
- Los filtros de lista (`tipo_eleccion`, `year`, etc.) aceptan **un solo valor** por parámetro. Para filtrar por múltiples valores, se repite el parámetro: `?tipo_eleccion=G&tipo_eleccion=A`.

### Filtros por endpoint

#### Elecciones (`/v1/elecciones`)
| Parámetro | Tipo | Ejemplo | Descripción |
|---|---|---|---|
| `tipo_eleccion` | str (repetible) | `G`, `A` | Código del tipo de elección |
| `year` | str (repetible) | `2019` | Año de la elección |
| `mes` | str (repetible) | `04` | Mes (con cero a la izquierda) |

#### Territorios (`/v1/territorios`)
| Parámetro | Tipo | Ejemplo | Descripción |
|---|---|---|---|
| `tipo` | str (repetible) | `ccaa`, `provincia` | Tipo de territorio (enum) |
| `codigo_ccaa` | str (repetible) | `01` | Código de comunidad autónoma |
| `codigo_provincia` | str (repetible) | `28` | Código de provincia |
| `nombre` | str | `madrid` | Búsqueda parcial por nombre |

#### Partidos (`/v1/partidos`)
| Parámetro | Tipo | Ejemplo | Descripción |
|---|---|---|---|
| `siglas` | str | `psoe` | Búsqueda parcial por siglas |
| `denominacion` | str | `socialista` | Búsqueda parcial por nombre completo |
| `partido_recode_id` | int (repetible) | `80` | ID del grupo/recode asociado |

#### Partidos Recode (`/v1/partidos-recode`)
| Parámetro | Tipo | Ejemplo | Descripción |
|---|---|---|---|
| `agrupacion` | str | `PCE/IU` | Búsqueda parcial por agrupación |

#### Resultados — Totales territorio (`/v1/resultados/totales-territorio`)
| Parámetro | Tipo | Ejemplo | Descripción |
|---|---|---|---|
| `eleccion_id` | int (repetible) | `208` | ID de elección |
| `tipo_territorio` | str (repetible) | `provincia` | tipo (enum) |
| `codigo_ccaa` | str (repetible) | `01` | Código CCAA |
| `codigo_provincia` | str (repetible) | `28` | Código provincia |

#### Resultados — Votos partido (`/v1/resultados/votos-partido`)
| Parámetro | Tipo | Ejemplo | Descripción |
|---|---|---|---|
| `eleccion_id` | int (repetible) | `208` | ID de elección |
| `territorio_id` | int (repetible) | `20` | ID de territorio |
| `partido_id` | int (repetible) | `9451` | ID de partido |

#### Resultados — Combinados (`/v1/resultados/combinados`)
Mismos filtros que totales territorio: `eleccion_id`, `tipo_territorio`, `codigo_ccaa`, `codigo_provincia`.

#### Totales territorio por elección (`/v1/elecciones/{id}/totales-territorio`)
| Parámetro | Tipo | Ejemplo | Descripción |
|---|---|---|---|
| `tipo_territorio` | str (repetible) | `provincia` | tipo de territorio |
| `codigo_ccaa` | str (repetible) | `01` | Código CCAA |
| `codigo_provincia` | str (repetible) | `28` | Código provincia |


## 5. Tipos de territorio (enum)

```
ccaa          → Comunidad autónoma
provincia     → Provincia
municipio     → Municipio
distrito      → Distrito censal
seccion       → Sección censal
circunscripcion → Circunscripción electoral
cera          → Censo de extranjeros (voto exterior)
```

## 6. Tipos de elección (códigos)

| Código | Descripción |
|---|---|
| `A` | Autonómicas |
| `E` | Europeas |
| `G` | Congreso (Generales) |
| `L` | Locales |
| `S` | Senado |

## 7. Estructura de datos — Relaciones clave

```
TipoEleccion (1) ──── (N) Eleccion
                              │
                              ├── (N) ResumenTerritorial ──── (1) Territorio
                              │         │
                              │         └── votos_validos, abstenciones, etc.
                              │
                              └── (N) VotoTerritorial ──── (1) Territorio
                                        │                  (1) Partido
                                        └── votos, representantes

Territorio (jerárquico)
  ├── parent_id → Territorio padre (null si es raíz)
  └── hijos → Territorios hijos (vía /territorios/{id}/hijos)

Partido (N) ──── (1) PartidoRecode (agrupación/grupo)
  - partido_recode_id puede ser null (partido sin agrupar)
  - Un PartidoRecode tiene N Partidos asociados

PartidoRecode
  ├── partido_recode: nombre corto ("PP", "PSOE")
  ├── agrupacion: familia ideológica ("AP/PP", "PSOE")
  └── color: color hexadecimal ("#008DDA")
```

## 8. Campos nullables

Los siguientes campos pueden ser `null`:

| Modelo | Campo | Cuándo es null |
|---|---|---|
| Territorio | `codigo_circunscripcion` | Territorios que no son circunscripción |
| Territorio | `parent_id` | Territorios raíz (ccaa) |
| Partido | `partido_recode_id` | Partido sin agrupación |
| Partido (detail) | `recode` | Partido sin agrupación |
| TotalTerritorio | `participacion_3` | Cuando no hay tercer avance de participación |

## 9. Formato de campos

| Campo | Formato | Ejemplo |
|---|---|---|
| `fecha` | ISO 8601 date (string) | `"2019-04-28"` |
| `year`, `mes`, `dia` | Strings con ceros | `"2019"`, `"04"`, `"28"` |
| `codigo_ccaa` | String 2 dígitos | `"01"` |
| `codigo_provincia` | String 2 dígitos | `"28"` |
| `codigo_municipio` | String 3 dígitos | `"999"` (wildcard) |
| `codigo_distrito` | String 2 dígitos | `"99"` (wildcard) |
| `codigo_seccion` | String 4 dígitos | `"9999"` (wildcard) |
| `codigo_completo` | String 13 dígitos | `"0199999999999"` |
| `color` | Hex color con # | `"#008DDA"` |

**Nota sobre wildcards**: Los códigos `99`, `999`, `9999` actúan como wildcards. Por ejemplo, una CCAA tiene `codigo_provincia="99"`, `codigo_municipio="999"`, etc.

## 10. Respuestas especiales

### Endpoints sin paginación (arrays directos)
- `GET /v1/tipos-eleccion` → devuelve un **array** directamente (no PaginatedResponse)

### Endpoints que devuelven objeto único (no paginado)
- `GET /v1/tipos-eleccion/{codigo}` → TipoEleccion
- `GET /v1/elecciones/{id}` → EleccionDetail
- `GET /v1/territorios/{id}` → TerritorioDetail
- `GET /v1/partidos/{id}` → PartidoDetail
- `GET /v1/partidos-recode/{id}` → PartidoRecodeDetail
- `GET /v1/elecciones/{id}/totales-territorio/{territorio_id}` → ResultadoCompleto

### Resultado completo (estructura compuesta)
`GET /v1/elecciones/{id}/totales-territorio/{territorio_id}` devuelve:
```json
{
  "totales_territorio": { ...TotalTerritorio },
  "votos_partido": [
    { ...VotoPartido, "partido": { ...Partido } }
  ]
}
```
Los votos están **ordenados por número de votos descendente**.

### Resultados combinados (todo expandido)
`GET /v1/resultados/combinados` devuelve votos con relaciones expandidas:
cada item incluye `partido` (con `recode` anidado), `territorio` y `eleccion`.

## 11. Manejo de errores

### HTTP 404 — Not Found
Ocurre cuando un recurso específico no existe. El body siempre tiene:
```json
{"detail": "Mensaje en español"}
```

Mensajes posibles:
- `"Elección no encontrada"`
- `"Tipo de elección no encontrado"`
- `"Territorio no encontrado"`
- `"Partido no encontrado"`
- `"Partido recode no encontrado"`
- `"No se encontraron resultados para esta elección y territorio"`

### HTTP 422 — Validation Error
Ocurre cuando los parámetros no pasan la validación de Pydantic. Estructura:
```json
{
  "detail": [
    {
      "type": "greater_than_equal",
      "loc": ["query", "limit"],
      "msg": "Input should be greater than or equal to 1",
      "input": "-5",
      "ctx": {"ge": 1}
    }
  ]
}
```
- `detail` es un **array** de errores
- `loc` indica la ubicación: `["query", "<param>"]` para query params, `["path", "<param>"]` para path params
- `msg` es en inglés (generado por Pydantic)

### HTTP 200 con datos vacíos
Cuando un filtro no coincide con nada, NO es un error. Se devuelve:
```json
{"total": 0, "skip": 0, "limit": 50, "data": []}
```

## 12. Consejos para el paquete R

1. **httr2 o httr**: Usar `httr2::request()` con `req_url_query()` para construir las llamadas.
2. **Paginación automática**: Crear un helper que recorra automáticamente todas las páginas usando `total` y `skip`.
3. **Filtros repetibles**: Para filtros tipo lista (p.ej. `tipo_eleccion=G&tipo_eleccion=A`), httr2 acepta vectores: `req_url_query(tipo_eleccion = c("G", "A"))`.
4. **Tibbles**: Las respuestas paginadas (`$data`) se convierten fácilmente a tibble con `tibble::as_tibble()` o `jsonlite::fromJSON(flatten=TRUE)`.
5. **Objetos anidados**: El recode dentro de partido y el tipo dentro de elección se pueden aplanar con `tidyr::unnest_wider()`.
6. **Campos null → NA**: jsonlite convierte `null` a `NA` automáticamente.
7. **max limit = 500**: Respetar el límite máximo para no provocar errores 422.
8. **Códigos son strings**: `codigo_ccaa`, `year`, `mes`, `dia` son **strings, no integers** (conservan ceros a la izquierda).
9. **API key obligatoria**: Todos los endpoints de `/v1/*` requieren el header `X-API-Key` (excepto `/v1/auth/*` y `/health`).
10. **Endpoint combinados**: Para análisis exploratorio rápido, `/resultados/combinados` devuelve todo en una sola llamada (partido+recode+territorio+elección), evitando múltiples joins en R.
