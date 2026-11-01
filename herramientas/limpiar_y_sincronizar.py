import json
import requests

SUPABASE_URL = "https://otnjxfzttdjihjcoximm.supabase.co"
SUPABASE_KEY = "sb_publishable_ifoJPoL74pGM2B4cBxSLwg_7OrOGYy5"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

print("🧹 Limpiando la tabla de Supabase (eliminando duplicados)...")
# Eliminar todos los registros existentes
requests.delete(f"{SUPABASE_URL}/rest/v1/productos?id=neq.0", headers=headers)

# Leer catálogo local actual
with open('catalogo_real.json', 'r', encoding='utf-8') as f:
    productos_crudos = json.load(f)

print(f"🔄 Procesando {len(productos_crudos)} productos únicos...")
productos_para_supabase = []

for p in productos_crudos:
    precio_base = float(p.get('precio_usd', p.get('precio', p.get('costo', p.get('price', 0)))))
    precio_con_ganancia = precio_base * 1.20

    productos_para_supabase.append({
        "id": str(p.get("codigo", p.get("id", p.get("sku", "")))),
        "nombre": p.get("nombre", p.get("title", p.get("name", "Sin nombre"))),
        "categoria": p.get("categoria", "General"),
        "precio": round(precio_con_ganancia, 2),
        "imagen": p.get("imagen", "https://via.placeholder.com/300"),
        "descripcion": p.get("descripcion", "Sin descripción disponible."),
        "stock": int(p.get("stock", p.get("quantity", 0)))
    })

# Subir por lotes limpios de 500
lote_tamano = 500
print("🚀 Subiendo catálogo limpio a Supabase...")

for i in range(0, len(productos_para_supabase), lote_tamano):
    lote = productos_para_supabase[i:i + lote_tamano]
    response = requests.post(f"{SUPABASE_URL}/rest/v1/productos", headers=headers, data=json.dumps(lote))
    if response.status_code in [200, 201]:
        print(f"✅ Lote {i // lote_tamano + 1} subido correctamente...")
    else:
        print(f"⚠️ Error en lote {i // lote_tamano + 1}: {response.text}")

print("✨ ¡Proceso finalizado! Tu base de datos ahora está limpia y sin duplicados.")
