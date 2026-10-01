from fastapi import FastAPI
from app.routers import activos, mantenimientos, tipos_mantenimiento, alertas

app = FastAPI()

@app.on_event("startup")
def on_startup():
    pass  # el esquema lo gestiona Alembic

@app.get("/")
def read_root():
    return {"status": "ok"}

app.include_router(activos.router)
app.include_router(mantenimientos.router)
app.include_router(tipos_mantenimiento.router)
app.include_router(alertas.router)