with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Agregar el número de WhatsApp a los enlaces de wa.me
content = content.replace('wa.me/?text=', 'wa.me/595995677862?text=')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("¡Número de WhatsApp configurado con éxito!")
