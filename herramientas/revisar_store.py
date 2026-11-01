import os

if os.path.exists("js/store.js"):
    with open("js/store.js", "r", encoding="utf-8") as f:
        contenido = f.read()
        print("📄 Contenido parcial de js/store.js:")
        print(contenido[:1500])
else:
    print("⚠️ No se encontró el archivo js/store.js en esta ruta.")
