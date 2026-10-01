from typing import Optional
from datetime import date
from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator

class Activo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    tipo: str
    matricula_o_codigo: str
    fecha_alta: date
    km_actuales: Optional[float] = None
    horas_uso_actuales: Optional[float] = None
    estado: str = "activo"

    mantenimientos: list["Mantenimiento"] = Relationship(back_populates="activo")


class TipoMantenimiento(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str  # ej. "cambio de aceite", "revisión ITV"
    periodicidad_km: Optional[float] = None
    periodicidad_dias: Optional[int] = None

    mantenimientos: list["Mantenimiento"] = Relationship(back_populates="tipo_mantenimiento")

    
class Mantenimiento(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    activo_id: int = Field(foreign_key="activo.id")
    tipo_mantenimiento_id: int = Field(foreign_key="tipomantenimiento.id")
    fecha_realizado: date
    km_en_ese_momento: Optional[float] = None
    coste: Optional[float] = None
    observaciones: Optional[str] = None

    activo: Optional[Activo] = Relationship(back_populates="mantenimientos")
    tipo_mantenimiento: Optional[TipoMantenimiento] = Relationship(back_populates="mantenimientos")

class ActivoCreate(SQLModel):
    nombre: str
    tipo: str
    matricula_o_codigo: str
    fecha_alta: date
    km_actuales: Optional[float] = None
    horas_uso_actuales: Optional[float] = None
    estado: str = "activo"

class MantenimientoCreate(SQLModel):
    activo_id: int
    tipo_mantenimiento_id: int
    fecha_realizado: date
    km_en_ese_momento: Optional[float] = None
    coste: Optional[float] = None
    observaciones: Optional[str] = None