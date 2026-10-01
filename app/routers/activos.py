from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models import Activo, ActivoCreate

router = APIRouter(prefix="/activos", tags=["activos"])

@router.post("")
def crear_activo(activo_in: ActivoCreate, session: Session = Depends(get_session)):
    activo = Activo.model_validate(activo_in)
    session.add(activo)
    session.commit()
    session.refresh(activo)
    return activo

@router.get("")
def listar_activos(session: Session = Depends(get_session)):
    return session.exec(select(Activo)).all()

@router.patch("/{activo_id}")
def actualizar_activo(activo_id: int, km_actuales: float, session: Session = Depends(get_session)):
    activo = session.get(Activo, activo_id)
    if not activo:
        raise HTTPException(status_code=404, detail="Activo no encontrado")
    activo.km_actuales = km_actuales
    session.add(activo)
    session.commit()
    session.refresh(activo)
    return activo