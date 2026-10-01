# Arquitectura — Microservicio de Mantenimiento de Flota

## Visión general

Microservicio backend para el seguimiento de mantenimiento de una flota de vehículos. Permite registrar activos, definir tipos de mantenimiento con su periodicidad, registrar mantenimientos realizados y calcular automáticamente qué activos tienen mantenimiento pendiente o vencido.

## Stack tecnológico

| Componente        | Tecnología                          |
|-------------------|--------------------------------------|
| Lenguaje          | Python 3.12                          |
| Framework API     | FastAPI                              |
| ORM / Validación  | SQLModel (SQLAlchemy + Pydantic)     |
| Base de datos     | PostgreSQL 16                        |
| Migraciones       | Alembic                              |
| Testing           | pytest + httpx (TestClient)          |
| Contenedores      | Docker + Docker Compose              |
| Despliegue        | Render                               |

## Estructura de carpetas

```
Microservicio_mantenimiento_flota/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── alembic.ini
├── alembic/
│   ├── env.py
│   └── versions/
├── app/
│   ├── main.py            # Punto de entrada, registro de routers
│   ├── database.py        # Engine, conexión, dependencia get_session
│   ├── models.py          # Modelos SQLModel (tabla + entrada/Create)
│   └── routers/
│       ├── activos.py
│       ├── mantenimientos.py
│       ├── tipos_mantenimiento.py
│       └── alertas.py
└── tests/
    ├── conftest.py         # Fixtures: session (SQLite en memoria) y client
    ├── test_activos.py
    └── test_alertas.py
```

## Modelo de datos

### `Activo`
Representa un vehículo o máquina de la flota.
- `id`, `nombre`, `tipo`, `matricula_o_codigo`, `fecha_alta`
- `km_actuales`, `horas_uso_actuales` (ambos opcionales)
- `estado` (activo/baja)
- Relación 1:N con `Mantenimiento`

### `TipoMantenimiento`
Catálogo de tipos de mantenimiento y su periodicidad.
- `id`, `nombre`
- `periodicidad_km`, `periodicidad_dias` (opcionales, puede tener uno, otro o ambos)
- Relación 1:N con `Mantenimiento`

### `Mantenimiento`
Histórico de mantenimientos realizados sobre un activo.
- `id`, `activo_id` (FK), `tipo_mantenimiento_id` (FK)
- `fecha_realizado`, `km_en_ese_momento`, `coste`, `observaciones`

### Patrón de modelos: `Create` vs tabla

Para los modelos con campos `date` (`Activo`, `Mantenimiento`), se usa un modelo de entrada separado (`ActivoCreate`, `MantenimientoCreate`) sin `table=True`. Motivo: los modelos SQLModel con `table=True` no ejecutan la validación de Pydantic al construirse desde JSON, por lo que un `date` puede llegar como string sin convertir a la base de datos. Postgres lo tolera (cast implícito); SQLite (usado en tests) no, y lo rechaza. El modelo `XCreate` fuerza la validación/conversión antes de construir el objeto de tabla con `Activo.model_validate(activo_in)`.

## Lógica de negocio: cálculo de alertas

Endpoint `GET /alertas/pendientes`. Para cada activo:
1. Agrupa sus mantenimientos por tipo, quedándose con el más reciente de cada uno (por `fecha_realizado`).
2. Compara contra **todos** los tipos de mantenimiento existentes (no solo los que el activo ya tiene registrados), para detectar también mantenimientos que nunca se han realizado.
3. Para cada tipo:
   - Si no hay mantenimiento previo → alerta con `"motivo": "nunca realizado"`.
   - Si hay mantenimiento previo → compara `km_actuales - km_en_ese_momento` contra `periodicidad_km`, y días transcurridos desde `fecha_realizado` contra `periodicidad_dias`. Vencido si se cumple **cualquiera** de las dos condiciones (`>=`).

## Migraciones (Alembic)

El esquema de la base de datos se gestiona exclusivamente con Alembic, no con `create_all()` en el arranque de la app. Flujo al cambiar un modelo:

```bash
docker compose exec api bash
alembic revision --autogenerate -m "descripción del cambio"
alembic upgrade head
```

## Testing

- Base de datos de test: SQLite en memoria (fixture `session` en `conftest.py`), aislada de Postgres.
- La dependencia `get_session` se sobreescribe en los tests (`app.dependency_overrides`) para inyectar la sesión de test.
- Cobertura actual: 9 tests — CRUD básico de `Activo` y casos de la lógica de alertas (sin mantenimiento previo, vencido por km, umbral exacto, mantenimiento más reciente entre varios).

## Despliegue

Objetivo: Render (web service para la API + PostgreSQL gestionado). Pendiente de configurar.

## Pendiente de pulir

- Aplicar el patrón `Create` a `MantenimientoCreate`/`TipoMantenimientoCreate` si se añaden campos `date` a `TipoMantenimiento` en el futuro.
- Sustituir `@app.on_event("startup")` (deprecado) por el patrón `lifespan` de FastAPI.