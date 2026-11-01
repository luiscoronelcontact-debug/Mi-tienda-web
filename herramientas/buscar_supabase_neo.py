import requests
from bs4 import BeautifulSoup
import re
import urllib.parse

url = "https://neoimport.net/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

print("🔍 Buscando la configuración de Supabase de Neo Import en sus scripts...")
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

textos_a_analizar = [response.text]

for script in soup.find_all('script'):
    src = script.get('src')
    if src:
        if not src.startswith('http'):
            src = urllib.parse.urljoin(url, src)
        try:
            res = requests.get(src, headers=headers, timeout=5)
            if res.status_code == 200:
                textos_a_analizar.append(res.text)
        except Exception:
            pass
    elif script.string:
        textos_a_analizar.append(script.string)

encontrado = False
for texto in textos_a_analizar:
    # Buscar URLs de Supabase
    sb_urls = re.findall(r'https?://[a-zA-Z0-9.-]+\.supabase\.co', texto)
    # Buscar claves anon/public de Supabase (formato JWT que empiezan con eyJ)
    keys = re.findall(r'["\'](eyJ[a-zA-Z0-9_.-]{50,})["\']', texto)
    
    if sb_urls or keys:
        print("\n🎉 ¡DATOS DE CONEXIÓN ENCONTRADOS!")
        if sb_urls:
            print(f"🔗 Supabase URL de Neo Import: {set(sb_urls)}")
            with open("neo_supabase_url.txt", "w") as f:
                f.write(list(sb_urls)[0])
        if keys:
            print(f"🔑 Supabase Key detectada (primeros caracteres): {[k[:20] + '...' for k in keys]}")
            with open("neo_supabase_key.txt", "w") as f:
                f.write(keys[0])
        encontrado = True

if not encontrado:
    print("⚠️ No se encontraron credenciales directas en los scripts. Buscando endpoints de API REST...")
    endpoints = set()
    for texto in textos_a_analizar:
        matches = re.findall(r'["\'](/rest/v1/[^"\']+|https?://[^"\']+/rest/v1/[^"\']*)["\']', texto)
        for m in matches:
            endpoints.add(m)
    if endpoints:
        print("✨ Endpoints REST detectados:")
        for ep in endpoints:
            print(f" -> {ep}")
    else:
        print("❌ No se detectaron patrones visibles.")
else:
    print("\n📁 Credenciales guardadas. Listos para descargar el catálogo.")
