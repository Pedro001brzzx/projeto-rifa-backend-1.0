# Implementação AbacatePay - Guia Rápido

## 🚀 Passos para Integração

### 1. Instalação
```bash
pip install abacatepay
```

### 2. Configuração (.env)
```bash
ABACATEPAY_API_KEY=sua-api-key-aqui
ABACATEPAY_WEBHOOK_SECRET=seu-secret-aqui
BASE_URL=https://seu-dominio.com
```

###3. Modificar `pagamento_controller.py`

Substitua a função `_gerar_dados_pagamento`:

```python
from abacatepay import AbacatePay
import os

def _gerar_dados_pagamento(compra, metodo_pagamento):
    """Gera dados de pagamento PIX usando AbacatePay"""
    
    if metodo_pagamento != 'pix':
        raise ValueError('Sistema aceita apenas pagamento via PIX')
    
    # Inicializar AbacatePay
    client = AbacatePay(api_key=os.getenv('ABACATEPAY_API_KEY'))
    
    # Criar cobrança
    billing = client.billing.create(
        amount=float(compra['valor_total']),
        description=f"Rifas - {compra['quantidade_titulos']} títulos",
        metadata={'compra_id': str(compra['id'])},
        frequency='once',
        methods=['PIX']
    )
    
    return {
        'tipo': 'pix',
        'qr_code': billing.pix_url,
        'qr_code_base64': billing.pix_qrcode_base64,
        'copia_cola': billing.pix_emv,
        'payment_id': billing.id,
        'expira_em': billing.expires_at,
        'instrucoes': 'Pague com PIX - Processamento instantâneo'
    }
```

### 4. Atualizar `pagamento_routes.py`

Adicione validação HMAC no webhook:

```python
import hmac
import hashlib
import os
from flask import request

@pagamento_bp.route('/pagamentos/webhook', methods=['POST'])
def processar_webhook():
    data = request.get_json()
    gateway = request.args.get('gateway', 'generic')
    
    if gateway == 'abacatepay':
        # VALIDAR ASSINATURA
        signature = request.headers.get('X-Webhook-Signature')
        webhook_secret = os.getenv('ABACATEPAY_WEBHOOK_SECRET')
        
        body_bytes = request.get_data()
        expected_sig = hmac.new(
            webhook_secret.encode(),
            body_bytes,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_sig):
            return jsonify({'erro': 'Assinatura inválida'}), 401
        
        # Processar pagamento aprovado
        if data.get('kind') == 'billing.paid':
            metadata = data.get('data', {}).get('metadata', {})
            compra_id = int(metadata.get('compra_id'))
            
            response, status = pagamento_controller.processar_webhook({
                'compra_id': compra_id,
                'status': 'aprovado'
            }, 'abacatepay')
            
            return jsonify(response), status
    
    # Fallback
    response, status = pagamento_controller.processar_webhook(data, gateway)
    return jsonify(response), status
```

### 5. Configurar Webhook no Dashboard

1. Acesse: https://abacatepay.com/dashboard/webhooks
2. Criar novo webhook:
   - **URL:** `https://seu-dominio.com/api/pagamentos/webhook?gateway=abacatepay`
   - **Secret:** Gere um segredo forte (use `openssl rand -hex 32`)
   - **Eventos:** Marque `billing.paid`
3. Salve o secret no `.env`

### 6. Testar

```bash
# Criar checkout
curl -X POST http://localhost:5000/api/checkout \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "campanha_id": 1,
    "quantidade_titulos": 5,
    "metodo_pagamento": "pix"
  }'
```

## ✅ Checklist

- [ ] Instalar `pip install abacatepay`
- [ ] Configurar `.env` com API_KEY e WEBHOOK_SECRET
- [ ] Modificar `_gerar_dados_pagamento()` 
- [ ] Adicionar validação HMAC no webhook
- [ ] Configurar webhook no dashboard AbacatePay
- [ ] Testar criação de checkout
- [ ] Testar recebimento de webhook
- [ ] Validar aprovação de pagamento

## 💰 Custo

**Taxa fixa:** R$ 0,80 por transação PIX

Excelente para rifas de qualquer valor!

## 📚 Documentação

- Site: https://abacatepay.com
- Docs: https://docs.abacatepay.com
- SDK Python: https://github.com/abacatepay/abacatepay-python-sdk
