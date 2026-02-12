"""
Script de Debug para AbacatePay API
PHASE 5: Specific User Data
"""
import os
import requests
import json
import random
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('ABACATEPAY_API_KEY')
OUTPUT_FILE = 'debug_results.log'

def log(msg):
    print(msg)
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write("=== DEBUG FASE 5: USER DATA ===\n")

def generate_email():
    return f"teste.{random.randint(1000, 9999)}@debug.com"

url_billing = 'https://api.abacatepay.com/v1/billing/create'
headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

log("\n--- TESTE 1: Billing Create com CPF/Phone do Usuario ---")
# USER PROVIDED DATA
cpf = "71081729414" 
cellphone = "83994099696"
email = generate_email()

log(f"CPF: {cpf}, Cellphone: {cellphone}")

payload = {
    'frequency': 'ONE_TIME',
    'methods': ['PIX'],
    'products': [{
        'externalId': '999',
        'name': 'Teste User Data',
        'quantity': 1,
        'price': 100
    }],
    'returnUrl': 'http://localhost:5173/checkout',
    'completionUrl': 'http://localhost:5000/api/pagamentos/webhook',
    'customer': {
        'name': 'Teste User',
        'email': email,
        'cellphone': cellphone,  
        'taxId': cpf
    }
}

try:
    response = requests.post(url_billing, json=payload, headers=headers, timeout=10)
    log(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            log("✅ SUCESSO Billing (User Data)!")
            log(f"Billing ID: {data.get('data', {}).get('id')}")
        else:
            log(f"❌ Falha Billing: {data.get('error')}")
    else:
        log(f"❌ Erro HTTP Billing: {response.text[:200]}")
except Exception as e:
    log(f"❌ Exceção Billing: {e}")

log("\n=== FIM DO DEBUG ===")
