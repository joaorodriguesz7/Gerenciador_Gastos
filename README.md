# 💰 Gerenciador de Gastos Pessoais

🔗 **Frontend:** https://joaorodriguesz7.github.io/Gerenciador_Gastos/
🚀 **API:** https://gerenciador-gastos-jade.vercel.app
📖 **Documentação:** https://gerenciador-gastos-jade.vercel.app/docs

---

## 📌 Problema
Muitas pessoas enfrentam dificuldades para manter o controle dos seus gastos no dia a dia. Pequenas despesas, como lanches, transporte ou compras rápidas, acabam não sendo registradas e, ao final do mês, o usuário não consegue identificar para onde seu dinheiro foi.

## 💡 Solução
O sistema permite registrar gastos, visualizar uma lista com todas as despesas e acompanhar o valor total gasto — agora com **persistência real em banco de dados na nuvem**, garantindo que os dados não se percam entre sessões.

## 👥 Equipe

| Aluno | GitHub |
|---|---|
| João Paulo Rodrigues de Oliveira | [@joaorodriguesz7](https://github.com/joaorodriguesz7) |
| Pedro Henrique Souza | [@pedro-username](https://github.com/) |
| Arthur Santana | [@arthur-username](https://github.com/) |

## ⚙️ Funcionalidades
- Adicionar gastos (salvos no banco de dados)
- Listar gastos persistidos
- Ver total em BRL
- Ver total convertido para USD (via AwesomeAPI)
- Remover gastos por ID

## 🛠 Tecnologias

### Backend
- Python 3.11
- FastAPI
- Supabase (PostgreSQL na nuvem) ← **novo**

### Qualidade & CI/CD
- Pytest + pytest-cov
- Ruff (lint)
- GitHub Actions
- Vercel (deploy contínuo)

## 🗄️ Banco de Dados — Supabase

A aplicação utiliza o **Supabase** como banco de dados PostgreSQL na nuvem.

### Estrutura da tabela `gastos`

```sql
create table gastos (
  id          bigint generated always as identity primary key,
  valor       numeric(10, 2) not null check (valor >= 0),
  descricao   text not null,
  criado_em   timestamptz default now()
);
```

### Variáveis de ambiente necessárias

| Variável | Onde obter |
|---|---|
| `SUPABASE_URL` | Painel do Supabase → Project Settings → API |
| `SUPABASE_KEY` | Painel do Supabase → Project Settings → API → `anon public` |

Configure em:
- **Vercel:** Dashboard → Project → Settings → Environment Variables
- **GitHub:** Repositório → Settings → Secrets and variables → Actions

## ▶️ Como executar localmente

```bash
# 1. Clonar o repositório
git clone https://github.com/joaorodriguesz7/Gerenciador_Gastos.git
cd Gerenciador_Gastos

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar variáveis de ambiente
export SUPABASE_URL="https://xxxx.supabase.co"
export SUPABASE_KEY="sua-chave-aqui"

# 4. Rodar a aplicação
uvicorn src.app:app --reload

# 5. Rodar os testes
pytest
```

## 🔀 Contribuições (Pull Requests)

| PR | Autor | Descrição |
|---|---|---|
| #1 | João Paulo | Integração com Supabase e refatoração do banco |
| #2 | Pedro Henrique | Adição de campo `categoria` nos gastos |
| #3 | Arthur Santana | Atualização do README e documentação |

## ℹ️ Informações Adicionais

Versão Atual: 3.0.0
Repositório: https://github.com/joaorodriguesz7/Gerenciador_Gastos.git
