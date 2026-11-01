import re

with open("js/store.js", "r", encoding="utf-8") as f:
    codigo = f.read()

# 1. Definir la función de doble precio de forma limpia
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

if "function formatearAmbosPrecios" in codigo:
    codigo = re.sub(r'function formatearAmbosPrecios\(p\) \{[\s\S]*?\n\}', funcion_doble.strip(), codigo)
else:
    codigo += "\n" + funcion_doble

# 2. Corregir las etiquetas de precio en las tarjetas y modales (quitando el $ sobrante)
codigo = codigo.replace('$${formatearPrecio(p)}', '${formatearAmbosPrecios(p)}')
codigo = codigo.replace('$${formatearAmbosPrecios(p)}', '${formatearAmbosPrecios(p)}')
codigo = codigo.replace('${formatearPrecio(p)}', '${formatearAmbosPrecios(p)}')

# 3. Corregir el botón de WhatsApp para que reciba el precio numérico correctamente
codigo = re.sub(
    r'comprarItemWhatsApp\(([^,]+),\s*\$\{formatearAmbosPrecios\(p\)\}\)', 
    r'comprarItemWhatsApp(\1, p.precio_usd || p.precio || 0)', 
    codigo
)

with open("js/store.js", "w", encoding="utf-8") as f:
    f.write(codigo)

print("✅ ¡Corrección aplicada con éxito en js/store.js!")
