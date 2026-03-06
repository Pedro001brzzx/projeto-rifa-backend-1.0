# Documentação da API - Sistema de Rifas Gêmeos Brasil

> Documentação completa para integração front-end

**Base URL (Produção):** `https://SEU_BACKEND.up.railway.app`  
**Base URL (Dev):** `http://localhost:5000`  
**Versão:** 2.0  
**Formato de resposta:** JSON  
**Autenticação:** JWT Bearer Token  
**Última atualização:** Março 2026

---

## 📋 Índice

- [Autenticação](#-autenticação)
- [Campanhas](#-campanhas)
- [Títulos Premiados](#-títulos-premiados)
- [Checkout e Pagamentos](#-checkout-e-pagamentos)
- [Compras e Títulos](#-compras-e-títulos)
- [Ganhadores](#-ganhadores)
- [Admin](#-admin)
- [Comunicados](#-comunicados)
- [Contato](#-contato)
- [Deploy (Railway)](#-deploy-railway)
- [Códigos de Status](#-códigos-de-status)

---

## 🔐 Autenticação

Todos os endpoints protegidos exigem o token JWT no header:

```
Authorization: Bearer {token}
```

### 1. Registro de Usuário

**`POST /api/auth/registro`** — Público

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

**`POST /api/auth/login`** — Público

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

**`POST /api/auth/logout`** — 🔒 Requer auth

```json
// Response 200
{ "mensagem": "Logout realizado com sucesso" }
```

---

### 4. Obter Perfil

**`GET /api/auth/perfil`** — 🔒 Requer auth

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

**`PUT /api/auth/perfil`** — 🔒 Requer auth

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

**`POST /api/auth/esqueci-senha`** — Público

```json
// Request
{ "email": "joao@email.com" }

// Response 200 (sempre, por segurança)
{ "mensagem": "Se o email estiver cadastrado, você receberá instruções de recuperação" }
```

**`POST /api/auth/redefinir-senha`** — Público

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

## 🎯 Campanhas

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
      "descricao": "...",
      "imagem_principal": "https://...",
      "premio": "iPhone 15 Pro Max 256GB",
      "valor_titulo": 10.00,
      "total_titulos": 10000,
      "titulos_vendidos": 5432,
      "titulos_disponiveis": 4568,
      "percentual_vendido": 54.32,
      "data_sorteio": "2026-06-01T20:00:00",
      "data_conclusao": null,
      "status": "ativo",
      "criado_em": "2026-01-01T00:00:00",
      "min_quantidade_compra": 1,
      "ganhador": null
    }
  ],
  "total": 15,
  "paginas": 2,
  "pagina_atual": 1
}
```

> **Novidade v2:** Sem filtro de status padrão — retorna ativas e concluídas. Campo `data_conclusao` incluído para campanhas finalizadas.

---

### 8. Detalhes da Campanha

**`GET /api/campanhas/{slug}`** — Público

```json
// Response 200 — Campanha ativa
{
  "id": 1,
  "public_id": "uuid-da-campanha",
  "titulo": "iPhone 15 Pro Max",
  "slug": "iphone-15-pro-max",
  "premio": "iPhone 15 Pro Max 256GB",
  "valor_titulo": 10.00,
  "status": "ativo",
  "ganhador": null,
  "min_quantidade_compra": 5
}

// Response 200 — Campanha concluída
{
  "id": 2,
  "status": "concluido",
  "data_conclusao": "15/03/2026",
  "numero_sorteado": "00123",
  "ganhador": {
    "nome": "Pedro H***",
    "telefone": "(**) *****-1234",
    "premio": "iPhone 15 Pro Max 256GB",
    "numero_sorteado": "00123",
    "data_conclusao": "15/03/2026"
  }
}
```

---

### 9. Criar Campanha

**`POST /api/campanhas`** — 🔒 Admin

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

**`PUT /api/campanhas/{campanha_id}`** — 🔒 Admin  
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

**`DELETE /api/campanhas/{campanha_id}`** — 🔒 Admin

```json
// Response 200
{ "mensagem": "Campanha deletada com sucesso" }
```

> **Atenção:** A exclusão realiza *cascade delete*, ou seja, apaga definitivamente todas as **Compras**, **Títulos** e **Títulos Premiados** associados à campanha para evitar erros de integridade no banco. Utilize com cautela.

---

### 12. Buscar Compradores da Campanha

**`GET /api/campanhas/{campanha_id}/compradores?q={termo}`** — 🔒 Admin

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

**`POST /api/campanhas/{campanha_id}/ganhador`** — 🔒 Admin

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

## 🏆 Títulos Premiados

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

> **Novidade v2:** Campo `dono` identifica **automaticamente** quem possui o número do título premiado via busca na tabela de compras aprovadas. Se `dono = null`, nenhuma compra aprovada possui aquele número.

---

### 15. Adicionar Título Premiado

**`POST /api/campanhas/{campanha_id}/titulos-premiados`** — 🔒 Admin

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

**`DELETE /api/campanhas/titulos-premiados/{titulo_id}`** — 🔒 Admin

```json
// Response 200
{ "mensagem": "Título premiado removido" }
```

---

## 💳 Checkout e Pagamentos

### 17. Criar Checkout

**`POST /api/checkout`** — 🔒 Requer auth

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
  "compra_id": 1,
  "public_id": "uuid-da-compra",
  "status_pagamento": "pendente",
  "valor_total": 100.00,
  "metodo_pagamento": "pix",
  "pagamento": {
    "tipo": "pix",
    "qr_code": "00020101...",
    "qr_code_base64": "data:image/png;base64,iVBOR...",
    "copia_cola": "00020101...",
    "payment_id": "bill_abc123",
    "expira_em": "2026-03-04T12:10:00",
    "instrucoes": "Pague com PIX via AbacatePay"
  },
  "compra": {
    "id": 1,
    "campanha": { "id": 1, "titulo": "iPhone 15 Pro Max", "slug": "iphone-15-pro-max" },
    "quantidade_titulos": 10,
    "valor_total": 100.00,
    "status_pagamento": "pendente",
    "titulos": [
      { "id": 1, "numero": "000123", "is_ganhador": false }
    ]
  }
}
```

> **Gateway:** AbacatePay (PIX). Em dev sem chave configurada retorna dados mock.

**Erros comuns:**

| Código | Mensagem |
|--------|----------|
| 400 | `campanha_id e quantidade_titulos são obrigatórios` |
| 400 | `Complete seu perfil para realizar o pagamento` |
| 400 | `Campanha não está ativa` |
| 400 | `Quantidade indisponível. X título(s) disponível(is)` |
| 400 | `Quantidade mínima de compra: N títulos` |

---

### 18. Consultar Status de Pagamento

**`GET /api/pagamentos/{compra_id}`** — 🔒 Requer auth  
Aceita `public_id` (UUID) ou `id` interno.

```json
// Response 200
{
  "compra_id": 1,
  "status_pagamento": "aprovado",
  "metodo_pagamento": "pix",
  "valor_total": 100.00,
  "quantidade_titulos": 10,
  "data_pagamento": "2026-03-04T12:05:00",
  "criado_em": "2026-03-04T12:00:00",
  "expira_em": "2026-03-04T12:10:00",
  "campanha": {
    "titulo": "iPhone 15 Pro Max",
    "slug": "iphone-15-pro-max",
    "valor_titulo": 10.00
  }
}
```

**Status:** `pendente` → `aprovado` | `cancelado` | `recusado` | `expirado`

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
      "products": [{ "externalId": "1" }]
    }
  }
}

// Response 200
{
  "mensagem": "Webhook processado com sucesso",
  "compra_id": 1,
  "status_anterior": "pendente",
  "status_atual": "aprovado",
  "gateway": "abacatepay"
}
```

> Ao aprovar: atualiza `data_pagamento`, incrementa `titulos_vendidos`, gera os títulos da compra.

---

## 📋 Compras e Títulos

### 20. Meus Títulos

**`GET /api/meus-titulos`** — 🔒 Requer auth

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `page` | integer | Página |
| `per_page` | integer | Itens por página |

```json
// Response 200
{
  "compras": [
    {
      "id": 1,
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

## 🏅 Ganhadores

### 21. Listar Ganhadores

**`GET /api/ganhadores`** — Público

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `limit` | integer | `10` | Máximo de registros |
| `page` | integer | `1` | Página |
| `per_page` | integer | `20` | Itens por página |

```json
// Response 200
{
  "ganhadores": [
    {
      "id": "uuid-da-campanha",
      "name": "Pedro H***",
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

> Todos os dados pessoais são **mascarados** automaticamente.

---

## 🛠 Admin

### 22. Listar Usuários

**`GET /api/painel-secreto-x9/usuarios`** — 🔒 Admin  
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
  "paginas": 5
}
```

---

### 23. Dashboard Admin

**`GET /api/painel-secreto-x9/dashboard`** — 🔒 Admin

```json
// Response 200
{
  "campanhas_ativas": 3,
  "campanhas_concluidas": 5,
  "total_usuarios": 150,
  "total_compras_aprovadas": 320,
  "receita_total": 9800.00
}
```

---

## 📢 Comunicados

### 24. Listar Comunicados

**`GET /api/comunicados`** — Público

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
  ]
}
```

**Tipos:** `informativo`, `alerta`, `aviso`

---

### 25. Criar Comunicado

**`POST /api/comunicados`** — 🔒 Admin

```json
// Request
{
  "titulo": "Novo Sorteio",
  "conteudo": "Participem do novo sorteio...",
  "tipo": "informativo"
}
// Response 201
{ "mensagem": "Comunicado criado", "comunicado": { ... } }
```

---

### 26. Atualizar Comunicado

**`PUT /api/comunicados/{id}`** — 🔒 Admin

```json
// Request (todos opcionais)
{ "titulo": "...", "conteudo": "...", "tipo": "alerta", "ativo": false }
// Response 200
{ "mensagem": "Comunicado atualizado", "comunicado": { ... } }
```

---

### 27. Excluir Comunicado

**`DELETE /api/comunicados/{id}`** — 🔒 Admin

```json
// Response 200
{ "mensagem": "Comunicado excluído" }
```

---

## 📬 Contato

### 28. Enviar Mensagem de Contato

**`POST /api/contato`** — Público

```json
// Request
{
  "nome": "João Silva",
  "email": "joao@email.com",
  "mensagem": "Tenho uma dúvida sobre..."
}
// Response 200
{ "mensagem": "Mensagem enviada com sucesso" }
```

---

## 🚀 Deploy Railway

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
| `ABACATEPAY_WEBHOOK_SECRET` | Secret do webhook AbacatePay |

### Geração de Chaves Seguras

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

> **DATABASE_URL:** O Railway fornece com prefixo `postgres://` — o sistema corrige automaticamente para `postgresql://` (compatível com SQLAlchemy).

---

## 📊 Códigos de Status

| Código | Significado |
|--------|-------------|
| `200` | OK |
| `201` | Criado com sucesso |
| `400` | Requisição inválida |
| `401` | Não autenticado |
| `403` | Sem permissão (admin requerido) |
| `404` | Recurso não encontrado |
| `429` | Too Many Requests (rate limiting) |
| `500` | Erro interno do servidor |

---

## 🔒 Segurança

- **UUIDs públicos:** Campanhas e compras expõem `public_id` (UUID) em vez de IDs internos
- **Mascaramento:** CPF, email e telefone são mascarados nas respostas
- **Rate Limiting:** Endpoints críticos têm limite de requisições
- **Rota Admin Ofuscada:** Prefixo configurável via `ADMIN_ROUTE_SECRET`
- **HMAC Webhook:** Assinatura validada em todos os webhooks de pagamento
- **JWT:** Tokens expiram em 7 dias
