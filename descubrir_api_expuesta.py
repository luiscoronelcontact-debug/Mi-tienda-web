import requests
from bs4 import BeautifulSoup
import re
import urllib.parse

url = "https://neoimport.net/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("🔍 Analizando la página principal y scripts externos de Neo Import...")
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

textos_a_analizar = [response.text]

# Descargar también los scripts externos vinculados
for script in soup.find_all('script'):
    src = script.get('src')
    if src:
        if not src.startswith('http'):
            src = urllib.parse.urljoin(url, src)
        try:
            print(f"📥 Leyendo script: {src.split('/')[-1]}")
            res_js = requests.get(src, headers=headers, timeout=5)
            if res_js.status_code == 200:
                textos_a_analizar.append(res_js.text)
        except Exception:
            pass
    elif script.string:
        textos_a_analizar.append(script.string)

# Buscar patrones de API, endpoints o llamadas fetch en el código
endpoints_encontrados = set()
for texto in textos_a_analizar:
    # Buscar rutas que contengan api, v1, v2, graphql o extensiones de datos
    matches = re.findall(r'["\'](/api/[^"\']+|https?://[^"\']+/api/[^"\']+|/[a-zA-Z0-9_-]+/v\d+/[^"\']+|[^"\']+\.json[^"\']*)["\']', texto)
    for m in matches:
        if len(m) < 100:  # Filtrar rutas válidas y descartar textos largos
            endpoints_encontrados.add(m)
            
    # Buscar llamadas fetch explícitas
    fetch_matches = re.findall(r'fetch\s*\(\s*["\']([^"\']+)["\']', texto)
    for f in fetch_matches:
        endpoints_encontrados.add(f)

print("\n✨ ¡Endpoints y rutas detectadas en el código fuente:")
for ep in sorted(endpoints_encontrados):
    print(f" -> {ep}")

with open('endpoints_descubiertos.txt', 'w', encoding='utf-8') as f:
    for ep in sorted(endpoints_encontrados):
        f.write(ep + '\n')

print("\n📁 Resultados guardados en 'endpoints_descubiertos.txt'.")
