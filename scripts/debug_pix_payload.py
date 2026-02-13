import os
import requests
import json
from datetime import datetime

# Configuração (Simulando o ambiente)
API_KEY = os.getenv('ABACATEPAY_API_KEY')
if not API_KEY:
    print("❌ ERRO: ABACATEPAY_API_KEY não encontrada no ambiente.")
    # Tentar ler do .env manualmente se não estiver carregado
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('ABACATEPAY_API_KEY='):
                    API_KEY = line.strip().split('=')[1]
                    print(f"✅ Chave carregada do .env: {API_KEY[:5]}...")
                    break
    except:
        pass

if not API_KEY:
    exit(1)

URL = 'https://api.abacatepay.com/v1/billing/create'
HEADERS = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

# Dados simulados (Baseado no usuário Pedro)
payload = {
    'frequency': 'ONE_TIME',
    'methods': ['PIX'],
    'products': [{
        'externalId': 'TEST-DEBUG-001',
        'name': 'Teste de Debug PIX',
        'description': 'Item de teste para validação de QR Code',
        'quantity': 1,
        'price': 1000 # R$ 10,00 (em centavos)
    }],
    'returnUrl': 'http://localhost:5173/checkout/sucesso',
    'completionUrl': 'http://localhost:5000/api/pagamentos/webhook',
    'customer': {
        'name': 'Pedro Henrique',
        'email': 'pedro@exemplo.com',
        'cellphone': '83994099696', # Sem 55, apenas DDD + numero (testar formato)
        'taxId': '71081729414'
    }
}

print("\n🚀 Enviando requisição para AbacatePay...")
print(json.dumps(payload, indent=2))

try:
    response = requests.post(URL, json=payload, headers=HEADERS)
    print(f"\n📡 Status Code: {response.status_code}")
    
    data = response.json()
    print("\n📦 Resposta da API:")
    print(json.dumps(data, indent=2))
    
    if data.get('success'):
        billing = data.get('data', {})
        pix_code = (
            billing.get('pixQrCode', {}).get('qrcode') or 
            billing.get('pixQrCode', {}).get('brcode') or
            billing.get('pix', {}).get('copyPaste') or
            billing.get('qrcode') or
            billing.get('brcode')
        )
        
        print("\n🔑 CÓDIGO PIX PARA VALIDAÇÃO:")
        print("-" * 50)
        print(pix_code)
        print("-" * 50)
        print("\n👉 Copie este código e valide em: https://pix.bcb.gov.br/")
    else:
        print("\n❌ Erro na criação da cobrança.")

except Exception as e:
    print(f"\n❌ Exceção: {e}")
