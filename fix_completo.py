with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# 1. Asegurar que el logo tenga el evento onclick="irAInicio()"
def add_logo_click(match):
    tag = match.group(0)
    if 'onclick="irAInicio()"' not in tag:
        return tag.replace('<a ', '<a onclick="irAInicio()" ')
    return tag

content = re.sub(r'<a\b[^>]*?>\s*<div[^>]*?>\s*<span[^>]*?>CELL', add_logo_click, content, flags=re.DOTALL | re.IGNORECASE)

# Si no encontró el logo exacto por regex, hacemos reemplazo directo seguro
if 'onclick="irAInicio()"' not in content:
    content = content.replace('class="flex items-center gap-3', 'onclick="irAInicio()" class="flex items-center gap-3')

# 2. Definir las funciones de sesión y navegación limpias
nuevo_bloque_js = """
        // Inicialización y verificación de sesión de Google
        async function cargarDatosIniciales() {
            actualizarContadorFavoritos();
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
            
            // Mostrar de nuevo el contenedor de productos y buscador de la tienda
            const prodContainer = document.getElementById('productosContainer');
            if (prodContainer) prodContainer.style.display = '';

            const buscador = document.getElementById('buscadorContainer') || document.querySelector('.max-w-7xl');
            if (buscador) buscador.style.display = '';

            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        async function mostrarPerfil() {
            // Ocultar sólo el catálogo de productos, manteniendo el header superior intacto
            const prodContainer = document.getElementById('productosContainer');
            if (prodContainer) prodContainer.style.display = 'none';

            const buscador = document.getElementById('buscadorContainer') || document.querySelector('.max-w-7xl');
            if (buscador) buscador.style.display = 'none';

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
"""

# Limpiamos y reemplazamos desde verificarSesionGoogle hasta el final de las funciones de auth/perfil anteriores
if 'async function verificarSesionGoogle' in content:
    start_idx = content.find('async function verificarSesionGoogle')
    # Buscamos un punto de corte seguro posterior (por ejemplo antes de Gestión de Favoritos o un script de cierre)
    cut_marker = '// Gestión de Favoritos'
    if cut_marker in content:
        end_idx = content.find(cut_marker)
        content = content[:start_idx] + nuevo_bloque_js + "\n\n        " + content[end_idx:]
    else:
        # Si no está Gestión de Favoritos, reemplazamos hasta el cierre del script principal
        pass

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("¡Corrección aplicada con éxito!")
