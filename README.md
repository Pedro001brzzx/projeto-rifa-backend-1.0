# 🎟️API de Rifas e Campanhas de Sorteio

Backend REST API para o sistema de campanhas e sorteios **Isorte Rifas**, construído com Flask seguindo o padrão arquitetural **MVC**. A API gerencia o ciclo completo de uma rifa digital: cadastro de campanhas, reserva e pagamento de títulos via PIX, apuração de ganhadores e auditoria de sorteios.

> **Versão atual:** `2.1` &nbsp;|&nbsp; **Deploy:** [Railway](https://railway.app) &nbsp;|&nbsp; **Linguagem:** Python 3.11+

---

## 📑 Sumário

- [Visão Geral](#-visão-geral)
- [Stack Tecnológica](#-stack-tecnológica)
- [Arquitetura](#-arquitetura)
- [Estrutura de Diretórios](#-estrutura-de-diretórios)
- [Modelos de Dados](#-modelos-de-dados)
- [Endpoints da API](#-endpoints-da-api)
- [Configuração e Execução](#-configuração-e-execução)
- [Testes](#-testes)
- [Deploy (Railway)](#-deploy-railway)
- [Histórico de Versões](#-histórico-de-versões)
- [Roadmap](#-roadmap)

---

## 🔍 Visão Geral

O sistema permite que administradores criem **campanhas de sorteio** com um número fixo de títulos. Participantes se cadastram, escolhem seus títulos e efetuam o pagamento via **PIX** integrado ao gateway **AbacatePay**. Após a confirmação do pagamento via webhook, os títulos são liberados. Quando a campanha encerra, um administrador define o número ganhador, e o evento é registrado no log de auditoria.

### Funcionalidades principais

| Módulo | Descrição |
|---|---|
| **Autenticação** | Registro, login, recuperação de senha via JWT |
| **Campanhas** | CRUD completo com slug único, controle de capacidade e status |
| **Títulos** | Formato `0XXXXX` (6 dígitos), reserva via bulk-insert otimizado |
| **Pagamentos** | Geração de QR Code PIX + webhook de confirmação (AbacatePay) |
| **Sorteio** | Definição de ganhador com auditoria completa por campanha |
| **Conteúdo** | Artigos e comunicados com paginação |
| **Admin** | Painel protegido por JWT + flag `is_admin`, com log de ações |
| **Scheduler** | Job em background para expiração proativa de compras pendentes |
| **Validação** | Schema Marshmallow em todos os endpoints de escrita (erro 400 estruturado) |
| **Migrations** | Flask-Migrate (Alembic) — versionamento de schema com `flask db migrate` |

---

## 🛠️ Stack Tecnológica

| Camada | Tecnologia | Versão |
|---|---|---|
| Framework | Flask | 3.0.0 |
| ORM | Flask-SQLAlchemy | 3.1.1 |
| Banco (prod) | PostgreSQL | — |
| Banco (dev/test) | SQLite | — |
| Autenticação | Flask-JWT-Extended | 4.6.0 |
| Hash de senhas | Flask-Bcrypt | 1.0.1 |
| CORS | Flask-CORS | 4.0.0 |
| Migrations | Flask-Migrate (Alembic) | 4.0.5 |
| Scheduler | APScheduler | 3.10.4 |
| Rate limiting | Flask-Limiter | 3.5.0 |
| Validação | Marshmallow | 3.20.1 |
| Documentação | Flasgger (Swagger/OpenAPI) | 0.9.7.1 |
| QR Code | qrcode[pil] | 7.4.2 |
| Servidor WSGI | Gunicorn | 21.2.0 |
| Testes | pytest + pytest-flask | 7.4.3 / 1.3.0 |

---

## 🏗️ Arquitetura

O projeto segue o padrão **MVC** com separação clara de responsabilidades:

```
Requisição HTTP
      │
      ▼
  [ Routes ]          ← Valida autenticação, extrai parâmetros, delega
      │
      ▼
  [ Schemas ]         ← Validação de entrada (Marshmallow) — erro 400 estruturado
      │
      ▼
  [ Controllers ]     ← Regras de negócio, orquestra models, retorna response
      │
      ▼
  [ Models ]          ← Entidades do banco, métodos to_dict(), queries
      │
      ▼
  [ PostgreSQL ]
```

- **Routes** (`app/routes/`) — Blueprints Flask. Recebem a requisição HTTP, aplicam decorators de autenticação (`@jwt_required`) e rate limit, e delegam ao controller correspondente.
- **Schemas** (`app/schemas/`) — Classes Marshmallow. Validam e deserializam o body JSON antes de chegar ao controller. Campos desconhecidos retornam `400 {"erro": "Dados inválidos"}`.
- **Controllers** (`app/controllers/`) — Toda a lógica de negócio. Interagem com os models e constroem a resposta JSON.
- **Models** (`app/models/`) — Classes SQLAlchemy. Cada modelo representa uma tabela e expõe `to_dict()` para serialização.
- **Utils** (`app/utils/`) — Funções auxiliares compartilhadas (logger de ações admin, validação de body).
- **Jobs** (`app/jobs/`) — Tasks executadas pelo APScheduler em background.
- **Scripts** (`scripts/`) — Utilitários de manutenção e inicialização do banco. **Não são parte da aplicação em produção.**

---

## 📁 Estrutura de Diretórios

```
Projeto-rifa/
├── app/
│   ├── __init__.py              # Application factory (create_app)
│   ├── config.py                # Configurações por ambiente (Dev/Prod/Test)
│   ├── extensions.py            # Instâncias das extensões Flask (db, bcrypt, migrate…)
│   ├── scheduler.py             # Inicialização do APScheduler
│   │
│   ├── models/
│   │   ├── usuario.py           # Usuário, autenticação, perfil, deleted_at
│   │   ├── campanha.py          # Campanha, status, sorteio_metodo, deleted_at
│   │   ├── compra.py            # Compra, status_pagamento, expira_em, deleted_at
│   │   ├── titulo.py            # Título individual (número 6 dígitos + campanha_id)
│   │   ├── titulo_premiado.py   # Registro de títulos ganhadores
│   │   ├── admin_log.py         # Log de ações administrativas (auditoria)
│   │   ├── artigo.py            # Artigos de conteúdo
│   │   ├── comunicado.py        # Comunicados/avisos
│   │   └── contato.py           # Mensagens de contato
│   │
│   ├── schemas/                 # Validação Marshmallow (Fase D)
│   │   ├── auth_schemas.py      # RegistroSchema, LoginSchema, AtualizarPerfilSchema
│   │   ├── campanha_schemas.py  # CriarCampanhaSchema, AtualizarCampanhaSchema
│   │   ├── compra_schemas.py    # CheckoutSchema
│   │   └── conteudo_schemas.py  # ArtigoSchema, ComunicadoSchema
│   │
│   ├── controllers/
│   │   ├── auth_controller.py       # Registro, login, perfil, recuperação de senha
│   │   ├── campanha_controller.py   # CRUD de campanhas, listagem, checkout
│   │   ├── compra_controller.py     # Fluxo de compra e reserva de títulos (bulk-insert)
│   │   ├── pagamento_controller.py  # Integração AbacatePay (PIX + webhook)
│   │   ├── ganhador_controller.py   # Definição de ganhador
│   │   ├── admin_controller.py      # Auditoria, gestão de usuários/campanhas
│   │   └── conteudo_controller.py   # Artigos e comunicados (com paginação)
│   │
│   ├── routes/
│   │   ├── auth_routes.py           # /api/auth/*
│   │   ├── campanha_routes.py       # /api/campanhas/*
│   │   ├── compra_routes.py         # /api/compras/*, /api/meus-titulos
│   │   ├── pagamento_routes.py      # /api/pagamentos/*
│   │   ├── ganhador_routes.py       # /api/ganhadores/*
│   │   ├── conteudo_routes.py       # /api/artigos/*, /api/comunicados/*
│   │   └── admin_routes.py          # /api/painel-secreto-x9/*
│   │
│   ├── utils/
│   │   ├── admin_logger.py          # Função log_admin_action()
│   │   ├── helpers.py               # Funções auxiliares gerais
│   │   └── validate_body.py         # Decorator @validate_body(Schema)
│   │
│   └── jobs/
│       └── cleanup_expired_purchases.py  # Job: expira compras pendentes
│
├── migrations/                  # Flask-Migrate / Alembic (Fase E)
│   ├── env.py                   # Configuração Alembic com import dos models
│   ├── alembic.ini
│   └── versions/
│       └── 56f40a500000_baseline_schema_completo_v2_1.py  # Baseline no-op
│
├── scripts/                     # Utilitários de manutenção (não deploy)
│   ├── create_admin.py          # Cria/atualiza admin inicial (usado no Procfile)
│   ├── test_e2e_flow.py         # Teste E2E: campanha → usuário → compra → aprovação
│   ├── init_db.py               # Inicialização do banco (legado)
│   └── …                        # Outros scripts de diagnóstico e correção
│
├── tests/
│   ├── conftest.py              # Fixtures pytest (app, client, tokens)
│   ├── test_auth.py             # Testes de autenticação
│   ├── test_campanhas.py        # Testes de campanhas
│   ├── test_comunicados.py      # Testes de comunicados + paginação
│   ├── test_auditoria.py        # Testes do endpoint de auditoria de sorteio
│   ├── test_ganhadores.py       # Testes de ganhadores
│   └── test_pagamentos.py       # Testes de pagamento/webhook
│
├── swagger.yaml                 # Especificação OpenAPI 3.0 completa
├── .env.example                 # Template de variáveis de ambiente
├── requirements.txt             # Dependências Python
├── pytest.ini                   # Configuração do pytest
├── Procfile                     # release: flask db upgrade + create_admin; web: gunicorn
├── railway.toml                 # Configuração do Railway
├── nixpacks.toml                # Build config (Railway/Nixpacks)
├── wsgi.py                      # Entry point WSGI (Gunicorn)
└── run.py                       # Entry point para desenvolvimento local
```

---

## 🗄️ Modelos de Dados

```
Usuario ──────────────────────┐
  id, public_id, nome,        │
  email, senha_hash,          │
  telefone, cpf,              │
  is_admin, criado_em,        │
  deleted_at                  │
                              │
Campanha ─────────────────────┤
  id, public_id, titulo,      │
  slug, descricao,            │   Compra ──────────────────────────┐
  valor_titulo, total_titulos,│     id, public_id,                │
  titulos_vendidos,           ├───  usuario_id → Usuario          │
  status, sorteio_metodo,     │     campanha_id → Campanha        │
  imagem_principal,           │     status_pagamento,             │
  criado_em, deleted_at       │     expira_em, data_pagamento,    │
                              │     valor_total, criado_em,       │
TituloPremiado                │     deleted_at                    │
  id, campanha_id,            │                                   │
  numero_sorteado,            │  Titulo ───────────────────────────┘
  ganhador_id → Usuario,      │    id, compra_id → Compra
  definido_por → Usuario,     │    campanha_id → Campanha
  definido_em                 │    numero (6 dígitos: 000001–099999)
                              │
AdminLog                      │
  id, admin_id → Usuario,     │
  acao, campanha_id,          │
  detalhes (JSON), ip,        │
  criado_em                   │
```

---

## 📡 Endpoints da API

> Documentação completa disponível em `/apidocs` (Swagger UI) e no arquivo [`API_DOCUMENTATION.md`](API_DOCUMENTATION.md).

### Autenticação — `/api/auth`

| Método | Endpoint | Auth | Descrição |
|---|---|---|---|
| `POST` | `/api/auth/registro` | — | Registrar novo usuário |
| `POST` | `/api/auth/login` | — | Login, retorna JWT |
| `POST` | `/api/auth/forgot-password` | — | Solicitar recuperação de senha |
| `POST` | `/api/auth/reset-password` | — | Redefinir senha com token |
| `GET` | `/api/auth/perfil` | ✅ JWT | Ver perfil do usuário autenticado |
| `PUT` | `/api/auth/perfil` | ✅ JWT | Atualizar dados do perfil |

### Campanhas — `/api/campanhas`

| Método | Endpoint | Auth | Descrição |
|---|---|---|---|
| `GET` | `/api/campanhas` | — | Listar campanhas ativas (paginado) |
| `GET` | `/api/campanhas/<slug>` | — | Detalhes de uma campanha |
| `POST` | `/api/campanhas` | ✅ Admin | Criar nova campanha |
| `PUT` | `/api/campanhas/<id>` | ✅ Admin | Atualizar campanha |
| `DELETE` | `/api/campanhas/<id>` | ✅ Admin | Remover campanha (soft delete) |
| `GET` | `/api/campanhas/<slug>/titulos-premiados` | — | Títulos premiados da campanha |
| `POST` | `/api/campanhas/<id>/titulos-premiados` | ✅ Admin | Definir título premiado |
| `DELETE` | `/api/campanhas/titulos-premiados/<id>` | ✅ Admin | Remover título premiado |
| `GET` | `/api/campanhas/<id>/compradores` | ✅ Admin | Listar compradores da campanha |

### Compras e Títulos — `/api/compras`

| Método | Endpoint | Auth | Body | Descrição |
|---|---|---|---|---|
| `POST` | `/api/compras` | ✅ JWT | `campanha_id` (UUID), `quantidade_titulos`, `metodo_pagamento` | Reservar títulos |
| `GET` | `/api/meus-titulos` | ✅ JWT | — | Listar compras + títulos do usuário |
| `DELETE` | `/api/compras/<id>` | ✅ Admin | — | Cancelar compra (soft delete) |

> **Atenção:** `campanha_id` deve ser o **UUID** (`public_id`) da campanha, não o integer `id`.

### Pagamentos — `/api/pagamentos`

| Método | Endpoint | Auth | Descrição |
|---|---|---|---|
| `GET` | `/api/pagamentos/<compra_id>` | ✅ JWT | Status + QR Code PIX da compra |
| `POST` | `/api/pagamentos/<compra_id>/aprovar` | ✅ Admin | Aprovar pagamento manualmente |
| `POST` | `/api/pagamentos/webhook` | Assinatura | Webhook de confirmação AbacatePay |

### Ganhadores — `/api/ganhadores`

| Método | Endpoint | Auth | Descrição |
|---|---|---|---|
| `GET` | `/api/ganhadores` | — | Listar ganhadores públicos |
| `POST` | `/api/campanhas/<id>/ganhador` | ✅ Admin | Definir ganhador + registrar auditoria |

### Conteúdo

| Método | Endpoint | Auth | Descrição |
|---|---|---|---|
| `GET` | `/api/artigos` | — | Listar artigos (paginado) |
| `GET` | `/api/artigos/<slug>` | — | Detalhes de artigo |
| `GET` | `/api/comunicados` | — | Listar comunicados (paginado) |
| `POST` | `/api/contato` | — | Enviar mensagem de contato |

### Admin — `/api/painel-secreto-x9`

| Método | Endpoint | Auth | Descrição |
|---|---|---|---|
| `GET` | `.../usuarios` | ✅ Admin | Listar todos os usuários |
| `GET` | `.../campanhas` | ✅ Admin | Listar todas as campanhas |
| `GET` | `.../compras/expiradas` | ✅ Admin | Listar compras expiradas |
| `GET` | `.../campanhas/<id>/auditoria` | ✅ Admin | Histórico de auditoria do sorteio |

---

## ⚙️ Configuração e Execução

### Pré-requisitos

- Python **3.11+**
- PostgreSQL (produção) ou SQLite (desenvolvimento)
- Conta no [AbacatePay](https://abacatepay.com) para integração PIX

### 1. Clonar e criar ambiente virtual

```bash
git clone https://github.com/<seu-usuario>/projeto-rifa.git
cd projeto-rifa

python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente

Copie o arquivo de exemplo e preencha os valores:

```bash
cp .env.example .env
```

| Variável | Obrigatória | Descrição |
|---|---|---|
| `SECRET_KEY` | ✅ | Chave secreta Flask (mín. 32 chars) |
| `JWT_SECRET_KEY` | ✅ | Chave JWT (mín. 32 chars) |
| `DATABASE_URL` | Produção | URL PostgreSQL (Railway preenche automaticamente) |
| `CORS_ORIGINS` | ✅ | URLs do frontend separadas por vírgula |
| `BASE_URL` | ✅ | URL base do backend (para webhooks) |
| `ABACATEPAY_API_KEY` | ✅ | Chave da API do gateway de pagamento |
| `ABACATEPAY_WEBHOOK_SECRET` | ✅ | Secret para validar webhooks |
| `ADMIN_PHONE` | — | Telefone do admin inicial (padrão: env ou valor no script) |
| `ADMIN_PASSWORD` | — | Senha do admin inicial |
| `FLASK_ENV` | — | `development` ou `production` |

> ⚠️ **Nunca** commite o arquivo `.env`. Ele já está no `.gitignore`.

### 4. Inicializar banco de dados

```bash
# Primeira vez — cria tabelas e aplica migrations
flask db upgrade

# Cria o admin inicial
python scripts/create_admin.py

# Servidor de desenvolvimento
python run.py
# Swagger UI disponível em http://localhost:5000/apidocs
```

### 5. Workflow de migrations (alterações de schema)

```bash
# Detectar mudanças nos models e gerar migration automaticamente
flask db migrate -m "descricao da mudanca"

# Revisar o arquivo gerado em migrations/versions/ antes de aplicar
flask db upgrade

# Rollback se necessário
flask db downgrade
```

---

## 🧪 Testes

### Testes unitários (pytest)

O projeto utiliza **pytest** com banco em memória (`SQLite :memory:`) para isolamento total.

```bash
# Rodar todos os testes
pytest

# Com detalhes
pytest -v

# Módulo específico
pytest tests/test_auditoria.py -v
```

| Arquivo de Teste | Cobertura |
|---|---|
| `test_auth.py` | Registro, login, perfil, tokens inválidos |
| `test_campanhas.py` | CRUD, slug, autorização |
| `test_comunicados.py` | Listagem, paginação, limites |
| `test_auditoria.py` | Auth, estrutura, registro pós-sorteio, paginação |
| `test_ganhadores.py` | Listagem pública |
| `test_pagamentos.py` | Webhook, confirmação de pagamento |

### Teste E2E integrado

O script `scripts/test_e2e_flow.py` executa o fluxo completo contra o servidor local:

```bash
python scripts/test_e2e_flow.py
```

Cobre: login admin → criar campanha (100k tickets, R$0,10) → criar usuário admin → login → compra de 10 títulos → aprovação → verificação dos títulos gerados.

---

## 🚀 Deploy (Railway)

O projeto está configurado para deploy zero-config no Railway.

### Arquivos de configuração

- **`railway.toml`** — Define o comando de build e start
- **`nixpacks.toml`** — Especifica a versão do Python para o buildpack
- **`Procfile`** — Fase `release` (migrations + admin) e fase `web` (Gunicorn)
- **`wsgi.py`** — Entry point WSGI

### Procfile

```
release: flask db upgrade && python scripts/create_admin.py
web: gunicorn wsgi:app --workers 2 --threads 2 --timeout 120 --bind 0.0.0.0:$PORT
```

A fase `release` executa **antes** do servidor subir em cada deploy, garantindo que migrations sejam aplicadas automaticamente.

### Passos

1. Criar projeto no [Railway](https://railway.app)
2. Adicionar o **plugin PostgreSQL** — a `DATABASE_URL` será injetada automaticamente
3. Configurar as variáveis de ambiente do `.env.example` no painel do Railway
4. Conectar o repositório GitHub → deploy automático a cada push na `main`

### Primeira vez em produção (banco vazio)

```
# O wsgi.py chama db.create_all() no boot — tabelas são criadas automaticamente
# Em seguida a fase release executa:
flask db upgrade        # stampa o baseline e aplica migrations pendentes
python scripts/create_admin.py  # cria o admin inicial
```

---

## 📋 Histórico de Versões

### v2.1 — 2026-05-09 (atual)

- ✅ **Fase E — Flask-Migrate:** versionamento de schema com Alembic; `release` phase no Procfile; migration baseline `56f40a500000`
- ✅ **Fase D — Marshmallow:** validação de schema em todos os endpoints de escrita; erro `400` estruturado com lista de campos inválidos
- ✅ **Fase B — Soft delete + Scheduler:** campo `deleted_at` em Campanha, Compra e Usuário; job APScheduler para expiração proativa de compras pendentes
- ✅ **Fase A:** paginação em `GET /api/comunicados` e `GET /api/artigos`; endpoint de auditoria por campanha
- Script `scripts/test_e2e_flow.py` — teste E2E completo do fluxo de compra
- `scripts/create_admin.py` — criação/atualização do admin inicial via Procfile

### v2.0
- Refatoração completa para arquitetura MVC
- Separação em Blueprints por domínio
- Integração com AbacatePay (PIX + webhook)
- Implementação do APScheduler para expiração proativa de compras
- Sistema de log de auditoria (`AdminLog`)
- Documentação Swagger/OpenAPI (`swagger.yaml`)
- Suite de testes com pytest
- Deploy no Railway com PostgreSQL

### v1.0
- Backend monolítico em Flask
- Funcionalidades básicas de campanha e compra

---

## 🗺️ Roadmap

| Fase | Funcionalidade | Status |
|---|---|---|
| **A** | Paginação + Auditoria de sorteio | ✅ Concluído |
| **B** | Soft delete + Scheduler de expiração | ✅ Concluído |
| **D** | Validação Marshmallow em todos os endpoints | ✅ Concluído |
| **E** | Flask-Migrate (Alembic) para versionamento de schema | ✅ Concluído |
| **C** | Sistema de roles (`usuario`, `moderador`, `admin`, `super_admin`) | ⏳ Planejado |
| **C** | Refresh token + endpoint `/api/auth/refresh` | ⏳ Planejado |

> Detalhes e especificações em [`2.1v-rifas-backend.md`](2.1v-rifas-backend.md).

---

## 📄 Documentação Adicional

| Arquivo | Conteúdo |
|---|---|
| [`API_DOCUMENTATION.md`](API_DOCUMENTATION.md) | Referência completa de todos os endpoints |
| [`swagger.yaml`](swagger.yaml) | Especificação OpenAPI 3.0 |
| [`2.1v-rifas-backend.md`](2.1v-rifas-backend.md) | Plano de fases e decisões técnicas |

---

<div align="center">
  <sub>Desenvolvido por Pedro &nbsp;·&nbsp; Gêmeos Brasil &nbsp;·&nbsp; 2025–2026</sub>
</div>
