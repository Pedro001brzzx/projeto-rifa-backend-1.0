"""
Script de Teste Completo de Checkout
Simula o fluxo do frontend: Login -> Compra -> Checkout
"""
import requests
import json
import random

BASE_URL = 'http://localhost:5000/api'

def generate_cpf():
    cpf = [random.randint(0, 9) for _ in range(9)]
    soma = sum(a*b for a, b in zip(cpf, range(10, 1, -1)))
    digito1 = (soma * 10 % 11) % 10
    cpf.append(digito1)
    soma = sum(a*b for a, b in zip(cpf, range(11, 1, -1)))
    digito2 = (soma * 10 % 11) % 10
    cpf.append(digito2)
    return "".join(map(str, cpf))

name = "PEDRO HENRIQUE ALVES LOPES"
email = "pedrohenriquealveslopes@live.com"
password = "123"
# MASKS: Testando sanitização regex
cpf_com_mascara = "711.082.184-66"
phone_com_mascara = "+55 (83) 9311-4250"

print(f"👤 [TEST] Usando dados formatados para validar sanitização: {name} | CPF: {cpf_com_mascara} | Tel: {phone_com_mascara}")

# 1. Registrar
r = requests.post(f'{BASE_URL}/auth/registro', json={
    'nome': name,
    'email': email,
    'senha': password,
    'telefone': phone_com_mascara,
    'cpf': cpf_com_mascara
})
print(f"Registro: {r.status_code}")

# 2. Login
print(f"Tentando login com telefone: {phone_com_mascara}")
r = requests.post(f'{BASE_URL}/auth/login', json={
    'telefone': phone_com_mascara,
    'senha': password
})
print(f"Login: {r.status_code}")
if r.status_code != 200:
    print(r.text)
    exit(1)

token = r.json()['token']
headers = {'Authorization': f'Bearer {token}'}

# 3. Criar Compra (Simulando uma rifa existente - ID 1 geralmente existe)
# Precisamos de uma campanha valida. 
# Vou assumir campanha_id=1. Se falhar, tento listar campanhas.
campanha_id = 1
r = requests.get(f'{BASE_URL}/campanhas?status=ativa') # Test campaign uses 'ativa'
if r.status_code == 200 and r.json().get('campanhas'):
    # Pagination format
    campanha_id = r.json()['campanhas'][0]['id']
    print(f"Usando campanha ID: {campanha_id}")
elif r.status_code == 200 and isinstance(r.json(), list) and r.json():
    # Legacy list format
    campanha_id = r.json()[0]['id']
    print(f"Usando campanha ID (list): {campanha_id}")
else:
     print(f"Aviso: Nenhuma campanha encontrada. Tentando ID={campanha_id}")

print("🛒 Criando Checkout...")
payload = {
    'campanha_id': campanha_id,
    'quantidade_titulos': 1,
    'metodo_pagamento': 'pix'
}

try:
    r = requests.post(f'{BASE_URL}/checkout', json=payload, headers=headers)
    print(f"Checkout Status: {r.status_code}")
    print(f"Response: {r.text[:500]}")

    if r.status_code == 200:
        checkout_response = r.json()
        compra = checkout_response.get('compra')
        pagamento = checkout_response.get('pagamento')

        if compra and pagamento:
            print(f"🔗 URL de Pagamento: {pagamento.get('payment_url')}")
            
            # NOVÍSSIMO TESTE: Validar o Polling (GET /api/pagamentos/<id>)
            # É aqui que o frontend pega os dados para exibir na tela de "Aguardando pagamento"
            print(f"\n🔍 [POLLING TEST] Consultando status da Compra #{compra.get('id')}...")
            r_poll = requests.get(f"{BASE_URL}/pagamentos/{compra.get('id')}", headers=headers)
            
            if r_poll.status_code == 200:
                poll_data = r_poll.json()
                status = poll_data.get('status_pagamento')
                pagamento_poll = poll_data.get('pagamento')
                
                print(f"📊 Status via Polling: {status}")
                if pagamento_poll:
                    print(f"✅ Objeto 'pagamento' encontrado no polling!")
                    print(f"📝 Pix Code: {pagamento_poll.get('pix_code')[:30]}...")
                    print(f"🖼️ QR Code: {pagamento_poll.get('qr_code')[:30]}...")
                else:
                    print("❌ ERRO: Objeto 'pagamento' AUSENTE no polling! O frontend não mostrará o QR Code.")
            else:
                print(f"❌ Falha no Polling: {r_poll.status_code} - {r_poll.text}")
        else:
            print("❌ ERRO: 'compra' ou 'pagamento' não encontrados na resposta do checkout.")
    else:
        print(f"Falha Checkout: {r.status_code}")
        print(r.text)

except Exception as e:
    print(f"Erro request: {e}")
