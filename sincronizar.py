import json
import requests

SUPABASE_URL = "https://otnjxfzttdjihjcoximm.supabase.co"
SUPABASE_KEY = "sb_publishable_ifoJPoL74pGM2B4cBxSLwg_7OrOGYy5"
ENDPOINT = f"{SUPABASE_URL}/rest/v1/productos"

def sincronizar():
    print("🔄 Leyendo el archivo completo productos.js...")
    try:
        with open("productos.js", "r", encoding="utf-8") as f:
            contenido = f.read()
        
        # Extraer el arreglo JSON dentro de la variable de JavaScript (const productos = [...])
        inicio = contenido.index('[')
        fin = contenido.rindex(']') + 1
        productos = json.loads(contenido[inicio:fin])
    except Exception as e:
        print(f"❌ Error leyendo productos.js: {e}")
        return

    total = len(productos)
    print(f"📦 Procesando los {total} productos hacia Supabase en bloques...")

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }

    batch_size = 500
    for i in range(0, total, batch_size):
        batch = productos[i:i+batch_size]
        response = requests.post(ENDPOINT, headers=headers, json=batch)
        
        if response.status_code in [200, 201, 204]:
            print(f"✅ Lote {i} al {min(i+batch_size, total)} de {total} sincronizado con éxito.")
        else:
            print(f"⚠️ Error en lote {i}: {response.status_code} - {response.text}")

    print("✅ ¡Sincronización masiva de todo el catálogo completada con éxito!")

if __name__ == "__main__":
    sincronizar()
