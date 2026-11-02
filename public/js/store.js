/* Cellzone — borrador local para revisión. No publicar sin pruebas adicionales. */
if (window.tailwind) {
    window.tailwind.config = {
        darkMode: 'class',
        theme: {
            extend: {
                colors: {
                    'neon-green': '#00FF66',
                    'dark-bg': '#050508',
                    'card-bg': '#0f131f',
                    'card-border': '#1a2235'
                }
            }
        }
    };
}

const SUPABASE_URL = 'https://otnjxfzttdjihjcoximm.supabase.co';
// Esta es una clave publicable, no una clave de servicio. La seguridad depende de RLS.
const SUPABASE_KEY = 'sb_publishable_ifoJPoL74pGM2B4cBxSLwg_7OrOGYy5';
const NUMERO_WHATSAPP = '595995677862';
const IMAGEN_SIN_FOTO = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300"%3E%3Crect width="300" height="300" fill="%230f131f"/%3E%3Cpath d="M80 190l45-50 30 30 20-20 45 40" fill="none" stroke="%234b5563" stroke-width="8"/%3E%3Ccircle cx="105" cy="100" r="14" fill="%234b5563"/%3E%3Ctext x="150" y="240" text-anchor="middle" fill="%239ca3af" font-family="sans-serif" font-size="18"%3ESin imagen%3C/text%3E%3C/svg%3E';

const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);
let carrito = [];
let monedaActual = obtenerGuardado('cellzone_moneda') === 'ARS' ? 'ARS' : 'USD';
let favoritos = leerFavoritos();
let categoriaActual = 'TODOS';
let timeoutBusqueda = null;
let timeoutToast = null;
let consultaActual = 0;
let todosLosResultadosActuales = [];
let productosVisibles = [];
let yaCargaronProductos = false;
let productoModalAbierto = null;

function obtenerGuardado(clave) {
    try { return localStorage.getItem(clave); } catch (_) { return null; }
}

function guardarLocal(clave, valor) {
    try { localStorage.setItem(clave, valor); } catch (_) { /* Se conserva durante la sesión. */ }
}

function leerFavoritos() {
    try {
        const valor = JSON.parse(obtenerGuardado('cellzone_favs') || '[]');
        return Array.isArray(valor) ? [...new Set(valor.map(String))] : [];
    } catch (_) {
        return [];
    }
}

function crearElemento(etiqueta, clases = '', texto) {
    const elemento = document.createElement(etiqueta);
    if (clases) elemento.className = clases;
    if (texto !== undefined && texto !== null) elemento.textContent = String(texto);
    return elemento;
}

function crearIcono(nombre, clases = '') {
    return crearElemento('span', `material-symbols-outlined ${clases}`.trim(), nombre);
}

// Se aceptan solo URLs web. Nunca se usa como HTML o como manejador de eventos.
function urlImagenSegura(valor) {
    if (typeof valor !== 'string' || !valor.trim()) return null;
    try {
        const url = new URL(valor, window.location.origin);
        return (url.protocol === 'https:' || url.protocol === 'http:') ? url.href : null;
    } catch (_) {
        return null;
    }
}

function crearImagen(valor, descripcion, clases) {
    const imagen = crearElemento('img', clases);
    imagen.alt = descripcion;
    imagen.loading = 'lazy';
    imagen.src = urlImagenSegura(valor) || IMAGEN_SIN_FOTO;
    imagen.addEventListener('error', () => {
        if (imagen.src !== IMAGEN_SIN_FOTO) imagen.src = IMAGEN_SIN_FOTO;
    }, { once: true });
    return imagen;
}

function numeroPrecio(valor) {
    if (valor === null || valor === undefined || valor === '') return null;
    const numero = Number(valor);
    if (!Number.isFinite(numero) || numero <= 0) return null;
    const centavos = Math.round((numero + Number.EPSILON * Math.abs(numero)) * 100);
    if (!Number.isSafeInteger(centavos) || centavos <= 0) return null;
    return centavos / 100;
}

function primerPrecioValido(...valores) {
    for (const valor of valores) {
        const numero = numeroPrecio(valor);
        if (numero !== null) return numero;
    }
    return null;
}

function normalizarProducto(p) {
    return {
        id: String(p.id),
        nombre: String(p.nombre || 'Sin nombre'),
        categoria: String(p.categoria || 'General'),
        // En los datos actuales, precio equivale a USD. No usar ARS como USD.
        precio_usd: primerPrecioValido(p.precio_usd, p.precioUSD, p.precio),
        precio_ars: primerPrecioValido(p.precio_ars, p.precioARS),
        imagen: typeof p.imagen === 'string' ? p.imagen : '',
        descripcion: String(p.descripcion || 'Sin descripción disponible.')
    };
}

function precioEnMoneda(producto, moneda = monedaActual) {
    return moneda === 'ARS' ? producto.precio_ars : producto.precio_usd;
}

function formatearMonto(valor, moneda) {
    if (valor === null || !Number.isFinite(valor)) return `${moneda}: consultar`;
    const numero = new Intl.NumberFormat('es-AR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(valor);
    return `${moneda} ${numero}`;
}

function crearBloquePrecios(producto) {
    const bloque = crearElemento('div', 'flex flex-col leading-tight gap-1');
    for (const moneda of ['USD', 'ARS']) {
        const activa = moneda === monedaActual;
        const clases = activa
            ? 'text-neon-green font-extrabold text-base sm:text-lg'
            : 'text-gray-400 text-xs font-semibold';
        bloque.append(crearElemento('span', clases, formatearMonto(precioEnMoneda(producto, moneda), moneda)));
    }
    return bloque;
}

function totalCarrito() {
    let centavos = 0;
    for (const item of carrito) {
        const precio = precioEnMoneda(item);
        if (precio === null || !Number.isSafeInteger(item.cantidad) || item.cantidad < 1) return null;
        const subtotal = Math.round(precio * 100) * item.cantidad;
        if (!Number.isSafeInteger(subtotal) || !Number.isSafeInteger(centavos + subtotal)) return null;
        centavos += subtotal;
    }
    return centavos / 100;
}

function nombreParaMensaje(nombre) {
    return String(nombre).replace(/\s+/g, ' ').trim().slice(0, 300) || 'Producto';
}

function abrirWhatsApp(mensaje) {
    const url = `https://wa.me/${NUMERO_WHATSAPP}?text=${encodeURIComponent(mensaje)}`;
    window.open(url, '_blank', 'noopener,noreferrer');
}

function showToast(titulo, subtitulo) {
    const toast = document.getElementById('toastNotification');
    if (!toast) return;
    document.getElementById('toastTitle').textContent = titulo;
    document.getElementById('toastSubtitle').textContent = subtitulo;
    toast.classList.remove('opacity-0', 'translate-y-24');
    clearTimeout(timeoutToast);
    timeoutToast = setTimeout(() => toast.classList.add('opacity-0', 'translate-y-24'), 3000);
}

async function cargarDatosIniciales() {
    actualizarContadorFavoritos();
    cambiarMoneda(monedaActual);
    supabaseClient.auth.onAuthStateChange(() => {
        // No consultar la sesión mientras el cliente de Auth tiene el bloqueo del evento.
        setTimeout(() => verificarSesionGoogle(), 0);
    });
    await verificarSesionGoogle();
    await consultarSupabase();
}

async function verificarSesionGoogle() {
    let session = null;
    try {
        const respuesta = await supabaseClient.auth.getSession();
        if (respuesta.error) throw respuesta.error;
        session = respuesta.data && respuesta.data.session;
    } catch (error) {
        console.error('No se pudo comprobar la sesión.', error);
    }

    const container = document.getElementById('authContainer');
    container.replaceChildren();
    if (session && session.user) {
        const user = session.user;
        const nombre = String(user.user_metadata?.full_name || user.email || 'Mi cuenta');
        const fila = crearElemento('div', 'flex items-center gap-1 sm:gap-2 bg-card-bg neon-border px-1.5 sm:px-3 py-1.5 rounded-xl');
        const perfil = crearElemento('button', 'flex items-center gap-1 text-[10px] text-neon-green hover:underline cursor-pointer font-bold bg-transparent border-none p-0');
        perfil.type = 'button';
        perfil.setAttribute('aria-label', 'Perfil');
        const avatar = urlImagenSegura(user.user_metadata?.avatar_url);
        if (avatar) perfil.append(crearImagen(avatar, 'Avatar', 'w-7 h-7 rounded-full object-cover border border-neon-green'));
        else perfil.append(crearIcono('account_circle', 'text-[22px] text-neon-green'));
        perfil.append(crearElemento('span', 'text-xs font-bold text-white hidden sm:inline max-w-[100px] truncate', nombre));
        perfil.append(crearElemento('span', 'hidden sm:inline', 'Perfil'));
        perfil.addEventListener('click', mostrarPerfil);
        const salir = crearElemento('button', 'flex items-center text-[10px] text-red-400 hover:underline cursor-pointer');
        salir.type = 'button';
        salir.setAttribute('aria-label', 'Cerrar sesión');
        salir.append(crearIcono('logout', 'text-[18px] sm:hidden'), crearElemento('span', 'hidden sm:inline', 'Salir'));
        salir.addEventListener('click', cerrarSesionGoogle);
        fila.append(perfil, salir);
        container.append(fila);
    } else {
        const boton = crearElemento('button', 'px-3.5 py-2 rounded-xl bg-card-bg neon-border hover:border-neon-green text-white text-xs font-bold transition-all flex items-center gap-2 cursor-pointer');
        boton.type = 'button';
        boton.setAttribute('aria-label', 'Ingresar con Google');
        boton.append(crearIcono('account_circle', 'text-[18px] text-neon-green'));
        boton.append(crearElemento('span', 'hidden sm:inline', 'Ingresar con Google'));
        boton.addEventListener('click', loginConGoogle);
        container.append(boton);
    }
}

async function loginConGoogle() {
    try {
        const { error } = await supabaseClient.auth.signInWithOAuth({
            provider: 'google',
            options: { redirectTo: window.location.origin }
        });
        if (error) throw error;
    } catch (error) {
        console.error('No se pudo iniciar sesión con Google.', error);
        showToast('No se pudo iniciar sesión', 'Intentá nuevamente.');
    }
}

async function cerrarSesionGoogle() {
    try {
        const { error } = await supabaseClient.auth.signOut();
        if (error) throw error;
        irAInicio();
        await verificarSesionGoogle();
    } catch (error) {
        console.error('No se pudo cerrar la sesión.', error);
        showToast('No se pudo cerrar la sesión', 'Intentá nuevamente.');
    }
}

function irAInicio() {
    const perfil = document.getElementById('vistaPerfil');
    const principal = document.querySelector('main');
    if (perfil) perfil.classList.add('hidden');
    if (principal) principal.style.display = '';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function mostrarPerfil() {
    try {
        const { data, error } = await supabaseClient.auth.getSession();
        if (error) throw error;
        const session = data && data.session;
        if (!session || !session.user) {
            showToast('Iniciá sesión', 'Necesitás ingresar para ver tu perfil.');
            return;
        }
        const user = session.user;
        const { data: perfil, error: errorPerfil } = await supabaseClient
            .from('profiles')
            .select('full_name, phone, province, city, address')
            .eq('id', user.id)
            .maybeSingle();
        if (errorPerfil) throw errorPerfil;

        const email = String(user.email || '');
        const nombre = String(perfil?.full_name || user.user_metadata?.full_name || email.split('@')[0] || 'Cliente');
        document.getElementById('perfilEmailTxt').textContent = email;
        document.getElementById('perfilNombreTxt').textContent = nombre;
        document.getElementById('profFullName').value = nombre;
        document.getElementById('profPhone').value = perfil?.phone || '';
        document.getElementById('profProvince').value = perfil?.province || '';
        document.getElementById('profCity').value = perfil?.city || '';
        document.getElementById('profAddress').value = perfil?.address || '';

        const avatar = urlImagenSegura(user.user_metadata?.avatar_url);
        const img = document.getElementById('perfilImgAvatar');
        const inicial = document.getElementById('perfilInitAvatar');
        if (avatar) {
            img.src = avatar;
            img.classList.remove('hidden');
            inicial.classList.add('hidden');
        } else {
            img.removeAttribute('src');
            img.classList.add('hidden');
            inicial.textContent = nombre.charAt(0).toUpperCase();
            inicial.classList.remove('hidden');
        }
        document.getElementById('seccionEditarPerfil').classList.add('hidden');
        document.querySelector('main').style.display = 'none';
        document.getElementById('vistaPerfil').classList.remove('hidden');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (error) {
        console.error('No se pudo cargar el perfil.', error);
        showToast('No se pudo cargar el perfil', 'Intentá nuevamente.');
    }
}

function cerrarPerfil() { irAInicio(); }

function toggleEditarPerfil() {
    document.getElementById('seccionEditarPerfil').classList.toggle('hidden');
}

async function guardarPerfil(event) {
    event.preventDefault();
    const boton = document.getElementById('btnGuardarPerfil');
    try {
        const { data, error } = await supabaseClient.auth.getSession();
        if (error) throw error;
        if (!data?.session?.user) {
            showToast('Iniciá sesión', 'Necesitás ingresar para guardar el perfil.');
            return;
        }
        const actualizacion = {
            id: data.session.user.id,
            full_name: document.getElementById('profFullName').value,
            phone: document.getElementById('profPhone').value,
            province: document.getElementById('profProvince').value,
            city: document.getElementById('profCity').value,
            address: document.getElementById('profAddress').value,
            updated_at: new Date().toISOString()
        };
        boton.disabled = true;
        boton.textContent = 'Guardando...';
        const resultado = await supabaseClient.from('profiles').upsert(actualizacion);
        if (resultado.error) throw resultado.error;
        document.getElementById('perfilNombreTxt').textContent = actualizacion.full_name;
        toggleEditarPerfil();
        showToast('Perfil actualizado', 'Tus datos se guardaron correctamente.');
    } catch (error) {
        console.error('No se pudo guardar el perfil.', error);
        showToast('No se pudo guardar el perfil', 'Intentá nuevamente.');
    } finally {
        boton.disabled = false;
        boton.textContent = 'Guardar cambios';
    }
}

function actualizarContadorFavoritos() {
    document.getElementById('favCountBadge').textContent = favoritos.length;
}

function toggleFavorito(id, event) {
    if (event) event.stopPropagation();
    id = String(id);
    const indice = favoritos.indexOf(id);
    if (indice >= 0) {
        favoritos.splice(indice, 1);
        showToast('Eliminado de favoritos', 'Producto removido de tu lista.');
    } else {
        favoritos.push(id);
        showToast('Añadido a favoritos', 'Guardado en tu lista personal.');
    }
    guardarLocal('cellzone_favs', JSON.stringify(favoritos));
    actualizarContadorFavoritos();
    if (categoriaActual === 'FAVORITOS') {
        consultarSupabase(document.getElementById('buscador').value, 'FAVORITOS');
    } else {
        renderizarProductos(productosVisibles);
    }
}

async function consultarSupabase(termino = '', categoria = 'TODOS') {
    const numeroConsulta = ++consultaActual;
    try {
        let datos;
        if (categoria === 'FAVORITOS') {
            if (!favoritos.length) {
                datos = [];
            } else {
                const { data, error } = await supabaseClient.from('productos').select('*').in('id', favoritos);
                if (error) throw error;
                datos = data || [];
            }
        } else {
            const url = new URL(`${SUPABASE_URL}/rest/v1/productos`);
            url.searchParams.set('select', '*');
            if (termino.trim()) url.searchParams.set('nombre', `ilike.*${termino.trim()}*`);
            if (categoria && categoria !== 'TODOS') url.searchParams.set('categoria', `eq.${categoria}`);
            url.searchParams.set('limit', '60');
            const response = await fetch(url, {
                headers: { apikey: SUPABASE_KEY }
            });
            if (!response.ok) throw new Error(`Respuesta ${response.status}`);
            datos = await response.json();
        }
        if (!Array.isArray(datos)) throw new Error('Respuesta de productos inválida.');
        if (numeroConsulta !== consultaActual) return;
        procesarYRenderizar(datos, termino, categoria);
    } catch (error) {
        if (numeroConsulta !== consultaActual) return;
        console.error('Error al consultar el catálogo.', error);
        todosLosResultadosActuales = [];
        productosVisibles = [];
        yaCargaronProductos = false;
        document.getElementById('productCounter').textContent = 'No se pudo cargar el catálogo';
        document.getElementById('productGrid').replaceChildren(
            crearElemento('div', 'col-span-full text-center py-10 text-red-400', 'No se pudo conectar con el catálogo. Intentá nuevamente.')
        );
    }
}

function procesarYRenderizar(datos, termino = '', categoria = categoriaActual) {
    todosLosResultadosActuales = datos
        .filter(p => p && p.id !== null && p.id !== undefined)
        .map(normalizarProducto);
    const busqueda = termino.trim().toLocaleLowerCase('es');
    productosVisibles = categoria === 'FAVORITOS' && busqueda
        ? todosLosResultadosActuales.filter(p => p.nombre.toLocaleLowerCase('es').includes(busqueda))
        : todosLosResultadosActuales;
    yaCargaronProductos = true;
    renderizarProductos(productosVisibles);
}

function buscarProductosServidor() {
    clearTimeout(timeoutBusqueda);
    const texto = document.getElementById('buscador').value;
    timeoutBusqueda = setTimeout(() => consultarSupabase(texto, categoriaActual), 300);
}

function filtrarCategoria(categoria, boton) {
    categoriaActual = categoria;
    document.querySelectorAll('.cat-pill').forEach(b => {
        b.className = 'cat-pill shrink-0 px-4 py-2.5 rounded-xl text-xs font-bold transition-all bg-card-bg text-gray-300 hover:text-white neon-border';
    });
    if (boton) boton.className = 'cat-pill shrink-0 px-4 py-2.5 rounded-xl text-xs font-bold transition-all bg-neon-green text-black shadow-sm';
    consultarSupabase(document.getElementById('buscador').value, categoriaActual);
}

function renderizarProductos(productos) {
    productosVisibles = productos;
    const grid = document.getElementById('productGrid');
    document.getElementById('productCounter').textContent = `Mostrando ${productos.length} resultados`;
    grid.replaceChildren();
    if (!productos.length) {
        grid.append(crearElemento('div', 'col-span-full text-center py-20 text-gray-500', 'No se encontraron productos en esta sección.'));
        return;
    }
    const fragmento = document.createDocumentFragment();
    for (const p of productos) {
        const articulo = crearElemento('article', 'product-card group flex flex-col justify-between bg-card-bg neon-border rounded-2xl p-3.5 sm:p-4 hover:border-neon-green transition-all duration-300 relative overflow-hidden cursor-pointer shadow-lg');
        articulo.tabIndex = 0;
        articulo.setAttribute('role', 'button');
        articulo.setAttribute('aria-label', `Ver detalles de ${p.nombre}`);
        articulo.addEventListener('click', () => openProductModal(p.id));
        articulo.addEventListener('keydown', event => {
            if (event.target === articulo && (event.key === 'Enter' || event.key === ' ')) {
                event.preventDefault();
                openProductModal(p.id);
            }
        });
        const superior = crearElemento('div');
        const marco = crearElemento('div', 'relative w-full aspect-square rounded-xl bg-black/40 overflow-hidden flex items-center justify-center p-3');
        const esFavorito = favoritos.includes(p.id);
        const colorFav = esFavorito ? 'text-red-500 fill-red-500' : 'text-gray-400 hover:text-red-400';
        const botonFav = crearElemento('button', `absolute top-2.5 right-2.5 z-10 p-2 rounded-full bg-black/60 backdrop-blur-md transition-all cursor-pointer ${colorFav}`);
        botonFav.type = 'button';
        botonFav.setAttribute('aria-label', esFavorito ? 'Quitar de favoritos' : 'Agregar a favoritos');
        botonFav.setAttribute('aria-pressed', String(esFavorito));
        botonFav.append(crearIcono('favorite', 'text-[20px]'));
        botonFav.addEventListener('click', event => toggleFavorito(p.id, event));
        marco.append(botonFav, crearImagen(p.imagen, p.nombre, 'w-full h-full object-contain group-hover:scale-105 transition-transform duration-300'));
        const info = crearElemento('div', 'mt-3.5 space-y-1');
        info.append(crearElemento('span', 'text-[10px] text-neon-green uppercase font-mono tracking-wider', p.categoria));
        info.append(crearElemento('h2', 'text-xs sm:text-sm font-bold text-white line-clamp-2 leading-snug', p.nombre));
        superior.append(marco, info);
        const inferior = crearElemento('div', 'mt-4 pt-3 border-t border-card-border space-y-3');
        inferior.append(crearBloquePrecios(p));
        const agregar = crearElemento('button', 'w-full py-2.5 px-3 rounded-xl bg-neon-green hover:brightness-110 text-black font-extrabold text-xs shadow-[0_0_10px_rgba(0,255,102,0.3)] transition-all flex items-center justify-center gap-1.5 cursor-pointer');
        agregar.type = 'button';
        agregar.append(crearIcono('add_shopping_cart', 'text-[16px]'), crearElemento('span', '', 'AGREGAR'));
        agregar.addEventListener('click', event => { event.stopPropagation(); agregarAlCarrito(p.id); });
        inferior.append(agregar);
        articulo.append(superior, inferior);
        fragmento.append(articulo);
    }
    grid.append(fragmento);
}

function openProductModal(id) {
    const producto = todosLosResultadosActuales.find(item => item.id === String(id));
    if (!producto) return;
    productoModalAbierto = producto.id;
    const container = document.getElementById('modalContentContainer');
    container.replaceChildren();
    const layout = crearElemento('div', 'grid grid-cols-1 md:grid-cols-2 gap-6');
    const marco = crearElemento('div', 'aspect-square bg-black/40 rounded-xl flex items-center justify-center p-4 neon-border');
    marco.append(crearImagen(producto.imagen, producto.nombre, 'max-h-full object-contain'));
    const info = crearElemento('div', 'flex flex-col justify-between space-y-4');
    const datos = crearElemento('div');
    datos.append(crearElemento('span', 'text-xs text-neon-green uppercase font-mono bg-neon-green/10 px-3 py-1 rounded-full border border-neon-green/30', producto.categoria));
    datos.append(crearElemento('h2', 'text-xl font-bold text-white mt-3', producto.nombre));
    const precios = crearElemento('div', 'text-2xl font-extrabold text-neon-green mt-2');
    precios.append(crearBloquePrecios(producto));
    datos.append(precios);
    datos.append(crearElemento('p', 'text-sm text-gray-300 mt-3 leading-relaxed bg-black/30 p-3.5 rounded-xl border border-card-border', producto.descripcion));
    const acciones = crearElemento('div', 'space-y-3');
    const agregar = crearElemento('button', 'w-full py-3.5 rounded-xl bg-card-border hover:bg-neon-green hover:text-black text-white font-bold transition-all cursor-pointer neon-border', 'Añadir al Carrito');
    agregar.type = 'button';
    agregar.addEventListener('click', () => { closeProductModal(); agregarAlCarrito(producto.id); });
    const whatsapp = crearElemento('button', 'w-full py-3.5 rounded-xl bg-neon-green text-black font-extrabold shadow-[0_0_15px_rgba(0,255,102,0.4)] hover:brightness-110 cursor-pointer flex items-center justify-center gap-2 transition-all');
    whatsapp.type = 'button';
    whatsapp.append(crearIcono('chat', 'text-[20px]'), crearElemento('span', '', 'Consultar por WhatsApp'));
    whatsapp.addEventListener('click', () => comprarItemWhatsApp(producto.id));
    acciones.append(agregar, whatsapp);
    info.append(datos, acciones);
    layout.append(marco, info);
    container.append(layout);
    const backdrop = document.getElementById('productModalBackdrop');
    backdrop.classList.remove('hidden');
    backdrop.classList.add('flex');
}

function closeProductModal() {
    productoModalAbierto = null;
    const backdrop = document.getElementById('productModalBackdrop');
    backdrop.classList.remove('flex');
    backdrop.classList.add('hidden');
}

function agregarAlCarrito(id) {
    const producto = todosLosResultadosActuales.find(item => item.id === String(id));
    if (!producto) return;
    const existente = carrito.find(item => item.id === producto.id);
    if (existente) existente.cantidad += 1;
    else carrito.push({ ...producto, cantidad: 1 });
    actualizarCarritoUI();
    showToast('Añadido al carrito', producto.nombre);
    toggleCartDrawer(true);
}

function eliminarDelCarrito(id) {
    carrito = carrito.filter(item => item.id !== String(id));
    actualizarCarritoUI();
}

function cambiarCantidad(id, delta) {
    const item = carrito.find(i => i.id === String(id));
    if (!item || !Number.isInteger(delta)) return;
    item.cantidad += delta;
    if (item.cantidad <= 0) eliminarDelCarrito(id);
    else actualizarCarritoUI();
}

function actualizarCarritoUI() {
    const totalItems = carrito.reduce((suma, item) => suma + item.cantidad, 0);
    document.getElementById('headerCartCount').textContent = totalItems;
    document.getElementById('cartDrawerCount').textContent = `(${totalItems})`;
    const container = document.getElementById('cartItemsContainer');
    container.replaceChildren();
    if (!carrito.length) {
        container.append(crearElemento('p', 'text-center text-gray-500 mt-10', 'Tu carrito está vacío'));
    } else {
        for (const item of carrito) {
            const fila = crearElemento('div', 'py-3 flex items-center justify-between gap-3');
            const info = crearElemento('div', 'flex-1 min-w-0');
            info.append(crearElemento('h4', 'text-xs font-semibold text-white truncate', item.nombre));
            const precio = precioEnMoneda(item);
            info.append(crearElemento('p', 'text-xs text-neon-green', `${formatearMonto(precio, monedaActual)} × ${item.cantidad}`));
            const acciones = crearElemento('div', 'flex items-center gap-2 mt-2');
            const menos = crearElemento('button', 'w-6 h-6 rounded bg-card-border font-bold hover:bg-neon-green hover:text-black transition-all', '−');
            menos.type = 'button';
            menos.setAttribute('aria-label', `Quitar una unidad de ${item.nombre}`);
            menos.addEventListener('click', () => cambiarCantidad(item.id, -1));
            const cantidad = crearElemento('span', 'text-xs font-semibold text-white', item.cantidad);
            const mas = crearElemento('button', 'w-6 h-6 rounded bg-card-border font-bold hover:bg-neon-green hover:text-black transition-all', '+');
            mas.type = 'button';
            mas.setAttribute('aria-label', `Agregar una unidad de ${item.nombre}`);
            mas.addEventListener('click', () => cambiarCantidad(item.id, 1));
            const eliminar = crearElemento('button', 'text-red-400 text-xs ml-auto hover:underline', 'Eliminar');
            eliminar.type = 'button';
            eliminar.addEventListener('click', () => eliminarDelCarrito(item.id));
            acciones.append(menos, cantidad, mas, eliminar);
            info.append(acciones);
            const subtotal = precio === null ? null : Math.round(precio * 100) * item.cantidad / 100;
            fila.append(info, crearElemento('div', 'font-bold text-sm text-neon-green', formatearMonto(subtotal, monedaActual)));
            container.append(fila);
        }
    }
    document.getElementById('cartTotal').textContent = formatearMonto(totalCarrito(), monedaActual);
}

function toggleCartDrawer(abrir) {
    const panel = document.getElementById('cartDrawerPanel');
    const backdrop = document.getElementById('cartDrawerBackdrop');
    if (abrir) {
        backdrop.classList.remove('hidden');
        setTimeout(() => panel.classList.remove('translate-x-full'), 10);
    } else {
        panel.classList.add('translate-x-full');
        setTimeout(() => backdrop.classList.add('hidden'), 300);
    }
}

function cambiarMoneda(nuevaMoneda) {
    if (nuevaMoneda !== 'USD' && nuevaMoneda !== 'ARS') return;
    monedaActual = nuevaMoneda;
    guardarLocal('cellzone_moneda', monedaActual);
    document.querySelectorAll('[data-currency]').forEach(boton => {
        const activo = boton.dataset.currency === monedaActual;
        boton.className = 'px-2 sm:px-2.5 py-1 rounded-lg text-xs font-extrabold transition-all ' +
            (activo ? 'bg-neon-green text-black' : 'text-gray-400 hover:text-white');
        boton.setAttribute('aria-pressed', String(activo));
    });
    if (yaCargaronProductos) renderizarProductos(productosVisibles);
    actualizarCarritoUI();
    if (productoModalAbierto) openProductModal(productoModalAbierto);
}

function checkoutViaWhatsApp() {
    if (!carrito.length) {
        showToast('Tu carrito está vacío', 'Agregá productos antes de enviar el pedido.');
        return;
    }
    let mensaje = '¡Hola CELLZONE IMPORTADOS! Deseo hacer el siguiente pedido:\n\n';
    for (const item of carrito) {
        const precio = formatearMonto(precioEnMoneda(item), monedaActual);
        mensaje += `- ${item.cantidad} × ${nombreParaMensaje(item.nombre)} (${precio} c/u)\n`;
    }
    const total = totalCarrito();
    mensaje += total === null
        ? `\n*Total en ${monedaActual}: a confirmar*`
        : `\n*Total estimado: ${formatearMonto(total, monedaActual)}*`;
    mensaje += '\n\nPor favor, confirmar precio y disponibilidad.';
    abrirWhatsApp(mensaje);
}

function comprarItemWhatsApp(id) {
    const producto = todosLosResultadosActuales.find(item => item.id === String(id));
    if (!producto) return;
    const precio = formatearMonto(precioEnMoneda(producto), monedaActual);
    const mensaje = `¡Hola CELLZONE! Me interesa este producto:\n\n*${nombreParaMensaje(producto.nombre)}*\nPrecio: ${precio}\n\n¿Tienen stock disponible?`;
    abrirWhatsApp(mensaje);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', cargarDatosIniciales, { once: true });
} else {
    cargarDatosIniciales();
}
