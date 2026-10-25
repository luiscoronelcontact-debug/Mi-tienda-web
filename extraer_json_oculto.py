import requests
import json
from bs4 import BeautifulSoup

url = "https://neoimport.net/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("🔍 Analizando la estructura interna de Neo Import...")
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# Buscar scripts que contengan datos JSON incrustados (como window.__NUXT__, __NEXT_DATA__, o estados globales)
productos_encontrados = []

for script in soup.find_all('script'):
    texto = script.string or ""
    if "product" in texto.lower() or "precio" in texto.lower() or "catalog" in texto.lower():
        # Intentar extraer bloques JSON dentro del script
        print("✨ ¡Se encontró un script con datos de productos incrustados!")
        # Aquí podemos parsear o volcar para inspeccionar

print("🔄 Si no hay JSON directo, ajustando método de búsqueda por API interna...")
