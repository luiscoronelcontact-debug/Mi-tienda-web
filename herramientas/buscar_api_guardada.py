import glob

print("🔍 Buscando rastros de la API o URLs y guardando en 'resultados_api.txt'...")
with open('resultados_api.txt', 'w', encoding='utf-8') as out:
    for archivo in glob.glob('*.py') + glob.glob('*.js') + glob.glob('js/*.js'):
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                for linea in f:
                    if any(k in linea.lower() for k in ['api', 'url', 'http', 'neoimport', 'fetch']):
                        out.write(f"[{archivo}] {linea.strip()}\n")
        except Exception:
            pass
print("✨ ¡Listo! Los resultados se guardaron en 'resultados_api.txt'.")
