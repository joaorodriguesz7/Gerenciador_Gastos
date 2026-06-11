from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

from src.database import (
    db_listar_gastos,
    db_adicionar_gasto,
    db_remover_gasto,
    db_calcular_total,
)

app = FastAPI(title="Gerenciador de Gastos", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------
# Schema de entrada (Pydantic valida automaticamente)
# -------------------------------------------------
class Gasto(BaseModel):
    valor: float
    descricao: str


# -------------------------------------------------
# Rotas CRUD — agora com persistência no Supabase
# -------------------------------------------------

@app.get("/")
def raiz():
    return {"mensagem": "Gerenciador de Gastos — API online ✅"}


@app.post("/gastos", status_code=201)
def adicionar_gasto(gasto: Gasto):
    if gasto.valor < 0:
        raise HTTPException(status_code=400, detail="Valor não pode ser negativo")
    novo = db_adicionar_gasto(gasto.valor, gasto.descricao)
    return {"mensagem": "Gasto adicionado", "gasto": novo}


@app.get("/gastos")
def listar_gastos():
    return {"gastos": db_listar_gastos()}


@app.get("/total")
def ver_total():
    return {"total_brl": db_calcular_total()}


@app.delete("/gastos/{gasto_id}", status_code=200)
def remover_gasto(gasto_id: int):
    removido = db_remover_gasto(gasto_id)
    if removido is None:
        raise HTTPException(status_code=404, detail="Gasto não encontrado")
    return {"mensagem": "Gasto removido", "gasto": removido}


# -------------------------------------------------
# Integração com API de câmbio (AwesomeAPI)
# -------------------------------------------------

def buscar_cotacao_dolar() -> float:
    """Busca a cotação atual do dólar em reais via AwesomeAPI."""
    url = "https://economia.awesomeapi.com.br/json/last/USD-BRL"
    resposta = requests.get(url, timeout=5)
    resposta.raise_for_status()
    dados = resposta.json()
    return float(dados["USDBRL"]["bid"])


@app.get("/total/dolar")
def ver_total_em_dolar():
    """Retorna o total dos gastos convertido para dólares (USD)."""
    try:
        cotacao = buscar_cotacao_dolar()
        total_brl = db_calcular_total()
        total_usd = round(total_brl / cotacao, 2)
        return {
            "total_brl": total_brl,
            "cotacao_usd_brl": cotacao,
            "total_usd": total_usd,
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Erro ao buscar cotação: {str(e)}")
