from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.database import get_session
from app.models import Activo, Mantenimiento, MantenimientoCreate

router = APIRouter(tags=["mantenimientos"])

@router.post("/mantenimientos")
def crear_mantenimiento(mantenimiento_in: MantenimientoCreate, session: Session = Depends(get_session)):
    mantenimiento = Mantenimiento.model_validate(mantenimiento_in)
    session.add(mantenimiento)
    session.commit()
    session.refresh(mantenimiento)
    return mantenimiento

@router.get("/activos/{activo_id}/mantenimientos")
def listar_mantenimientos_de_activo(activo_id: int, session: Session = Depends(get_session)):
    activo = session.get(Activo, activo_id)
    if not activo:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    return activo.mantenimientos