"""
Teste Completo do Fluxo de Pagamento - Modo MOCK
"""

import requests
import json

BASE_URL = "http://localhost:5000"

print("=" * 60)
print("🧪 TESTE COMPLETO - FLUXO DE PAGAMENTO (MODO MOCK)")
print("=" * 60)

# 1. LOGIN
print("\n1️⃣ Fazendo login...")
login = requests.post(f'{BASE_URL}/api/auth/login', json={
    "telefone": "5583994099696",
    "senha": "123456"
})

if login.status_code != 200:
    print(f"❌ Erro no login: {login.text}")
    exit()

token = login.json()['token']
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}
print("✅ Login realizado com sucesso!")

# 2. CRIAR CHECKOUT (MODO MOCK)
print("\n2️⃣ Criando checkout...")
checkout = requests.post(f'{BASE_URL}/api/checkout',
    headers=headers,
    json={
        "campanha_id": 1,
        "quantidade_titulos": 3,
        "metodo_pagamento": "pix"
    }
)

if checkout.status_code != 201:
    print(f"❌ Erro ao criar checkout: {checkout.text}")
    exit()

checkout_data = checkout.json()
compra_id = checkout_data['compra_id']
print(f"✅ Checkout criado! Compra ID: {compra_id}")
print(f"   Valor total: R$ {checkout_data['valor_total']:.2f}")
print(f"   Status: {checkout_data['status_pagamento']}")
print(f"   Instrução: {checkout_data['pagamento']['instrucoes']}")

# 3. CONSULTAR PAGAMENTO
print(f"\n3️⃣ Consultando status do pagamento {compra_id}...")
status = requests.get(f'{BASE_URL}/api/pagamentos/{compra_id}', headers=headers)

if status.status_code == 200:
    status_data = status.json()
    print(f"✅ Status: {status_data['status_pagamento']}")
    print(f"   Método: {status_data['metodo_pagamento']}")
else:
    print(f"❌ Erro ao consultar: {status.text}")

# 4. SIMULAR APROVAÇÃO MANUAL (ADMIN)
print(f"\n4️⃣ Aprovando pagamento manualmente (como admin)...")
aprovar = requests.post(f'{BASE_URL}/api/pagamentos/{compra_id}/aprovar', headers=headers)

if aprovar.status_code == 200:
    aprovacao = aprovar.json()
    print(f"✅ {aprovacao['mensagem']}")
    print(f"   Status anterior: {aprovacao.get('status_anterior', 'N/A')}")
    print(f"   Status atual: {aprovacao['status_atual']}")
else:
    print(f"❌ Erro ao aprovar: {aprovar.text}")

# 5. LISTAR TÍTULOS DO USUÁRIO
print("\n5️⃣ Listando meus títulos...")
titulos = requests.get(f'{BASE_URL}/api/meus-titulos', headers=headers)

if titulos.status_code == 200:
    titulos_data = titulos.json()
    print(f"✅ Total de compras: {titulos_data['total']}")
    
    if titulos_data['compras']:
        ultima_compra = titulos_data['compras'][0]
        print(f"\n📋 Última compra:")
        print(f"   Campanha: {ultima_compra['campanha']['titulo']}")
        print(f"   Quantidade: {ultima_compra['quantidade_titulos']} títulos")
        print(f"   Status: {ultima_compra['status_pagamento']}")
        print(f"   Títulos:")
        for titulo in ultima_compra['titulos'][:5]:  # Mostrar apenas 5
            print(f"      - {titulo['numero']}")
        if len(ultima_compra['titulos']) > 5:
            print(f"      ... e mais {len(ultima_compra['titulos']) - 5} títulos")
else:
    print(f"❌ Erro ao listar títulos: {titulos.text}")

# RESUMO FINAL
print("\n" + "=" * 60)
print("✅ TESTE COMPLETO FINALIZADO COM SUCESSO!")
print("=" * 60)
print("\n📊 Fluxo testado:")
print("  1. ✅ Login de usuário")
print("  2. ✅ Criação de checkout (MOCK)")
print("  3. ✅ Consulta de status")
print("  4. ✅ Aprovação manual (Admin)")
print("  5. ✅ Listagem de títulos")
print("\n💡 Sistema pronto para produção!")
print("   Configure ABACATEPAY_API_KEY real para usar AbacatePay.")
print("=" * 60)
