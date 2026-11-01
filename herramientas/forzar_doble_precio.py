import re

with open("js/store.js", "r", encoding="utf-8") as f:
    codigo = f.read()

# Definir la función de doble precio
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

# Reemplazar cualquier patrón de impresión de precio de producto en las tarjetas o modales
codigo = re.sub(r'\$\{p\.precio[^}]*\}', '${formatearAmbosPrecios(p)}', codigo)

with open("js/store.js", "w", encoding="utf-8") as f:
    f.write(codigo)

print("✅ ¡js/store.js actualizado correctamente!")
