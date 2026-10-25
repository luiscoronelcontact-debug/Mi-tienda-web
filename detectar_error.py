import re, os

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extraemos todo el código JavaScript de tu página
scripts = re.findall(r'<script.*?>(.*?)</script>', content, re.DOTALL | re.IGNORECASE)

with open('prueba.js', 'w', encoding='utf-8') as f:
    for i, s in enumerate(scripts):
        f.write(f"// --- SCRIPT {i+1} ---\n")
        f.write(s + '\n')

print("Buscando errores de sintaxis en tu JavaScript...")
os.system('node -c prueba.js')
