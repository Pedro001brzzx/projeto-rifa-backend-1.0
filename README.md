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
| **Títulos** | Formato configurável (ex: `001-A`), reserva e liberação automática |
| **Pagamentos** | Geração de QR Code PIX + webhook de confirmação (AbacatePay) |
| **Sorteio** | Definição de ganhador com auditoria completa por campanha |
| **Conteúdo** | Artigos e comunicados com paginação |
| **Admin** | Painel protegido por JWT + flag `is_admin`, com log de ações |
| **Scheduler** | Job em background para expiração proativa de compras pendentes |

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
  [ Controllers ]     ← Regras de negócio, orquestra models, retorna response
      │
      ▼
  [ Models ]          ← Entidades do banco, métodos to_dict(), queries
      │
      ▼
  [ PostgreSQL ]
```

- **Routes** (`app/routes/`) — Blueprints Flask. Recebem a requisição HTTP, aplicam decorators de autenticação (`@jwt_required`) e rate limit, e delegam ao controller correspondente.
- **Controllers** (`app/controllers/`) — Toda a lógica de negócio. Validam dados de entrada, interagem com os models e constroem a resposta JSON.
- **Models** (`app/models/`) — Classes SQLAlchemy. Cada modelo representa uma tabela e expõe métodos `to_dict()` para serialização.
- **Utils** (`app/utils/`) — Funções auxiliares compartilhadas (logger de ações admin, helpers gerais).
- **Jobs** (`app/jobs/`) — Tasks executadas pelo APScheduler em background.
- **Scripts** (`scripts/`) — Utilitários de manutenção e inicialização do banco. **Não são parte da aplicação em produção.**

---

## 📁 Estrutura de Diretórios

```
Projeto-rifa/
├── app/
│   ├── __init__.py              # Application factory (create_app)
│   ├── config.py                # Configurações por ambiente (Dev/Prod/Test)
│   ├── extensions.py            # Instâncias das extensões Flask (db, bcrypt, jwt…)
│   ├── scheduler.py             # Inicialização do APScheduler
│   │
│   ├── models/
│   │   ├── usuario.py           # Usuário, autenticação, perfil
│   │   ├── campanha.py          # Campanha, status, sorteio_metodo
│   │   ├── compra.py            # Compra, status_pagamento, expira_em
│   │   ├── titulo.py            # Título individual (número + formato)
│   │   ├── titulo_premiado.py   # Registro de títulos ganhadores
│   │   ├── admin_log.py         # Log de ações administrativas (auditoria)
│   │   ├── artigo.py            # Artigos de conteúdo
│   │   ├── comunicado.py        # Comunicados/avisos
│   │   └── contato.py           # Mensagens de contato
│   │
│   ├── controllers/
│   │   ├── auth_controller.py       # Registro, login, perfil, recuperação de senha
│   │   ├── campanha_controller.py   # CRUD de campanhas, listagem, checkout
│   │   ├── compra_controller.py     # Fluxo de compra e reserva de títulos
│   │   ├── pagamento_controller.py  # Integração AbacatePay (PIX + webhook)
│   │   ├── ganhador_controller.py   # Definição de ganhador
│   │   ├── admin_controller.py      # Auditoria, gestão de usuários/campanhas
│   │   └── conteudo_controller.py   # Artigos e comunicados (com paginação)
│   │
│   ├── routes/
│   │   ├── auth_routes.py           # /api/auth/*
│   │   ├── campanha_routes.py       # /api/campanhas/*
│   │   ├── compra_routes.py         # /api/compras/*
│   │   ├── pagamento_routes.py      # /api/pagamentos/*
│   │   ├── ganhador_routes.py       # /api/ganhadores/*
│   │   ├── conteudo_routes.py       # /api/artigos/*, /api/comunicados/*
│   │   └── admin_routes.py          # /api/painel-secreto-x9/*
│   │
│   ├── utils/
│   │   ├── admin_logger.py          # Função log_admin_action()
│   │   └── helpers.py               # Funções auxiliares gerais
│   │
│   └── jobs/
│       └── cleanup_expired_purchases.py  # Job: expira compras pendentes
│
├── scripts/                     # Utilitários de manutenção (não deploy)
│   ├── init_db.py               # Inicialização do banco
│   ├── migrations/              # Migrations Alembic
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
├── Procfile                     # Entrada para Heroku-style deploys
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
  is_admin, criado_em         │
                              │
Campanha ─────────────────────┤
  id, public_id, titulo,      │
  slug, descricao,            │   Compra ──────────────────────────┐
  preco_titulo, num_titulos,  │     id, public_id,                │
  titulos_vendidos,           ├───  usuario_id → Usuario          │
  status, sorteio_metodo,     │     campanha_id → Campanha        │
  imagem_url, criado_em       │     status_pagamento,             │
                              │     expira_em, pago_em            │
TituloPremiado                │     valor_total, criado_em        │
  id, campanha_id,            │                                   │
  numero_sorteado,            │  Titulo ───────────────────────────┘
  ganhador_id → Usuario,      │    id, compra_id → Compra
  definido_por → Usuario,     │    numero, numero_formatado
  definido_em                 │
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
| `POST` | `/api/auth/recuperar-senha` | — | Solicitar recuperação de senha |
| `GET` | `/api/auth/perfil` | ✅ JWT | Ver perfil do usuário autenticado |
| `PUT` | `/api/auth/perfil` | ✅ JWT | Atualizar dados do perfil |

### Campanhas — `/api/campanhas`

| Método | Endpoint | Auth | Descrição |
|---|---|---|---|
| `GET` | `/api/campanhas` | — | Listar campanhas ativas (paginado) |
| `GET` | `/api/campanhas/<slug>` | — | Detalhes de uma campanha |
| `POST` | `/api/campanhas` | ✅ Admin | Criar nova campanha |
| `PUT` | `/api/campanhas/<id>` | ✅ Admin | Atualizar campanha |
| `DELETE` | `/api/campanhas/<id>` | ✅ Admin | Remover campanha |
| `GET` | `/api/campanhas/<id>/titulos-disponiveis` | — | Títulos disponíveis para compra |

### Compras e Títulos — `/api/compras`

| Método | Endpoint | Auth | Descrição |
|---|---|---|---|
| `POST` | `/api/compras` | ✅ JWT | Reservar títulos (inicia fluxo de pagamento) |
| `GET` | `/api/meus-titulos` | ✅ JWT | Listar títulos do usuário autenticado |

### Pagamentos — `/api/pagamentos`

| Método | Endpoint | Auth | Descrição |
|---|---|---|---|
| `GET` | `/api/pagamentos/<compra_id>` | ✅ JWT | Status + QR Code PIX da compra |
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
| `GET` | `.../compras` | ✅ Admin | Listar todas as compras |
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
| `FLASK_ENV` | — | `development` ou `production` |

> ⚠️ **Nunca** commite o arquivo `.env`. Ele já está no `.gitignore`.

### 4. Inicializar banco de dados

```bash
# Desenvolvimento (SQLite criado automaticamente)
python run.py

# Produção (após configurar DATABASE_URL)
python scripts/init_db.py
```

### 5. Executar localmente

```bash
python run.py
# Servidor disponível em http://localhost:5000
# Swagger UI em http://localhost:5000/apidocs
```

---

## 🧪 Testes

O projeto utiliza **pytest** com banco em memória (`SQLite :memory:`) para isolamento total.

```bash
# Rodar todos os testes
pytest

# Com detalhes e cobertura por arquivo
pytest -v

# Rodar um módulo específico
pytest tests/test_auditoria.py -v
```

### Cobertura atual

| Arquivo de Teste | Casos | Cobertura |
|---|---|---|
| `test_auth.py` | Registro, login, perfil, tokens inválidos | ✅ |
| `test_campanhas.py` | CRUD, slug, autorização | ✅ |
| `test_comunicados.py` | Listagem, paginação, limites | ✅ |
| `test_auditoria.py` | Auth, estrutura, registro pós-sorteio, paginação | ✅ |
| `test_ganhadores.py` | Listagem pública | ✅ |
| `test_pagamentos.py` | Webhook, confirmação de pagamento | ✅ |

---

## 🚀 Deploy (Railway)

O projeto está configurado para deploy zero-config no Railway.

### Arquivos de configuração

- **`railway.toml`** — Define o comando de build e start
- **`nixpacks.toml`** — Especifica a versão do Python para o buildpack
- **`Procfile`** — Comando Gunicorn para produção
- **`wsgi.py`** — Entry point WSGI

### Passos

1. Criar projeto no [Railway](https://railway.app)
2. Adicionar o **plugin PostgreSQL** — a `DATABASE_URL` será injetada automaticamente
3. Configurar as variáveis de ambiente do `.env.example` no painel do Railway
4. Conectar o repositório GitHub → deploy automático a cada push na `main`

---

## 📋 Histórico de Versões

### v2.1 — 2026-05-03 (atual)
- ✅ **Fase A completa**
- Paginação em `GET /api/comunicados` e `GET /api/artigos` (`?page` e `?per_page`)
- Endpoint de auditoria por campanha: `GET /api/painel-secreto-x9/campanhas/<id>/auditoria`
- 6 novos testes em `test_auditoria.py`
- 4 novos testes de paginação em `test_comunicados.py`
- `swagger.yaml` e `API_DOCUMENTATION.md` atualizados

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

Próximas fases planejadas (ver [`2.1v-rifas-backend.md`](2.1v-rifas-backend.md) para detalhes):

| Fase | Funcionalidade | Prioridade |
|---|---|---|
| **B** | Expiração proativa de compras via Scheduler | Alta |
| **B** | Soft delete (campo `deleted_at`) em campanhas, compras e usuários | Alta |
| **C** | Sistema de roles (`usuario`, `moderador`, `admin`, `super_admin`) | Média |
| **C** | Refresh token + endpoint `/api/auth/refresh` | Média |
| **D** | Validação de schema com Marshmallow em todos os endpoints de escrita | Média |

---

## 📄 Documentação Adicional

| Arquivo | Conteúdo |
|---|---|
| [`API_DOCUMENTATION.md`](API_DOCUMENTATION.md) | Referência completa de todos os endpoints |
| [`swagger.yaml`](swagger.yaml) | Especificação OpenAPI 3.0 |
| [`SETUP.md`](SETUP.md) | Guia detalhado de configuração do ambiente |
| [`POSTMAN_GUIDE.md`](POSTMAN_GUIDE.md) | Como importar e usar a coleção Postman |
| [`MAINTENANCE.md`](MAINTENANCE.md) | Procedimentos de manutenção e operações no banco |
| [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) | Erros comuns e soluções |
| [`FORMATO_TITULOS.md`](FORMATO_TITULOS.md) | Especificação do formato dos números de título |

---

<div align="center">
  <sub>Desenvolvido por Pedro &nbsp;·&nbsp; Gêmeos Brasil &nbsp;·&nbsp; 2025–2026</sub>
</div>
