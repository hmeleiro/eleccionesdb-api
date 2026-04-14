---
title: "Desarrolladores"
description: "Accede programáticamente a datos electorales y de opinión pública en España."
layout: list
---

## Acceso a la API de eleccionesdb

La API de eleccionesdb permite acceder de forma programática a los datos electorales de España. Está diseñada para investigadores, periodistas y desarrolladores que quieran integrar estos datos en sus proyectos.

### ¿Qué puedo hacer con la API?

- Consultar resultados electorales históricos
- Acceder a datos armonizados de encuestas del CIS
- Integrar datos en aplicaciones, dashboards o investigaciones

### ¿Cómo empiezo?

Para utilizar la API necesitas una **API key**. El proceso es sencillo:

1. **Regístrate** como desarrollador proporcionando tu email, nombre, organización y uso previsto
2. **Verifica tu email** mediante el enlace que recibirás
3. **Obtén tu API key** y empieza a hacer peticiones

<div class="api-actions">
<a href="register/" class="btn btn-primary">Registrarse</a>
<a href="account/" class="btn btn-secondary">Panel de cuenta</a>
</div>

### ¿Has perdido tu API key?

Si has perdido el acceso a tu cuenta o tus claves, puedes [recuperar tu acceso](recover/) mediante un enlace temporal enviado a tu email.

### Documentación

La documentación completa de los endpoints está disponible en la [documentación de la API](https://api.spainelectoralproject.com/docs).

### Autenticación

Todas las peticiones a la API requieren autenticación mediante el header `X-API-Key`:

```
X-API-Key: tu_api_key_aquí
```
