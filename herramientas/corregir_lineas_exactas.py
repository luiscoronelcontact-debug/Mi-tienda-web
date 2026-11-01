with open("js/store.js", "r", encoding="utf-8") as f:
    codigo = f.read()

# Reemplazar las líneas exactas que tienen el problema del doble dólar y función vieja
codigo = codigo.replace(
    '<div class="font-extrabold text-base sm:text-lg text-neon-green">$${formatearPrecio(p)}</div>',
    '${formatearAmbosPrecios(p)}'
)
codigo = codigo.replace(
    '<div class="text-2xl font-extrabold text-neon-green mt-2">$${formatearPrecio(p)}</div>',
    '${formatearAmbosPrecios(p)}'
)

# Por si acaso quedaron con formatearAmbosPrecios pero con el $ sobrante
codigo = codigo.replace(
    '<div class="font-extrabold text-base sm:text-lg text-neon-green">$${formatearAmbosPrecios(p)}</div>',
    '${formatearAmbosPrecios(p)}'
)
codigo = codigo.replace(
    '<div class="text-2xl font-extrabold text-neon-green mt-2">$${formatearAmbosPrecios(p)}</div>',
    '${formatearAmbosPrecios(p)}'
)

with open("js/store.js", "w", encoding="utf-8") as f:
    f.write(codigo)

print("✅ ¡Líneas corregidas con éxito!")
