with open("js/store.js", "r", encoding="utf-8") as f:
    lineas = f.readlines()

print("🔍 Líneas que contienen 'precio' en js/store.js:")
for i, l in enumerate(lineas):
    if "precio" in l.lower() or "usd" in l.lower():
        print(f"Línea {i+1}: {l.strip()}")
