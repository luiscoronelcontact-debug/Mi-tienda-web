with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

supabase_cdn = '<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>'

# Agregar el CDN de Supabase antes del script de la tienda si no está presente
if 'supabase-js' not in html:
    html = html.replace('<script src="js/store.js"></script>', f'{supabase_cdn}\n    <script src="js/store.js"></script>')
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("¡Librería de Supabase agregada con éxito!")
else:
    print("La librería de Supabase ya estaba incluida.")
