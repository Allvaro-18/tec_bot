from fastapi.testclient import TestClient

from app.main import app
from app.services.rag import ADVERTENCIA, RESPUESTA_SIN_EVIDENCIA

client = TestClient(app)


def test_salud() -> None:
    response = client.get("/salud")
    assert response.status_code == 200
    assert response.json() == {"estado": "ok"}


def test_consulta_con_evidencia() -> None:
    response = client.post("/consultas", json={"pregunta": "¿Qué necesito para el servicio social?"})
    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {"respuesta", "fuentes", "advertencia"}
    assert isinstance(data["respuesta"], str) and data["respuesta"].strip()
    assert isinstance(data["fuentes"], list) and len(data["fuentes"]) >= 1
    assert data["fuentes"][0]["documento"] == "servicio-social.md"
    assert isinstance(data["fuentes"][0]["fragmento"], str) and data["fuentes"][0]["fragmento"].strip()
    assert data["advertencia"] == ADVERTENCIA


def test_consulta_sin_evidencia() -> None:
    response = client.post("/consultas", json={"pregunta": "¿Cuál es el horario de la cafetería?"})
    assert response.status_code == 200
    data = response.json()
    assert data["respuesta"] == RESPUESTA_SIN_EVIDENCIA
    assert data["fuentes"] == []
    assert data["advertencia"] == ADVERTENCIA


def test_consulta_pregunta_vacia() -> None:
    response = client.post("/consultas", json={"pregunta": "   "})
    assert response.status_code == 422


def test_pagina_chat() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "TecBot Académico" in response.text
