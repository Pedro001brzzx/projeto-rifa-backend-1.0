import requests
import json

# 1. Login
print("🔐 Fazendo login...")
login = requests.post('http://localhost:5000/api/auth/login', json={
    "telefone": "5583994099696",
    "senha": "123456"
})

if login.status_code != 200:
    print(f"❌ Erro no login: {login.text}")
    exit()

token = login.json()['token']
print(f"✅ Login OK! Token obtido.\n")

# 2. Criar checkout
print("🛒 Criando checkout com AbacatePay...")
checkout = requests.post('http://localhost:5000/api/checkout', 
    headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    },
    json={
        "campanha_id": 1,
        "quantidade_titulos": 5,
        "metodo_pagamento": "pix"
    }
)

print(f"\n📊 Status: {checkout.status_code}")

# Mostrar erro se houver
if checkout.status_code != 201:
    print(f"❌ Erro: {checkout.text}")
else:
    print(f"\n📦 Resposta:")
    print(json.dumps(checkout.json(), indent=2, ensure_ascii=False))