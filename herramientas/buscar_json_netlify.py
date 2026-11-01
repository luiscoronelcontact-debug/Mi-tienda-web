import requests
from bs4 import BeautifulSoup
import urllib.parse
import json

url = "https://neoimport.net/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("🔍 Buscando archivos JSON y catálogos en Netlify...")
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

enlaces = set()
for tag in soup.find_all(['script', 'link', 'a']):
    src = tag.get('src') or tag.get('href') or tag.get('data-url')
    if src:
        completa = urllib.parse.urljoin(url, src)
        if any(k in completa.lower() for k in ['.json', 'catalog', 'product', 'data', 'api', 'db']):
            enlaces.add(completa)

# Probar también rutas comunes de archivos estáticos en Netlify
rutas_comunes = [
    "/catalog.json",
    "/productos.json",
    "/data/products.json",
    "/assets/catalog.json",
    "/db.json"
]

for r in rutas_comunes:
    enlaces.add(urllib.parse.urljoin(url, r))

print(f"\n✨ Probando {len(enlaces)} rutas candidatas...")
for link in enlaces:
    try:
        res = requests.get(link, headers=headers, timeout=5)
        print(f"[{res.status_code}] {link}")
        if res.status_code == 200 and ('json' in res.headers.get('content-type', '') or res.text.strip().startswith(('{', '['))):
            print(f"\n🎉 ¡ENCONTRADO ARCHIVO DE DATOS! -> {link}")
            with open("catalogo_encontrado.json", "w", encoding="utf-8") as f:
                f.write(res.text)
            print("📁 Guardado en 'catalogo_encontrado.json'. Muestra:")
            print(res.text[:300])
            break
    except Exception:
        pass
