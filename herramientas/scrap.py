import requests

url = "https://neoimport.net/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("🔍 Probando conexión con Neo Import...")
response = requests.get(url, headers=headers)
print(f"Código de estado HTTP: {response.status_code}")
print("Primeros 300 caracteres de la respuesta:")
print(response.text[:300])
