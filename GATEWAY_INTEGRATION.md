# Guia de Integração com Gateways de Pagamento

**Versão:** 1.0  
**Última Atualização:** 2026-01-19

---

## 📋 Índice

- [Introdução](#introdução)
- [AbacatePay](#abacatepay) ⭐ **Recomendado**
- [Mercado Pago](#mercado-pago)
- [Asaas](#asaas)
- [PagSeguro](#pagseguro)
- [Testando Localmente](#testando-localmente)

---

## 🎯 Introdução

O sistema de rifas suporta integração com diferentes gateways de pagamento **exclusivamente via PIX**. Atualmente, os dados de pagamento retornados são **mockups** para desenvolvimento. Para produção, você deve integrar com um gateway real.

> ⚠️ **Apenas PIX:** O sistema aceita somente pagamentos via PIX. Outros métodos (cartão, boleto) não são suportados.

### Fluxo de Pagamento PIX

```
1. Cliente seleciona rifas → POST /api/checkout
2. Sistema cria compra (status: pendente) e gera títulos
3. Sistema chama gateway para criar pagamento PIX
4. Gateway retorna QR Code PIX e código copia-e-cola
5. Cliente realiza pagamento PIX
6. Gateway notifica sistema → POST /api/pagamentos/webhook
7. Sistema atualiza status para "aprovado"
8. Títulos aparecem em /api/meus-titulos
```

---

## 🥑 AbacatePay

> ⭐ **Recomendado para Rifas:** Taxa fixa de R$ 0,80 por transação, API simples, ideal para alto volume.

### Vantagens
- ✅ **Taxa fixa**: Apenas R$ 0,80 por transação PIX (excelente para rifas de baixo valor)
- ✅ **Especializado em PIX**: Foco total em pagamentos instantâneos
- ✅ **API moderna**: Python SDK oficial, bem documentado
- ✅ **Webhook robusto**: HMAC-SHA256 signature validation
- ✅ **Brasileiro**: Suporte em português, documentação clara

### Instalação

```bash
pip install abacatepay
```

### Configuração

1. **Criar conta em:** https://abacatepay.com

2. **Obter API Key:**
   - Acesse Dashboard → Configurações → API
   - Copie a API Key (começa com `xxxx-xxxx-xxxx`)

3. **Configurar Webhook:**
   - Dashboard → Webhooks → Novo Webhook
   - URL: `https://seu-dominio.com/api/pagamentos/webhook?gateway=abacatepay`
   - Secret: Gere um secret único
   - Eventos: Marque `billing.paid`

4. **Adicionar ao `.env`:**
   ```
   ABACATEPAY_API_KEY=sua-api-key-aqui
   ABACATEPAY_WEBHOOK_SECRET=seu-webhook-secret-aqui
   BASE_URL=https://seu-dominio.com
   ```

### Implementação

**1. Modificar `pagamento_controller.py`:**

```python
import os
from abacatepay import AbacatePay

def _gerar_dados_pagamento(compra, metodo_pagamento):
    """Gera dados de pagamento PIX usando AbacatePay"""
    
    # Sistema aceita apenas PIX
    if metodo_pagamento != 'pix':
        raise ValueError('Sistema aceita apenas pagamento via PIX')
    
    # Inicializar client
    client = AbacatePay(api_key=os.getenv('ABACATEPAY_API_KEY'))
    
    # Criar cobrança PIX
    billing = client.billing.create(
        amount=float(compra['valor_total']),
        description=f"Compra de {compra['quantidade_titulos']} títulos - Campanha {compra['campanha']['titulo']}",
        customer_id=compra.get('usuario_id'),  # Opcional
        metadata={
            'compra_id': str(compra['id']),
            'campanha_id': str(compra['campanha']['id']),
            'quantidade_titulos': compra['quantidade_titulos']
        },
        frequency='once',  # Cobrança única
        methods=['PIX']
    )
    
    return {
        'tipo': 'pix',
        'qr_code': billing.pix_url,  # QR Code completo
        'qr_code_base64': billing.pix_qrcode_base64,  # Imagem base64
        'copia_cola': billing.pix_emv,  # Código copia e cola
        'payment_id': billing.id,
        'expira_em': billing.expires_at,
        'instrucoes': 'Escaneie o QR Code ou use o código Pix Copia e Cola para realizar o pagamento'
    }
```

**2. Processar Webhook em `pagamento_routes.py`:**

```python
import hmac
import hashlib
from flask import request

@pagamento_bp.route('/pagamentos/webhook', methods=['POST'])
def processar_webhook():
    """
    Endpoint para receber webhooks do AbacatePay
    
    IMPORTANTE: Validação de assinatura HMAC para segurança
    """
    data = request.get_json()
    gateway = request.args.get('gateway', 'generic')
    
    if gateway == 'abacatepay':
        # VALIDAÇÃO CRÍTICA: Verificar assinatura HMAC
        signature = request.headers.get('X-Webhook-Signature')
        webhook_secret = os.getenv('ABACATEPAY_WEBHOOK_SECRET')
        
        # Recalcular HMAC com o body recebido
        body_bytes = request.get_data()
        expected_signature = hmac.new(
            webhook_secret.encode(),
            body_bytes,
            hashlib.sha256
        ).hexdigest()
        
        # Comparação segura
        if not hmac.compare_digest(signature, expected_signature):
            return jsonify({'erro': 'Assinatura inválida'}), 401
        
        # Processar evento
        if data.get('kind') == 'billing.paid':
            # Pagamento aprovado!
            billing_id = data.get('data', {}).get('id')
            metadata = data.get('data', {}).get('metadata', {})
            compra_id = int(metadata.get('compra_id'))
            
            # Atualizar compra para aprovado
            response, status = pagamento_controller.processar_webhook({
                'compra_id': compra_id,
                'status': 'aprovado'
            }, 'abacatepay')
            
            return jsonify(response), status
    
    # Fallback para outros gateways
    response, status = pagamento_controller.processar_webhook(data, gateway)
    return jsonify(response), status
```

**3. Consultar Status do Pagamento (Opcional):**

```python
from abacatepay import AbacatePay

def consultar_pagamento_abacatepay(payment_id):
    """Consulta status de um pagamento no AbacatePay"""
    
    client = AbacatePay(api_key=os.getenv('ABACATEPAY_API_KEY'))
    billing = client.billing.get(payment_id)
    
    # Mapear status do AbacatePay para nosso sistema
    status_map = {
        'PENDING': 'pendente',
        'PAID': 'aprovado',
        'EXPIRED': 'cancelado',
        'CANCELLED': 'cancelado'
    }
    
    return {
        'status': status_map.get(billing.status, 'pendente'),
        'amount': billing.amount,
        'paid_at': billing.paid_at,
        'expires_at': billing.expires_at
    }
```

### Testar no Sandbox

AbacatePay possui ambiente de **Desenvolvimento** separado:

1. **Criar conta de testes:**
   - Acesse: https://abacatepay.com
   - Crie uma conta de desenvolvimento

2. **Usar API Key de desenvolvimento:**
   ```
   ABACATEPAY_API_KEY=dev-xxxx-xxxx-xxxx
   ```

3. **Simular pagamento:**
   - A documentação fornece PIX de teste
   - Webhook será chamado automaticamente após "pagamento"

### Webhooks Disponíveis

| Evento | Descrição | Quando usar |
|--------|-----------|-------------|
| `billing.paid` | Cobrança paga | ✅ **Aprovar compra** |
| `billing.cancelled` | Cobrança cancelada | Cancelar compra |
| `billing.expired` | Cobrança expirada | Marcar como expirado |

### Validação de Segurança HMAC

**CRÍTICO:** Sempre valide a assinatura para evitar fraudes!

```python
import hmac
import hashlib

def validar_webhook_abacatepay(request):
    """Valida assinatura HMAC do webhook AbacatePay"""
    
    # Obter assinatura do header
    signature = request.headers.get('X-Webhook-Signature')
    if not signature:
        return False
    
    # Obter secret configurado
    webhook_secret = os.getenv('ABACATEPAY_WEBHOOK_SECRET')
    
    # Calcular HMAC do body (RAW bytes)
    body_bytes = request.get_data()
    expected_signature = hmac.new(
        webhook_secret.encode('utf-8'),
        body_bytes,
        hashlib.sha256
    ).hexdigest()
    
    # Comparação segura (previne timing attacks)
    return hmac.compare_digest(signature, expected_signature)
```

### Exemplo Completo de Integração

```python
# app/controllers/pagamento_controller.py
import os
from abacatepay import AbacatePay
from datetime import datetime

def criar_checkout_abacatepay(usuario_id, data):
    """Cria checkout usando AbacatePay"""
    from app.controllers.compra_controller import criar_compra
    
    # Criar compra no sistema
    response, status = criar_compra(usuario_id, data)
    if status != 201:
        return response, status
    
    compra = response['compra']
    
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
    
    # Retornar dados do checkout
    return {
        'mensagem': 'Checkout criado com sucesso',
        'compra_id': compra['id'],
        'status_pagamento': 'pendente',
        'valor_total': compra['valor_total'],
        'metodo_pagamento': 'pix',
        'pagamento': {
            'tipo': 'pix',
            'qr_code': billing.pix_url,
            'qr_code_base64': billing.pix_qrcode_base64,
            'copia_cola': billing.pix_emv,
            'payment_id': billing.id,
            'expira_em': billing.expires_at,
            'instrucoes': 'Pague com PIX - Processamento instantâneo'
        },
        'compra': compra
    }, 201
```

### Documentação Oficial

- **Site:** https://abacatepay.com
- **Docs:** https://docs.abacatepay.com
- **Python SDK:** https://github.com/abacatepay/abacatepay-python-sdk
- **Suporte:** contato@abacatepay.com

---

## 💙 Mercado Pago

### Vantagens
- ✅ Muito popular no Brasil
- ✅ PIX instantâneo e em tempo real
- ✅ SDK Python robusto
- ✅ Documentação excelente
- ✅ Sandbox para testes

### Instalação

```bash
pip install mercadopago
```

### Configuração

1. **Criar conta em:** https://www.mercadopago.com.br

2. **Obter credenciais:**
   - Acesse: https://www.mercadopago.com.br/developers/panel/credentials
   - Copie `Access Token` (começando com `APP_USR-...`)

3. **Adicionar ao `.env`:**
   ```
   MERCADOPAGO_ACCESS_TOKEN=APP_USR-seu-token-aqui
   ```

### Implementação

**1. Modificar `pagamento_controller.py`:**

```python
import os
import mercadopago

def _gerar_dados_pagamento(compra, metodo_pagamento):
    """Gera dados de pagamento PIX usando Mercado Pago"""
    
    # Sistema aceita apenas PIX
    if metodo_pagamento != 'pix':
        raise ValueError('Sistema aceita apenas pagamento via PIX')
    
    # Inicializar SDK
    sdk = mercadopago.SDK(os.getenv('MERCADOPAGO_ACCESS_TOKEN'))
    
    # Criar pagamento PIX
    payment_data = {
        "transaction_amount": float(compra['valor_total']),
        "description": f"Compra de {compra['quantidade_titulos']} títulos - {compra['campanha']['titulo']}",
        "payment_method_id": "pix",
        "payer": {
            "email": compra.get('usuario_email', 'cliente@email.com'),
            "first_name": compra.get('usuario_nome', 'Cliente'),
        },
        "external_reference": str(compra['id']),  # Identificador da compra
        "notification_url": f"{os.getenv('BASE_URL')}/api/pagamentos/webhook?gateway=mercadopago"
    }
    
    result = sdk.payment().create(payment_data)
    payment = result["response"]
    
    return {
        'tipo': 'pix',
        'qr_code': payment["point_of_interaction"]["transaction_data"]["qr_code"],
        'qr_code_base64': payment["point_of_interaction"]["transaction_data"]["qr_code_base64"],
        'copia_cola': payment["point_of_interaction"]["transaction_data"]["qr_code"],
        'payment_id': payment["id"],
        'expira_em': payment["date_of_expiration"],
        'instrucoes': 'Escaneie o QR Code ou use o código Pix Copia e Cola para realizar o pagamento'
    }
```

**2. Processar Webhook:**

```python
def processar_webhook_mercadopago(data):
    """
    Processa webhook do Mercado Pago
    Docs: https://www.mercadopago.com.br/developers/pt/docs/your-integrations/notifications/webhooks
    """
    
    # Mercado Pago envia notification type e ID
    if data.get('type') == 'payment':
        payment_id = data.get('data', {}).get('id')
        
        # Buscar detalhes do pagamento
        sdk = mercadopago.SDK(os.getenv('MERCADOPAGO_ACCESS_TOKEN'))
        payment_info = sdk.payment().get(payment_id)
        payment = payment_info["response"]
        
        # Obter ID da compra (external_reference)
        compra_id = int(payment.get('external_reference'))
        
        # Mapear status do Mercado Pago para nosso sistema
        status_map = {
            'approved': 'aprovado',
            'pending': 'pendente',
            'in_process': 'pendente',
            'rejected': 'recusado',
            'cancelled': 'cancelado'
        }
        
        novo_status = status_map.get(payment['status'], 'pendente')
        
        # Atualizar compra
        compra = Compra.query.get(compra_id)
        if compra:
            compra.status_pagamento = novo_status
            if novo_status == 'aprovado':
                compra.data_pagamento = datetime.utcnow()
                compra.campanha.titulos_vendidos += compra.quantidade_titulos
            db.session.commit()
            
        return {'success': True, 'compra_id': compra_id, 'status': novo_status}
```

### Testar no Sandbox

1. Use o Access Token de **TEST**
2. Cartões de teste: https://www.mercadopago.com.br/developers/pt/docs/checkout-api/integration-test/test-cards

---

## 🟢 Asaas

### Vantagens
- ✅ Taxas competitivas
- ✅ Excelente para PMEs brasileiras
- ✅ PIX instantâneo e confirmação em tempo real
- ✅ API REST simples e direta

### Instalação

```bash
pip install requests  # Já deve estar instalado
```

### Configuração

1. **Criar conta em:** https://www.asaas.com

2. **Obter API Key:**
   - Acesse: Configurações → Integrações → API
   - Copie a API Key

3. **Adicionar ao `.env`:**
   ```
   ASAAS_API_KEY=seu-api-key-aqui
   ```

### Implementação

```python
import requests

def _gerar_dados_pagamento_asaas(compra, metodo_pagamento):
    """Gera dados de pagamento usando Asaas"""
    
    headers = {
        'access_token': os.getenv('ASAAS_API_KEY'),
        'Content-Type': 'application/json'
    }
    
    # Criar cobrança
    payload = {
        "customer": compra.get('usuario_asaas_id'),  # ID do cliente no Asaas
        "billingType": "PIX" if metodo_pagamento == 'pix' else "BOLETO",
        "value": float(compra['valor_total']),
        "dueDate": (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
        "description": f"Compra #{compra['id']} - Rifas",
        "externalReference": str(compra['id'])
    }
    
    response = requests.post(
        'https://www.asaas.com/api/v3/payments',
        headers=headers,
        json=payload
    )
    
    payment = response.json()
    
    if metodo_pagamento == 'pix':
        # Obter QR Code PIX
        qr_response = requests.get(
            f'https://www.asaas.com/api/v3/payments/{payment["id"]}/pixQrCode',
            headers=headers
        )
        pix_data = qr_response.json()
        
        return {
            'tipo': 'pix',
            'qr_code': pix_data['payload'],
            'qr_code_base64': pix_data['encodedImage'],
            'copia_cola': pix_data['payload'],
            'payment_id': payment['id'],
            'expira_em': payment['dueDate']
        }
    
    else:  # Boleto
        return {
            'tipo': 'boleto',
            'linha_digitavel': payment['identificationField'],
            'boleto_url': payment['bankSlipUrl'],
            'payment_id': payment['id'],
            'vencimento': payment['dueDate']
        }
```

**Webhook:**

```python
def processar_webhook_asaas(data):
    """Processa webhook do Asaas"""
    
    event_type = data.get('event')
    payment = data.get('payment', {})
    
    compra_id = int(payment.get('externalReference'))
    
    status_map = {
        'PAYMENT_RECEIVED': 'aprovado',
        'PAYMENT_CONFIRMED': 'aprovado',
        'PAYMENT_OVERDUE': 'pendente',
        'PAYMENT_DELETED': 'cancelado'
    }
    
    novo_status = status_map.get(event_type, 'pendente')
    
    # Atualizar compra...
```

---

## 🔵 PagSeguro

### Vantagens
- ✅ Muito conhecido
- ✅ Proteção ao vendedor
- ✅ Checkout transparente

### Instalação

```bash
pip install pagseguro-python
```

### Configuração

1. **Criar conta em:** https://pagseguro.uol.com.br

2. **Obter credenciais:**
   - Email da conta
   - Token de integração

3. **Adicionar ao `.env`:**
   ```
   PAGSEGURO_EMAIL=seu-email@email.com
   PAGSEGURO_TOKEN=seu-token-aqui
   ```

### Implementação

```python
from pagseguro import PagSeguro

def _gerar_dados_pagamento_pagseguro(compra, metodo_pagamento):
    """Gera dados de pagamento usando PagSeguro"""
    
    pg = PagSeguro(
        email=os.getenv('PAGSEGURO_EMAIL'),
        token=os.getenv('PAGSEGURO_TOKEN'),
        config={'sandbox': False}  # True para testes
    )
    
    pg.items.add(
        id=str(compra['id']),
        description=f"Rifas - {compra['campanha']['titulo']}",
        amount=Decimal(str(compra['valor_total'])),
        quantity=1
    )
    
    pg.reference = str(compra['id'])
    pg.redirect_url = f"{os.getenv('FRONTEND_URL')}/checkout/sucesso"
    pg.notification_url = f"{os.getenv('BASE_URL')}/api/pagamentos/webhook?gateway=pagseguro"
    
    response = pg.checkout()
    
    return {
        'tipo': 'redirect',
        'checkout_url': response.payment_url,
        'code': response.code,
        'instrucoes': 'Você será redirecionado para completar o pagamento'
    }
```

---

## 🧪 Testando Localmente

### 1. Testar Criação de Checkout

```bash
curl -X POST http://localhost:5000/api/checkout \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "campanha_id": 1,
    "quantidade_titulos": 5,
    "metodo_pagamento": "pix"
  }'
```

### 2. Simular Webhook (Desenvolvimento)

```bash
# Aprovar pagamento
curl -X POST "http://localhost:5000/api/pagamentos/webhook?gateway=test" \
  -H "Content-Type: application/json" \
  -d '{"compra_id": 1, "status": "aprovado"}'
```

### 3. Consultar Status

```bash
curl -X GET http://localhost:5000/api/pagamentos/1 \
  -H "Authorization: Bearer {token}"
```

### 4. Verificar Títulos Aprovados

```bash
curl -X GET http://localhost:5000/api/meus-titulos \
  -H "Authorization: Bearer {token}"
```

---

## 🔒 Segurança

### Validação de Webhook

**CRÍTICO:** Sempre valide a assinatura do webhook em produção!

**Exemplo Mercado Pago:**

```python
import hashlib
import hmac

def validar_webhook_mercadopago(request):
    """Valida assinatura do webhook do Mercado Pago"""
    
    x_signature = request.headers.get('x-signature')
    x_request_id = request.headers.get('x-request-id')
    
    # Separar partes da assinatura
    parts = x_signature.split(',')
    ts = None
    hash_value = None
    
    for part in parts:
        key, value = part.split('=')
        if key == 'ts':
            ts = value
        elif key == 'v1':
            hash_value = value
    
    # Construir string para validação
    secret = os.getenv('MERCADOPAGO_WEBHOOK_SECRET')
    manifest = f"id:{x_request_id};request-id:{x_request_id};ts:{ts};"
    
    # Calcular hash
    expected_hash = hmac.new(
        secret.encode(),
        manifest.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_hash, hash_value)
```

---

## 📊 Monitoramento

### Logs Recomendados

```python
import logging

logger = logging.getLogger('pagamentos')

# Ao criar pagamento
logger.info(f"Pagamento criado: compra_id={compra_id}, gateway={gateway}, metodo={metodo}")

# Ao receber webhook
logger.info(f"Webhook recebido: gateway={gateway}, compra_id={compra_id}, status={status}")

# Erros
logger.error(f"Erro ao criar pagamento: {str(e)}", exc_info=True)
```

### Métricas Importantes

- Taxa de conversão (checkout → pagamento aprovado)
- Tempo médio até aprovação
- Falhas de webhook
- Pagamentos pendentes há mais de 24h

---

## 🆘 Troubleshooting

### Webhook não chegando

1. **Verificar URL pública:** Use ngrok ou similar para testes locais
   ```bash
   ngrok http 5000
   ```

2. **Configurar URL no gateway:**
   - Usar URL do ngrok: `https://xxxx.ngrok.io/api/pagamentos/webhook`

3. **Verificar logs do gateway:**
   - Mercado Pago: Dashboard → Webhooks → Histórico
   - Asaas: Integrações → Webhooks → Logs

### Pagamento aprovado mas status não atualiza

1. Verificar se webhook está cadastrado corretamente
2. Verificar logs do servidor
3. Testar webhook manualmente
4. Aprovar manualmente via `/api/pagamentos/{id}/aprovar`

---

**Última Atualização:** 2026-01-19  
**Autor:** Equipe Técnica Gêmeos Brasil
