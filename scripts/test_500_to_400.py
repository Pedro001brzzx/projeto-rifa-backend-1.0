import requests
import json

BASE_URL = 'http://localhost:5000/api'

def test_validation_checkout():
    # 1. Login
    print("🔑 Realizando login com conta de teste...")
    r_login = requests.post(f'{BASE_URL}/auth/login', json={
        'telefone': '558393114250',
        'senha': '123'
    })
    
    if r_login.status_code != 200:
        print(f"❌ Falha no login: {r_login.status_code}")
        return

    token = r_login.json().get('token')
    headers = {'Authorization': f'Bearer {token}'}
    
    # 2. Criar checkout com quantidade inválida ou algo que dispare a falha (ou simular CPF inválido se possível)
    # Como o CPF/Tel vem do banco para o AbacatePay, e o teste usa um usuário existente,
    # se o usuário do banco tiver CPF inválido (ex: length != 11), deve retornar 400 agora.
    
    print("🚀 Testando checkout (deve capturar erros 400 em vez de 500)...")
    payload = {
        'campanha_id': 1,
        'quantidade_titulos': 1,
        'metodo_pagamento': 'pix'
    }
    
    r = requests.post(f'{BASE_URL}/checkout', json=payload, headers=headers)
    
    print(f"Status Code: {r.status_code}")
    print(f"Response: {json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    
    if r.status_code == 400:
        print("✅ SUCESSO: O sistema capturou o erro de validação e retornou 400!")
    elif r.status_code == 201:
        print("✅ SUCESSO: Checkout criado (usuário estava com dados válidos).")
    elif r.status_code == 500:
        print("❌ FALHA: O sistema ainda está retornando 500!")

if __name__ == "__main__":
    test_validation_checkout()
