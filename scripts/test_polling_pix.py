import requests
import json

BASE_URL = 'http://localhost:5000/api'

def test_polling():
    # 1. Login
    print("🔑 Realizando login...")
    r_login = requests.post(f'{BASE_URL}/auth/login', json={
        'telefone': '558393114250',
        'senha': '123'
    })
    
    if r_login.status_code != 200:
        print(f"❌ Falha no login: {r_login.status_code}")
        print(r_login.text)
        return

    token = r_login.json().get('token')
    headers = {'Authorization': f'Bearer {token}'}
    
    # 2. Consultar última compra (ou ID 50 que sabemos que tem dados)
    print("🔍 Consultando status da Compra #50...")
    r = requests.get(f'{BASE_URL}/pagamentos/50', headers=headers)
    
    if r.status_code == 200:
        data = r.json()
        print("\n✅ Resposta do Polling OK!")
        print(f"Chaves no Top Level: {list(data.keys())}")
        
        pagamento_poll = data.get('pagamento')
        if pagamento_poll:
            print(f"✅ Objeto 'pagamento' PRESENTE!")
            print(f"Chaves em 'pagamento': {list(pagamento_poll.keys())}")
            print(f"qr_code_base64 (len): {len(pagamento_poll.get('qr_code_base64', ''))}")
            print(f"copia_cola (len): {len(pagamento_poll.get('copia_cola', ''))}")
        else:
            print("\n❌ ERRO: Objeto 'pagamento' está AUSENTE!")
    else:
        print(f"❌ Erro na consulta: {r.status_code}")
        print(r.text)

if __name__ == "__main__":
    test_polling()
