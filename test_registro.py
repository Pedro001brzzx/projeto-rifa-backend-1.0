# Teste de Registro via Python
# Execute este arquivo para testar o endpoint de registro

import requests
import json

# URL do backend
BASE_URL = "http://localhost:5000"

# Dados para registro
dados_registro = {
    "nome": "Usuario Teste",
    "telefone": "11987654321",
    "senha": "senha123",
    "email": "teste@email.com",
    "cidade": "São Paulo",
    "estado": "SP"
}

print("🧪 Testando endpoint de registro...")
print(f"📍 URL: {BASE_URL}/api/auth/registro")
print(f"📦 Dados: {json.dumps(dados_registro, indent=2)}")
print("\n" + "="*50 + "\n")

try:
    response = requests.post(
        f"{BASE_URL}/api/auth/registro",
        json=dados_registro,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"✅ Status Code: {response.status_code}")
    print(f"📄 Response:\n{json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        print("\n🎉 SUCESSO! Usuário registrado!")
        print(f"🔑 Token: {response.json()['token'][:50]}...")
        print(f"👤 Usuário: {response.json()['usuario']['nome']}")
    elif response.status_code == 400:
        print("\n⚠️ Usuário já existe ou dados inválidos")
    else:
        print(f"\n❌ Erro: {response.json()}")
        
except requests.exceptions.ConnectionError:
    print("❌ ERRO: Backend não está rodando em http://localhost:5000")
    print("Execute: python app.py")
except Exception as e:
    print(f"❌ Erro inesperado: {e}")
