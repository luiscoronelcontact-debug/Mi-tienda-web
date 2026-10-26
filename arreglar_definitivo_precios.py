import re

with open("js/store.js", "r", encoding="utf-8") as f:
    codigo = f.read()

# 1. Definir correctamente la función que genera ambos precios con HTML limpio
funcion_ideal = """
function formatearAmbosPrecios(p) {
    const usd = parseFloat(p.precio_usd || p.precio || 0);
    const ars = parseFloat(p.precio_ars || (usd * 1200));
    return `<div class="flex flex-col leading-tight">
        <span class="text-neon-green font-extrabold text-base sm:text-lg">$${usd.toFixed(2)} USD</span>
        <span class="text-gray-400 text-xs font-semibold">$${Math.round(ars).toLocaleString('es-AR')} ARS</span>
    </div>`;
}
"""

# Actualizar o insertar la función
if "function formatearAmbosPrecios" in codigo:
    codigo = re.sub(r'function formatearAmbosPrecios\(p\) \{[\s\S]*?\n\}', funcion_ideal.strip(), codigo)
else:
    codigo += "\n" + funcion_ideal

# 2. Limpiar cualquier formato viejo de precios en las tarjetas y modales
# Reemplazamos cualquier variante de formatearPrecio o etiquetas duplicadas por la nueva función
codigo = re.sub(r'\$\s*\$\{\s*formatear(?:Precio|AmbosPrecios)\(p\)\s*\}', '${formatearAmbosPrecios(p)}', codigo)
codigo = re.sub(r'\$\s*\{\s*formatearPrecio\(p\)\s*\}', '${formatearAmbosPrecios(p)}', codigo)

# Asegurar que los divs de precios en el renderizado usen ${formatearAmbosPrecios(p)} directamente sin un $ adelante
codigo = re.sub(r'\$+\s*\$\{p\.precio[^}]*\}', '${formatearAmbosPrecios(p)}', codigo)

with open("js/store.js", "w", encoding="utf-8") as f:
    f.write(codigo)

print("✅ ¡Archivo js/store.js corregido de forma definitiva!")
