import os
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")


def get_client() -> Client:
    """Retorna um cliente autenticado do Supabase."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError(
            "Variáveis de ambiente SUPABASE_URL e SUPABASE_KEY não configuradas."
        )
    return create_client(SUPABASE_URL, SUPABASE_KEY)


# ------------------------------------------------------------------
# Funções de acesso ao banco
# ------------------------------------------------------------------

def db_listar_gastos() -> list[dict]:
    """Busca todos os gastos salvos no banco, ordenados do mais recente."""
    client = get_client()
    resposta = client.table("gastos").select("*").order("id", desc=True).execute()
    return resposta.data


def db_adicionar_gasto(valor: float, descricao: str) -> dict:
    """Insere um novo gasto e retorna o registro criado."""
    client = get_client()
    resposta = (
        client.table("gastos")
        .insert({"valor": valor, "descricao": descricao})
        .execute()
    )
    return resposta.data[0]


def db_remover_gasto(gasto_id: int) -> dict | None:
    """Remove um gasto pelo ID. Retorna o registro removido ou None."""
    client = get_client()
    resposta = (
        client.table("gastos")
        .delete()
        .eq("id", gasto_id)
        .execute()
    )
    if not resposta.data:
        return None
    return resposta.data[0]


def db_calcular_total() -> float:
    """Soma todos os valores de gastos diretamente no banco."""
    gastos = db_listar_gastos()
    return sum(g["valor"] for g in gastos)
