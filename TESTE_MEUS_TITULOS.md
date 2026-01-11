# Como Testar "Meus Títulos" no Postman

> Guia passo a passo para testar a rota `/api/meus-titulos`

## 📋 Pré-requisitos

Para ter títulos, você precisa primeiro comprá-los! Este guia mostra o fluxo completo.

---

## 🎯 Fluxo Completo: Da Compra aos Títulos

### **Passo 1: Registrar e Fazer Login**

**Método:** `POST`  
**URL:** `http://localhost:5000/api/auth/registro`

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "nome": "João Comprador",
  "telefone": "11988888888",
  "senha": "senha123",
  "email": "joao@email.com"
}
```

**Resposta:**
```json
{
  "mensagem": "Usuário cadastrado com sucesso",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "usuario": { ... }
}
```

**⚠️ COPIE O TOKEN!** Você vai precisar dele.

---

### **Passo 2: Verificar Campanhas Disponíveis**

Antes de comprar, veja quais campanhas estão ativas.

**Método:** `GET`  
**URL:** `http://localhost:5000/api/campanhas?status=ativo`

**Headers:** (nenhum necessário)

**Resposta:**
```json
{
  "campanhas": [
    {
      "id": 1,
      "titulo": "iPhone 15 Pro Max",
      "slug": "iphone-15-pro-max",
      "valor_titulo": 10.0,
      "titulos_disponiveis": 9950,
      "status": "ativo"
    }
  ]
}
```

**📝 Anote o `id` da campanha** (ex: 1)

**Se não houver campanhas:**
- Você precisa criar uma primeiro (veja [POSTMAN_GUIDE.md](file:///c:/Projetos/Projeto-rifa/POSTMAN_GUIDE.md))
- Ou use o admin para criar

---

### **Passo 3: Criar uma Compra**

Agora vamos comprar alguns títulos!

**Método:** `POST`  
**URL:** `http://localhost:5000/api/compras`

**Headers:**
```
Content-Type: application/json
Authorization: Bearer SEU_TOKEN_AQUI
```

**⚠️ IMPORTANTE:** Cole o token que você copiou no Passo 1!

**Body:**
```json
{
  "campanha_id": 1,
  "quantidade_titulos": 5,
  "metodo_pagamento": "pix"
}
```

**Configuração no Postman:**

1. Crie nova requisição **POST**
2. URL: `http://localhost:5000/api/compras`
3. **Headers:**
   - Key: `Content-Type` | Value: `application/json`
   - Key: `Authorization` | Value: `Bearer eyJhbGc...` (seu token)
4. **Body:**
   - Selecione **raw**
   - Selecione **JSON**
   - Cole o JSON acima (ajuste o `campanha_id` se necessário)
5. Clique em **Send**

**Resposta Esperada (201 Created):**
```json
{
  "mensagem": "Compra realizada com sucesso",
  "compra": {
    "id": 1,
    "campanha": {
      "id": 1,
      "titulo": "iPhone 15 Pro Max",
      "slug": "iphone-15-pro-max"
    },
    "quantidade_titulos": 5,
    "valor_total": 50.0,
    "status_pagamento": "pendente",
    "metodo_pagamento": "pix",
    "criado_em": "2026-01-03T02:00:00",
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
      },
      {
        "id": 3,
        "numero": "345678",
        "is_ganhador": false
      },
      {
        "id": 4,
        "numero": "901234",
        "is_ganhador": false
      },
      {
        "id": 5,
        "numero": "567890",
        "is_ganhador": false
      }
    ]
  }
}
```

✅ **Compra criada!** Mas note que `status_pagamento` está como `"pendente"`.

---

### **Passo 4: Aprovar o Pagamento (Simular)**

⚠️ **IMPORTANTE:** A rota `/api/meus-titulos` só retorna compras com `status_pagamento = "aprovado"`!

Como não temos integração de pagamento real, você precisa aprovar manualmente no banco de dados.

#### **Opção A: Via SQLite Browser**

1. Abra `gemeos_brasil.db` com SQLite Browser
2. Vá em "Browse Data"
3. Selecione tabela `compras`
4. Encontre sua compra (id = 1)
5. Dê duplo clique em `status_pagamento`
6. Mude de `pendente` para `aprovado`
7. Clique em "Write Changes"

#### **Opção B: Via Script Python**

Crie arquivo `aprovar_compra.py`:

```python
from app import create_app
from app.models import db, Compra

app = create_app()
with app.app_context():
    # Aprovar todas as compras pendentes
    compras = Compra.query.filter_by(status_pagamento='pendente').all()
    for compra in compras:
        compra.status_pagamento = 'aprovado'
        print(f'✅ Compra #{compra.id} aprovada - {compra.quantidade_titulos} títulos')
    
    db.session.commit()
    print(f'\n✅ Total: {len(compras)} compras aprovadas!')
```

Execute:
```bash
python aprovar_compra.py
```

#### **Opção C: SQL Direto**

```bash
sqlite3 gemeos_brasil.db "UPDATE compras SET status_pagamento = 'aprovado' WHERE status_pagamento = 'pendente';"
```

---

### **Passo 5: Testar Meus Títulos** ⭐

Finalmente! Agora você pode ver seus títulos.

**Método:** `GET`  
**URL:** `http://localhost:5000/api/meus-titulos`

**Headers:**
```
Authorization: Bearer SEU_TOKEN_AQUI
```

**Query Parameters (Opcionais):**
- `page` - Número da página (padrão: 1)
- `per_page` - Itens por página (padrão: 20)

**Configuração no Postman:**

1. Crie nova requisição **GET**
2. URL: `http://localhost:5000/api/meus-titulos`
3. **Headers:**
   - Key: `Authorization` 
   - Value: `Bearer eyJhbGc...` (seu token)
4. **(Opcional) Params:**
   - Key: `page` | Value: `1`
   - Key: `per_page` | Value: `10`
5. Clique em **Send**

**Resposta Esperada (200 OK):**
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
        "valor_titulo": 10.0,
        "data_sorteio": "2026-02-15T20:00:00",
        "status": "ativo"
      },
      "quantidade_titulos": 5,
      "valor_total": 50.0,
      "status_pagamento": "aprovado",
      "metodo_pagamento": "pix",
      "data_pagamento": null,
      "criado_em": "2026-01-03T02:00:00",
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
        },
        {
          "id": 3,
          "numero": "345678",
          "is_ganhador": false
        },
        {
          "id": 4,
          "numero": "901234",
          "is_ganhador": false
        },
        {
          "id": 5,
          "numero": "567890",
          "is_ganhador": false
        }
      ]
    }
  ],
  "total": 1,
  "paginas": 1,
  "pagina_atual": 1
}
```

🎉 **Sucesso!** Você conseguiu ver seus títulos!

---

## 🧪 Testando Paginação

Se você tiver muitas compras, teste a paginação:

**Exemplo 1: Primeira página, 5 itens**
```
GET http://localhost:5000/api/meus-titulos?page=1&per_page=5
```

**Exemplo 2: Segunda página**
```
GET http://localhost:5000/api/meus-titulos?page=2&per_page=5
```

---

## ❌ Possíveis Erros

### Erro: Lista vazia

```json
{
  "compras": [],
  "total": 0,
  "paginas": 0,
  "pagina_atual": 1
}
```

**Causas possíveis:**

1. **Você não fez nenhuma compra** → Volte ao Passo 3
2. **Suas compras não estão aprovadas** → Volte ao Passo 4
3. **Token de outro usuário** → Verifique se está usando o token correto

### Erro 401: Missing Authorization Header

```json
{
  "msg": "Missing Authorization Header"
}
```

**Solução:** Adicione o header `Authorization: Bearer TOKEN`

### Erro 422: Token expired

```json
{
  "msg": "Token has expired"
}
```

**Solução:** Faça login novamente para obter novo token (tokens expiram em 7 dias)

---

## 💡 Dica: Criar Múltiplas Compras para Teste

Para testar melhor a paginação, crie várias compras:

```bash
# Cole no Postman (Body) e envie 3 vezes:
{
  "campanha_id": 1,
  "quantidade_titulos": 3,
  "metodo_pagamento": "pix"
}
```

Depois aprove todas e teste a rota!

---

## 📊 Resumo do Fluxo

```
1. Registrar usuário → Obter TOKEN
                           ↓
2. Verificar campanhas → Anotar ID da campanha
                           ↓
3. Criar compra → Com TOKEN + campanha_id
                           ↓
4. Aprovar pagamento → No banco de dados
                           ↓
5. Ver meus títulos → GET /api/meus-titulos com TOKEN
```

---

## 🎯 Collection do Postman

Adicione à sua collection:

```json
{
  "name": "Meus Títulos",
  "request": {
    "method": "GET",
    "header": [
      {
        "key": "Authorization",
        "value": "Bearer {{token}}"
      }
    ],
    "url": {
      "raw": "{{baseUrl}}/api/meus-titulos?page=1&per_page=20",
      "host": ["{{baseUrl}}"],
      "path": ["api", "meus-titulos"],
      "query": [
        {
          "key": "page",
          "value": "1"
        },
        {
          "key": "per_page",
          "value": "20"
        }
      ]
    }
  }
}
```

---

## 🔗 Links Úteis

- [Guia Completo do Postman](file:///c:/Projetos/Projeto-rifa/POSTMAN_GUIDE.md)
- [Documentação da API](file:///c:/Projetos/Projeto-rifa/API_DOCUMENTATION.md)
- [Troubleshooting](file:///c:/Projetos/Projeto-rifa/TROUBLESHOOTING.md)

---

**Última atualização:** 2026-01-03  
**Versão:** 1.0
