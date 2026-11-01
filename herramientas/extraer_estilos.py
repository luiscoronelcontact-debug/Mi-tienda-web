import re

with open('index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Buscar contenido entre etiquetas <style>
style_match = re.search(r'<style>(.*?)</style>', html_content, re.DOTALL)

if style_match:
    css_content = style_match.group(1)
    # Guardar en el nuevo archivo CSS
    with open('css/styles.css', 'w', encoding='utf-8') as f_css:
        f_css.write(css_content.strip())
    
    # Reemplazar el bloque <style> en el index.html por el enlace externo
    new_html = re.sub(r'<style>.*?</style>', '<link rel="stylesheet" href="css/styles.css">', html_content, flags=re.DOTALL)
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_html)
    
    print("¡Estilos extraídos a css/styles.css y enlace agregado a index.html con éxito!")
else:
    print("No se encontró un bloque <style> en el index.html (quizás ya estaba limpio).")
