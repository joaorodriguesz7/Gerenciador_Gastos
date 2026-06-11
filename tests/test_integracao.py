"""
Testes de integração — simulam o banco e a API externa de câmbio,
testando o comportamento end-to-end das rotas HTTP.
"""

from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.app import app, buscar_cotacao_dolar
import pytest

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_db(monkeypatch):
    """Mesma fixture de mock do banco usada nos testes unitários."""
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


# -------------------------------------------------------
# Teste 1: buscar_cotacao_dolar() retorna float correto
# quando a API externa responde normalmente.
# -------------------------------------------------------
def test_buscar_cotacao_dolar_sucesso():
    resposta_falsa = MagicMock()
    resposta_falsa.json.return_value = {"USDBRL": {"bid": "5.25"}}
    resposta_falsa.raise_for_status.return_value = None

    with patch("src.app.requests.get", return_value=resposta_falsa):
        cotacao = buscar_cotacao_dolar()

    assert isinstance(cotacao, float)
    assert cotacao == 5.25


# -------------------------------------------------------
# Teste 2: GET /total/dolar calcula conversão corretamente
# usando dados reais do banco (mockado) e câmbio mockado.
# -------------------------------------------------------
def test_endpoint_total_em_dolar():
    client.post("/gastos", json={"valor": 105.0, "descricao": "supermercado"})

    resposta_falsa = MagicMock()
    resposta_falsa.json.return_value = {"USDBRL": {"bid": "5.25"}}
    resposta_falsa.raise_for_status.return_value = None

    with patch("src.app.requests.get", return_value=resposta_falsa):
        resposta = client.get("/total/dolar")

    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["total_brl"] == 105.0
    assert dados["cotacao_usd_brl"] == 5.25
    assert dados["total_usd"] == 20.0  # 105 / 5.25 = 20.0


# -------------------------------------------------------
# Teste 3: retorna 503 quando a API de câmbio está fora.
# -------------------------------------------------------
def test_endpoint_total_dolar_api_indisponivel():
    client.post("/gastos", json={"valor": 50.0, "descricao": "teste"})

    with patch("src.app.requests.get", side_effect=Exception("Connection refused")):
        resposta = client.get("/total/dolar")

    assert resposta.status_code == 503
    assert "Erro ao buscar cotação" in resposta.json()["detail"]


# -------------------------------------------------------
# Teste 4 (novo): fluxo completo — adicionar, listar,
# verificar total e remover em sequência.
# -------------------------------------------------------
def test_fluxo_completo_crud():
    # Adiciona dois gastos
    r1 = client.post("/gastos", json={"valor": 80.0, "descricao": "aluguel"})
    r2 = client.post("/gastos", json={"valor": 20.0, "descricao": "internet"})
    assert r1.status_code == 201
    assert r2.status_code == 201

    # Lista e verifica quantidade
    lista = client.get("/gastos").json()["gastos"]
    assert len(lista) == 2

    # Verifica total
    total = client.get("/total").json()["total_brl"]
    assert total == 100.0

    # Remove o primeiro gasto pelo ID
    id_remover = r1.json()["gasto"]["id"]
    del_resp = client.delete(f"/gastos/{id_remover}")
    assert del_resp.status_code == 200

    # Total deve ser apenas o segundo gasto
    total_apos = client.get("/total").json()["total_brl"]
    assert total_apos == 20.0
