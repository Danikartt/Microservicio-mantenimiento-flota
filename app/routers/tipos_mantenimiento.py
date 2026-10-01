from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.database import get_session
from app.models import TipoMantenimiento

router = APIRouter(prefix="/tipos-mantenimiento", tags=["tipos-mantenimiento"])

@router.post("")
def crear_tipo_mantenimiento(tipo: TipoMantenimiento, session: Session = Depends(get_session)):
    session.add(tipo)
    session.commit()
    session.refresh(tipo)
    return tipo

@router.get("")
def listar_tipos_mantenimiento(session: Session = Depends(get_session)):
    return session.exec(select(TipoMantenimiento)).all()