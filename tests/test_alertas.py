from fastapi.testclient import TestClient


def crear_activo(client: TestClient, km_actuales=0, nombre="Activo test"):
    response = client.post("/activos", json={
        "nombre": nombre,
        "tipo": "vehiculo",
        "matricula_o_codigo": "0000TST",
        "fecha_alta": "2026-01-01",
        "km_actuales": km_actuales,
        "estado": "activo",
    })
    return response.json()


def crear_tipo(client: TestClient, nombre="cambio de aceite", periodicidad_km=10000, periodicidad_dias=None):
    response = client.post("/tipos-mantenimiento", json={
        "nombre": nombre,
        "periodicidad_km": periodicidad_km,
        "periodicidad_dias": periodicidad_dias,
    })
    return response.json()


def crear_mantenimiento(client: TestClient, activo_id, tipo_id, fecha_realizado, km_en_ese_momento):
    response = client.post("/mantenimientos", json={
        "activo_id": activo_id,
        "tipo_mantenimiento_id": tipo_id,
        "fecha_realizado": fecha_realizado,
        "km_en_ese_momento": km_en_ese_momento,
    })
    return response.json()


def test_sin_mantenimientos_no_hay_alertas(client: TestClient):
    crear_activo(client, km_actuales=5000)
    response = client.get("/alertas/pendientes")
    assert response.status_code == 200
    assert response.json() == []


def test_activo_sin_mantenimiento_de_tipo_existente(client: TestClient):
    crear_activo(client, km_actuales=5000)
    crear_tipo(client, nombre="revisión ITV")

    response = client.get("/alertas/pendientes")
    alertas = response.json()

    assert len(alertas) == 1
    assert alertas[0]["motivo"] == "nunca realizado"
    assert alertas[0]["tipo_mantenimiento"] == "revisión ITV"


def test_mantenimiento_al_dia_no_genera_alerta(client: TestClient):
    activo = crear_activo(client, km_actuales=5000)
    tipo = crear_tipo(client, periodicidad_km=10000)
    crear_mantenimiento(client, activo["id"], tipo["id"], "2026-09-01", km_en_ese_momento=4500)

    response = client.get("/alertas/pendientes")
    assert response.json() == []


def test_vencido_por_km(client: TestClient):
    activo = crear_activo(client, km_actuales=15000)
    tipo = crear_tipo(client, periodicidad_km=10000, periodicidad_dias=None)
    crear_mantenimiento(client, activo["id"], tipo["id"], "2026-09-01", km_en_ese_momento=4000)

    response = client.get("/alertas/pendientes")
    alertas = response.json()

    assert len(alertas) == 1
    assert alertas[0]["vencido_por_km"] is True
    assert alertas[0]["vencido_por_fecha"] is False


def test_justo_en_el_umbral_cuenta_como_vencido(client: TestClient):
    activo = crear_activo(client, km_actuales=14000)
    tipo = crear_tipo(client, periodicidad_km=10000, periodicidad_dias=None)
    crear_mantenimiento(client, activo["id"], tipo["id"], "2026-09-01", km_en_ese_momento=4000)

    response = client.get("/alertas/pendientes")
    alertas = response.json()

    # 14000 - 4000 = 10000, exactamente la periodicidad -> según la lógica (>=), debe contar como vencido
    assert len(alertas) == 1
    assert alertas[0]["vencido_por_km"] is True


def test_usa_el_mantenimiento_mas_reciente(client: TestClient):
    activo = crear_activo(client, km_actuales=8000)
    tipo = crear_tipo(client, periodicidad_km=10000, periodicidad_dias=None)

    # Mantenimiento antiguo (haría saltar la alerta si se usara este)
    crear_mantenimiento(client, activo["id"], tipo["id"], "2025-01-01", km_en_ese_momento=0)
    # Mantenimiento más reciente (no debería saltar alerta)
    crear_mantenimiento(client, activo["id"], tipo["id"], "2026-08-01", km_en_ese_momento=6000)

    response = client.get("/alertas/pendientes")
    assert response.json() == []  # 8000 - 6000 = 2000, por debajo de 10000