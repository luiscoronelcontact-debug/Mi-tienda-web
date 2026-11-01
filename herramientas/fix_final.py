import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Quitar el onclick erróneo del contenedor de los botones de sesión y carrito (que causaba el "rebote")
content = re.sub(
    r'<div\s+onclick="irAInicio\(\)"\s+class="flex items-center gap-3">\s*<div id="authContainer">', 
    '<div class="flex items-center gap-3">\n                <div id="authContainer">', 
    content
)

# 2. Asegurarnos de que el logo real (CELLZONE) tenga el evento correcto
idx_cell = content.find('CELL<span class="text-neon-green">ZONE</span>')
if idx_cell != -1:
    idx_a = content.rfind('<a ', 0, idx_cell)
    if idx_a != -1:
        idx_a_end = content.find('>', idx_a)
        a_tag = content[idx_a:idx_a_end+1]
        
        new_a_tag = a_tag
        if 'onclick' not in new_a_tag:
            new_a_tag = new_a_tag.replace('<a ', '<a onclick="irAInicio(); return false;" ')
        
        # Prevenir que el logo intente recargar la página entera en Vercel
        new_a_tag = re.sub(r'href="[^"]*"', 'href="#"', new_a_tag)
        
        content = content[:idx_a] + new_a_tag + content[idx_a_end+1:]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("¡Contenedor limpiado y logo reparado con éxito!")
