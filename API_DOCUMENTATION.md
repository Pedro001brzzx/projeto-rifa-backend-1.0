# Documentação da API - Sistema de Rifas 

> Documentação completa para integração front-end

**Base URL (Produção):** `https://SEU_BACKEND.up.railway.app`  
**Base URL (Dev):** `http://localhost:5000`  
**Versão:** 2.1  
**Formato de resposta:** JSON  
**Autenticação:** JWT Bearer Token  
**Última atualização:** Maio 2026 (Fase A concluída)

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

---

## Índice

- [Autenticação](#autenticação)
- [Campanhas](#campanhas)
- [Títulos Premiados](#títulos-premiados)
- [Checkout e Pagamentos](#checkout-e-pagamentos)
- [Compras e Títulos](#compras-e-títulos)
- [Ganhadores](#ganhadores)
- [Admin](#admin)
- [Artigos](#artigos)
- [Comunicados](#comunicados)
- [Contato](#contato)
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

### 11. Deletar Campanha

**`DELETE /api/campanhas/{campanha_id}`** — Admin

```json
// Response 200
{ "mensagem": "Campanha deletada com sucesso" }
```

> **Hard delete:** Remove permanentemente a campanha e todos os registros associados (Compras, Títulos, Títulos Premiados) via cascade. Funciona mesmo que existam compras aprovadas. Use com cautela.

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

> Registra automaticamente: criação de campanha, atualização, exclusão e definição de ganhador (via `@with_admin_log`). O campo `details` contém `metodo` (manual/automatico), `ganhador_id`, `numero_sorteado` e `campanha_id` para o sorteio.

---

## Artigos

### 26. Listar Artigos

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

### 27. Detalhes do Artigo

**`GET /api/artigos/{slug}`** — Público

```json
// Response 200
{ ... }

// Response 404
{ "erro": "Artigo não encontrado" }
```

---

## Comunicados

### 28. Listar Comunicados

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

### 29. Criar Comunicado

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

### 30. Atualizar Comunicado

**`PUT /api/comunicados/{id}`** — Admin

```json
// Request (todos opcionais)
{ "titulo": "...", "conteudo": "...", "tipo": "alerta", "ativo": false }
// Response 200
{ "mensagem": "Comunicado atualizado", "comunicado": { ... } }
```

---

### 31. Excluir Comunicado

**`DELETE /api/comunicados/{id}`** — Admin

```json
// Response 200
{ "mensagem": "Comunicado excluído com sucesso" }
```

---

## Contato

### 32. Enviar Mensagem de Contato

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

## Deploy Railway

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
