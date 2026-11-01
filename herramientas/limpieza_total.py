import re

# 1. Limpiar index.html (quitar el texto de Servidor Supabase Activo)
with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Reemplazar o limpiar cualquier mención al servidor activo en el HTML
html = re.sub(r'<[^>]*>[^<]*Servidor Supabase Activo[^<]*</[^>]*>', '', html, flags=re.IGNORECASE)
html = html.replace('Servidor Supabase Activo', '')

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

# 2. Corregir js/store.js para mostrar ambos precios limpios y sin símbolos duplicados
with open("js/store.js", "r", encoding="utf-8") as f:
    js = f.read()

# Definir la función de doble precio limpia
funcion_limpia = """
function formatearAmbosPrecios(p) {
    const usd = parseFloat(p.precio_usd || p.precio || 0);
    const ars = parseFloat(p.precio_ars || (usd * 1200));
    return `<div class="flex flex-col leading-tight">
        <span class="text-neon-green font-extrabold text-base sm:text-lg">$${usd.toFixed(2)} USD</span>
        <span class="text-gray-400 text-xs font-semibold">$${Math.round(ars).toLocaleString('es-AR')} ARS</span>
    </div>`;
}
"""

if "function formatearAmbosPrecios" in js:
    js = re.sub(r'function formatearAmbosPrecios\(p\) \{[\s\S]*?\n\}', funcion_limpia.strip(), js)
else:
    js += "\n" + funcion_limpia

# Reemplazar cualquier formato viejo de precios por la función de ambos precios limpia
js = re.sub(r'\$\s*\$\{[^}]+\}', '${formatearAmbosPrecios(p)}', js)
js = re.sub(r'\$\s*\{formatearPrecio\(p\)\}', '${formatearAmbosPrecios(p)}', js)
js = re.sub(r'<div class="font-extrabold[^"]*text-neon-green"[^>]*>[\s\S]*?</div>', '<div class="font-extrabold text-base sm:text-lg text-neon-green">${formatearAmbosPrecios(p)}</div>', js)

with open("js/store.js", "w", encoding="utf-8") as f:
    f.write(js)

print("✅ ¡Limpieza y corrección aplicada con éxito!")
