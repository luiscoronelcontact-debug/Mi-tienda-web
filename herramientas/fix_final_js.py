import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

start_idx = content.find('const SUPABASE_URL')
end_idx = content.find('// Gestión de Favoritos')

nuevo_bloque_js = """const SUPABASE_URL = "https://otnjxfzttdjihjcoximm.supabase.co";
        const SUPABASE_KEY = "sb_publishable_ifoJPoL74pGM2B4cBxSLwg_7OrOGYy5";

        const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

        let carrito = [];
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
        
        """

content = content[:start_idx] + nuevo_bloque_js + content[end_idx:]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("¡Código JavaScript reemplazado exitosamente!")
