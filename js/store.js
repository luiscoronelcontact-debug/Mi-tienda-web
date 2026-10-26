tailwind.config = {
            darkMode: "class",
            theme: {
                extend: {
                    colors: {
                        "neon-green": "#00FF66",
                        "dark-bg": "#050508",
                        "card-bg": "#0f131f",
                        "card-border": "#1a2235"
                    }
                }
            }
        }

window.onerror = function(msg, url, lineNo, columnNo, error) {
    alert("ERROR JS: " + msg + "\nLínea: " + lineNo);
    return false;
};
window.onunhandledrejection = function(event) {
    alert("PROMESA FALLIDA: " + (event.reason ? event.reason.message : "Error en Supabase"));
};

const SUPABASE_URL = "https://otnjxfzttdjihjcoximm.supabase.co";
        const SUPABASE_KEY = "sb_publishable_ifoJPoL74pGM2B4cBxSLwg_7OrOGYy5";

        const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

        let carrito = [];
let monedaActual = localStorage.getItem('cellzone_moneda') || 'USD';
let _ultimosProductos = [];
        let favoritos = JSON.parse(localStorage.getItem('cellzone_favs') || '[]');
        let categoriaActual = 'TODOS';
        let timeoutBusqueda = null;
        let todosLosResultadosActuales = [];

        // Inicialización y verificación de sesión de Google
        async function cargarDatosIniciales() {
            actualizarContadorFavoritos();

            // Escuchar automáticamente los cambios de sesión (ej. al volver de Google)
            supabaseClient.auth.onAuthStateChange((event, session) => {
                if (event === 'SIGNED_IN' || event === 'SIGNED_OUT') {
                    verificarSesionGoogle();
                }
            });

            await verificarSesionGoogle();
            await consultarSupabase();
        }

        async function verificarSesionGoogle() {
            const { data: { session } } = await supabaseClient.auth.getSession();
            if (session && session.user) {
                const user = session.user;
                const avatar = user.user_metadata?.avatar_url || 'https://via.placeholder.com/40';
                const nombre = user.user_metadata?.full_name || user.email;

                document.getElementById('authContainer').innerHTML = `
                    <div class="flex items-center gap-2 bg-card-bg neon-border px-3 py-1.5 rounded-xl">
                        <img src="${avatar}" alt="Avatar" class="w-7 h-7 rounded-full object-cover border border-neon-green">
                        <span class="text-xs font-bold text-white hidden sm:inline max-w-[100px] truncate">${nombre}</span>
                        <button onclick="mostrarPerfil()" class="text-[10px] text-neon-green hover:underline ml-1 cursor-pointer font-bold bg-transparent border-none p-0" title="Mi Perfil">Perfil</button>
                        <button onclick="cerrarSesionGoogle()" class="text-[10px] text-red-400 hover:underline ml-1 cursor-pointer" title="Cerrar sesión">Salir</button>
                    </div>
                `;
            } else {
                document.getElementById('authContainer').innerHTML = `
                    <button onclick="loginConGoogle()" class="px-3.5 py-2 rounded-xl bg-card-bg neon-border hover:border-neon-green text-white text-xs font-bold transition-all flex items-center gap-2 cursor-pointer">
                        <span class="material-symbols-outlined text-[18px] text-neon-green">account_circle</span>
                        <span class="hidden sm:inline">Ingresar con Google</span>
                    </button>
                `;
            }
        }

        async function loginConGoogle() {
            const { error } = await supabaseClient.auth.signInWithOAuth({
                provider: 'google',
                options: { redirectTo: window.location.href }
            });
            if (error) console.error("Error al iniciar sesión con Google:", error.message);
        }

        async function cerrarSesionGoogle() {
            await supabaseClient.auth.signOut();
            location.reload();
        }

        function irAInicio() {
            const perfilDiv = document.getElementById('vistaPerfil');
            if (perfilDiv) perfilDiv.classList.add('hidden');

            const prodContainer = document.getElementById('productosContainer');
            if (prodContainer) prodContainer.style.display = '';

            const buscador = document.getElementById('buscadorContainer') || document.querySelector('.max-w-7xl');
            if (buscador) buscador.style.display = '';

            const sectionHero = document.querySelector('section');
            if (sectionHero) sectionHero.style.display = '';
            
            const mainContent = document.querySelector('main');
            if (mainContent) {
                Array.from(mainContent.children).forEach(child => {
                    if (child.id !== 'vistaPerfil') child.style.display = '';
                });
            }

            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
        
        async function mostrarPerfil() {
            // Ocultar TODO menos el header y el perfil
            const prodContainer = document.getElementById('productosContainer');
            if (prodContainer) prodContainer.style.display = 'none';

            const buscador = document.getElementById('buscadorContainer') || document.querySelector('.max-w-7xl');
            if (buscador) buscador.style.display = 'none';
            
            const sectionHero = document.querySelector('section');
            if (sectionHero) sectionHero.style.display = 'none';
            
            const mainContent = document.querySelector('main');
            if (mainContent) {
                Array.from(mainContent.children).forEach(child => {
                    if (child.id !== 'vistaPerfil') child.style.display = 'none';
                });
            }

            const perfilDiv = document.getElementById('vistaPerfil');
            if (perfilDiv) perfilDiv.classList.remove('hidden');
            
            const editSec = document.getElementById('seccionEditarPerfil');
            if (editSec) editSec.classList.add('hidden');

            const { data: { session } } = await supabaseClient.auth.getSession();
            if (!session) return;

            const user = session.user;
            const email = user.email || '';
            const avatar = user.user_metadata?.avatar_url;
            const nombreMeta = user.user_metadata?.full_name || email.split('@')[0];

            document.getElementById('perfilEmailTxt').innerText = email;

            const { data, error } = await supabaseClient
                .from('profiles')
                .select('full_name, phone, province, city, address')
                .eq('id', user.id)
                .single();

            const fullName = data?.full_name || nombreMeta;
            document.getElementById('perfilNombreTxt').innerText = fullName;
            
            const profFullName = document.getElementById('profFullName');
            if (profFullName) profFullName.value = fullName;

            if (avatar) {
                const img = document.getElementById('perfilImgAvatar');
                if (img) {
                    img.src = avatar;
                    img.classList.remove('hidden');
                }
                const initDiv = document.getElementById('perfilInitAvatar');
                if (initDiv) initDiv.classList.add('hidden');
            } else {
                const initDiv = document.getElementById('perfilInitAvatar');
                if (initDiv) {
                    initDiv.innerText = fullName.charAt(0).toUpperCase();
                    initDiv.classList.remove('hidden');
                }
                const img = document.getElementById('perfilImgAvatar');
                if (img) img.classList.add('hidden');
            }

            if (data) {
                const profPhone = document.getElementById('profPhone');
                if (profPhone) profPhone.value = data.phone || '';
                
                const profProvince = document.getElementById('profProvince');
                if (profProvince) profProvince.value = data.province || '';
                
                const profCity = document.getElementById('profCity');
                if (profCity) profCity.value = data.city || '';
                
                const profAddress = document.getElementById('profAddress');
                if (profAddress) profAddress.value = data.address || '';
            }
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        function cerrarPerfil() {
            irAInicio();
        }

        function toggleEditarPerfil() {
            const editSec = document.getElementById('seccionEditarPerfil');
            if (editSec) editSec.classList.toggle('hidden');
        }

        async function guardarPerfil(e) {
            e.preventDefault();
            const { data: { session } } = await supabaseClient.auth.getSession();
            if (!session) return;

            const updates = {
                id: session.user.id,
                full_name: document.getElementById('profFullName').value,
                phone: document.getElementById('profPhone').value,
                province: document.getElementById('profProvince').value,
                city: document.getElementById('profCity').value,
                address: document.getElementById('profAddress').value,
                updated_at: new Date(),
            };

            const btn = document.getElementById('btnGuardarPerfil');
            if (btn) btn.innerText = "Guardando...";
            
            let { error } = await supabaseClient.from('profiles').upsert(updates);
            if (btn) btn.innerText = "Guardar cambios";

            if (error) {
                alert('Error al actualizar el perfil');
            } else {
                alert('¡Perfil actualizado con éxito!');
                const perfilNombreTxt = document.getElementById('perfilNombreTxt');
                if (perfilNombreTxt) perfilNombreTxt.innerText = updates.full_name;
                toggleEditarPerfil();
            }
        }
        
        // Gestión de Favoritos
        function toggleFavorito(id, event) {
            if(event) event.stopPropagation();
            const index = favoritos.indexOf(id);
            if (index > -1) {
                favoritos.splice(index, 1);
                showToast('Eliminado de Favoritos', 'Producto removido de tu lista');
            } else {
                favoritos.push(id);
                showToast('❤️ Añadido a Favoritos', 'Guardado en tu lista personal');
            }
            localStorage.setItem('cellzone_favs', JSON.stringify(favoritos));
            actualizarContadorFavoritos();

            // Si está en la vista de favoritos, refrescar
            if (categoriaActual === 'FAVORITOS') {
                consultarSupabase('', 'FAVORITOS');
            } else {
                renderizarProductos(todosLosResultadosActuales);
            }
        }

        function actualizarContadorFavoritos() {
            document.getElementById('favCountBadge').textContent = favoritos.length;
        }

        // Consultas a Supabase
        async function consultarSupabase(termino = '', categoria = 'TODOS') {
            try {
                if (categoria === 'FAVORITOS') {
                    if (favoritos.length === 0) {
                        todosLosResultadosActuales = [];
                        renderizarProductos([]);
                        return;
                    }
                    // Consultar los productos favoritos por ID
                    const { data, error } = await supabaseClient
                        .from('productos')
                        .select('*')
                        .in('id', favoritos);
                    
                    if (error) throw error;
                    procesarYRenderizar(data || [], termino);
                    return;
                }

                let url = `${SUPABASE_URL}/rest/v1/productos?select=*`;
                
                if (termino.trim() !== '') {
                    url += `&nombre=ilike.*${encodeURIComponent(termino.trim())}*`;
                }

                if (categoria && categoria !== 'TODOS') {
                    url += `&categoria=eq.${encodeURIComponent(categoria)}`;
                }

                url += `&limit=60`;

                const response = await fetch(url, {
                    headers: {
                        "apikey": SUPABASE_KEY,
                        "Authorization": `Bearer ${SUPABASE_KEY}`
                    }
                });
                const data = await response.json();
                procesarYRenderizar(data || [], termino);

            } catch (error) {
                console.error("Error conectando con Supabase:", error);
                document.getElementById('productGrid').innerHTML = '<div class="col-span-full text-center py-10 text-red-400">Error al conectar con la base de datos.</div>';
            }
        }

        function procesarYRenderizar(data, termino) {
            todosLosResultadosActuales = data.map(p => {
                const baseUSD = parseFloat(p.precioUSD || p.precio_usd || p.precioARS || p.precio_ars || p.precio || 0);
                const precioFinal = Math.round((baseUSD * 1.20) * 100) / 100;
                return {
                    id: p.id,
                    nombre: p.nombre || 'Sin nombre',
                    categoria: p.categoria || 'General',
                    precio: precioFinal,
                    imagen: p.imagen || 'https://via.placeholder.com/300',
                    descripcion: p.descripcion || 'Sin descripción disponible.'
                };
            });

            // Si hay término de búsqueda activo y estamos en vista favoritos, filtrar localmente también
            let finalProcesados = todosLosResultadosActuales;
            if (termino.trim() !== '' && categoriaActual === 'FAVORITOS') {
                const t = termino.toLowerCase();
                finalProcesados = todosLosResultadosActuales.filter(p => p.nombre.toLowerCase().includes(t));
            }

            renderizarProductos(finalProcesados);
        }

        function buscarProductosServidor() {
            clearTimeout(timeoutBusqueda);
            const texto = document.getElementById('buscador').value;
            timeoutBusqueda = setTimeout(() => {
                consultarSupabase(texto, categoriaActual);
            }, 300);
        }

        function filtrarCategoria(cat, btn) {
            categoriaActual = cat;
            document.querySelectorAll('.cat-pill').forEach(b => {
                b.className = "cat-pill shrink-0 px-4 py-2.5 rounded-xl text-xs font-bold transition-all bg-card-bg text-gray-300 hover:text-white neon-border";
            });
            if(btn) {
                if(cat === 'FAVORITOS') {
                    btn.className = "cat-pill shrink-0 px-4 py-2.5 rounded-xl text-xs font-bold transition-all bg-neon-green text-black shadow-sm flex items-center gap-1";
                } else {
                    btn.className = "cat-pill shrink-0 px-4 py-2.5 rounded-xl text-xs font-bold transition-all bg-neon-green text-black shadow-sm";
                }
            }
            const texto = document.getElementById('buscador').value;
            consultarSupabase(texto, categoriaActual);
        }

        function renderizarProductos(productos) {
    window._ultimosProductos = productos;
            const grid = document.getElementById('productGrid');
            document.getElementById('productCounter').textContent = `Mostrando ${productos.length} resultados`;

            if (productos.length === 0) {
                grid.innerHTML = '<div class="col-span-full text-center py-20 text-gray-500">No se encontraron productos en esta sección.</div>';
                return;
            }

            grid.innerHTML = productos.map(p => {
                const esFavorito = favoritos.includes(String(p.id));
                const favColor = esFavorito ? 'text-red-500 fill-red-500' : 'text-gray-400 hover:text-red-400';
                return `
                    <article class="product-card group flex flex-col justify-between bg-card-bg neon-border rounded-2xl p-3.5 sm:p-4 hover:border-neon-green transition-all duration-300 relative overflow-hidden cursor-pointer shadow-lg" onclick="openProductModal('${p.id}')">
                        <div>
                            <div class="relative w-full aspect-square rounded-xl bg-black/40 overflow-hidden flex items-center justify-center p-3">
                                <button onclick="toggleFavorito('${p.id}', event)" class="absolute top-2.5 right-2.5 z-10 p-2 rounded-full bg-black/60 backdrop-blur-md transition-all cursor-pointer ${favColor}">
                                    <span class="material-symbols-outlined text-[20px]">favorite</span>
                                </button>
                                <img alt="${p.nombre}" class="w-full h-full object-contain group-hover:scale-105 transition-transform duration-300" src="${p.imagen}" loading="lazy"/>
                            </div>
                            <div class="mt-3.5 space-y-1">
                                <span class="text-[10px] text-neon-green uppercase font-mono tracking-wider">${p.categoria}</span>
                                <h2 class="text-xs sm:text-sm font-bold text-white line-clamp-2 leading-snug">${p.nombre}</h2>
                            </div>
                        </div>
                        <div class="mt-4 pt-3 border-t border-card-border space-y-3">
                            <div class="font-extrabold text-base sm:text-lg text-neon-green">$${formatearPrecio(p)}</div>
                            <button onclick="event.stopPropagation(); agregarAlCarrito('${p.id}')" class="w-full py-2.5 px-3 rounded-xl bg-neon-green hover:brightness-110 text-black font-extrabold text-xs shadow-[0_0_10px_rgba(0,255,102,0.3)] transition-all flex items-center justify-center gap-1.5 cursor-pointer">
                                <span class="material-symbols-outlined text-[16px]">add_shopping_cart</span>
                                <span>AGREGAR</span>
                            </button>
                        </div>
                    </article>
                `;
            }).join('');
        }

        function openProductModal(id) {
            const p = todosLosResultadosActuales.find(item => item.id == id);
            if (!p) return;

            document.getElementById('modalContentContainer').innerHTML = `
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="aspect-square bg-black/40 rounded-xl flex items-center justify-center p-4 neon-border">
                        <img src="${p.imagen}" alt="${p.nombre}" class="max-h-full object-contain">
                    </div>
                    <div class="flex flex-col justify-between space-y-4">
                        <div>
                            <span class="text-xs text-neon-green uppercase font-mono bg-neon-green/10 px-3 py-1 rounded-full border border-neon-green/30">${p.categoria}</span>
                            <h2 class="text-xl font-bold text-white mt-3">${p.nombre}</h2>
                            <div class="text-2xl font-extrabold text-neon-green mt-2">$${formatearPrecio(p)}</div>
                            <p class="text-sm text-gray-300 mt-3 leading-relaxed bg-black/30 p-3.5 rounded-xl border border-card-border">${p.descripcion}</p>
                        </div>
                        <div class="space-y-3">
                            <button onclick="agregarAlCarrito('${p.id}'); closeProductModal();" class="w-full py-3.5 rounded-xl bg-card-border hover:bg-neon-green hover:text-black text-white font-bold transition-all cursor-pointer neon-border">
                                Añadir al Carrito
                            </button>
                            <button onclick="comprarItemWhatsApp('${p.nombre.replace(/'/g, "")}', ${p.precio})" class="w-full py-3.5 rounded-xl bg-neon-green text-black font-extrabold shadow-[0_0_15px_rgba(0,255,102,0.4)] hover:brightness-110 cursor-pointer flex items-center justify-center gap-2 transition-all">
                                <span class="material-symbols-outlined text-[20px]">chat</span>
                                Consultar por WhatsApp
                            </button>
                        </div>
                    </div>
                </div>
            `;

            const backdrop = document.getElementById('productModalBackdrop');
            backdrop.classList.remove('hidden');
            backdrop.classList.add('flex');
        }

        function closeProductModal() {
            const backdrop = document.getElementById('productModalBackdrop');
            backdrop.classList.remove('flex');
            backdrop.classList.add('hidden');
        }

        function agregarAlCarrito(id) {
            const producto = todosLosResultadosActuales.find(item => item.id == id);
            if (!producto) return;
            
            const existente = carrito.find(item => item.id == id);
            if (existente) {
                existente.cantidad++;
            } else {
                carrito.push({ ...producto, cantidad: 1 });
            }
            actualizarCarritoUI();
            showToast('¡Añadido al Carrito!', producto.nombre);
            toggleCartDrawer(true);
        }

        function eliminarDelCarrito(id) {
            carrito = carrito.filter(item => item.id != id);
            actualizarCarritoUI();
        }

        function cambiarCantidad(id, delta) {
            const item = carrito.find(i => i.id == id);
            if(!item) return;
            item.cantidad += delta;
            if(item.cantidad <= 0) {
                eliminarDelCarrito(id);
            } else {
                actualizarCarritoUI();
            }
        }

        function actualizarCarritoUI() {
            const totalItems = carrito.reduce((sum, item) => sum + item.cantidad, 0);
            document.getElementById('headerCartCount').textContent = totalItems;
            document.getElementById('cartDrawerCount').textContent = `(${totalItems})`;

            const container = document.getElementById('cartItemsContainer');
            if (carrito.length === 0) {
                container.innerHTML = '<p class="text-center text-gray-500 mt-10">Tu carrito está vacío</p>';
                document.getElementById('cartTotal').textContent = '$0.00';
                return;
            }

            let total = 0;
            container.innerHTML = carrito.map(item => {
                const subtotal = item.precio * item.cantidad;
                total += subtotal;
                return `
                    <div class="py-3 flex items-center justify-between gap-3">
                        <div class="flex-1 min-w-0">
                            <h4 class="text-xs font-semibold text-white truncate">${item.nombre}</h4>
                            <p class="text-xs text-neon-green">$${item.precio.toFixed(2)} x ${item.cantidad}</p>
                            <div class="flex items-center gap-2 mt-2">
                                <button onclick="cambiarCantidad('${item.id}', -1)" class="w-6 h-6 rounded bg-card-border font-bold hover:bg-neon-green hover:text-black transition-all">-</button>
                                <span class="text-xs font-semibold text-white">${item.cantidad}</span>
                                <button onclick="cambiarCantidad('${item.id}', 1)" class="w-6 h-6 rounded bg-card-border font-bold hover:bg-neon-green hover:text-black transition-all">+</button>
                                <button onclick="eliminarDelCarrito('${item.id}')" class="text-red-400 text-xs ml-auto hover:underline">Eliminar</button>
                            </div>
                        </div>
                        <div class="font-bold text-sm text-neon-green">$${subtotal.toFixed(2)}</div>
                    </div>
                `;
            }).join('');

            document.getElementById('cartTotal').textContent = `$${total.toFixed(2)}`;
        }

        function toggleCartDrawer(open) {
            const panel = document.getElementById('cartDrawerPanel');
            const backdrop = document.getElementById('cartDrawerBackdrop');
            if (open) {
                backdrop.classList.remove('hidden');
                setTimeout(() => panel.classList.remove('translate-x-full'), 10);
            } else {
                panel.classList.add('translate-x-full');
                setTimeout(() => backdrop.classList.add('hidden'), 300);
            }
        }

        function checkoutViaWhatsApp() {
            if (carrito.length === 0) return;
            let mensaje = "¡Hola CELLZONE IMPORTADOS! Deseo hacer el siguiente pedido:\n\n";
            let total = 0;
            carrito.forEach(i => {
                mensaje += `- ${i.cantidad}x ${i.nombre} ($${(i.precio * i.cantidad).toFixed(2)})\n`;
                total += i.precio * i.cantidad;
            });
            mensaje += `\n*Total a pagar: $${total.toFixed(2)}*`;
            window.open(`https://wa.me/595995677862?text=${encodeURIComponent(mensaje)}`, '_blank');
        }

        function comprarItemWhatsApp(nombre, precio) {
            const mensaje = `¡Hola CELLZONE! Me interesa este producto:\n\n*${nombre}*\nPrecio: $${precio}\n\n¿Tienen stock disponible?`;
            window.open(`https://wa.me/595995677862?text=${encodeURIComponent(mensaje)}`, '_blank');
        }

        function showToast(title, subtitle) {
            const toast = document.getElementById('toastNotification');
            document.getElementById('toastTitle').textContent = title;
            document.getElementById('toastSubtitle').textContent = subtitle;
            toast.classList.remove('opacity-0', 'translate-y-24');
            setTimeout(() => toast.classList.add('opacity-0', 'translate-y-24'), 2500);
        }

        cargarDatosIniciales();

function irAInicio() {
            const perfilDiv = document.getElementById('vistaPerfil');
            if (perfilDiv) perfilDiv.classList.add('hidden');
            
            // Restaurar todos los contenedores principales de la tienda
            const mainElements = document.querySelectorAll('main, #productosContainer, .max-w-7xl, section');
            mainElements.forEach(el => {
                if (el.id !== 'vistaPerfil' && !el.contains(perfilDiv)) {
                    el.style.display = '';
                }
            });
            
            const prodContainer = document.getElementById('productosContainer');
            if (prodContainer) prodContainer.style.display = '';
            
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        async function mostrarPerfil() {
            const mainElements = document.querySelectorAll('main, #productosContainer, .max-w-7xl, section');
            mainElements.forEach(el => {
                if (el.id !== 'vistaPerfil' && !el.contains(document.getElementById('vistaPerfil'))) {
                    if (!el.querySelector('#authContainer')) {
                        el.style.display = 'none';
                    }
                }
            });
            
            const prodContainer = document.getElementById('productosContainer');
            if (prodContainer) prodContainer.style.display = 'none';

            const perfilDiv = document.getElementById('vistaPerfil');
            if (perfilDiv) perfilDiv.classList.remove('hidden');
            
            document.getElementById('seccionEditarPerfil').classList.add('hidden');

            const { data: { session } } = await supabaseClient.auth.getSession();
            if (!session) return;

            const user = session.user;
            const email = user.email || '';
            const avatar = user.user_metadata?.avatar_url;
            const nombreMeta = user.user_metadata?.full_name || email.split('@')[0];

            document.getElementById('perfilEmailTxt').innerText = email;

            const { data, error } = await supabaseClient
                .from('profiles')
                .select('full_name, phone, province, city, address')
                .eq('id', user.id)
                .single();

            const fullName = data?.full_name || nombreMeta;
            document.getElementById('perfilNombreTxt').innerText = fullName;
            document.getElementById('profFullName').value = fullName;

            if (avatar) {
                const img = document.getElementById('perfilImgAvatar');
                img.src = avatar;
                img.classList.remove('hidden');
                document.getElementById('perfilInitAvatar').classList.add('hidden');
            } else {
                const initDiv = document.getElementById('perfilInitAvatar');
                initDiv.innerText = fullName.charAt(0).toUpperCase();
                initDiv.classList.remove('hidden');
                document.getElementById('perfilImgAvatar').classList.add('hidden');
            }

            if (data) {
                document.getElementById('profPhone').value = data.phone || '';
                document.getElementById('profProvince').value = data.province || '';
                document.getElementById('profCity').value = data.city || '';
                document.getElementById('profAddress').value = data.address || '';
            }
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        function cerrarPerfil() {
            irAInicio();
        }

        function toggleEditarPerfil() {
            const editSec = document.getElementById('seccionEditarPerfil');
            editSec.classList.toggle('hidden');
        }

        async function guardarPerfil(e) {
            e.preventDefault();
            const { data: { session } } = await supabaseClient.auth.getSession();
            if (!session) return;

            const updates = {
                id: session.user.id,
                full_name: document.getElementById('profFullName').value,
                phone: document.getElementById('profPhone').value,
                province: document.getElementById('profProvince').value,
                city: document.getElementById('profCity').value,
                address: document.getElementById('profAddress').value,
                updated_at: new Date(),
            };

            const btn = document.getElementById('btnGuardarPerfil');
            btn.innerText = "Guardando...";
            
            let { error } = await supabaseClient.from('profiles').upsert(updates);
            btn.innerText = "Guardar cambios";

            if (error) {
                alert('Error al actualizar el perfil');
            } else {
                alert('¡Perfil actualizado con éxito!');
                document.getElementById('perfilNombreTxt').innerText = updates.full_name;
                toggleEditarPerfil();
            }
        }

document.addEventListener("DOMContentLoaded", () => {
    // 1. Forzar que el logo de CELLZONE lleve al inicio siempre
    const enlaces = document.querySelectorAll('header a');
    enlaces.forEach(a => {
        if(a.innerText.toUpperCase().includes('CELL') || a.innerText.toUpperCase().includes('ZONE')) {
            a.onclick = (e) => {
                e.preventDefault();
                if(typeof irAInicio === 'function') irAInicio();
            };
        }
    });

    // 2. Forzar que el inicio de sesión use tu dominio oficial
    window.loginConGoogle = async function() {
        const { error } = await supabaseClient.auth.signInWithOAuth({
            provider: 'google',
            options: { redirectTo: window.location.origin }
        });
        if (error) alert("Error al conectar con Google: " + error.message);
    };

    // 3. Obligar a Supabase a actualizar los botones apenas detecte la sesión
    supabaseClient.auth.onAuthStateChange((event, session) => {
        if (event === 'SIGNED_IN' || event === 'INITIAL_SESSION' || event === 'USER_UPDATED') {
            if(typeof verificarSesionGoogle === 'function') verificarSesionGoogle();
        }
    });
    
    // 4. Doble chequeo de seguridad 1 segundo después de cargar la web
    setTimeout(() => {
        if(typeof verificarSesionGoogle === 'function') verificarSesionGoogle();
    }, 1000);
});

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


function formatearAmbosPrecios(p) {
    const usd = parseFloat(p.precio_usd || p.precio || 0);
    const ars = parseFloat(p.precio_ars || (usd * 1200));
    return `<div class="flex flex-col">
        <span class="text-neon-green font-extrabold text-base sm:text-lg">$${usd.toFixed(2)} USD</span>
        <span class="text-gray-400 text-xs font-semibold">$${Math.round(ars).toLocaleString('es-AR')} ARS</span>
    </div>`;
}
