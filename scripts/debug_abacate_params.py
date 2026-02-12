
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('ABACATEPAY_API_KEY')
print(f"API Key: {api_key}")

url = "https://api.abacatepay.com/v1/customer/create"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "name": "Teste Debug Customer",
    "email": "teste.customer@exemplo.com",
    "taxId": "03963606060",
    "cellphone": "(85) 99999-9999" 
}

print(f"Sending POST to {url}")
print(f"Payload: {payload}")

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {response.headers}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
