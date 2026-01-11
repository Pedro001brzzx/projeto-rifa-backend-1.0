# Guia Postman - Sistema de Rifas Gêmeos Brasil

> Tutorial completo para testar a API usando Postman

## 📋 Pré-requisitos

1. Postman instalado ([Download aqui](https://www.postman.com/downloads/))
2. Servidor Flask rodando em `http://localhost:5000`
3. Verificar que o servidor está ativo: `GET http://localhost:5000/`

---

## 🚀 Passo a Passo para Criar uma Campanha

### **Passo 1: Criar um Usuário Administrador**

Primeiro, você precisa ter um usuário com permissão de admin.

**Método:** `POST`  
**URL:** `http://localhost:5000/api/auth/registro`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "nome": "Admin Teste",
  "telefone": "11999999999",
  "senha": "admin123",
  "email": "admin@teste.com"
}
```

**Configuração no Postman:**

1. Abra o Postman
2. Clique em "New" → "HTTP Request"
3. Selecione método **POST**
4. Cole a URL: `http://localhost:5000/api/auth/registro`
5. Vá na aba **Headers**
   - Key: `Content-Type`
   - Value: `application/json`
6. Vá na aba **Body**
   - Selecione **raw**
   - Selecione **JSON** no dropdown
   - Cole o JSON acima
7. Clique em **Send**

**Resposta Esperada (201 Created):**
```json
{
  "mensagem": "Usuário cadastrado com sucesso",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "usuario": {
    "id": 1,
    "nome": "Admin Teste",
    "telefone": "11999999999",
    "email": "admin@teste.com",
    "cpf": null,
    "cidade": null,
    "estado": null,
    "criado_em": "2026-01-03T01:00:00"
  }
}
```

**⚠️ IMPORTANTE:** Copie o valor do `token` retornado!

---

### **Passo 2: Tornar o Usuário Admin no Banco de Dados**

Como a API não tem endpoint para tornar usuário admin (por segurança), você precisa fazer isso diretamente no banco.

#### **Opção A: SQLite (mais fácil)**

1. Instale SQLite Browser: https://sqlitebrowser.org/dl/
2. Abra o arquivo `gemeos_brasil.db` na raiz do projeto
3. Vá na aba "Browse Data"
4. Selecione a tabela `usuarios`
5. Encontre seu usuário (id = 1)
6. Clique duas vezes no campo `is_admin`
7. Mude de `0` para `1`
8. Clique em "Write Changes" (ícone de disquete)

#### **Opção B: Comando SQL Direto**

Execute no terminal (na pasta do projeto):

```bash
# Windows PowerShell
sqlite3 gemeos_brasil.db "UPDATE usuarios SET is_admin = 1 WHERE id = 1;"

# Se não tiver sqlite3, instale:
# choco install sqlite (com Chocolatey)
```

#### **Opção C: Python Script**

Crie um arquivo `make_admin.py` na raiz do projeto:

```python
from app import create_app
from app.models import db, Usuario

app = create_app()
with app.app_context():
    usuario = Usuario.query.filter_by(telefone='11999999999').first()
    if usuario:
        usuario.is_admin = True
        db.session.commit()
        print(f'✅ {usuario.nome} agora é admin!')
    else:
        print('❌ Usuário não encontrado')
```

Execute:
```bash
python make_admin.py
```

---

### **Passo 3: Fazer Login (Opcional)**

Se você ainda tiver o token do registro, pode pular esta etapa.

**Método:** `POST`  
**URL:** `http://localhost:5000/api/auth/login`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "telefone": "11999999999",
  "senha": "admin123"
}
```

**Resposta:** Copie o `token` retornado.

---

### **Passo 4: Criar uma Campanha**

Agora você pode criar campanhas!

**Método:** `POST`  
**URL:** `http://localhost:5000/api/campanhas`

**Headers:**
```
Content-Type: application/json
Authorization: Bearer SEU_TOKEN_AQUI
```

**⚠️ IMPORTANTE:** Substitua `SEU_TOKEN_AQUI` pelo token que você copiou!

**Body (JSON) - Exemplo Completo:**
```json
{
  "titulo": "iPhone 15 Pro Max",
  "descricao": "Concorra a um iPhone 15 Pro Max 256GB novo, na caixa, com nota fiscal e garantia Apple de 1 ano!",
  "slug": "iphone-15-pro-max-janeiro-2026",
  "imagem_principal": "https://exemplo.com/iphone15.jpg",
  "codigo": "CAMP001",
  "tipo": "regular",
  "premio": "iPhone 15 Pro Max 256GB Titânio Natural",
  "valor_titulo": 10.00,
  "total_titulos": 10000,
  "data_sorteio": "2026-02-15T20:00:00",
  "regulamento": "1. Cada título vale 1 chance no sorteio.\n2. O sorteio será realizado ao vivo.\n3. O ganhador será contactado por telefone."
}
```

**Configuração no Postman:**

1. Crie nova requisição **POST**
2. URL: `http://localhost:5000/api/campanhas`
3. **Headers:**
   - `Content-Type`: `application/json`
   - `Authorization`: `Bearer eyJhbGc...` (cole seu token completo)
4. **Body:**
   - Selecione **raw**
   - Selecione **JSON**
   - Cole o JSON acima
5. Clique em **Send**

**Resposta Esperada (201 Created):**
```json
{
  "mensagem": "Campanha criada com sucesso",
  "campanha": {
    "id": 1,
    "titulo": "iPhone 15 Pro Max",
    "descricao": "Concorra a um iPhone 15 Pro Max...",
    "slug": "iphone-15-pro-max-janeiro-2026",
    "imagem_principal": "https://exemplo.com/iphone15.jpg",
    "codigo": "CAMP001",
    "tipo": "regular",
    "premio": "iPhone 15 Pro Max 256GB Titânio Natural",
    "valor_titulo": 10.0,
    "total_titulos": 10000,
    "titulos_vendidos": 0,
    "data_sorteio": "2026-02-15T20:00:00",
    "status": "ativo",
    "criado_em": "2026-01-03T01:20:00"
  }
}
```

---

## 🔧 Possíveis Erros e Soluções

### ❌ Erro 401: Unauthorized

```json
{
  "msg": "Missing Authorization Header"
}
```

**Solução:** Você esqueceu de adicionar o header `Authorization` ou o token está incorreto.

1. Vá em **Headers**
2. Adicione: `Authorization` com valor `Bearer SEU_TOKEN`
3. Certifique-se que há um espaço entre "Bearer" e o token

---

### ❌ Erro 403: Forbidden

```json
{
  "erro": "Acesso negado"
}
```

**Solução:** O usuário não é admin.

1. Verifique se você executou o Passo 2 corretamente
2. Confirme no banco que `is_admin = 1`
3. Faça login novamente se alterou no banco

---

### ❌ Erro 400: Bad Request

```json
{
  "erro": "KeyError: 'titulo'"
}
```

**Solução:** Faltam campos obrigatórios no JSON.

Campos **obrigatórios**:
- `titulo`
- `slug`
- `data_sorteio`

---

## 📚 Salvando Configuração no Postman

### Criar Collection

1. Clique em "Collections" (barra lateral)
2. Clique em "+" ou "New Collection"
3. Nomeie: "API Gêmeos Brasil"

### Adicionar Variáveis de Ambiente

1. Clique no ícone de "olho" (canto superior direito)
2. Clique em "Add" ao lado de "Environments"
3. Nome: "Local Development"
4. Adicione variáveis:

| Variable | Initial Value | Current Value |
|----------|--------------|---------------|
| `baseUrl` | `http://localhost:5000` | `http://localhost:5000` |
| `token` | | (cole seu token aqui) |

5. Clique em "Save"
6. Selecione o ambiente "Local Development" no dropdown

### Usar Variáveis nas Requisições

Agora você pode usar:

- **URL:** `{{baseUrl}}/api/campanhas`
- **Header Authorization:** `Bearer {{token}}`

---

## 🧪 Testando Outros Endpoints

### Listar Campanhas (Público)

**Método:** `GET`  
**URL:** `http://localhost:5000/api/campanhas`  
**Headers:** (nenhum necessário)

### Detalhes de uma Campanha

**Método:** `GET`  
**URL:** `http://localhost:5000/api/campanhas/iphone-15-pro-max-janeiro-2026`  
**Headers:** (nenhum necessário)

### Criar Compra (Autenticado)

**Método:** `POST`  
**URL:** `http://localhost:5000/api/compras`  
**Headers:**
```
Content-Type: application/json
Authorization: Bearer {{token}}
```

**Body:**
```json
{
  "campanha_id": 1,
  "quantidade_titulos": 5,
  "metodo_pagamento": "pix"
}
```

### Meus Títulos

**Método:** `GET`  
**URL:** `http://localhost:5000/api/meus-titulos`  
**Headers:**
```
Authorization: Bearer {{token}}
```

---

## 💾 Exemplo de Collection Completa para Importar

Salve este JSON como `gemeos_brasil_postman.json`:

```json
{
  "info": {
    "name": "API Gêmeos Brasil",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Auth",
      "item": [
        {
          "name": "Registro",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"nome\": \"Admin Teste\",\n  \"telefone\": \"11999999999\",\n  \"senha\": \"admin123\",\n  \"email\": \"admin@teste.com\"\n}"
            },
            "url": {
              "raw": "{{baseUrl}}/api/auth/registro",
              "host": ["{{baseUrl}}"],
              "path": ["api", "auth", "registro"]
            }
          }
        },
        {
          "name": "Login",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"telefone\": \"11999999999\",\n  \"senha\": \"admin123\"\n}"
            },
            "url": {
              "raw": "{{baseUrl}}/api/auth/login",
              "host": ["{{baseUrl}}"],
              "path": ["api", "auth", "login"]
            }
          }
        }
      ]
    },
    {
      "name": "Campanhas",
      "item": [
        {
          "name": "Criar Campanha",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              },
              {
                "key": "Authorization",
                "value": "Bearer {{token}}"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"titulo\": \"iPhone 15 Pro Max\",\n  \"slug\": \"iphone-15-pro-max\",\n  \"descricao\": \"Concorra a um iPhone 15 Pro Max novo!\",\n  \"valor_titulo\": 10.00,\n  \"total_titulos\": 10000,\n  \"data_sorteio\": \"2026-02-15T20:00:00\",\n  \"premio\": \"iPhone 15 Pro Max 256GB\"\n}"
            },
            "url": {
              "raw": "{{baseUrl}}/api/campanhas",
              "host": ["{{baseUrl}}"],
              "path": ["api", "campanhas"]
            }
          }
        },
        {
          "name": "Listar Campanhas",
          "request": {
            "method": "GET",
            "url": {
              "raw": "{{baseUrl}}/api/campanhas",
              "host": ["{{baseUrl}}"],
              "path": ["api", "campanhas"]
            }
          }
        }
      ]
    }
  ]
}
```

**Importar no Postman:**
1. Postman → File → Import
2. Selecione o arquivo `gemeos_brasil_postman.json`
3. Clique em "Import"

---

## 🎯 Resumo Rápido

1. ✅ Criar usuário: `POST /api/auth/registro`
2. ✅ Tornar admin no banco: `UPDATE usuarios SET is_admin = 1 WHERE id = 1`
3. ✅ Fazer login: `POST /api/auth/login` (copiar token)
4. ✅ Criar campanha: `POST /api/campanhas` com header `Authorization: Bearer TOKEN`

---

## 📞 Precisa de Ajuda?

Consulte a documentação completa: [API_DOCUMENTATION.md](file:///c:/Projetos/Projeto-rifa/API_DOCUMENTATION.md)

---

**Última atualização:** 2026-01-03  
**Versão:** 1.0
