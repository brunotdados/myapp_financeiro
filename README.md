# Mini App Financas

Mini app de financas pessoais com backend em FastAPI e frontend em Streamlit.

## Backend local

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Depois de configurar o `.env`, a primeira rota de email fica em:

```text
GET /api/emails/nubank
```

Para baixar o extrato mais recente de cada conta e gerar o CSV consolidado:

```text
POST /api/emails/nubank/extrato-fatura/mais-recente/processar
```

## Frontend local

```bash
cd frontend
copy .env.example .env
..\..\.venv\Scripts\pip install -r requirements.txt
..\..\.venv\Scripts\streamlit run app/main.py
```

## Deploy gratuito

Para deploy gratuito com dados persistentes, use Streamlit Community Cloud + Supabase.

No Streamlit Community Cloud, configure:

```text
Repository: brunotdados/myapp_financeiro
Branch: main
Main file path: frontend/app/main.py
```

Secrets obrigatorios:

```text
FINANCE_APP_USER
FINANCE_APP_PASSWORD
SUPABASE_URL
SUPABASE_KEY
```

Para o botao "Buscar email mais recente" do Nubank funcionar no Streamlit Cloud,
adicione tambem:

```text
BRUNO_EMAIL
BRUNO_EMAIL_APP_PASSWORD
MAYARA_EMAIL
MAYARA_EMAIL_APP_PASSWORD
NUBANK_STATEMENT_SUBJECT="Extrato da fatura do Cartão Nubank"
```

As senhas dos Gmails precisam ser senhas de app do Google, nao a senha normal da
conta.

Antes do deploy, crie as tabelas no Supabase usando:

```text
docs/supabase_schema.sql
```

## Estrutura

```text
mini_app_financas/
  backend/
    app/
      api/routes/     # Rotas HTTP da API
      core/           # Configuracoes, variaveis e dependencias centrais
      db/             # Conexao e persistencia de dados
      models/         # Modelos internos/ORM
      schemas/        # Schemas de entrada e saida da API
      services/       # Regras de negocio
    tests/            # Testes do backend
  frontend/
    app/
      components/     # Componentes reutilizaveis do Streamlit
      pages/          # Paginas do app
      services/       # Clientes para chamar a API
      styles/         # CSS/tema do Streamlit
    tests/            # Testes do frontend
  shared/
    finance/          # Codigo compartilhado entre backend e frontend
  data/
    raw/              # Dados brutos importados
    processed/        # Dados tratados
    exports/          # Arquivos gerados pelo app
  docker/             # Arquivos auxiliares de Docker
  scripts/            # Scripts operacionais
  docs/               # Documentacao do projeto
```
