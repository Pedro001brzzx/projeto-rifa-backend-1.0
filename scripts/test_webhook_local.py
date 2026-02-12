
import requests
import hmac
import hashlib
import json
import os
import sys
from datetime import datetime

# Configuração (deve bater com o .env local)
WEBHOOK_SECRET = "test_secret_123" 
BASE_URL = "http://localhost:5000"

def simulate_webhook(compra_id):
    """
    Simula um webhook do AbacatePay para aprovar uma compra.
    """
    
    # Payload similar ao do AbacatePay
    payload = {
        "event": "billing.paid",
        "data": {
            "billing": {
                "id": f"bill_simulated_{compra_id}",
                "status": "PAID",
                "products": [
                    {
                        "externalId": str(compra_id),
                        "name": "Rifa Teste"
                    }
                ]
            }
        }
    }
    # Payload similar ao do AbacatePay (Compact JSON default often used in webhooks)
    # Mas o importante é que a assinatura bata com o corpo
    payload_json = json.dumps(payload, separators=(',', ':')) # Compact
    payload_bytes = payload_json.encode('utf-8')
    
    body_hash = hashlib.sha256(payload_bytes).hexdigest()
    print(f"📦 Payload Bytes: {payload_bytes}")
    print(f"🔑 Body Hash: {body_hash}")
    
    # Gerar assinatura HMAC
    signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()
    
    print(f"📦 Payload Bytes: {payload_bytes}")
    print(f"🔐 Signature: {signature}")
    
    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Signature": signature
    }
    
    url = f"{BASE_URL}/api/pagamentos/webhook?gateway=abacatepay"
    
    print(f"🚀 Enviando POST para {url}...")
    try:
        response = requests.post(url, data=payload_bytes, headers=headers)
        print(f"📡 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python test_webhook_local.py <compra_id>")
        sys.exit(1)
        
    compra_id_target = sys.argv[1]
    simulate_webhook(compra_id_target)
