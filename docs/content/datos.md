---
title: "Datos y fuentes"
description: "Cobertura, fuentes oficiales y opciones de descarga de los datos electorales."
---

## Cobertura

La API da acceso a los datos de [eleccionesdb](https://hmeleiro.github.io/eleccionesdb-etl/), una base de datos relacional con resultados electorales de España.

### Ámbitos electorales

| Tipo | Código | Cobertura temporal aprox. |
|---|---|---|
| **Congreso** (Generales) | `G` | 1977 – actualidad |
| **Andalucía** | `A` | 1982 – actualidad |
| **Aragón** | `A` | 1983 – actualidad |
| **Asturias** | `A` | 1983 – actualidad |
| **Baleares** | `A` | 1983 – actualidad |
| **Canarias** | `A` | 1983 – actualidad |
| **Castilla y León** | `A` | 1983 – actualidad |
| **Cataluña** | `A` | 1980 – actualidad |
| **Comunidad Valenciana** | `A` | 1983 – actualidad |
| **Comunidad de Madrid** | `A` | 1983 – actualidad |

### Niveles territoriales

Los resultados están disponibles a distintos niveles de la jerarquía territorial:

- **Comunidad autónoma** (`ccaa`)
- **Provincia** (`provincia`)
- **Municipio** (`municipio`)
- **Sección censal** (`seccion`)

La disponibilidad de cada nivel varía según la comunidad y la convocatoria.

## Fuentes de datos

Los datos provienen de **fuentes oficiales** de cada comunidad autónoma:

- **Portales de datos abiertos** autonómicos y estatales
- **APIs institucionales**: Junta de Andalucía, PARCAN (Canarias), etc.
- **Institutos estadísticos**: IBESTAT (Baleares), ISTAC (Canarias), SADEI (Asturias), etc.
- **Paquetes R**: [`infoelectoral`](https://github.com/rOpenSpain/infoelectoral) para datos del Ministerio del Interior
- **Datos históricos a nivel de mesa**: [Spanish Electoral Archive (SEA)](https://gipeyop.uv.es/gipeyop/sea.html) del GIPEYOP (Universitat de València)

Para el listado completo y detallado de fuentes por comunidad autónoma, consulta la [documentación de fuentes de datos](https://hmeleiro.github.io/eleccionesdb-etl/fuentes.html) del proyecto eleccionesdb.

## Modelo de datos

Los datos siguen un **esquema estrella** con:

- **5 tablas de dimensiones**: tipos de elección, elecciones, territorios (con jerarquía CCAA → provincia → municipio → sección), recodificaciones de partidos y partidos.
- **2 tablas de hechos principales**: resumen territorial (censo, participación, votos válidos/blancos/nulos) y votos territoriales (votos y representantes electos por partido).
- **2 tablas CERA**: resumen y votos de residentes ausentes.

Para más detalles, consulta el [modelo de datos](https://hmeleiro.github.io/eleccionesdb-etl/modelo-datos.html) de eleccionesdb.

## Paquete R

El paquete [`eleccionesdb`](https://hmeleiro.github.io/eleccionesdb-r/) permite consultar esta API directamente desde R. Devuelve tibbles listos para análisis, gestiona la paginación automáticamente y aplana las estructuras JSON anidadas.

```r
# Instalación
remotes::install_github("hmeleiro/eleccionesdb-r")

# Ejemplo rápido
library(eleccionesdb)
elecciones <- edb_elecciones(tipo_eleccion = "G")
resultados <- edb_resultados_combinados(eleccion_id = 208, tipo_territorio = "provincia")
```

Más información y ejemplos en la [documentación del paquete](https://hmeleiro.github.io/eleccionesdb-r/).

## Descarga directa de datos

Además de consumir los datos a través de esta API, puedes descargar la base de datos completa en tres formatos:

| Formato | Caso de uso | Descripción |
|---|---|---|
| **Parquet** | Análisis con R / Python / DuckDB | Tablas individuales normalizadas |
| **SQLite** | Consultas SQL, exploración relacional | Esquema completo con PKs, FKs e índices |
| **CSV** | Uso rápido, hojas de cálculo | Tablas de hechos pre-joineadas con dimensiones |

Consulta la sección de [descargas](https://hmeleiro.github.io/eleccionesdb-etl/descargas.html) del proyecto eleccionesdb.

## Enlaces

- [**eleccionesdb — Web del proyecto**](https://hmeleiro.github.io/eleccionesdb-etl/) — Documentación completa de la base de datos
- [**Fuentes de datos**](https://hmeleiro.github.io/eleccionesdb-etl/fuentes.html) — Listado detallado por comunidad
- [**Modelo de datos**](https://hmeleiro.github.io/eleccionesdb-etl/modelo-datos.html) — Diagrama E/R y descripción de tablas
- [**Descargas**](https://hmeleiro.github.io/eleccionesdb-etl/descargas.html) — Parquet, SQLite y CSV
- [**Código fuente del ETL**](https://github.com/hmeleiro/eleccionesdb-etl) — Repositorio en GitHub
- [**`eleccionesdb` — Paquete R**](https://hmeleiro.github.io/eleccionesdb-r/) — Cliente R para consultar la API
