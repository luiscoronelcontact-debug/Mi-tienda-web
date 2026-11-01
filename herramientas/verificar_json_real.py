import requests
import json

rutas = [
    "https://neoimport.net/productos.json",
    "https://neoimport.net/catalog.json",
    "https://neoimport.net/assets/catalog.json",
    "https://neoimport.net/data/products.json",
    "https://neoimport.net/db.json"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

for url in rutas:
    print(f"\n🔍 Probando contenido de: {url}")
    try:
        res = requests.get(url, headers=headers, timeout=5)
        texto = res.text.strip()
        if texto.startswith(("{", "[")) and "<html" not in texto.lower():
            print(f"🎉 ¡ESTE ES EL ARCHIVO REAL! -> {url}")
            data = res.json()
            print(f"📊 Cantidad de elementos / Estructura: {type(data)}")
            if isinstance(data, list):
                print(f"📦 Total de productos en el JSON: {len(data)}")
            elif isinstance(data, dict):
                print(f"📦 Claves principales: {list(data.keys())[:5]}")
            
            with open("catalogo_real.json", "w", encoding="utf-8") as f:
                f.write(res.text)
            print("📁 Guardado exitosamente como 'catalogo_real.json'.")
            break
        else:
            print("❌ Es un archivo HTML (página de respaldo de Netlify), no es JSON.")
    except Exception as e:
        print(f"❌ Error al leer: {e}")
