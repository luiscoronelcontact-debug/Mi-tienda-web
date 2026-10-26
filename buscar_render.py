with open("js/store.js", "r", encoding="utf-8") as f:
    lineas = f.readlines()

print("🔍 Buscando funciones de renderizado en js/store.js:")
for i, linea in enumerate(lineas):
    if "function render" in linea or "precio" in linea.lower() or "card" in linea.lower():
        print(f"Línea {i+1}: {linea.strip()}")
