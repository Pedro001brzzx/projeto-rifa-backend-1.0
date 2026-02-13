import requests
import json
import os
import hmac
import hashlib

# Configurações
BASE_URL = 'http://localhost:5000/api/pagamentos/webhook'
WEBHOOK_SECRET = os.getenv('ABACATEPAY_WEBHOOK_SECRET', 'test_secret_123')

def simular_pagamento(compra_id):
    """
    Envia um webhook falso para a API local simulando um pagamento aprovado.
    """
    print(f"🚀 Simulando pagamento para Compra #{compra_id}...")
    
    # Payload do evento 'billing.paid'
    payload = {
        "event": "billing.paid",
        "data": {
            "billing": {
                "id": f"bill_fake_{compra_id}",
                "status": "PAID",
                "products": [
                    {
                        "externalId": str(compra_id),
                        "quantity": 1
                    }
                ]
            }
        }
    }
    
    payload_json = json.dumps(payload)
    
    # Gerar assinatura HMAC (se necessário, mas em DEV o controller aceita sem se não tiver secret)
    # Mas vamos gerar para garantir
    signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload_json.encode(),
        hashlib.sha256
    ).hexdigest()
    
    headers = {
        'Content-Type': 'application/json',
        'X-Webhook-Signature': signature
    }
    
    try:
        response = requests.post(BASE_URL, data=payload_json, headers=headers)
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"📦 Resposta: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ Pagamento simulado com sucesso! Verifique se os títulos foram gerados.")
        else:
            print("\n❌ Falha ao simular pagamento.")
            
    except Exception as e:
        print(f"\n❌ Erro de conexão: {e}")
        print("Certifique-se que o servidor está rodando em localhost:5000")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python scripts/simulate_webhook.py <ID_DA_COMPRA>")
        print("Exemplo: python scripts/simulate_webhook.py 123")
    else:
        compra_id = sys.argv[1]
        simular_pagamento(compra_id)
