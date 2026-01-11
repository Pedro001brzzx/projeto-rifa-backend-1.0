# Teste de Geração de Números de Títulos

## ✅ Formato Atualizado

Os números de títulos agora seguem o padrão:
- **6 caracteres**
- **Sempre começam com 0**
- **Formato: 0XXXXX**

## 📋 Exemplos de Números Válidos

```
000001
000234
012345
054398
087654
099999
```

## 🔧 Como Funciona

### Geração
1. Sistema gera número aleatório entre **0 e 99999**
2. Formata com **6 dígitos** usando `f"{numero:06d}"`
3. Resultado: sempre 6 caracteres começando com 0

### Exemplos de Formatação

```python
0       → 000000
1       → 000001
1234    → 001234
54398   → 054398
99999   → 099999
```

## 🧪 Testando

### 1. Criar uma compra

```
POST http://localhost:5000/api/compras
Headers:
  Authorization: Bearer TOKEN
Body:
{
  "campanha_id": 1,
  "quantidade_titulos": 5,
  "metodo_pagamento": "pix"
}
```

### 2. Ver os números gerados

```json
{
  "titulos": [
    {
      "id": 1,
      "numero": "012345",
      "is_ganhador": false
    },
    {
      "id": 2,
      "numero": "054398",
      "is_ganhador": false
    },
    {
      "id": 3,
      "numero": "087654",
      "is_ganhador": false
    }
  ]
}
```

## ✅ Características

- ✅ Sempre 6 caracteres
- ✅ Sempre começa com 0
- ✅ Números únicos por campanha
- ✅ Geração aleatória

## 📊 Capacidade

- **Máximo de títulos únicos por campanha:** 100.000
- **Range:** 000000 a 099999

---

**Atualização:** 2026-01-03
