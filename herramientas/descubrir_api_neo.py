import requests
from bs4 import BeautifulSoup
import re
import urllib.parse

url = "https://neoimport.net/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("🔍 Conectando a Neo Import y buscando endpoints...")
try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"✅ Conexión exitosa. Código HTTP: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    textos_a_analizar = [response.text]

    # Analizar scripts internos y externos
    for script in soup.find_all('script'):
        src = script.get('src')
        if src:
            if not src.startswith('http'):
                src = urllib.parse.urljoin(url, src)
            try:
                res_js = requests.get(src, headers=headers, timeout=5)
                if res_js.status_code == 200:
                    textos_a_analizar.append(res_js.text)
            except Exception:
                pass
        elif script.string:
            textos_a_analizar.append(script.string)

    endpoints_encontrados = set()
    for texto in textos_a_analizar:
        matches = re.findall(r'["\'](/api/[^"\']+|https?://[^"\']+/api/[^"\']+|/[a-zA-Z0-9_-]+/v\d+/[^"\']+|[^"\']+\.json[^"\']*)["\']', texto)
        for m in matches:
            if len(m) < 100:
                endpoints_encontrados.add(m)
        
        fetch_matches = re.findall(r'fetch\s*\(\s*["\']([^"\']+)["\']', texto)
        for f in fetch_matches:
            endpoints_encontrados.add(f)

    print("\n✨ Endpoints o rutas detectadas:")
    for ep in sorted(endpoints_encontrados):
        print(f" -> {ep}")

    with open('endpoints_neo.txt', 'w', encoding='utf-8') as f:
        for ep in sorted(endpoints_encontrados):
            f.write(ep + '\n')
            
    print("\n📁 Guardado en 'endpoints_neo.txt'.")

except Exception as e:
    print(f"❌ Error de conexión: {e}")
