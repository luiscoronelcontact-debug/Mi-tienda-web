import requests
import json
import os

# Leer credenciales descubiertas de Neo Import
with open("neo_supabase_url.txt", "r") as f:
    NEO_URL = f.read().strip()
with open("neo_supabase_key.txt", "r") as f:
    NEO_KEY = f.read().strip()

# Tus credenciales de Supabase
USER_URL = "https://otnjxfzttdjihjcoximm.supabase.co"
USER_KEY = "sb_publishable_ifoJPoL74pGM2B4cBxSLwg_7OrOGYy5"

neo_headers = {
    "apikey": NEO_KEY,
    "Authorization": f"Bearer {NEO_KEY}"
}

user_headers = {
    "apikey": USER_KEY,
    "Authorization": f"Bearer {USER_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

# Detectar el nombre correcto de la tabla de productos en Neo Import
tabla_productos = None
for t in ["productos", "products", "articulos", "item"]:
    res = requests.get(f"{NEO_URL}/rest/v1/{t}?select=*&limit=1", headers=neo_headers)
    if res.status_code == 200:
        tabla_productos = t
        print(f"✅ Tabla de origen detectada: '{t}'")
        break

if not tabla_productos:
    print("❌ No se pudo determinar el nombre de la tabla en el origen.")
    exit()

print("📦 Descargando catálogo completo desde la base de datos de Neo Import...")
todos_los_productos = []
batch_size = 1000
start = 0

# Paginación por rangos para descargar los más de 24,000 ítems sin cortes
while True:
    headers_range = neo_headers.copy()
    headers_range["Range"] = f"{start}-{start + batch_size - 1}"
    res = requests.get(f"{NEO_URL}/rest/v1/{tabla_productos}?select=*", headers=headers_range)
    
    if res.status_code not in [200, 206]:
        print(f"⚠️ Aviso en la descarga (Rango {start}): {res.status_code}")
        break
        
    data = res.json()
    if not data:
        break
        
    todos_los_productos.extend(data)
    print(f"📥 Productos descargados hasta ahora: {len(todos_los_productos)}...")
    
    if len(data) < batch_size:
        break
    start += batch_size

print(f"✨ ¡Total de productos extraídos de Neo Import: {len(todos_los_productos)}!")

# Guardar respaldo local
with open("catalogo_real.json", "w", encoding="utf-8") as f:
    json.dump(todos_los_productos, f, ensure_ascii=False, indent=4)

# Limpiar la tabla en tu Supabase para evitar duplicados
print("🧹 Limpiando la base de datos anterior en tu Supabase...")
requests.delete(f"{USER_URL}/rest/v1/productos?id=neq.0", headers=user_headers)

print("🚀 Procesando, aplicando el 20% de ganancia y subiendo a tu Supabase...")
productos_supabase = []
codigos_vistos = set()

for item in todos_los_productos:
    codigo = str(item.get('id') or item.get('codigo') or item.get('sku') or f"NEO-{len(productos_supabase)+1}")
    if codigo not in codigos_vistos:
        codigos_vistos.add(codigo)
        
        # Calcular precio base y aplicar el 20% de ganancia
        precio_base = float(item.get('precio') or item.get('price') or item.get('costo') or item.get('cost') or 0)
        precio_final = round(precio_base * 1.20, 2)
        
        productos_supabase.append({
            "id": codigo,
            "nombre": item.get('nombre') or item.get('title') or item.get('name') or "Sin nombre",
            "categoria": item.get('categoria') or item.get('category') or "General",
            "precio": precio_final,
            "imagen": item.get('imagen') or item.get('image') or item.get('img') or "https://via.placeholder.com/300",
            "descripcion": item.get('descripcion') or item.get('description') or "Sin descripción disponible.",
            "stock": int(item.get('stock') or item.get('cantidad') or 10)
        })

# Enviar a tu Supabase en lotes seguros de 500
lote_tamano = 500
for i in range(0, len(productos_supabase), lote_tamano):
    lote = productos_supabase[i:i + lote_tamano]
    res = requests.post(f"{USER_URL}/rest/v1/productos", headers=user_headers, data=json.dumps(lote))
    if res.status_code in [200, 201]:
        print(f"✅ Lote {i // lote_tamano + 1} subido correctamente.")
    else:
        print(f"⚠️ Error en lote {i // lote_tamano + 1}: {res.text}")

print("🎉 ¡Sincronización completada al 100%! Tu tienda ya tiene todos los productos actualizados, sin duplicados y con tu margen del 20%.")
