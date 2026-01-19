# 🥑 AbacatePay - Status da Integração

## ✅ O que está implementado

- [x] SDK instalado (`pip install abacatepay`)
- [x] Controller com integração completa
- [x] Webhook com validação HMAC
- [x] Fallback automático para MOCK em desenvolvimento
- [x] Validação de erros e tratamento de exceções

## 📋 Modo Atual: MOCK

O sistema está configurado para usar **dados MOCK** (falsos) para desenvolvimento.

### Por que usar MOCK?

1. **Desenvolvimento local** - Não precisa de URL pública
2. **Testes rápidos** - Sem depender de API externa
3. **Sem custos** - R$ 0,80 por teste seria caro
4. **Aprovação manual** - Use endpoint admin para simular aprovação

### Como testar pagamentos em MOCK

```bash
# 1. Criar checkout (recebe QR Code fake)
POST /api/checkout

# 2. Aprovar manualmente (como admin)
POST /api/pagamentos/{compra_id}/aprovar
```

## 🚀 Para Produção - Passo a Passo

### 1. Pré-requisitos

- ✅ Servidor deployado com domínio público (HTTPS)
- ✅ Conta AbacatePay criada
- ✅ API Key obtida

### 2. Configurar .env em Produção

```bash
# AbacatePay - Produção
ABACATEPAY_API_KEY=abc_prod_SUA_CHAVE_REAL
ABACATEPAY_WEBHOOK_SECRET=seu-secret-forte-aqui
BASE_URL=https://seu-dominio.com
```

### 3. Configurar Webhook no Dashboard AbacatePay

**URL do Webhook:**
```
https://seu-dominio.com/api/pagamentos/webhook?gateway=abacatepay
```

**Gerar Secret:**
```bash
openssl rand -hex 32
```

**Eventos:** Marque apenas `billing.paid`

### 4. Testar em Produção

```bash
# Criar checkout - vai chamar AbacatePay real!
curl -X POST https://seu-dominio.com/api/checkout \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "campanha_id": 1,
    "quantidade_titulos": 1,
    "metodo_pagamento": "pix"
  }'
```

## 🐛 Troubleshooting

### Erro: "AbacatePay não configurado"

- Verifique se `ABACATEPAY_API_KEY` existe no `.env`
- API Key não pode começar com `sua-api`
- Reinicie o servidor após configurar

### Erro: "API Error"

- Verifique se API Key está correta
- Teste com valor mínimo (R$ 1,00)
- Check logs do servidor para erro completo
- Valide formato dos dados enviados

### Webhook não chega

- URL deve ser HTTPS e pública
- Verifique logs no dashboard AbacatePay
- Confirme que `gateway=abacatepay` está na URL
- Secret deve ser exatamente igual ao configurado

## 💰 Custos

**AbacatePay:** R$ 0,80 por transação PIX

## 📚 Documentação Oficial

- Site: https://abacatepay.com
- Docs: https://docs.abacatepay.com
- SDK Python: https://github.com/abacatepay/abacatepay-python-sdk
- Suporte: contato@abacatepay.com

## ✨ Próximos Passos

**Agora (em MOCK):**
1. Testar fluxo completo de compra
2. Validar geração de títulos
3. Testar aprovação manual
4. Desenvolver frontend

**Depois (em Produção):**
1. Deploy da aplicação
2. Configurar credenciais AbacatePay
3. Criar webhook
4. Testar com PIX real
5. Monitorar primeiros pagamentos
