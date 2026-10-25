import json

try:
    with open('catalogo_real.json', 'r', encoding='utf-8') as f:
        productos = json.load(f)
        
    if productos:
        print("🔍 ¡Columnas (claves) encontradas en la base de datos de Neo Import:")
        print(list(productos[0].keys()))
        
        print("\n📦 Ejemplo del primer producto en bruto:")
        print(json.dumps(productos[0], indent=2, ensure_ascii=False))
    else:
        print("El archivo JSON está vacío.")
except Exception as e:
    print(f"Error al leer el archivo: {e}")
