---
title: "Datos y fuentes"
description: "Cobertura, fuentes oficiales y opciones de descarga de los datos electorales."
---

## Cobertura

La API da acceso a los datos de [eleccionesdb](https://eleccionesdb.spainelectoralproject.com/), una base de datos relacional con resultados electorales de España. 

Es recomendable leer la pagina sobre la [calidad de los datos](https://eleccionesdb.spainelectoralproject.com/calidad/).

### Ámbitos electorales

| Tipo | Código | Cobertura temporal aprox. |
|---|---|---|
| **Congreso** | `G` | 1977 – 2023 |
| **Municipales** | `L` | 1979 – 2023 |
| **Andalucía** | `A` | 1982 – 2022 |
| **Aragón** | `A` | 2007 – 2023 |
| **Asturias** | `A` | 1983 – 2023 |
| **Baleares** | `A` | 1983 – 2023 |
| **Canarias** | `A` | 1983 – 2023 |
| **Cantabria** | `A` | 1983 – 2023 |
| **Castilla y León** | `A` | 1983 – 2022 |
| **Castilla-La Mancha** | `A` | 1983 – 2023 |
| **Cataluña** | `A` | 1980 – 2023 |
| **Comunidad Valenciana** | `A` | 1983 – 2023 |
| **Extremadura** | `A` | 1983 – 2023 |
| **Galicia** | `A` | 1981 – 2024 |
| **Comunidad de Madrid** | `A` | 1983 – 2023 |
| **Región de Murcia** | `A` | 1983 – 2023 |
| **Comunidad Foral de Navarra** | `A` | 1979 – 2023 |
| **País Vasco** | `A` | 1980 – 2024 |
| **La Rioja** | `A` | 1983 – 2023 |

### Niveles territoriales

Los resultados están disponibles a distintos niveles de la jerarquía territorial:

- **Comunidad autónoma** (`ccaa`)
- **Provincia** (`provincia`)
- **Municipio** (`municipio`)
- **Sección censal** (`seccion`)

La disponibilidad de cada nivel varía según la comunidad y la convocatoria.

## Fuentes de datos

Los datos provienen de **fuentes oficiales**:

- **Portales de datos abiertos** autonómicos y estatales
- **APIs institucionales**: Junta de Andalucía, PARCAN (Canarias), etc.
- **Institutos estadísticos**: IBESTAT (Baleares), ISTAC (Canarias), SADEI (Asturias), etc.
- **Paquetes R**: [`infoelectoral`](https://github.com/rOpenSpain/infoelectoral) para datos del Ministerio del Interior
- [**Spanish Electoral Archive (SEA)**](https://gipeyop.uv.es/gipeyop/sea.html) del GIPEYOP (Universitat de València) para otros procesos electorales que no estaban disponibles por fuentes oficiales directas.

Para el listado completo y detallado de fuentes por comunidad autónoma, consulta la [documentación de fuentes de datos](https://eleccionesdb.spainelectoralproject.com/fuentes) del proyecto eleccionesdb.

## Modelo de datos

Los datos siguen un **esquema estrella** con:

- **5 tablas de dimensiones**: tipos de elección, elecciones, territorios (con jerarquía CCAA → provincia → municipio → sección), recodificaciones de partidos y partidos.
- **2 tablas de hechos principales**: resumen territorial (censo, participación, votos válidos/blancos/nulos) y votos territoriales (votos y representantes electos por partido).
- **2 tablas CERA**: resumen y votos de residentes ausentes.

Para más detalles, consulta el [modelo de datos](https://eleccionesdb.spainelectoralproject.com/modelo-datos/) de eleccionesdb.

## Paquete R

El paquete [`eleccionesdb`](https://eleccionesdb-r.spainelectoralproject.com/) permite consultar esta API directamente desde R. Devuelve tibbles listos para análisis, gestiona la paginación automáticamente y aplana las estructuras JSON anidadas.

```r
# Instalación
remotes::install_github("hmeleiro/eleccionesdb-r")

# Ejemplo rápido
library(eleccionesdb)
elecciones <- edb_elecciones(tipo_eleccion = "G")
resultados <- edb_resultados_combinados(eleccion_id = 208, tipo_territorio = "provincia")
```

Más información y ejemplos en la [documentación del paquete](https://eleccionesdb-r.spainelectoralproject.com/).

## Descarga directa de datos

Además de consumir los datos a través de esta API, puedes descargar la base de datos completa en tres formatos:

| Formato | Caso de uso | Descripción |
|---|---|---|
| **Parquet** | Análisis con R / Python / DuckDB | Tablas individuales normalizadas |
| **SQLite** | Consultas SQL, exploración relacional | Esquema completo con PKs, FKs e índices |
| **CSV** | Uso rápido, hojas de cálculo | Tablas de hechos pre-joineadas con dimensiones |

Consulta la sección de [descargas](https://eleccionesdb.spainelectoralproject.com/descargas/) del proyecto eleccionesdb.

## Enlaces

- [**eleccionesdb — Web del proyecto**](https://eleccionesdb.spainelectoralproject.com/) — Documentación completa de la base de datos
- [**Código fuente del ETL**](https://github.com/hmeleiro/eleccionesdb-etl/) — Repositorio en GitHub
- [**Fuentes de datos**](https://eleccionesdb.spainelectoralproject.com/fuentes/) — Listado detallado por comunidad
- [**Modelo de datos**](https://eleccionesdb.spainelectoralproject.com/modelo-datos/) — Diagrama E/R y descripción de tablas
- [**Descargas**](https://eleccionesdb.spainelectoralproject.com/descargas/) — Parquet, SQLite y CSV
- [**`eleccionesdb` — Paquete R**](https://eleccionesdb-r.spainelectoralproject.com/) — Cliente R para consultar la API
