with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# 1. Asegurar que el logo tenga onclick="irAInicio()"
def fix_logo(match):
    tag = match.group(0)
    if 'onclick' not in tag:
        return tag.replace('<a ', '<a onclick="irAInicio()" ')
    return tag

content = re.sub(r'<a\b[^>]*>.*?CELLZONE.*?</a>', fix_logo, content, flags=re.DOTALL | re.IGNORECASE)

# 2. HTML renovado del perfil con botón de retorno bien visible
nuevo_html_perfil = """    <!-- Vista de Perfil Estilizada -->
    <div id="vistaPerfil" class="hidden max-w-2xl mx-auto p-4 mt-6 mb-12 text-white">
        <button onclick="irAInicio()" class="px-4 py-2.5 bg-card-bg neon-border rounded-xl text-neon-green hover:bg-neon-green hover:text-black transition-all mb-6 flex items-center gap-2 cursor-pointer font-bold text-xs shadow-lg">
            <span class="material-symbols-outlined text-[18px]">arrow_back</span> Volver a la tienda
        </button>

        <!-- Tarjeta de Usuario -->
        <div class="bg-card-bg neon-border rounded-2xl p-6 mb-6 flex flex-col sm:flex-row items-center gap-4 text-center sm:text-left">
            <div id="perfilAvatarContainer">
                <img id="perfilImgAvatar" src="" alt="Avatar" class="w-20 h-20 rounded-full object-cover border-2 border-neon-green hidden">
                <div id="perfilInitAvatar" class="w-20 h-20 rounded-full bg-neon-green text-black font-bold text-2xl flex items-center justify-center border-2 border-neon-green hidden"></div>
            </div>
            <div class="flex-1">
                <h2 id="perfilNombreTxt" class="text-xl font-bold text-white"></h2>
                <p id="perfilEmailTxt" class="text-xs text-gray-400 mt-1"></p>
                <button onclick="toggleEditarPerfil()" class="mt-3 px-4 py-2 bg-neon-green/10 border border-neon-green text-neon-green rounded-xl text-xs font-bold hover:bg-neon-green hover:text-black transition-all flex items-center gap-1.5 mx-auto sm:mx-0 cursor-pointer">
                    <span class="material-symbols-outlined text-[16px]">edit</span> Editar perfil
                </button>
            </div>
        </div>

        <!-- Sección Mis Pedidos -->
        <div class="bg-card-bg neon-border rounded-2xl p-6 mb-6">
            <h3 class="text-base font-bold text-white flex items-center gap-2 mb-4">
                <span class="material-symbols-outlined text-neon-green">package</span> Mis pedidos
            </h3>
            <div class="text-center py-8 text-gray-400 border border-dashed border-gray-800 rounded-xl">
                <span class="material-symbols-outlined text-[36px] text-gray-600 mb-2">inventory_2</span>
                <p class="text-sm">Todavía no tenés pedidos.</p>
            </div>
        </div>

        <!-- Formulario de Edición (Oculto por defecto) -->
        <div id="seccionEditarPerfil" class="hidden bg-card-bg neon-border rounded-2xl p-6">
            <h3 class="text-base font-bold text-neon-green mb-4">Actualizar tus datos</h3>
            <form onsubmit="guardarPerfil(event)" class="space-y-4">
                <div>
                    <label class="block text-xs font-medium text-gray-300 mb-1">Nombre completo</label>
                    <input type="text" id="profFullName" class="w-full p-2.5 bg-black/50 border border-gray-700 rounded-xl text-white text-sm focus:border-neon-green outline-none" />
                </div>
                <div>
                    <label class="block text-xs font-medium text-gray-300 mb-1">Teléfono</label>
                    <input type="text" id="profPhone" class="w-full p-2.5 bg-black/50 border border-gray-700 rounded-xl text-white text-sm focus:border-neon-green outline-none" />
                </div>
                <div>
                    <label class="block text-xs font-medium text-gray-300 mb-1">Provincia</label>
                    <input type="text" id="profProvince" class="w-full p-2.5 bg-black/50 border border-gray-700 rounded-xl text-white text-sm focus:border-neon-green outline-none" />
                </div>
                <div>
                    <label class="block text-xs font-medium text-gray-300 mb-1">Ciudad</label>
                    <input type="text" id="profCity" class="w-full p-2.5 bg-black/50 border border-gray-700 rounded-xl text-white text-sm focus:border-neon-green outline-none" />
                </div>
                <div>
                    <label class="block text-xs font-medium text-gray-300 mb-1">Dirección</label>
                    <input type="text" id="profAddress" class="w-full p-2.5 bg-black/50 border border-gray-700 rounded-xl text-white text-sm focus:border-neon-green outline-none" />
                </div>
                <div class="flex gap-2 pt-2">
                    <button type="submit" id="btnGuardarPerfil" class="flex-1 bg-neon-green text-black font-bold p-2.5 rounded-xl hover:opacity-90 transition-all cursor-pointer text-sm">
                        Guardar cambios
                    </button>
                    <button type="button" onclick="toggleEditarPerfil()" class="px-4 py-2.5 bg-gray-800 text-gray-300 rounded-xl text-sm font-semibold hover:bg-gray-700 cursor-pointer">
                        Cancelar
                    </button>
                </div>
            </form>
        </div>
    </div>"""

# 3. Funciones JavaScript robustas para navegación y perfil
script_nuevo = """    <script>
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
    </script>"""

# Reemplazar o insertar el bloque de perfil y scripts antes del cierre del body
if '<div id="vistaPerfil"' in content:
    start_pos = content.find('<div id="vistaPerfil"')
    end_pos = content.find('</body>')
    content = content[:start_pos] + nuevo_html_perfil + "\n\n" + script_nuevo + "\n" + content[end_pos:]
elif '</body>' in content:
    content = content.replace('</body>', nuevo_html_perfil + "\n\n" + script_nuevo + "\n</body>")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("¡Navegación y perfil corregidos con éxito!")
