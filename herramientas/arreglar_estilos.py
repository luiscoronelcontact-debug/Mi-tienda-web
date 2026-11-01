with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Asegurar que Tailwind CSS esté en el <head>
tailwind_cdn = '<script src="https://cdn.tailwindcss.com"></script>'
if 'tailwindcss.com' not in html:
    html = html.replace('<head>', f'<head>\n    {tailwind_cdn}')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("¡Tailwind CDN restaurado con éxito!")
