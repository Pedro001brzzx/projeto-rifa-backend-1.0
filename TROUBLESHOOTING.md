# Troubleshooting - Erros Comuns da API

## ❌ Erro 422: "Subject must be a String"

### Problema
Ao fazer login ou tentar acessar rotas autenticadas, você recebe:
```json
{
  "msg": "Subject must be a String"
}
```

### Causa
O JWT-Extended espera que o `identity` (subject) seja uma string, mas estava recebendo um inteiro.

### Solução
✅ **JÁ CORRIGIDO!** O código foi atualizado para converter o ID do usuário para string ao criar tokens.

Se ainda ocorrer, reinicie o servidor:
```bash
# Pare o servidor (Ctrl+C)
# Inicie novamente
python app.py
```

### Como Funciona Agora
- **Criar token:** `create_access_token(identity=str(usuario.id))` → string
- **Ler token:** `int(get_jwt_identity())` → converte de volta para inteiro

---

## ❌ Erro 401: Missing Authorization Header

### Problema
```json
{
  "msg": "Missing Authorization Header"
}
```

### Solução
Adicione o header `Authorization` com o token:

**No Postman:**
1. Aba **Headers**
2. Key: `Authorization`
3. Value: `Bearer SEU_TOKEN_AQUI`

⚠️ **Importante:** Deve ter um espaço entre "Bearer" e o token!

---

## ❌ Erro 403: Acesso negado

### Problema
```json
{
  "erro": "Acesso negado"
}
```

### Causa
Usuário não é administrador.

### Solução
Execute:
```bash
python make_admin.py
```

Digite o telefone do usuário que deve ser admin.

---

## ❌ Erro 400: Campos obrigatórios

### Problema
```json
{
  "erro": "KeyError: 'titulo'"
}
```

### Causa
Campos obrigatórios faltando no JSON.

### Solução
Para criar campanha, **obrigatório**:
- `titulo`
- `slug`
- `data_sorteio`

### Exemplo mínimo:
```json
{
  "titulo": "Teste",
  "slug": "teste-campanha",
  "data_sorteio": "2026-02-15T20:00:00"
}
```

---

## ❌ Token Expirado

### Problema
```json
{
  "msg": "Token has expired"
}
```

### Solução
Faça login novamente:
```
POST /api/auth/login
```

Copie o novo token.

---

## 🔄 Passo a Passo Completo (Sem Erros)

### 1. Registrar
```
POST http://localhost:5000/api/auth/registro
Body:
{
  "nome": "Admin",
  "telefone": "11999999999",
  "senha": "admin123"
}
```
→ Copie o **token**

### 2. Tornar Admin
```bash
python make_admin.py
```

### 3. Criar Campanha
```
POST http://localhost:5000/api/campanhas
Headers:
  Authorization: Bearer SEU_TOKEN
Body:
{
  "titulo": "iPhone 15",
  "slug": "iphone-15",
  "data_sorteio": "2026-02-15T20:00:00"
}
```

✅ **Sucesso!**
