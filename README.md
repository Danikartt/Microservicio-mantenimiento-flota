
# Microservicio de Mantenimiento de Flota

Microservicio en Python para el seguimiento de mantenimiento de una flota de vehículos: registro de activos, tipos de mantenimiento con periodicidad, historial de mantenimientos realizados y cálculo automático de alertas de mantenimiento pendiente o vencido (por kilometraje o por fecha).

## Stack

FastAPI · SQLModel · PostgreSQL · Alembic · pytest · Docker

Ver [ARQUITECTURA.md](./ARQUITECTURA.md) para el detalle del modelo de datos, la lógica de negocio y las decisiones de diseño.

## Requisitos

- Docker y Docker Compose

## Puesta en marcha

```bash
docker compose up --build
```

La API queda disponible en `http://localhost:8000`, con documentación interactiva (Swagger) en `http://localhost:8000/docs`.

## Migraciones

El esquema de base de datos se gestiona con Alembic. Tras cambiar un modelo:

```bash
docker compose exec api bash
alembic revision --autogenerate -m "descripción del cambio"
alembic upgrade head
```

## Tests

```bash
docker compose exec api bash
python -m pytest -v
```

## Endpoints principales

| Método | Ruta                              | Descripción                              |
|--------|------------------------------------|-------------------------------------------|
| POST   | `/activos`                         | Crear un activo                           |
| GET    | `/activos`                         | Listar activos                            |
| PATCH  | `/activos/{id}`                    | Actualizar km actuales de un activo       |
| POST   | `/tipos-mantenimiento`             | Crear un tipo de mantenimiento            |
| GET    | `/tipos-mantenimiento`             | Listar tipos de mantenimiento             |
| POST   | `/mantenimientos`                  | Registrar un mantenimiento realizado      |
| GET    | `/activos/{id}/mantenimientos`     | Historial de mantenimientos de un activo  |
| GET    | `/alertas/pendientes`              | Alertas de mantenimiento pendiente/vencido|

## Despliegue

Desplegado en [Render](https://render.com): API + PostgreSQL gestionado. Las migraciones de Alembic se aplican automáticamente al arrancar el contenedor (`start.sh`).

🔗 **API en vivo:** https://flota-api-ly54.onrender.com/docs

> **Nota sobre el plan gratuito**: el servicio web se "duerme" tras 15 minutos de inactividad (la primera petición tras ello puede tardar 30-50s), y la base de datos gratuita de Render no garantiza persistencia a largo plazo. El esquema se recupera automáticamente en cada deploy gracias a las migraciones versionadas de Alembic.

## Estado del proyecto

Completo y desplegado — próximas mejoras posibles: autenticación, endpoint de resumen de costes por activo, tests adicionales sobre `Mantenimiento` y `TipoMantenimiento`.

