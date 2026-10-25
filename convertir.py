import json

print("Leyendo el catálogo real...")
with open('catalogo_real.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

productos_limpios = []
for i, p in enumerate(data):
    # Filtramos solo los que estén activos y tengan imagen válida
    if p.get('estado') == 'Activo' and p.get('imagen'):
        # Aplicamos el 20% de ganancia (multiplicando por 1.20) y redondeamos a 2 decimales
        precio_usd = round(float(p.get('precio_usd', 0)) * 1.20, 2)
        precio_ars = round(float(p.get('precio_ars', 0)) * 1.20, 2)

        productos_limpios.append({
            "id": i + 1,
            "nombre": p.get('nombre', 'Sin nombre'),
            "categoria": p.get('categoria', 'General'),
            "precioUSD": precio_usd,
            "precioARS": precio_ars,
            "imagen": p.get('imagen'),
            "descripcion": p.get('descripcion', ''),
            "destacado": p.get('destacado', False)
        })

# Generamos un archivo de JavaScript limpio
js_contenido = f"const productos = {json.dumps(productos_limpios, indent=4, ensure_ascii=False)};"

with open('productos.js', 'w', encoding='utf-8') as f:
    f.write(js_contenido)

print(f"\n¡Éxito total! Se procesaron {len(productos_limpios)} productos con el 20% de ganancia aplicada y se guardaron en 'productos.js'.")
