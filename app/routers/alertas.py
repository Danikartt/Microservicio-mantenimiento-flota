from datetime import date
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.database import get_session
from app.models import Activo, TipoMantenimiento

router = APIRouter(prefix="/alertas", tags=["alertas"])

@router.get("/pendientes")
def alertas_pendientes(session: Session = Depends(get_session)):
    activos = session.exec(select(Activo)).all()
    todos_los_tipos = session.exec(select(TipoMantenimiento)).all()
    alertas = []

    for activo in activos:
        ultimos_por_tipo = {}
        for m in activo.mantenimientos:
            tipo_id = m.tipo_mantenimiento_id
            if tipo_id not in ultimos_por_tipo or m.fecha_realizado > ultimos_por_tipo[tipo_id].fecha_realizado:
                ultimos_por_tipo[tipo_id] = m

        for tipo in todos_los_tipos:
            ultimo = ultimos_por_tipo.get(tipo.id)

            if ultimo is None:
                alertas.append({
                    "activo_id": activo.id,
                    "activo_nombre": activo.nombre,
                    "tipo_mantenimiento": tipo.nombre,
                    "vencido_por_km": None,
                    "vencido_por_fecha": None,
                    "ultimo_mantenimiento": None,
                    "motivo": "nunca realizado",
                })
                continue

            vencido_por_km = False
            vencido_por_fecha = False

            if tipo.periodicidad_km and activo.km_actuales is not None and ultimo.km_en_ese_momento is not None:
                km_recorridos = activo.km_actuales - ultimo.km_en_ese_momento
                vencido_por_km = km_recorridos >= tipo.periodicidad_km

            if tipo.periodicidad_dias:
                dias_pasados = (date.today() - ultimo.fecha_realizado).days
                vencido_por_fecha = dias_pasados >= tipo.periodicidad_dias

            if vencido_por_km or vencido_por_fecha:
                alertas.append({
                    "activo_id": activo.id,
                    "activo_nombre": activo.nombre,
                    "tipo_mantenimiento": tipo.nombre,
                    "vencido_por_km": vencido_por_km,
                    "vencido_por_fecha": vencido_por_fecha,
                    "ultimo_mantenimiento": ultimo.fecha_realizado,
                    "motivo": "periodicidad superada",
                })

    return alertas