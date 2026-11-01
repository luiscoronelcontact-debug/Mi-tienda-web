with open("js/store.js", "r", encoding="utf-8") as f:
    codigo = f.read()

# 1. Asegurar que la función de doble precio esté presente
funcion_doble = """
function formatearAmbosPrecios(p) {
    const usd = parseFloat(p.precio_usd || p.precio || 0);
    const ars = parseFloat(p.precio_ars || (usd * 1200));
    return `<div class="flex flex-col">
        <span class="text-neon-green font-extrabold text-base sm:text-lg">$${usd.toFixed(2)} USD</span>
        <span class="text-gray-400 text-xs font-semibold">$${Math.round(ars).toLocaleString('es-AR')} ARS</span>
    </div>`;
}
"""

if "function formatearAmbosPrecios" not in codigo:
    codigo += "\n" + funcion_doble

# 2. Reemplazar las etiquetas de precio único en las tarjetas de productos y modales
codigo = codigo.replace(
    '<div class="font-extrabold text-base sm:text-lg text-neon-green">$${p.precio.toFixed(2)}</div>',
    '${formatearAmbosPrecios(p)}'
);

codigo = codigo.replace(
    '<div class="text-2xl font-extrabold text-neon-green mt-2">$${p.precio.toFixed(2)}</div>',
    '${formatearAmbosPrecios(p)}'
);

with open("js/store.js", "w", encoding="utf-8") as f:
    f.write(codigo)

print("✅ ¡js/store.js actualizado para renderizar ambos precios!")
