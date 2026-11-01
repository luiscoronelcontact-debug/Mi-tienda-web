import json

with open("catalogo_real.json", "r", encoding="utf-8") as f:
    datos = json.load(f)

if datos:
    print("🔍 Claves disponibles en el primer producto:")
    print(list(datos[0].keys()))
    print("\n📦 Datos del primer producto:")
    print(json.dumps(datos[0], indent=2, ensure_ascii=False))
