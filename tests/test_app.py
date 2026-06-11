"""
Testes unitários — toda chamada ao banco é mockada,
então os testes rodam sem precisar de conexão real.
"""

from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.app import app
import pytest

client = TestClient(app)

# Gastos fictícios que simulam retorno do banco
GASTOS_FALSOS = [
    {"id": 1, "valor": 50.0, "descricao": "mercado"},
    {"id": 2, "valor": 30.0, "descricao": "lanche"},
]


@pytest.fixture(autouse=True)
def mock_db(monkeypatch):
    """Substitui todas as funções de banco por versões fake antes de cada teste."""
    gastos_em_memoria: list[dict] = []
    proximo_id = {"v": 1}

    def fake_listar():
        return list(gastos_em_memoria)

    def fake_adicionar(valor, descricao):
        novo = {"id": proximo_id["v"], "valor": valor, "descricao": descricao}
        gastos_em_memoria.append(novo)
        proximo_id["v"] += 1
        return novo

    def fake_remover(gasto_id):
        for i, g in enumerate(gastos_em_memoria):
            if g["id"] == gasto_id:
                return gastos_em_memoria.pop(i)
        return None

    def fake_total():
        return sum(g["valor"] for g in gastos_em_memoria)

    monkeypatch.setattr("src.app.db_listar_gastos", fake_listar)
    monkeypatch.setattr("src.app.db_adicionar_gasto", fake_adicionar)
    monkeypatch.setattr("src.app.db_remover_gasto", fake_remover)
    monkeypatch.setattr("src.app.db_calcular_total", fake_total)

    yield
    gastos_em_memoria.clear()


# ------------------------------------------------------------------
# Testes das rotas
# ------------------------------------------------------------------

def test_adicionar_gasto():
    resposta = client.post("/gastos", json={"valor": 50.0, "descricao": "mercado"})
    assert resposta.status_code == 201
    assert resposta.json()["gasto"]["valor"] == 50.0


def test_valor_negativo():
    resposta = client.post("/gastos", json={"valor": -10.0, "descricao": "erro"})
    assert resposta.status_code == 400


def test_listar_gastos():
    client.post("/gastos", json={"valor": 30.0, "descricao": "lanche"})
    resposta = client.get("/gastos")
    assert resposta.status_code == 200
    assert len(resposta.json()["gastos"]) == 1


def test_ver_total():
    client.post("/gastos", json={"valor": 100.0, "descricao": "supermercado"})
    client.post("/gastos", json={"valor": 50.0, "descricao": "farmácia"})
    resposta = client.get("/total")
    assert resposta.json()["total_brl"] == 150.0


def test_remover_gasto():
    adicionar = client.post("/gastos", json={"valor": 20.0, "descricao": "lanche"})
    gasto_id = adicionar.json()["gasto"]["id"]
    resposta = client.delete(f"/gastos/{gasto_id}")
    assert resposta.status_code == 200
    assert client.get("/total").json()["total_brl"] == 0.0


def test_remover_id_invalido():
    resposta = client.delete("/gastos/9999")
    assert resposta.status_code == 404
