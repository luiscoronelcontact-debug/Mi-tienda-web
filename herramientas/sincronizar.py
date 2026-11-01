import json
import requests

# Credenciales directas de tu proyecto
SUPABASE_URL = "https://otnjxfzttdjihjcoximm.supabase.co"
SUPABASE_KEY = "sb_publishable_ifoJPoL74pGM2B4cBxSLwg_7OrOGYy5"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

def sincronizar_catalogo():
    try:
        # 1. Leer el archivo local completo de Neo Import
        print("📂 Leyendo catalogo_real.json...")
        with open('catalogo_real.json', 'r', encoding='utf-8') as f:
            productos_crudos = json.load(f)
        
        if not productos_crudos:
            print("❌ El archivo catalogo_real.json está vacío.")
            return

        total_productos = len(productos_crudos)
        print(f"🔄 Procesando {total_productos} productos y aplicando el 20% de ganancia...")
        
        productos_para_supabase = []
        for p in productos_crudos:
            # Soportar diferentes nombres de claves que puedan venir en el JSON original
            precio_base = float(p.get('precio_usd', p.get('precio', p.get('costo', p.get('price', 0)))))
            precio_con_ganancia = precio_base * 1.20  # Aplicando tu 20% de ganancia

            producto_formateado = {
                "id": str(p.get("codigo", p.get("id", p.get("sku", "")))),
                "nombre": p.get("nombre", p.get("title", p.get("name", "Sin nombre"))),
                "categoria": p.get("categoria", "General"),
                "precio": round(precio_con_ganancia, 2),
                "imagen": p.get("imagen", "https://via.placeholder.com/300"),
                "descripcion": p.get("descripcion", "Sin descripción disponible."),
                "stock": int(p.get("stock", p.get("quantity", 0)))
            }
            productos_para_supabase.append(producto_formateado)

        # 2. Enviar por lotes (batches de 500) para evitar saturar Supabase con los 24,000 ítems
        url = f"{SUPABASE_URL}/rest/v1/productos"
        lote_tamano = 500
        print(f"🚀 Subiendo a Supabase en bloques de {lote_tamano} productos...")

        for i in range(0, len(productos_para_supabase), lote_tamano):
            lote = productos_para_supabase[i:i + lote_tamano]
            response = requests.post(url, headers=headers, data=json.dumps(lote))
            
            if response.status_code in [200, 201]:
                print(f"✅ Lote {i // lote_tamano + 1} subido con éxito ({min(i + lote_tamano, total_productos)}/{total_productos})...")
            else:
                print(f"⚠️ Error en el lote {i // lote_tamano + 1} ({response.status_code}): {response.text}")
                return

        print("✨ ¡Catálogo completo sincronizado exitosamente en Supabase con el 20% de ganancia aplicado!")

    except Exception as e:
        print(f"❌ Ocurrió un error durante la sincronización: {e}")

if __name__ == "__main__":
    sincronizar_catalogo()
