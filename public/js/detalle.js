/* Cellzone — detalle de producto para el borrador local; sin tasas inventadas. */
const SUPABASE_URL = 'https://otnjxfzttdjihjcoximm.supabase.co';
const SUPABASE_KEY = 'sb_publishable_ifoJPoL74pGM2B4cBxSLwg_7OrOGYy5';
const NUMERO_WHATSAPP = '595995677862';
const IMAGEN_SIN_FOTO = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300"%3E%3Crect width="300" height="300" fill="%23e2e8f0"/%3E%3Ctext x="150" y="155" text-anchor="middle" fill="%2364748b" font-family="sans-serif" font-size="18"%3ESin imagen%3C/text%3E%3C/svg%3E';
let moneda = 'USD';
try { if (localStorage.getItem('cellzone_moneda') === 'ARS') moneda = 'ARS'; } catch (_) { /* Usar USD durante la sesión. */ }

function crear(etiqueta, clases = '', texto) {
    const el = document.createElement(etiqueta);
    if (clases) el.className = clases;
    if (texto !== undefined && texto !== null) el.textContent = String(texto);
    return el;
}

function numeroPrecio(valor) {
    if (valor === null || valor === undefined || valor === '') return null;
    const numero = Number(valor);
    if (!Number.isFinite(numero) || numero <= 0) return null;
    const centavos = Math.round((numero + Number.EPSILON * Math.abs(numero)) * 100);
    return Number.isSafeInteger(centavos) && centavos > 0 ? centavos / 100 : null;
}

function primero(...valores) {
    for (const valor of valores) {
        const n = numeroPrecio(valor);
        if (n !== null) return n;
    }
    return null;
}

function formatear(valor, unidad) {
    if (valor === null) return `${unidad}: consultar`;
    return `${unidad} ${new Intl.NumberFormat('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(valor)}`;
}

function imagenSegura(valor) {
    if (typeof valor !== 'string' || !valor.trim()) return IMAGEN_SIN_FOTO;
    try {
        const url = new URL(valor, window.location.origin);
        return url.protocol === 'https:' || url.protocol === 'http:' ? url.href : IMAGEN_SIN_FOTO;
    } catch (_) { return IMAGEN_SIN_FOTO; }
}

function mostrarAviso(texto) {
    document.getElementById('app').replaceChildren(crear('div', 'loading', texto));
}

function mostrarDetalle(p) {
    const nombre = String(p.nombre || 'Sin nombre');
    const precios = {
        USD: primero(p.precio_usd, p.precioUSD, p.precio),
        ARS: primero(p.precio_ars, p.precioARS)
    };
    const layout = crear('div', 'detalle-container');
    const foto = crear('div', 'detalle-imagen');
    const imagen = crear('img');
    imagen.src = imagenSegura(p.imagen);
    imagen.alt = nombre;
    imagen.addEventListener('error', () => { imagen.src = IMAGEN_SIN_FOTO; }, { once: true });
    foto.append(imagen);
    const info = crear('div', 'detalle-info');
    const datos = crear('div');
    datos.append(crear('span', 'categoria-tag', p.categoria || 'General'));
    datos.append(crear('h1', 'titulo', nombre));
    datos.append(crear('div', 'precio', formatear(precios.USD, 'USD')));
    datos.append(crear('div', 'precio-secundario', formatear(precios.ARS, 'ARS')));
    const selector = crear('div', 'monedas');
    selector.append(crear('span', '', 'Moneda para la consulta:'));
    const botones = {};
    for (const unidad of ['USD', 'ARS']) {
        const boton = crear('button', 'moneda-btn', unidad);
        boton.type = 'button';
        boton.addEventListener('click', () => {
            moneda = unidad;
            try { localStorage.setItem('cellzone_moneda', moneda); } catch (_) { /* Sin persistencia. */ }
            actualizarBotones();
        });
        botones[unidad] = boton;
        selector.append(boton);
    }
    function actualizarBotones() {
        for (const unidad of ['USD', 'ARS']) {
            botones[unidad].classList.toggle('moneda-activa', moneda === unidad);
            botones[unidad].setAttribute('aria-pressed', String(moneda === unidad));
        }
    }
    actualizarBotones();
    datos.append(selector);
    const descripcion = crear('div', 'descripcion');
    descripcion.append(crear('strong', '', 'Descripción:'));
    descripcion.append(document.createElement('br'));
    descripcion.append(document.createTextNode(String(p.descripcion || 'Sin descripción disponible para este producto.')));
    const comprar = crear('button', 'btn-comprar', 'Consultar / Pedir por WhatsApp 📱');
    comprar.type = 'button';
    comprar.addEventListener('click', () => {
        const nombreMensaje = nombre.replace(/\s+/g, ' ').trim().slice(0, 300) || 'Producto';
        const mensaje = `¡Hola! Me interesa este producto:\n\n*${nombreMensaje}*\nPrecio: ${formatear(precios[moneda], moneda)}\n\n¿Tienen stock disponible?`;
        window.open(`https://wa.me/${NUMERO_WHATSAPP}?text=${encodeURIComponent(mensaje)}`, '_blank', 'noopener,noreferrer');
    });
    info.append(datos, descripcion, comprar);
    layout.append(foto, info);
    document.getElementById('app').replaceChildren(layout);
}

async function cargarDetalle() {
    const id = new URLSearchParams(window.location.search).get('id');
    if (!id) { mostrarAviso('Producto no encontrado.'); return; }
    try {
        const url = new URL(`${SUPABASE_URL}/rest/v1/productos`);
        url.searchParams.set('id', `eq.${id}`);
        url.searchParams.set('select', '*');
        const respuesta = await fetch(url, {
            headers: { apikey: SUPABASE_KEY }
        });
        if (!respuesta.ok) throw new Error(`Respuesta ${respuesta.status}`);
        const datos = await respuesta.json();
        if (!Array.isArray(datos)) throw new Error('Respuesta de producto inválida.');
        if (!datos.length) { mostrarAviso('El producto no existe.'); return; }
        mostrarDetalle(datos[0]);
    } catch (error) {
        console.error('No se pudo cargar el detalle.', error);
        mostrarAviso('Error al cargar el producto. Intentá nuevamente.');
    }
}

cargarDetalle();
