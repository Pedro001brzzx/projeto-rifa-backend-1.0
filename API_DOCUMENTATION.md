# Documentação da API - Sistema de Rifas 

> Documentação completa para integração front-end

**Base URL (Produção):** `https://SEU_BACKEND.up.railway.app`  
**Base URL (Dev):** `http://localhost:5000`  
**Versão:** 2.1  
**Formato de resposta:** JSON  
**Autenticação:** JWT Bearer Token  
**Última atualização:** Maio 2026 (Fases A, B, D e E concluídas)

---

## Swagger UI

Com o servidor rodando, acesse a documentação interativa em:

```
http://localhost:5000/apidocs/
```

O spec OpenAPI completo fica disponível em `/apispec.json` e é gerado a partir do arquivo [`swagger.yaml`](swagger.yaml) na raiz do projeto.

---

## Testes Automatizados

### Executar todos os testes

```bash
pytest
```

### Executar com detalhes

```bash
pytest -v
```

### Executar um módulo específico

```bash
pytest tests/test_auth.py
pytest tests/test_campanhas.py
pytest tests/test_comunicados.py
pytest tests/test_ganhadores.py
pytest tests/test_pagamentos.py
```

### Estrutura dos testes

```
tests/
├── conftest.py          # Fixtures: app (SQLite in-memory), client, token_usuario, token_admin
├── test_auth.py         # Registro, login, perfil, recuperação de senha (19 testes)
├── test_campanhas.py    # CRUD campanhas, compradores, títulos premiados (16 testes)
├── test_comunicados.py  # Comunicados (paginação), artigos e contato (18 testes)
├── test_ganhadores.py   # Listagem de ganhadores (3 testes)
├── test_auditoria.py    # Auditoria do sorteio (6 testes) — Fase A
└── test_pagamentos.py   # Checkout, webhook, aprovação manual, admin (13 testes)
```

> Os testes usam SQLite em memória — não afetam o banco de dados de desenvolvimento ou produção.  
> O scheduler de tarefas é desativado automaticamente no modo de teste.  
> **Nota Fase B:** O campo `deleted_at` é criado automaticamente via `flask db upgrade` ou `db.create_all()`. Scripts manuais `migrate_fase_b.py` / `migrate_fase_c.py` são obsoletos — use Flask-Migrate.  
> **Nota Fase D:** A validação Marshmallow retorna `400` para campos obrigatórios ausentes ou inválidos. Os testes existentes continuam válidos pois as asserções de status code `400` em cenários de erro são compatíveis com o novo formato de resposta.  
> **Nota Fase E:** O projeto agora usa Flask-Migrate para versionamento de schema. Ver seção [Deploy Railway](#deploy-railway) para instruções de migração.

---

## Índice

- [Autenticação](#autenticação)
- [Campanhas](#campanhas) — incl. soft delete e restauração
- [Títulos Premiados](#títulos-premiados)
- [Checkout e Pagamentos](#checkout-e-pagamentos)
- [Compras e Títulos](#compras-e-títulos)
- [Ganhadores](#ganhadores)
- [Admin](#admin) — incl. compras expiradas
- [Artigos](#artigos)
- [Comunicados](#comunicados)
- [Contato](#contato)
- [Validação de Entrada](#validação-de-entrada)
- [Deploy (Railway)](#deploy-railway)
- [Códigos de Status](#códigos-de-status)

---

## Autenticação

Todos os endpoints protegidos exigem o token JWT no header:

```
Authorization: Bearer {token}
```

### 1. Registro de Usuário

**`POST /api/auth/registro`** — Público | Rate limit: 5/min

```json
// Request
{
  "nome": "João Silva",
  "telefone": "11999999999",
  "senha": "senha123",
  "email": "joao@email.com",
  "cpf": "12345678900",
  "cidade": "São Paulo",
  "estado": "SP"
}

// Response 201
{
  "mensagem": "Usuário cadastrado com sucesso",
  "token": "eyJhbGci...",
  "usuario": {
    "id": 1,
    "nome": "João Silva",
    "telefone": "11999999999",
    "email": "joao@email.com",
    "cpf": "123.***.***-**",
    "cidade": "São Paulo",
    "estado": "SP",
    "is_admin": false,
    "criado_em": "2026-03-04T00:00:00"
  }
}
```

> **Campos obrigatórios:** `nome`, `telefone`, `senha`, `email`, `cpf`  
> **Dados sensíveis:** CPF retornado mascarado na resposta.

---

### 2. Login

**`POST /api/auth/login`** — Público | Rate limit: 5/min

```json
// Request
{
  "telefone": "11999999999",
  "senha": "senha123"
}

// Response 200
{
  "mensagem": "Login realizado com sucesso",
  "token": "eyJhbGci...",
  "usuario": {
    "id": 1,
    "nome": "João Silva",
    "telefone": "11999999999",
    "is_admin": false
  }
}
```

> **Flexibilidade de Telefone:** Aceita `83994099696` ou `5583994099696` (com ou sem +55).

---

### 3. Logout

**`POST /api/auth/logout`** — Requer auth

```json
// Response 200
{ "mensagem": "Logout realizado com sucesso" }
```

---

### 4. Obter Perfil

**`GET /api/auth/perfil`** — Requer auth

```json
// Response 200
{
  "id": 1,
  "nome": "João Silva",
  "telefone": "11999999999",
  "email": "jo***@email.com",
  "cpf": "123.***.***-**",
  "cidade": "São Paulo",
  "estado": "SP",
  "is_admin": false,
  "criado_em": "2026-03-04T00:00:00"
}
```

> **Mascaramento:** Email e CPF retornam mascarados por segurança.

---

### 5. Atualizar Perfil

**`PUT /api/auth/perfil`** — Requer auth

```json
// Request (todos opcionais)
{
  "nome": "João Santos",
  "email": "novo@email.com",
  "cidade": "Rio de Janeiro",
  "estado": "RJ"
}

// Response 200
{
  "mensagem": "Perfil atualizado com sucesso",
  "usuario": { ... }
}
```

---

### 6. Recuperar Senha

**`POST /api/auth/forgot-password`** — Público | Rate limit: 3/min

```json
// Request
{ "email": "joao@email.com" }

// Response 200 (sempre, por segurança)
{ "mensagem": "Se o email estiver cadastrado, você receberá instruções de recuperação" }
```

**`POST /api/auth/reset-password`** — Público | Rate limit: 5/min

```json
// Request
{
  "token": "token_de_recuperacao",
  "nova_senha": "novaSenha123"
}

// Response 200
{ "mensagem": "Senha redefinida com sucesso" }
```

---

## Campanhas

### 7. Listar Campanhas

**`GET /api/campanhas`** — Público

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `status` | string | (todos) | `ativo`, `concluido`, `cancelado` — omitir retorna todos |
| `page` | integer | `1` | Página |
| `per_page` | integer | `20` | Itens por página |

```json
// Response 200
{
  "campanhas": [
    {
      "id": 1,
      "public_id": "uuid-da-campanha",
      "titulo": "iPhone 15 Pro Max",
      "slug": "iphone-15-pro-max",
      "descricao": "Concorra a um iPhone...",
      "regulamento": "1. Regra...",
      "premio": "iPhone 15 Pro Max 256GB",
      "imagem_principal": "https://...",
      "codigo": null,
      "tipo": "automatico",
      "valor_titulo": 10.00,
      "status": "ativo",
      "data_sorteio": "2026-06-01T20:00:00",
      "data_fim": null,
      "min_quantidade_compra": 1,
      "max_quantidade_compra": 500,
      "total_titulos": 10000,
      "titulos_vendidos": 5432,
      "titulos_disponiveis": 4568,
      "progresso": 54.32,
      "totalTickets": 10000,
      "soldTickets": 5432,
      "availableTickets": 4568,
      "ganhador": null
    }
  ],
  "total": 15,
  "paginas": 2,
  "pagina_atual": 1
}
```

> `ganhador` aparece preenchido apenas quando a campanha está concluída e tem vencedor definido. Sem vencedor, o campo não é incluído na resposta.

---

### 8. Detalhes da Campanha

**`GET /api/campanhas/{slug}`** — Público

```json
// Response 200 — Campanha ativa (sem ganhador)
{
  "id": 1,
  "public_id": "uuid-da-campanha",
  "titulo": "iPhone 15 Pro Max",
  "slug": "iphone-15-pro-max",
  "descricao": "Concorra a um iPhone...",
  "regulamento": "1. Regra...",
  "premio": "iPhone 15 Pro Max 256GB",
  "valor_titulo": 10.00,
  "status": "ativo",
  "progresso": 54.32,
  "total_titulos": 10000,
  "titulos_vendidos": 5432,
  "titulos_disponiveis": 4568,
  "min_quantidade_compra": 5
}

// Response 200 — Campanha concluída com ganhador
{
  "id": 2,
  "status": "concluido",
  "numero_sorteado": "00123",
  "ganhador": {
    "nome": "Pedro ***",
    "cidade": "João Pessoa",
    "estado": "PB",
    "telefone": "(**) *****-1234",
    "premio": "iPhone 15 Pro Max 256GB",
    "numero_sorteado": "00123",
    "data_conclusao": "15/03/2026"
  }
}
```

---

### 9. Criar Campanha

**`POST /api/campanhas`** — Admin

```json
// Request
{
  "titulo": "iPhone 15 Pro Max",
  "descricao": "Concorra a um iPhone...",
  "imagem_principal": "https://...",
  "premio": "iPhone 15 Pro Max 256GB",
  "valor_titulo": 10.00,
  "total_titulos": 10000,
  "min_quantidade_compra": 1,
  "max_quantidade_compra": 500,
  "data_sorteio": "2026-06-01T20:00:00",
  "regulamento": "1. Regra..."
}

// Response 201
{
  "mensagem": "Campanha criada com sucesso",
  "campanha": { ... }
}
```

> **Auto-Slug:** Gerado automaticamente do título se não fornecido.

---

### 10. Atualizar Campanha

**`PUT /api/campanhas/{campanha_id}`** — Admin  
Aceita `public_id` (UUID) ou `id` interno.

```json
// Request (todos opcionais)
{
  "titulo": "Novo Título",
  "status": "concluido",
  "data_sorteio": "2026-07-01T20:00:00"
}

// Response 200
{
  "mensagem": "Campanha atualizada com sucesso",
  "campanha": { ... }
}
```

---

### 11. Deletar Campanha (Soft Delete)

**`DELETE /api/campanhas/{campanha_id}`** — Admin  
**`DELETE /api/campanhas/{campanha_id}?permanente=true`** — Admin (hard delete irreversível)

Por padrão executa **soft delete**: a campanha é marcada com `deleted_at = now` e some das listagens públicas, mas pode ser restaurada. Com `?permanente=true`, a campanha e todos os registros associados são removidos permanentemente.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `permanente` | boolean | `false` | `true` para hard delete irreversível |

```json
// Soft delete — Response 200
{ "mensagem": "Campanha removida com sucesso (reversível via /restaurar)" }

// Hard delete — Response 200
{ "mensagem": "Campanha excluída permanentemente" }
```

**Erros:**

| Código | Condição |
|--------|----------|
| `403` | Usuário não é admin |
| `404` | Campanha não encontrada |
| `409` | Campanha já está removida (soft delete duplicado) |

> **Soft delete:** Campanhas removidas não aparecem em `GET /api/campanhas`, `GET /api/campanhas/{slug}` nem podem receber novas compras. O contador do dashboard também as exclui.  
> **Hard delete:** Remove permanentemente Compras, Títulos e Títulos Premiados em cascade. Use com cautela — a operação é irreversível.

---

### 12. Restaurar Campanha

**`POST /api/campanhas/{campanha_id}/restaurar`** — Admin

Desfaz um soft delete, tornando a campanha visível novamente.

```json
// Response 200
{
  "mensagem": "Campanha restaurada com sucesso",
  "campanha": { "...campos da campanha..." }
}
```

**Erros:**

| Código | Condição |
|--------|----------|
| `403` | Usuário não é admin |
| `404` | Campanha não encontrada |
| `409` | Campanha não está removida |

> A ação é registrada no `AdminLog` com a action `"Restauração de Campanha"`.

---

### 12. Buscar Compradores da Campanha

**`GET /api/campanhas/{campanha_id}/compradores?q={termo}`** — Admin

Busca compradores aprovados por nome, telefone ou número de cota.

```json
// Response 200
{
  "compradores": [
    {
      "compra_id": 45,
      "titulo_id": 1230,
      "usuario_id": 7,
      "nome": "Pedro Henrique",
      "telefone": "83994099696",
      "numero_titulo": "00123",
      "data_compra": "2026-03-01T10:00:00Z"
    }
  ],
  "total": 1
}
```

---

### 13. Definir Ganhador da Campanha

**`POST /api/campanhas/{campanha_id}/ganhador`** — Admin

```json
// Request
{
  "compra_id": 45,
  "titulo_id": 1230
}

// Response 200
{
  "mensagem": "Ganhador definido com sucesso",
  "ganhador": {
    "nome": "Pedro Henrique",
    "campanha": "iPhone 15 Pro Max"
  }
}
```

> Define `status = 'concluido'`, `data_conclusao = hoje`, `numero_sorteado` e marca o título como ganhador.

---

## Títulos Premiados

### 14. Listar Títulos Premiados

**`GET /api/campanhas/{slug}/titulos-premiados`** — Público

```json
// Response 200
{
  "titulos_premiados": [
    {
      "id": 1,
      "numero_titulo": "011111",
      "valor_premio": 500.00,
      "status": "disponivel",
      "ganhador_nome": null,
      "dono": {
        "compra_id": 45,
        "titulo_id": 1230,
        "usuario_id": 7,
        "nome": "Pedro Henrique",
        "telefone": "83994099696"
      }
    },
    {
      "id": 2,
      "numero_titulo": "099999",
      "valor_premio": 300.00,
      "status": "disponivel",
      "ganhador_nome": null,
      "dono": null
    }
  ],
  "total": 2,
  "ganhos": 0,
  "disponiveis": 2
}
```

> Campo `dono` identifica automaticamente quem possui aquele número via busca nas compras aprovadas. `dono = null` significa que nenhuma compra aprovada possui aquele número.

---

### 15. Adicionar Título Premiado

**`POST /api/campanhas/{campanha_id}/titulos-premiados`** — Admin

```json
// Request
{
  "numero_titulo": "011111",
  "valor_premio": 500.00
}

// Response 201
{
  "mensagem": "Título premiado adicionado",
  "titulo": {
    "id": 1,
    "numero_titulo": "011111",
    "valor_premio": 500.00,
    "status": "disponivel"
  }
}
```

---

### 16. Remover Título Premiado

**`DELETE /api/campanhas/titulos-premiados/{titulo_id}`** — Admin

```json
// Response 200
{ "mensagem": "Título premiado removido" }
```

---

## Checkout e Pagamentos

### 17. Criar Checkout

**`POST /api/checkout`** — Requer auth

```json
// Request
{
  "campanha_id": 1,
  "quantidade_titulos": 10,
  "metodo_pagamento": "pix"
}

// Response 201
{
  "mensagem": "Checkout criado com sucesso",
  "compra_id": "uuid-da-compra",
  "status_pagamento": "pendente",
  "valor_total": 100.00,
  "metodo_pagamento": "pix",
  "pagamento": {
    "tipo": "pix",
    "pix_code": "00020101...",
    "qr_code": "data:image/png;base64,iVBOR...",
    "qr_code_base64": "data:image/png;base64,iVBOR...",
    "copia_cola": "00020101...",
    "payment_url": "https://...",
    "payment_id": "bill_abc123",
    "expira_em": "2026-03-04T12:10:00Z",
    "instrucoes": "Escaneie o QR Code ou use o Copia e Cola no app do seu banco."
  },
  "compra": {
    "id": "uuid-da-compra",
    "campanha": { "id": 1, "titulo": "iPhone 15 Pro Max", "slug": "iphone-15-pro-max" },
    "quantidade_titulos": 10,
    "valor_total": 100.00,
    "status_pagamento": "pendente"
  }
}
```

> **Gateway:** AbacatePay (PIX). Sem `ABACATEPAY_API_KEY` configurada, retorna dados mock para desenvolvimento.  
> **Perfil obrigatório:** CPF (11 dígitos), e-mail válido e telefone com DDD são exigidos pelo gateway — o checkout retorna 400 se o perfil estiver incompleto.

**Erros comuns:**

| Código | Mensagem |
|--------|----------|
| 400 | `campanha_id e quantidade_titulos são obrigatórios` |
| 400 | `Complete seu perfil para realizar o pagamento: CPF obrigatório, ...` |
| 400 | `Campanha não está ativa` |
| 400 | `Quantidade indisponível. X título(s) disponível(is)` |
| 400 | `Quantidade mínima de compra: N títulos` |

---

### 18. Consultar Status de Pagamento

**`GET /api/pagamentos/{compra_id}`** — Requer auth  
Aceita `public_id` (UUID) ou `id` interno.

```json
// Response 200
{
  "compra_id": "uuid-da-compra",
  "status_pagamento": "aprovado",
  "metodo_pagamento": "pix",
  "valor_total": 100.00,
  "quantidade_titulos": 10,
  "data_pagamento": "2026-03-04T12:05:00Z",
  "criado_em": "2026-03-04T12:00:00Z",
  "expira_em": "2026-03-04T12:10:00Z",
  "campanha": {
    "id": "uuid-da-campanha",
    "titulo": "iPhone 15 Pro Max",
    "slug": "iphone-15-pro-max",
    "imagem_principal": "https://...",
    "valor_titulo": 10.00,
    "total_titulos": 10000
  },
  "pagamento": {
    "tipo": "pix",
    "pix_code": "00020101...",
    "qr_code": "data:image/png;base64,...",
    "copia_cola": "00020101...",
    "qr_code_base64": "data:image/png;base64,..."
  }
}
```

> `pagamento` é `null` se não houver dados PIX salvos (compra já aprovada ou expirada).  
> **Status:** `pendente` → `aprovado` | `cancelado` | `recusado` | `expirado`  
> **Expiração em tempo real:** Se a compra ultrapassou `expira_em`, o status é atualizado para `expirado` na consulta.

---

### 19. Webhook de Pagamento

**`POST /api/pagamentos/webhook`** — Validação HMAC

Header: `X-Webhook-Signature: {assinatura_hmac}`

```json
// Request (AbacatePay)
{
  "event": "billing.paid",
  "data": {
    "billing": {
      "id": "bill_abc123",
      "status": "PAID",
      "products": [{ "externalId": "uuid-da-compra" }]
    }
  }
}

// Response 200
{ "mensagem": "Pagamento aprovado com sucesso" }

// Response 200 (já processado)
{ "mensagem": "Já processado" }

// Response 200 (evento ignorado)
{ "mensagem": "Evento ignorado" }
```

> Ao aprovar: incrementa `titulos_vendidos`, gera os títulos da compra e atualiza `data_pagamento`.  
> Em produção, `ABACATEPAY_WEBHOOK_SECRET` é obrigatório — requisições sem assinatura válida retornam 401.

---

### 20. Aprovar Pagamento Manualmente

**`POST /api/pagamentos/{compra_id}/aprovar`** — Admin

```json
// Response 200
{
  "mensagem": "Pagamento aprovado manualmente",
  "compra_id": "uuid-da-compra",
  "status_anterior": "pendente",
  "status_atual": "aprovado",
  "aprovado_por": "Nome do Admin"
}
```

> Útil para pagamentos offline ou testes. Não pode aprovar compras expiradas.

---

## Compras e Títulos

### 21. Meus Títulos

**`GET /api/meus-titulos`** — Requer auth

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `page` | integer | Página |
| `per_page` | integer | Itens por página |

```json
// Response 200
{
  "compras": [
    {
      "id": "uuid-da-compra",
      "campanha": {
        "id": 1,
        "titulo": "iPhone 15 Pro Max",
        "slug": "iphone-15-pro-max",
        "imagem_principal": "https://...",
        "status": "ativo"
      },
      "quantidade_titulos": 10,
      "valor_total": 100.00,
      "status_pagamento": "aprovado",
      "metodo_pagamento": "pix",
      "criado_em": "2026-03-04T12:00:00Z",
      "titulos": [
        { "id": 1, "numero": "000123", "is_ganhador": false }
      ]
    }
  ],
  "total": 1,
  "paginas": 1,
  "pagina_atual": 1
}
```

> **Ordenação:** Pendentes → Aprovadas → Expiradas.

---

### 22. Deletar Compra

**`DELETE /api/compras/{compra_id}`** — Admin  
Aceita `public_id` (UUID) ou `id` interno.

```json
// Response 200
{ "mensagem": "Compra deletada com sucesso" }
```

---

## Ganhadores

### 23. Listar Ganhadores

**`GET /api/ganhadores`** — Público

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `page` | integer | `1` | Página |
| `per_page` | integer | `20` | Itens por página |

```json
// Response 200
{
  "ganhadores": [
    {
      "id": "uuid-da-campanha",
      "name": "Pedro ***",
      "campaignTitle": "iPhone 15 Pro Max",
      "prize": "iPhone 15 Pro Max 256GB",
      "luckyNumber": "00123",
      "drawDate": "15/03/2026",
      "phone": "(**) *****-1234"
    }
  ],
  "total": 5,
  "paginas": 1
}
```

> Todos os dados pessoais são mascarados automaticamente.

---

## Admin

### 24. Listar Usuários

**`GET /api/painel-secreto-x9/usuarios`** — Admin  
*(Prefixo configurável via `ADMIN_ROUTE_SECRET`)*

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `page` | integer | Página |
| `per_page` | integer | Itens por página |

```json
// Response 200
{
  "usuarios": [
    {
      "id": 1,
      "nome": "João Silva",
      "telefone": "(**) *****-9999",
      "email": "jo***@email.com",
      "cpf": "123.***.***-**",
      "is_admin": false,
      "criado_em": "2026-03-04T00:00:00"
    }
  ],
  "total": 100,
  "paginas": 5,
  "pagina_atual": 1
}
```

---

### 25. Dashboard Admin

**`GET /api/painel-secreto-x9/dashboard`** — Admin

```json
// Response 200
{
  "stats": {
    "total_usuarios": 150,
    "total_campanhas": 8,
    "campanhas_ativas": 3,
    "receita_total": 9800.00
  },
  "ultimas_vendas": [
    {
      "id": "uuid-da-compra",
      "campanha": "iPhone 15 Pro Max",
      "usuario": "João Silva",
      "valor": 100.00,
      "data": "2026-04-30T12:00:00"
    }
  ]
}
```

---

### 26. Auditoria do Sorteio da Campanha

**`GET /api/painel-secreto-x9/campanhas/{campanha_id}/auditoria`** — Admin  
Aceita `public_id` (UUID) ou `id` interno. Prefixo configurável via `ADMIN_ROUTE_SECRET`.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `page` | integer | `1` | Página |
| `per_page` | integer | `20` | Itens por página (máx. 50) |

```json
// Response 200
{
  "campanha_id": "uuid-da-campanha",
  "campanha_titulo": "iPhone 15 Pro Max",
  "auditoria": [
    {
      "id": 12,
      "admin_name": "Pedro Admin",
      "action": "Definição de Ganhador",
      "details": "campanha_id=uuid-... | campanha='iPhone 15 Pro Max' | ganhador_id=7 | ganhador='Pedro' | numero_sorteado=00123 | metodo=manual",
      "ip_address": "177.x.x.x",
      "created_at": "2026-05-03T18:00:00Z"
    },
    {
      "id": 3,
      "admin_name": "Pedro Admin",
      "action": "Criação de Campanha",
      "details": "Args: {}",
      "ip_address": "177.x.x.x",
      "created_at": "2026-04-01T10:00:00Z"
    }
  ],
  "total": 2,
  "pagina": 1,
  "por_pagina": 20,
  "paginas": 1
}
```

> Registra automaticamente: criação de campanha, atualização, soft delete, restauração e definição de ganhador (via `@with_admin_log`). O campo `details` contém `metodo` (manual/automatico), `ganhador_id`, `numero_sorteado` e `campanha_id` para o sorteio.  
> Ações do sistema (expiração automática de compras) aparecem com `admin_name = "Sistema/Desconhecido"`.

---

### 27. Compras Expiradas

**`GET /api/painel-secreto-x9/compras/expiradas`** — Admin

Lista todas as compras com `status_pagamento = 'expirado'`, ordenadas da mais recente para a mais antiga. Prefixo configurável via `ADMIN_ROUTE_SECRET`.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `page` | integer | `1` | Página |
| `per_page` | integer | `20` | Itens por página (máx. 50) |

```json
// Response 200
{
  "compras": [
    {
      "id": "uuid-da-compra",
      "campanha": "iPhone 15 Pro Max",
      "usuario": "João Silva",
      "quantidade_titulos": 10,
      "valor_total": 100.00,
      "expira_em": "2026-05-07T14:10:00Z",
      "criado_em": "2026-05-07T14:00:00Z"
    }
  ],
  "total": 38,
  "pagina": 1,
  "por_pagina": 20,
  "paginas": 2
}
```

> Compras são expiradas automaticamente pelo scheduler a cada **5 minutos**. Cada execução gera uma entrada no `AdminLog` com `action = "Expiração Automática de Compras"` e os campos `compras_expiradas`, `titulos_liberados` e `duracao` em `details`.

---

## Artigos

### 28. Listar Artigos

**`GET /api/artigos`** — Público

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `page` | integer | `1` | Página |
| `per_page` | integer | `10` | Itens por página |

```json
// Response 200
{
  "artigos": [ { ... } ],
  "total": 5,
  "paginas": 1
}
```

---

### 29. Detalhes do Artigo

**`GET /api/artigos/{slug}`** — Público

```json
// Response 200
{ ... }

// Response 404
{ "erro": "Artigo não encontrado" }
```

---

## Comunicados

### 30. Listar Comunicados

**`GET /api/comunicados`** — Público  
Retorna comunicados ativos, ordenados do mais recente ao mais antigo, com suporte a paginação.

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `page` | integer | `1` | Página (começa em 1) |
| `per_page` | integer | `10` | Itens por página (máximo: **50**) |

```json
// Response 200
{
  "comunicados": [
    {
      "id": 1,
      "titulo": "Manutenção Programada",
      "conteudo": "O sistema estará em manutenção...",
      "tipo": "aviso",
      "ativo": true,
      "criado_em": "2026-03-04T00:00:00"
    }
  ],
  "total": 42,
  "pagina": 1,
  "por_pagina": 10,
  "paginas": 5
}
```

**Tipos:** `informativo`, `alerta`, `aviso`

---

### 31. Criar Comunicado

**`POST /api/comunicados`** — Admin

```json
// Request
{
  "titulo": "Novo Sorteio",
  "conteudo": "Participem do novo sorteio...",
  "tipo": "informativo"
}
// Response 201
{ "mensagem": "Comunicado criado com sucesso", "comunicado": { ... } }
```

---

### 32. Atualizar Comunicado

**`PUT /api/comunicados/{id}`** — Admin

```json
// Request (todos opcionais)
{ "titulo": "...", "conteudo": "...", "tipo": "alerta", "ativo": false }
// Response 200
{ "mensagem": "Comunicado atualizado", "comunicado": { ... } }
```

---

### 33. Excluir Comunicado

**`DELETE /api/comunicados/{id}`** — Admin

```json
// Response 200
{ "mensagem": "Comunicado excluído com sucesso" }
```

---

## Contato

### 34. Enviar Mensagem de Contato

**`POST /api/contato`** — Público | Rate limit: 3/min

```json
// Request
{
  "nome": "João Silva",
  "email": "joao@email.com",
  "mensagem": "Tenho uma dúvida sobre...",
  "telefone": "11999999999",
  "assunto": "Dúvida"
}
// Response 201
{ "mensagem": "Mensagem enviada com sucesso" }
```

> **Obrigatórios:** `nome`, `email`, `mensagem`. Campos `telefone` e `assunto` são opcionais.

---

## Validação de Entrada

Todos os endpoints de escrita (POST/PUT) utilizam validação automática via **Marshmallow**. Quando o corpo da requisição não satisfaz o schema esperado, a API retorna:

**`400 Bad Request`**

```json
{
  "erro": "Dados inválidos",
  "campos": {
    "email": ["Not a valid email address."],
    "titulo": ["Missing data for required field."],
    "quantidade_titulos": ["Must be greater than or equal to 1."]
  }
}
```

### Regras gerais

| Regra | Comportamento |
|-------|---------------|
| Campo obrigatório ausente | `400` com `"Missing data for required field."` |
| Campo extra não esperado | `400` com `"Unknown field."` |
| Tipo inválido | `400` com mensagem descritiva do tipo esperado |
| Email inválido | `400` com `"Not a valid email address."` |
| Telefone com menos de 10 dígitos | `400` com `"Telefone inválido (mínimo 10 dígitos)."` |
| CPF diferente de 11 dígitos | `400` com `"CPF deve conter exatamente 11 dígitos."` |
| String fora do tamanho permitido | `400` com `"Shorter than minimum length X."` / `"Longer than maximum length X."` |

### Campos opcionais em endpoints PUT

Endpoints de atualização (`PUT`) aceitam qualquer subconjunto dos campos — campos ausentes são simplesmente ignorados, sem sobrescrever o valor atual. Exemplo: um `PUT /api/auth/perfil` enviando apenas `{ "cidade": "Recife" }` atualiza somente a cidade.

### Schemas por endpoint

| Endpoint | Schema |
|----------|--------|
| `POST /api/auth/registro` | `RegistroSchema` |
| `POST /api/auth/login` | `LoginSchema` |
| `POST /api/auth/forgot-password` | `ForgotSenhaSchema` |
| `POST /api/auth/reset-password` | `ResetSenhaSchema` |
| `PUT /api/auth/perfil` | `AtualizarPerfilSchema` |
| `POST /api/campanhas` | `CriarCampanhaSchema` |
| `PUT /api/campanhas/{id}` | `AtualizarCampanhaSchema` |
| `POST /api/campanhas/{id}/titulos-premiados` | `TitulosPremiadosSchema` |
| `POST /api/campanhas/{id}/ganhador` | `GanhadorSchema` |
| `POST /api/compras` | `CheckoutSchema` |
| `POST /api/comunicados` | `ComunicadoSchema` |
| `PUT /api/comunicados/{id}` | `AtualizarComunicadoSchema` |
| `POST /api/contato` | `ContatoSchema` |

---

## Deploy Railway

### Migrations de Schema (Flask-Migrate)

O projeto usa **Flask-Migrate** para versionamento de schema. O `Procfile` já está configurado para rodar as migrations automaticamente a cada deploy:

```
release: flask db upgrade && python scripts/create_admin.py
web:     gunicorn wsgi:app ...
```

O comando `release` executa **antes** do servidor subir. Para cada deploy:
- Se o banco já estiver atualizado → `flask db upgrade` não faz nada
- Se houver migrations pendentes → aplica em ordem antes do servidor receber tráfego

**Primeiro deploy (banco PostgreSQL vazio):**

```bash
# O wsgi.py cria todas as tabelas via db.create_all() na inicialização.
# O release phase stampa a baseline e aplica qualquer migration pendente.
# Nenhuma ação manual necessária.
```

**Adicionar uma coluna nova (workflow completo):**

```bash
# 1. Editar o modelo (ex: app/models/usuario.py)

# 2. Gerar migration localmente
flask db migrate -m "adiciona campo X em usuarios"

# 3. Revisar o arquivo gerado em migrations/versions/

# 4. Aplicar localmente
flask db upgrade

# 5. Commitar modelo + migration juntos
git add app/models/ migrations/
git commit -m "feat: adiciona campo X"
# Railway aplica via release: flask db upgrade no próximo deploy
```

**Comandos úteis:**

```bash
flask db current    # versão aplicada no banco
flask db history    # histórico de migrations
flask db upgrade    # aplica migrations pendentes
flask db downgrade  # reverte a migration anterior
```

---

### Variáveis de Ambiente Obrigatórias

| Variável | Descrição |
|----------|-----------|
| `DATABASE_URL` | Gerado automaticamente pelo plugin PostgreSQL |
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | Chave secreta Flask (mín. 32 chars) |
| `JWT_SECRET_KEY` | Chave JWT (mín. 32 chars) |
| `CORS_ORIGINS` | URLs do frontend separadas por vírgula |
| `BASE_URL` | URL do backend no Railway |
| `ABACATEPAY_API_KEY` | Chave de produção AbacatePay |
| `ABACATEPAY_WEBHOOK_SECRET` | Secret do webhook AbacatePay (obrigatório em produção) |
| `ADMIN_ROUTE_SECRET` | Prefixo da rota admin (padrão: `/api/painel-secreto-x9`) |

### Geração de Chaves Seguras

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

> **DATABASE_URL:** O Railway fornece com prefixo `postgres://` — o sistema corrige automaticamente para `postgresql://` (compatível com SQLAlchemy).

---

## Códigos de Status

| Código | Significado |
|--------|-------------|
| `200` | OK |
| `201` | Criado com sucesso |
| `400` | Requisição inválida |
| `401` | Não autenticado / Assinatura inválida |
| `403` | Sem permissão (admin requerido) |
| `404` | Recurso não encontrado |
| `429` | Too Many Requests (rate limiting) |
| `500` | Erro interno do servidor |

---

## Segurança

- **UUIDs públicos:** Campanhas e compras expõem `public_id` (UUID) em vez de IDs internos
- **Mascaramento:** CPF, email e telefone são mascarados nas respostas
- **Rate Limiting:** Registro e login (5/min), forgot-password (3/min), contato (3/min)
- **Rota Admin Ofuscada:** Prefixo configurável via `ADMIN_ROUTE_SECRET`
- **HMAC Webhook:** Assinatura HMAC-SHA256 validada em todos os webhooks de pagamento em produção
- **JWT:** Tokens expiram em 7 dias
