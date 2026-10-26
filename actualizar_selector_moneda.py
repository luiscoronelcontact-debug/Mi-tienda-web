import re

with open("js/store.js", "r", encoding="utf-8") as f:
    codigo = f.read()

# 1. Agregar variables globales de moneda si no están
if "let monedaActual" not in codigo:
    codigo = codigo.replace(
        "let carrito = [];",
        "let carrito = [];\nlet monedaActual = localStorage.getItem('cellzone_moneda') || 'USD';\nlet _ultimosProductos = [];"
    )

# 2. Agregar funciones de formateo y cambio de moneda al final o antes de renderizar
funciones_moneda = """
function cambiarMoneda(nuevaMoneda) {
    monedaActual = nuevaMoneda;
    localStorage.setItem('cellzone_moneda', monedaActual);
    
    // Actualizar estilo visual de los botones del selector
    const btnUsd = document.getElementById('btn-usd');
    const btnArs = document.getElementById('btn-ars');
    if (btnUsd && btnArs) {
        if (monedaActual === 'USD') {
            btnUsd.className = "px-2.5 py-1 rounded-lg text-xs font-extrabold bg-neon-green text-black transition-all";
            btnArs.className = "px-2.5 py-1 rounded-lg text-xs font-extrabold text-gray-400 hover:text-white transition-all";
        } else {
            btnArs.className = "px-2.5 py-1 rounded-lg text-xs font-extrabold bg-neon-green text-black transition-all";
            btnUsd.className = "px-2.5 py-1 rounded-lg text-xs font-extrabold text-gray-400 hover:text-white transition-all";
        }
    }

    if (typeof _ultimosProductos !== 'undefined' && _ultimosProductos.length > 0) {
        renderizarProductos(_ultimosProductos);
    }
}

function formatearPrecio(p) {
    const usd = parseFloat(p.precio_usd || p.precio || 0);
    const ars = parseFloat(p.precio_ars || (usd * 1100)); // fallback estimado si faltara ars
    if (monedaActual === 'ARS') {
        return `$${Math.round(ars).toLocaleString('es-AR')} ARS`;
    } else {
        return `$${usd.toFixed(2)} USD`;
    }
}

function obtenerPrecioNum(p) {
    const usd = parseFloat(p.precio_usd || p.precio || 0);
    const ars = parseFloat(p.precio_ars || (usd * 1100));
    return monedaActual === 'ARS' ? ars : usd;
}
"""

if "function cambiarMoneda" not in codigo:
    codigo += "\n" + funciones_moneda

# 3. Guardar una copia de los productos cuando se carguen/rendericen
codigo = codigo.replace(
    "function renderizarProductos(productos) {",
    "function renderizarProductos(productos) {\n    window._ultimosProductos = productos;"
)

# 4. Reemplazar la visualización de precios fijos por la función dinámica
# Reemplazar $${p.precio.toFixed(2)} en las cards e interfaz
codigo = re.sub(r'\$\{p\.precio\.toFixed\(2\)\}', '${formatearPrecio(p)}', codigo)

with open("js/store.js", "w", encoding="utf-8") as f:
    f.write(codigo)

print("✅ ¡Archivo js/store.js actualizado con soporte para USD y ARS!")
