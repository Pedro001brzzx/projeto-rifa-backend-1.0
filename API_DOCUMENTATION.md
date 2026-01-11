# Documentação da API - Sistema de Rifas Gêmeos Brasil

> Documentação completa para integração front-end

**Base URL:** `http://localhost:5000`  
**Versão:** 1.0  
**Formato de resposta:** JSON  
**Autenticação:** JWT Bearer Token

---

## 📋 Índice

- [Autenticação](#autenticação)
- [Campanhas](#campanhas)
- [Compras e Títulos](#compras-e-títulos)
- [Ganhadores](#ganhadores)
- [Admin](#admin)
- [Artigos](#artigos)
- [Comunicados](#comunicados)
- [Contato](#contato)
- [Códigos de Status](#códigos-de-status)
- [Tipos de Dados](#tipos-de-dados)

---

## 🔐 Autenticação

Todos os endpoints que requerem autenticação devem incluir o token JWT no header:

```
Authorization: Bearer {token}
```

### 1. Registro de Usuário

**Endpoint:** `POST /api/auth/registro`  
**Autenticação:** Não requerida  
**Descrição:** Registra um novo usuário no sistema

#### Request Body

```json
{
  "nome": "João Silva",
  "telefone": "11999999999",
  "senha": "senha123",
  "email": "joao@email.com",
  "cpf": "123.456.789-00",
  "cidade": "São Paulo",
  "estado": "SP"
}
```

**Campos obrigatórios:**
- `nome` (string)
- `telefone` (string) - Deve ser único
- `senha` (string)

**Campos opcionais:**
- `email` (string)
- `cpf` (string)
- `cidade` (string)
- `estado` (string, 2 caracteres)

#### Response (201 Created)

```json
{
  "mensagem": "Usuário cadastrado com sucesso",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "usuario": {
    "id": 1,
    "nome": "João Silva",
    "telefone": "11999999999",
    "email": "joao@email.com",
    "cpf": "123.456.789-00",
    "cidade": "São Paulo",
    "estado": "SP",
    "criado_em": "2026-01-03T00:00:00"
  }
}
```

#### Possíveis Erros

```json
// 400 Bad Request - Dados faltando
{
  "erro": "Nome, telefone e senha são obrigatórios"
}

// 400 Bad Request - Telefone já existe
{
  "erro": "Telefone já cadastrado"
}

// 400 Bad Request - Email já existe
{
  "erro": "Email já cadastrado"
}
```

---

### 2. Login

**Endpoint:** `POST /api/auth/login`  
**Autenticação:** Não requerida  
**Descrição:** Autentica um usuário e retorna token JWT

#### Request Body

```json
{
  "telefone": "11999999999",
  "senha": "senha123"
}
```

**Campos obrigatórios:**
- `telefone` (string) - Pode ser com ou sem código do país (+55)
- `senha` (string)

> 💡 **Flexibilidade de Telefone:** O sistema aceita login com número local (ex: `83994099696`) ou com código do país (ex: `5583994099696`). Se não encontrar o número exato, tentará adicionar o prefixo 55 automaticamente.

#### Response (200 OK)

```json
{
  "mensagem": "Login realizado com sucesso",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "usuario": {
    "id": 1,
    "nome": "João Silva",
    "telefone": "11999999999",
    "email": "joao@email.com",
    "cpf": "123.456.789-00",
    "cidade": "São Paulo",
    "estado": "SP",
    "is_admin": false,
    "criado_em": "2026-01-03T00:00:00"
  }
}
```

#### Possíveis Erros

```json
// 400 Bad Request
{
  "erro": "Telefone e senha são obrigatórios"
}

// 401 Unauthorized
{
  "erro": "Telefone ou senha inválidos"
}

// 403 Forbidden
{
  "erro": "Usuário inativo"
}
```

---

### 3. Logout

**Endpoint:** `POST /api/auth/logout`  
**Autenticação:** ✅ Requerida  
**Descrição:** Realiza logout do usuário (principalmente client-side)

#### Request Headers

```
Authorization: Bearer {token}
```

#### Response (200 OK)

```json
{
  "mensagem": "Logout realizado com sucesso"
}
```

> 📝 **Nota:** Como JWT é stateless, o logout é principalmente gerenciado no client-side removendo o token. Este endpoint confirma a ação.

---

### 4. Recuperar Senha

**Endpoint:** `POST /api/auth/recuperar-senha`  
**Autenticação:** Não requerida  
**Descrição:** Inicia processo de recuperação de senha

#### Request Body

```json
{
  "telefone": "11999999999"
}
```

#### Response (200 OK)

```json
{
  "mensagem": "Se o telefone estiver cadastrado, você receberá um SMS com instruções"
}
```

> ⚠️ **Nota:** Por segurança, sempre retorna sucesso mesmo se o telefone não existir

---

### 5. Obter Perfil

**Endpoint:** `GET /api/auth/perfil`  
**Autenticação:** ✅ Requerida  
**Descrição:** Obtém dados do perfil do usuário autenticado

#### Request Headers

```
Authorization: Bearer {token}
```

#### Response (200 OK)

```json
{
  "id": 1,
  "nome": "João Silva",
  "telefone": "11999999999",
  "email": "joao@email.com",
  "cpf": "123.456.789-00",
  "cidade": "São Paulo",
  "estado": "SP",
  "criado_em": "2026-01-03T00:00:00"
}
```

#### Possíveis Erros

```json
// 404 Not Found
{
  "erro": "Usuário não encontrado"
}

// 401 Unauthorized (token inválido)
{
  "msg": "Missing Authorization Header"
}
```

---

### 6. Atualizar Perfil

**Endpoint:** `PUT /api/auth/perfil`  
**Autenticação:** ✅ Requerida  
**Descrição:** Atualiza dados do perfil do usuário

#### Request Headers

```
Authorization: Bearer {token}
Content-Type: application/json
```

#### Request Body

```json
{
  "nome": "João Silva Santos",
  "email": "joao.novo@email.com",
  "endereco": "Rua das Flores, 123",
  "cidade": "Rio de Janeiro",
  "estado": "RJ",
  "cep": "20000-000"
}
```

**Todos os campos são opcionais** - Envie apenas os que deseja atualizar

#### Response (200 OK)

```json
{
  "mensagem": "Perfil atualizado com sucesso",
  "usuario": {
    "id": 1,
    "nome": "João Silva Santos",
    "telefone": "11999999999",
    "email": "joao.novo@email.com",
    "cpf": "123.456.789-00",
    "cidade": "Rio de Janeiro",
    "estado": "RJ",
    "criado_em": "2026-01-03T00:00:00"
  }
}
```

---

## 🎯 Campanhas

### 7. Listar Campanhas

**Endpoint:** `GET /api/campanhas`  
**Autenticação:** Não requerida  
**Descrição:** Lista campanhas com paginação e filtros

#### Query Parameters

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `status` | string | `ativo` | Status da campanha: `ativo`, `concluido`, `cancelado` |
| `page` | integer | `1` | Número da página |
| `per_page` | integer | `20` | Itens por página (máx: 100) |

#### Exemplo de Request

```
GET /api/campanhas?status=ativo&page=1&per_page=10
```

#### Response (200 OK)

```json
{
  "campanhas": [
    {
      "id": 1,
      "titulo": "iPhone 15 Pro Max",
      "descricao": "Concorra a um iPhone 15 Pro Max novo",
      "slug": "iphone-15-pro-max",
      "imagem_principal": "https://exemplo.com/iphone.jpg",
      "codigo": "CAMP001",
      "tipo": "regular",
      "premio": "iPhone 15 Pro Max 256GB",
      "valor_titulo": 10.00,
      "total_titulos": 10000,
      "titulos_vendidos": 5432,
      "data_sorteio": "2026-02-01T20:00:00",
      "status": "ativo",
      "criado_em": "2026-01-01T00:00:00",
      "percentual_vendido": 54.32,
      "titulos_disponiveis": 4568,
      "ganhador": null
    }
  ],
  "total": 15,
  "paginas": 2,
  "pagina_atual": 1
}
```

---

### 8. Detalhes da Campanha

**Endpoint:** `GET /api/campanhas/{slug}`  
**Autenticação:** Não requerida  
**Descrição:** Obtém detalhes completos de uma campanha específica

#### Exemplo de Request

```
GET /api/campanhas/iphone-15-pro-max
```

#### Response (200 OK)

```json
{
  "id": 1,
  "titulo": "iPhone 15 Pro Max",
  "descricao": "Concorra a um iPhone 15 Pro Max novo...",
  "slug": "iphone-15-pro-max",
  "imagem_principal": "https://exemplo.com/iphone.jpg",
  "codigo": "CAMP001",
  "tipo": "regular",
  "premio": "iPhone 15 Pro Max 256GB",
  "valor_titulo": 10.00,
  "total_titulos": 10000,
  "titulos_vendidos": 5432,
  "data_sorteio": "2026-02-01T20:00:00",
  "status": "ativo",
  "criado_em": "2026-01-01T00:00:00",
  "percentual_vendido": 54.32,
  "titulos_disponiveis": 4568,
  "ganhador": null
}
```

#### Possíveis Erros

```json
// 404 Not Found
{
  "erro": "Campanha não encontrada"
}
```

---

### 9. Criar Campanha

**Endpoint:** `POST /api/campanhas`  
**Autenticação:** ✅ Requerida (Admin)  
**Descrição:** Cria uma nova campanha (apenas administradores)

#### Request Headers

```
Authorization: Bearer {token}
Content-Type: application/json
```

#### Request Body

```json
{
  "titulo": "iPhone 15 Pro Max",
  "descricao": "Concorra a um iPhone 15 Pro Max novo",
  "slug": "iphone-15-pro-max",
  "imagem_principal": "https://exemplo.com/iphone.jpg",
  "codigo": "CAMP001",
  "tipo": "regular",
  "premio": "iPhone 15 Pro Max 256GB",
  "valor_titulo": 10.00,
  "total_titulos": 10000,
  "data_sorteio": "2026-02-01T20:00:00",
  "regulamento": "1. Compre seus títulos..."
}
```

**Campos obrigatórios:**
- `titulo` (string)

**Campos opcionais (gerados automaticamente se não fornecidos):**
- `slug` (string) - Gerado automaticamente do título se não fornecido (ex: "iPhone 15" → "iphone-15")
- `data_sorteio` (datetime ISO 8601) - Opcional, pode ser definido posteriormente
- `data_fim` (datetime ISO 8601) - Data de encerramento da campanha

> 💡 **Auto-Slug:** Se o slug não for enviado, o sistema cria automaticamente baseado no título. Se já existir, adiciona um sufixo numérico.

#### Response (201 Created)

```json
{
  "mensagem": "Campanha criada com sucesso",
  "campanha": {
    "id": 1,
    "titulo": "iPhone 15 Pro Max",
    "slug": "iphone-15-pro-max",
    // ... demais campos
  }
}
```

#### Possíveis Erros

```json
// 403 Forbidden
{
  "erro": "Acesso negado"
}
```

---

### 10. Atualizar Campanha

**Endpoint:** `PUT /api/campanhas/{campanha_id}`  
**Autenticação:** ✅ Requerida (Admin)  
**Descrição:** Atualiza uma campanha existente (apenas administradores)

#### Request Headers

```
Authorization: Bearer {token}
Content-Type: application/json
```

#### Request Body

```json
{
  "titulo": "iPhone 15 Pro Max ATUALIZADO",
  "status": "concluido",
  "data_fim": "2026-02-20T20:00:00"
}
```

**Todos os campos são opcionais** - Envie apenas os que deseja atualizar:
- `titulo`, `descricao`, `slug`, `imagem_principal`, `codigo`
- `tipo`, `premio`, `valor_titulo`, `total_titulos`
- `regulamento`, `status`, `data_sorteio`, `data_fim`

#### Response (200 OK)

```json
{
  "mensagem": "Campanha atualizada com sucesso",
  "campanha": {
    "id": 1,
    "titulo": "iPhone 15 Pro Max ATUALIZADO",
    // ... demais campos
  }
}
```

#### Possíveis Erros

```json
// 403 Forbidden
{
  "erro": "Acesso negado"
}

// 404 Not Found
{
  "erro": "Campanha não encontrada"
}
```

---

### 11. Deletar Campanha

**Endpoint:** `DELETE /api/campanhas/{campanha_id}`  
**Autenticação:** ✅ Requerida (Admin)  
**Descrição:** Deleta uma campanha (apenas administradores, somente se não houver compras)

#### Request Headers

```
Authorization: Bearer {token}
```

#### Response (200 OK)

```json
{
  "mensagem": "Campanha deletada com sucesso"
}
```

#### Possíveis Erros

```json
// 400 Bad Request - Tem compras associadas
{
  "erro": "Não é possível deletar campanha com compras associadas",
  "sugestao": "Considere alterar o status para 'cancelado' ao invés de deletar"
}

// 403 Forbidden
{
  "erro": "Acesso negado"
}

// 404 Not Found
{
  "erro": "Campanha não encontrada"
}
```

---

## 🛒 Compras e Títulos

### 12. Criar Compra

**Endpoint:** `POST /api/compras`  
**Autenticação:** ✅ Requerida  
**Descrição:** Cria uma nova compra de títulos

#### Request Headers

```
Authorization: Bearer {token}
Content-Type: application/json
```

#### Request Body

```json
{
  "campanha_id": 1,
  "quantidade_titulos": 10,
  "metodo_pagamento": "pix"
}
```

**Campos obrigatórios:**
- `campanha_id` (integer)
- `quantidade_titulos` (integer)

**Campos opcionais:**
- `metodo_pagamento` (string) - Padrão: `pix`. Valores: `pix`, `cartao`, `boleto`

#### Response (201 Created)

```json
{
  "mensagem": "Compra realizada com sucesso",
  "compra": {
    "id": 1,
    "campanha": {
      "id": 1,
      "titulo": "iPhone 15 Pro Max",
      "slug": "iphone-15-pro-max",
      // ... demais campos da campanha
    },
    "quantidade_titulos": 10,
    "valor_total": 100.00,
    "status_pagamento": "pendente",
    "metodo_pagamento": "pix",
    "data_pagamento": null,
    "criado_em": "2026-01-03T00:00:00",
    "titulos": [
      {
        "id": 1,
        "numero": "123456",
        "is_ganhador": false
      },
      {
        "id": 2,
        "numero": "789012",
        "is_ganhador": false
      }
      // ... mais 8 títulos
    ]
  }
}
```

#### Possíveis Erros

```json
// 404 Not Found
{
  "erro": "Campanha não encontrada"
}

// 400 Bad Request
{
  "erro": "Campanha não está ativa"
}

// 400 Bad Request
{
  "erro": "Quantidade de títulos indisponível"
}
```

---

### 13. Meus Títulos

**Endpoint:** `GET /api/meus-titulos`  
**Autenticação:** ✅ Requerida  
**Descrição:** Lista todos os títulos comprados pelo usuário autenticado

#### Query Parameters

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `page` | integer | `1` | Número da página |
| `per_page` | integer | `20` | Itens por página |

#### Request Headers

```
Authorization: Bearer {token}
```

#### Exemplo de Request

```
GET /api/meus-titulos?page=1&per_page=10
```

#### Response (200 OK)

```json
{
  "compras": [
    {
      "id": 1,
      "campanha": {
        "id": 1,
        "titulo": "iPhone 15 Pro Max",
        "slug": "iphone-15-pro-max",
        "imagem_principal": "https://exemplo.com/iphone.jpg",
        "valor_titulo": 10.00,
        "data_sorteio": "2026-02-01T20:00:00",
        "status": "ativo"
      },
      "quantidade_titulos": 10,
      "valor_total": 100.00,
      "status_pagamento": "aprovado",
      "metodo_pagamento": "pix",
      "data_pagamento": "2026-01-03T00:15:00",
      "criado_em": "2026-01-03T00:00:00",
      "titulos": [
        {
          "id": 1,
          "numero": "123456",
          "is_ganhador": false
        },
        {
          "id": 2,
          "numero": "789012",
          "is_ganhador": false
        }
        // ... demais títulos
      ]
    }
  ],
  "total": 3,
  "paginas": 1,
  "pagina_atual": 1
}
```

> 📝 **Nota:** Apenas retorna compras com `status_pagamento: "aprovado"`

---

### 14. Deletar Compra

**Endpoint:** `DELETE /api/compras/{compra_id}`  
**Autenticação:** ✅ Requerida (Admin)  
**Descrição:** Deleta uma compra e seus títulos associados (apenas admin)

#### Request Headers

```
Authorization: Bearer {token}
```

#### Response (200 OK)

```json
{
  "mensagem": "Compra deletada com sucesso"
}
```

#### Possíveis Erros

```json
// 400 Bad Request - Campanha já concluída
{
  "erro": "Não é possível deletar compra de campanha já concluída"
}

// 403 Forbidden
{
  "erro": "Acesso negado"
}

// 404 Not Found
{
  "erro": "Compra não encontrada"
}
```

---

## 🏆 Ganhadores

### 15. Listar Ganhadores

**Endpoint:** `GET /api/ganhadores`  
**Autenticação:** Não requerida  
**Descrição:** Lista os ganhadores de campanhas concluídas

#### Query Parameters

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `page` | integer | `1` | Número da página |
| `per_page` | integer | `20` | Itens por página |

#### Exemplo de Request

```
GET /api/ganhadores?page=1&per_page=10
```

#### Response (200 OK)

```json
{
  "ganhadores": [
    {
      "id": 5,
      "titulo": "iPhone 15 Pro Max",
      "slug": "iphone-15-pro-max-jan",
      "premio": "iPhone 15 Pro Max 256GB",
      "data_sorteio": "2026-01-15T20:00:00",
      "status": "concluido",
      "numero_sorteado": "123456",
      "ganhador": {
        "nome": "João Silva",
        "cidade": "São Paulo",
        "estado": "SP"
      }
    }
  ],
  "total": 25,
  "paginas": 3
}
```

---

## 👨‍💼 Admin

### 16. Listar Usuários (Admin)

**Endpoint:** `GET /api/admin/usuarios`  
**Autenticação:** ✅ Requerida (Admin)  
**Descrição:** Lista todos os usuários cadastrados (apenas administradores)

#### Query Parameters

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|----------- |
| `page` | integer | `1` | Número da página |
| `per_page` | integer | `20` | Itens por página |

#### Request Headers

```
Authorization: Bearer {token}
```

#### Response (200 OK)

```json
{
  "usuarios": [
    {
      "id": 1,
      "nome": "João Silva",
      "email": "joao@email.com",
      "telefone": "11999999999",
      "is_admin": false,
      "criado_em": "2026-01-01T00:00:00"
    },
    {
      "id": 2,
      "nome": "Admin User",
      "email": "admin@gemeos.com",
      "telefone": "5583994099696",
      "is_admin": true,
      "criado_em": "2025-12-01T00:00:00"
    }
  ],
  "total": 150,
  "paginas": 8,
  "pagina_atual": 1
}
```

#### Possíveis Erros

```json
// 403 Forbidden
{
  "erro": "Acesso negado. Apenas administradores."
}
```

---

### 17. Dashboard Administrativo

**Endpoint:** `GET /api/admin/dashboard`  
**Autenticação:** ✅ Requerida (Admin)  
**Descrição:** Retorna estatísticas gerais do sistema (apenas administradores)

#### Request Headers

```
Authorization: Bearer {token}
```

#### Response (200 OK)

```json
{
  "stats": {
    "total_usuarios": 150,
    "total_campanhas": 25,
    "campanhas_ativas": 8,
    "receita_total": 45890.50
  },
  "ultimas_vendas": [
    {
      "id": 127,
      "campanha": "iPhone 15 Pro Max",
      "usuario": "João Silva",
      "valor": 100.00,
      "data": "2026-01-11T14:30:00"
    },
    {
      "id": 126,
      "campanha": "Notebook Gamer",
      "usuario": "Maria Santos",
      "valor": 50.00,
      "data": "2026-01-11T13:15:00"
    }
  ]
}
```

#### Possíveis Erros

```json
// 403 Forbidden
{
  "erro": "Acesso negado. Apenas administradores."
}
```

---

## 📰 Artigos

### 18. Listar Artigos

**Endpoint:** `GET /api/artigos`  
**Autenticação:** Não requerida  
**Descrição:** Lista artigos publicados

#### Query Parameters

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `page` | integer | `1` | Número da página |
| `per_page` | integer | `10` | Itens por página |

#### Response (200 OK)

```json
{
  "artigos": [
    {
      "id": 1,
      "titulo": "Como funcionam os sorteios?",
      "slug": "como-funcionam-os-sorteios",
      "conteudo": "Os sorteios são realizados...",
      "imagem": "https://exemplo.com/artigo1.jpg",
      "autor": "Equipe Gêmeos Brasil",
      "criado_em": "2026-01-01T00:00:00"
    }
  ],
  "total": 15,
  "paginas": 2
}
```

---

### 19. Detalhes do Artigo

**Endpoint:** `GET /api/artigos/{slug}`  
**Autenticação:** Não requerida  
**Descrição:** Obtém detalhes completos de um artigo

#### Response (200 OK)

```json
{
  "id": 1,
  "titulo": "Como funcionam os sorteios?",
  "slug": "como-funcionam-os-sorteios",
  "conteudo": "Os sorteios são realizados de forma totalmente transparente...",
  "imagem": "https://exemplo.com/artigo1.jpg",
  "autor": "Equipe Gêmeos Brasil",
  "criado_em": "2026-01-01T00:00:00"
}
```

#### Possíveis Erros

```json
// 404 Not Found
{
  "erro": "Artigo não encontrado"
}
```

---

## 📢 Comunicados

### 20. Listar Comunicados

**Endpoint:** `GET /api/comunicados`  
**Autenticação:** Não requerida  
**Descrição:** Lista comunicados ativos (últimos 10)

#### Response (200 OK)

```json
{
  "comunicados": [
    {
      "id": 1,
      "titulo": "Manutenção programada",
      "conteudo": "Sistema ficará fora do ar...",
      "tipo": "alerta",
      "criado_em": "2026-01-03T00:00:00"
    }
  ]
}
```

**Tipos de comunicado:**
- `informativo` - Informação geral
- `alerta` - Atenção necessária
- `aviso` - Avisos importantes

---

## 📧 Contato

### 21. Enviar Contato

**Endpoint:** `POST /api/contato`  
**Autenticação:** Não requerida  
**Descrição:** Envia uma mensagem de contato

#### Request Body

```json
{
  "nome": "Maria Santos",
  "email": "maria@email.com",
  "telefone": "11988888888",
  "assunto": "Dúvida sobre sorteio",
  "mensagem": "Gostaria de saber quando será o próximo sorteio..."
}
```

**Campos obrigatórios:**
- `nome` (string)
- `email` (string)
- `mensagem` (string)

**Campos opcionais:**
- `telefone` (string)
- `assunto` (string)

#### Response (201 Created)

```json
{
  "mensagem": "Mensagem enviada com sucesso"
}
```

#### Possíveis Erros

```json
// 400 Bad Request
{
  "erro": "Nome, email e mensagem são obrigatórios"
}
```

---

## 📌 Códigos de Status

| Código | Descrição |
|--------|-----------|
| 200 | OK - Requisição bem-sucedida |
| 201 | Created - Recurso criado com sucesso |
| 400 | Bad Request - Dados inválidos ou faltando |
| 401 | Unauthorized - Token inválido ou ausente |
| 403 | Forbidden - Sem permissão para acessar |
| 404 | Not Found - Recurso não encontrado |
| 500 | Internal Server Error - Erro no servidor |

---

## 🔧 Tipos de Dados

### DateTime Format

Todas as datas seguem o formato ISO 8601:

```
2026-01-03T00:00:00
```

### Status de Pagamento

- `pendente` - Aguardando pagamento
- `aprovado` - Pagamento confirmado
- `cancelado` - Pagamento cancelado

### Status de Campanha

- `ativo` - Campanha em andamento
- `concluido` - Campanha finalizada
- `cancelado` - Campanha cancelada

### Métodos de Pagamento

- `pix` - Pagamento via PIX
- `cartao` - Cartão de crédito
- `boleto` - Boleto bancário

---

## 🔒 Segurança e Boas Práticas

### Headers Recomendados

```http
Content-Type: application/json
Accept: application/json
Authorization: Bearer {token}
```

### Armazenamento do Token

- Armazene o token JWT de forma segura (localStorage ou sessionStorage)
- Inclua em todas as requisições autenticadas
- Token expira em 7 dias

### Tratamento de Erros

Sempre verifique o status code e trate os erros adequadamente:

```javascript
const response = await fetch('/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ telefone, senha })
});

const data = await response.json();

if (response.ok) {
  // Sucesso
  localStorage.setItem('token', data.token);
} else {
  // Erro
  alert(data.erro);
}
```

---

## 📱 Exemplo de Integração (JavaScript/React)

### Configuração do Axios

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Interceptor para adicionar token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

### Exemplos de Uso

```javascript
// Login
const login = async (telefone, senha) => {
  const response = await api.post('/auth/login', { telefone, senha });
  localStorage.setItem('token', response.data.token);
  return response.data.usuario;
};

// Listar campanhas
const getCampanhas = async (status = 'ativo', page = 1) => {
  const response = await api.get('/campanhas', {
    params: { status, page }
  });
  return response.data;
};

// Criar compra
const criarCompra = async (campanhaId, quantidade) => {
  const response = await api.post('/compras', {
    campanha_id: campanhaId,
    quantidade_titulos: quantidade,
    metodo_pagamento: 'pix'
  });
  return response.data;
};

// Meus títulos
const getMeusTitulos = async (page = 1) => {
  const response = await api.get('/meus-titulos', {
    params: { page }
  });
  return response.data;
};
```

---

## 🚀 Testando a API

### Com cURL

```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"telefone":"11999999999","senha":"senha123"}'

# Listar campanhas
curl http://localhost:5000/api/campanhas?status=ativo

# Meus títulos (com autenticação)
curl http://localhost:5000/api/meus-titulos \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### Com Postman

1. Importe a collection (pode criar baseada nesta documentação)
2. Configure variável de ambiente `baseUrl` como `http://localhost:5000`
3. Configure variável `token` após fazer login
4. Use `{{baseUrl}}` e `{{token}}` nas requisições

---

## 📞 Suporte

Para dúvidas ou problemas com a integração:

- **Email:** suporte@gemeosbrasil.com
- **Documentação completa:** [README.md](file:///c:/Projetos/Projeto-rifa/README.md)

---

**Última atualização:** 2026-01-11  
**Versão da API:** 1.1  
**Changelog:**
- ✅ Flexibilidade de login (telefone com/sem DDI)
- ✅ Endpoint de logout
- ✅ Auto-geração de slug em campanhas
- ✅ Campo `is_admin` em respostas de usuário
- ✅ Endpoints Admin: listar usuários e dashboard
- ✅ CRUD completo de campanhas (PUT, DELETE)
- ✅ DELETE de compras (apenas admin)
- ✅ `data_sorteio` opcional na criação de campanhas
