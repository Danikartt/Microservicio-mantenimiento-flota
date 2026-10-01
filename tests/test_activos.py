from fastapi.testclient import TestClient

def test_crear_activo(client: TestClient):
    response = client.post("/activos", json={
        "nombre": "Furgoneta test",
        "tipo": "vehiculo",
        "matricula_o_codigo": "0000TST",
        "fecha_alta": "2026-01-01",
        "km_actuales": 1000,
        "estado": "activo",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Furgoneta test"
    assert data["id"] is not None

def test_listar_activos_vacio(client: TestClient):
    response = client.get("/activos")
    assert response.status_code == 200
    assert response.json() == []

def test_actualizar_activo_no_existente(client: TestClient):
    response = client.patch("/activos/999?km_actuales=5000")
    assert response.status_code == 404