import re

with open('index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Buscar bloques <script> internos (que no sean enlaces externos con src)
scripts = re.findall(r'<script\b[^>]*>(.*?)</script>', html_content, re.DOTALL)

if scripts:
    # Unir el código JavaScript encontrado
    js_content = "\n\n".join([s.strip() for s in scripts if s.strip()])
    
    with open('js/store.js', 'w', encoding='utf-8') as f_js:
        f_js.write(js_content)
    
    # Eliminar los bloques <script> internos del index.html
    new_html = re.sub(r'<script\b[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
    
    # Agregar la llamada al nuevo archivo js/store.js justo antes de cerrar el </body>
    script_tag = '  <script src="js/store.js"></script>\n</body>'
    if '</body>' in new_html:
        new_html = new_html.replace('</body>', script_tag)
    else:
        new_html += '\n<script src="js/store.js"></script>'
        
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_html)
        
    print("¡Lógica de JavaScript extraída a js/store.js y enlazada con éxito!")
else:
    print("No se encontraron bloques de script internos.")
