---
title: "Ejemplos de uso"
description: "Peticiones y respuestas reales de la API EleccionesDB."
---

## Autenticación por API key

Todos los endpoints de `/v1/*` requieren el header `X-API-Key`.

### Ejemplo de petición autenticada

```bash
curl -H "X-API-Key: TU_API_KEY" https://api.spainelectoralproject.com/v1/elecciones?limit=1
```

### Ejemplo de error 401

Si la clave es inválida, revocada o falta:

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

Ejemplos reales de peticiones y respuestas de la API. Todos los ejemplos usan `https://api.spainelectoralproject.com` como base URL.

## Health check

```
GET /health
```

```json
{
  "status": "ok",
  "environment": "production",
  "database": "ok"
}
```

## Tipos de elección

Lista completa del catálogo (array simple, sin paginación).

```
GET /v1/tipos-eleccion
```

```json
[
  {"codigo": "A", "descripcion": "Autómicas"},
  {"codigo": "E", "descripcion": "Europeas"},
  {"codigo": "G", "descripcion": "Congreso"},
  {"codigo": "L", "descripcion": "Locales"},
  {"codigo": "S", "descripcion": "Senado"}
]
```

## Listado de elecciones (paginado)

```
GET /v1/elecciones?limit=3
```

```json
{
  "total": 254,
  "skip": 0,
  "limit": 3,
  "data": [
    {
      "id": 1,
      "tipo_eleccion": "G",
      "year": "1977",
      "mes": "06",
      "dia": "15",
      "fecha": "1977-06-15",
      "descripcion": "Elecciones Generales 1977",
      "ambito": "Nacional",
      "slug": "elecciones-generales-1977"
    },
    {
      "id": 2,
      "tipo_eleccion": "G",
      "year": "1979",
      "mes": "03",
      "dia": "01",
      "fecha": "1979-03-01",
      "descripcion": "Elecciones Generales 1979",
      "ambito": "Nacional",
      "slug": "elecciones-generales-1979"
    },
    {
      "id": 3,
      "tipo_eleccion": "A",
      "year": "1979",
      "mes": "04",
      "dia": "03",
      "fecha": "1979-04-03",
      "descripcion": "Elecciones Autonómicas Navarra 1979",
      "ambito": "Autonómico",
      "slug": "elecciones-autonomicas-1979"
    }
  ]
}
```

## Elecciones filtradas por tipo y año

Se pueden combinar varios filtros. Para múltiples valores del mismo filtro se repite el parámetro.

```
GET /v1/elecciones?tipo_eleccion=G&year=2019&limit=5
```

```json
{
  "total": 2,
  "skip": 0,
  "limit": 5,
  "data": [
    {
      "id": 208,
      "tipo_eleccion": "G",
      "year": "2019",
      "mes": "04",
      "dia": "28",
      "fecha": "2019-04-28",
      "descripcion": "Elecciones Generales 2019",
      "ambito": "Nacional",
      "slug": "elecciones-generales-2019"
    },
    {
      "id": 226,
      "tipo_eleccion": "G",
      "year": "2019",
      "mes": "11",
      "dia": "10",
      "fecha": "2019-11-10",
      "descripcion": "Elecciones Generales 2019",
      "ambito": "Nacional",
      "slug": "elecciones-generales-2019"
    }
  ]
}
```

## Detalle de una elección

Incluye el tipo de elección como objeto expandido.

```
GET /v1/elecciones/208
```

```json
{
  "id": 208,
  "tipo_eleccion": "G",
  "year": "2019",
  "mes": "04",
  "dia": "28",
  "fecha": "2019-04-28",
  "codigo_ccaa": "99",
  "numero_vuelta": 1,
  "descripcion": "Elecciones Generales 2019",
  "ambito": "Nacional",
  "slug": "elecciones-generales-2019",
  "tipo": {
    "codigo": "G",
    "descripcion": "Congreso"
  }
}
```

## Fuente de una elección

Devuelve la fuente oficial de los datos de una elección. Responde 404 si la elección no tiene fuente registrada.

```
GET /v1/elecciones/208/fuente
```

```json
{
  "eleccion_id": 1,
  "fuente": "Ministerio del Interior (Infoelectoral)",
  "url_fuente": "https://infoelectoral.interior.gob.es/",
  "observaciones": "Paquete R infoelectoral"
}
```

## Territorios por tipo

```
GET /v1/territorios?tipo=ccaa&limit=3
```

```json
{
  "total": 19,
  "skip": 0,
  "limit": 3,
  "data": [
    {
      "id": 1,
      "nombre": "Andalucía",
      "tipo": "ccaa",
      "codigo_ccaa": "01",
      "codigo_provincia": null,
      "codigo_municipio": null,
      "codigo_distrito": null,
      "codigo_seccion": null,
      "parent_id": null
    },
    {
      "id": 2,
      "nombre": "Aragón",
      "tipo": "ccaa",
      "codigo_ccaa": "02",
      "codigo_provincia": null,
      "codigo_municipio": null,
      "codigo_distrito": null,
      "codigo_seccion": null,
      "parent_id": null
    },
    {
      "id": 3,
      "nombre": "Asturias",
      "tipo": "ccaa",
      "codigo_ccaa": "03",
      "codigo_provincia": null,
      "codigo_municipio": null,
      "codigo_distrito": null,
      "codigo_seccion": null,
      "parent_id": null
    }
  ]
}
```

## Navegación jerárquica de territorios

Los hijos directos de un territorio (p. ej., provincias de Andalucía).

```
GET /v1/territorios/1/hijos?limit=3
```

```json
{
  "total": 8,
  "skip": 0,
  "limit": 3,
  "data": [
    {
      "id": 20,
      "nombre": "Almería",
      "tipo": "provincia",
      "codigo_ccaa": "01",
      "codigo_provincia": "04",
      "codigo_municipio": null,
      "codigo_distrito": null,
      "codigo_seccion": null,
      "parent_id": 1
    },
    {
      "id": 21,
      "nombre": "Cádiz",
      "tipo": "provincia",
      "codigo_ccaa": "01",
      "codigo_provincia": "11",
      "codigo_municipio": null,
      "codigo_distrito": null,
      "codigo_seccion": null,
      "parent_id": 1
    },
    {
      "id": 22,
      "nombre": "Córdoba",
      "tipo": "provincia",
      "codigo_ccaa": "01",
      "codigo_provincia": "14",
      "codigo_municipio": null,
      "codigo_distrito": null,
      "codigo_seccion": null,
      "parent_id": 1
    }
  ]
}
```

## Búsqueda de territorios por nombre

```
GET /v1/territorios?nombre=madrid&tipo=ccaa
```

```json
{
  "total": 1,
  "skip": 0,
  "limit": 50,
  "data": [
    {
      "id": 13,
      "nombre": "Comunidad de Madrid",
      "tipo": "ccaa",
      "codigo_ccaa": "13",
      "codigo_provincia": null,
      "codigo_municipio": null,
      "codigo_distrito": null,
      "codigo_seccion": null,
      "parent_id": null
    }
  ]
}
```

## Búsqueda de partidos por siglas

```
GET /v1/partidos?siglas=psoe&limit=3
```

```json
{
  "total": 345,
  "skip": 0,
  "limit": 3,
  "data": [
    {
      "id": 9451,
      "siglas": "PSOE",
      "denominacion": "PARTIDO SOCIALISTA OBRERO ESPAÑOL",
      "recode_id": 1,
      "recode": {
        "id": 1,
        "agrupacion": "PSOE",
        "color": "#E30613"
      }
    },
    {
      "id": 9452,
      "siglas": "PSOE-A",
      "denominacion": "PARTIDO SOCIALISTA OBRERO ESPAÑOL DE ANDALUCÍA",
      "recode_id": 1,
      "recode": {
        "id": 1,
        "agrupacion": "PSOE",
        "color": "#E30613"
      }
    },
    {
      "id": 9453,
      "siglas": "PSC-PSOE",
      "denominacion": "PARTIT DELS SOCIALISTES DE CATALUNYA",
      "recode_id": 1,
      "recode": {
        "id": 1,
        "agrupacion": "PSOE",
        "color": "#E30613"
      }
    }
  ]
}
```

## Resultados: totales territoriales

Totales de participación para las Generales de abril de 2019 en Madrid (provincia).

```
GET /v1/resultados/totales-territorio?eleccion_id=208&tipo_territorio=provincia&codigo_provincia=28
```

```json
{
  "total": 1,
  "skip": 0,
  "limit": 50,
  "data": [
    {
      "eleccion_id": 208,
      "territorio_id": 33,
      "censo": 4727940,
      "votantes": 3603490,
      "votos_validos": 3571793,
      "votos_nulos": 31697,
      "votos_blancos": 13543
    }
  ]
}
```

## Resultados: votos por partido

Votos en las mismas elecciones y territorio, ordenados por votos (descendente).

```
GET /v1/resultados/votos-partido?eleccion_id=208&tipo_territorio=provincia&codigo_provincia=28&limit=5
```

```json
{
  "total": 21,
  "skip": 0,
  "limit": 5,
  "data": [
    {
      "eleccion_id": 208,
      "territorio_id": 33,
      "partido_id": 9451,
      "votos": 1094925,
      "electos": 12
    },
    {
      "eleccion_id": 208,
      "territorio_id": 33,
      "partido_id": 15233,
      "votos": 832812,
      "electos": 9
    },
    {
      "eleccion_id": 208,
      "territorio_id": 33,
      "partido_id": 14965,
      "votos": 618517,
      "electos": 7
    },
    {
      "eleccion_id": 208,
      "territorio_id": 33,
      "partido_id": 14946,
      "votos": 534819,
      "electos": 5
    },
    {
      "eleccion_id": 208,
      "territorio_id": 33,
      "partido_id": 14893,
      "votos": 335038,
      "electos": 3
    }
  ]
}
```

## Resultados combinados

Vista desnormalizada con partido (+ recode), territorio y elección expandidos.

```
GET /v1/resultados/combinados?eleccion_id=208&tipo_territorio=provincia&codigo_provincia=28&limit=2
```

```json
{
  "total": 21,
  "skip": 0,
  "limit": 2,
  "data": [
    {
      "eleccion_id": 208,
      "territorio_id": 33,
      "partido_id": 9451,
      "votos": 1094925,
      "electos": 12,
      "partido": {
        "id": 9451,
        "siglas": "PSOE",
        "denominacion": "PARTIDO SOCIALISTA OBRERO ESPAÑOL",
        "recode_id": 1,
        "recode": {
          "id": 1,
          "agrupacion": "PSOE",
          "color": "#E30613"
        }
      },
      "territorio": {
        "id": 33,
        "nombre": "Madrid",
        "tipo": "provincia",
        "codigo_ccaa": "13",
        "codigo_provincia": "28"
      },
      "eleccion": {
        "id": 208,
        "tipo_eleccion": "G",
        "year": "2019",
        "mes": "04",
        "descripcion": "Elecciones Generales 2019"
      }
    },
    {
      "eleccion_id": 208,
      "territorio_id": 33,
      "partido_id": 15233,
      "votos": 832812,
      "electos": 9,
      "partido": {
        "id": 15233,
        "siglas": "PP",
        "denominacion": "PARTIDO POPULAR",
        "recode_id": 2,
        "recode": {
          "id": 2,
          "agrupacion": "PP",
          "color": "#0056A0"
        }
      },
      "territorio": {
        "id": 33,
        "nombre": "Madrid",
        "tipo": "provincia",
        "codigo_ccaa": "13",
        "codigo_provincia": "28"
      },
      "eleccion": {
        "id": 208,
        "tipo_eleccion": "G",
        "year": "2019",
        "mes": "04",
        "descripcion": "Elecciones Generales 2019"
      }
    }
  ]
}
```

## Desde R

Si trabajas con R, puedes usar el paquete [`eleccionesdb`](https://eleccionesdb-r.spainelectoralproject.com/) para consultar la API sin construir peticiones HTTP manualmente:

```r
library(eleccionesdb)

# Elecciones generales
generales <- edb_elecciones(tipo_eleccion = "G")

# Resultados combinados (votos + info territorial) de las generales de abril 2019 en Madrid
resultados <- edb_resultados_combinados(
  eleccion_id = 208,
  tipo_territorio = "provincia",
  codigo_provincia = "28"
)
```

Más información en la [documentación del paquete](https://eleccionesdb-r.spainelectoralproject.com/).
