import json
import requests

USER_URL = "https://otnjxfzttdjihjcoximm.supabase.co"
USER_KEY = "sb_publishable_ifoJPoL74pGM2B4cBxSLwg_7OrOGYy5"

user_headers = {
    "apikey": USER_KEY,
    "Authorization": f"Bearer {USER_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

with open("catalogo_real.json", "r", encoding="utf-8") as f:
    todos_los_productos = json.load(f)

print(f"🔄 Sincronizando y corrigiendo precios para {len(todos_los_productos)} productos...")

productos_supabase = []
for item in todos_los_productos:
    codigo = item.get('id')
    p_usd = float(item.get('precio_usd') or 0)
    p_ars = float(item.get('precio_ars') or (p_usd * 1200))
    
    # Aplicar 20% de ganancia
    precio_usd_final = round(p_usd * 1.20, 2)
    precio_ars_final = round(p_ars * 1.20, 2)
    
    productos_supabase.append({
        "id": codigo,
        "nombre": item.get('nombre', 'Sin nombre'),
        "categoria": item.get('categoria', 'General'),
        "precio": precio_usd_final,       # Columna principal por defecto
        "precio_usd": precio_usd_final,
        "precio_ars": precio_ars_final,
        "imagen": item.get('imagen', 'https://via.placeholder.com/300'),
        "descripcion": item.get('descripcion', 'Sin descripción disponible.'),
        "stock": int(item.get('stock', 10))
    })

# Enviar a Supabase en lotes de 500
lote_tamano = 500
for i in range(0, len(productos_supabase), lote_tamano):
    lote = productos_supabase[i:i + lote_tamano]
    res = requests.post(f"{USER_URL}/rest/v1/productos", headers=user_headers, data=json.dumps(lote))
    if res.status_code in [200, 201]:
        print(f"✅ Lote {i // lote_tamano + 1} actualizado con éxito.")
    else:
        print(f"⚠️ Error en lote {i // lote_tamano + 1}: {res.text}")

print("🎉 ¡Precios corregidos y actualizados en Supabase!")
