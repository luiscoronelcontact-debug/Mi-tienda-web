with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Actualizar el enlace en verificarSesionGoogle para que llame a una función JS en vez de href
old_link = '<a href="/perfil" class="text-[10px] text-neon-green hover:underline ml-1 cursor-pointer font-bold" title="Mi Perfil">Perfil</a>'
new_link = '<button onclick="mostrarPerfil()" class="text-[10px] text-neon-green hover:underline ml-1 cursor-pointer font-bold bg-transparent border-none p-0" title="Mi Perfil">Perfil</button>'

content = content.replace(old_link, new_link)

# 2. Agregar el contenedor de perfil y la función JS antes del cierre del body o script principal
profile_code = """
    <!-- Vista de Perfil Oculta por defecto -->
    <div id="vistaPerfil" class="hidden max-w-md mx-auto p-4 bg-card-bg neon-border rounded-xl mt-6 mb-12 text-white">
        <div class="flex justify-between items-center mb-4">
            <h2 class="text-xl font-bold text-neon-green">Mi Perfil</h2>
            <button onclick="cerrarPerfil()" class="text-xs text-gray-400 hover:text-white cursor-pointer">Volver a la tienda</button>
        </div>
        <form id="formPerfil" onsubmit="guardarPerfil(event)" class="space-y-4">
            <div>
                <label class="block text-xs font-medium text-gray-300">Nombre completo</label>
                <input type="text" id="profFullName" class="w-full p-2.5 bg-black/50 border border-gray-700 rounded-lg text-white text-sm focus:border-neon-green outline-none" />
            </div>
            <div>
                <label class="block text-xs font-medium text-gray-300">Teléfono</label>
                <input type="text" id="profPhone" class="w-full p-2.5 bg-black/50 border border-gray-700 rounded-lg text-white text-sm focus:border-neon-green outline-none" />
            </div>
            <div>
                <label class="block text-xs font-medium text-gray-300">Provincia</label>
                <input type="text" id="profProvince" class="w-full p-2.5 bg-black/50 border border-gray-700 rounded-lg text-white text-sm focus:border-neon-green outline-none" />
            </div>
            <div>
                <label class="block text-xs font-medium text-gray-300">Ciudad</label>
                <input type="text" id="profCity" class="w-full p-2.5 bg-black/50 border border-gray-700 rounded-lg text-white text-sm focus:border-neon-green outline-none" />
            </div>
            <div>
                <label class="block text-xs font-medium text-gray-300">Dirección</label>
                <input type="text" id="profAddress" class="w-full p-2.5 bg-black/50 border border-gray-700 rounded-lg text-white text-sm focus:border-neon-green outline-none" />
            </div>
            <button type="submit" id="btnGuardarPerfil" class="w-full bg-neon-green text-black font-bold p-2.5 rounded-lg hover:opacity-90 transition-all cursor-pointer text-sm">
                Guardar cambios
            </button>
        </form>
    </div>

    <script>
        async function mostrarPerfil() {
            // Ocultar sección principal de productos/buscador si existe
            const mainContent = document.querySelector('main') || document.getElementById('productosContainer') || document.querySelector('.max-w-7xl');
            // Ocultamos todo el contenido principal de la tienda y mostramos el perfil
            const perfilDiv = document.getElementById('vistaPerfil');
            perfilDiv.classList.remove('hidden');
            
            // Cargar datos actuales de Supabase
            const { data: { session } } = await supabaseClient.auth.getSession();
            if (!session) return;

            const { data, error } = await supabaseClient
                .from('profiles')
                .select('full_name, phone, province, city, address')
                .eq('id', session.user.id)
                .single();

            if (data) {
                document.getElementById('profFullName').value = data.full_name || '';
                document.getElementById('profPhone').value = data.phone || '';
                document.getElementById('profProvince').value = data.province || '';
                document.getElementById('profCity').value = data.city || '';
                document.getElementById('profAddress').value = data.address || '';
            }
        }

        function cerrarPerfil() {
            document.getElementById('vistaPerfil').classList.add('hidden');
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
                cerrarPerfil();
            }
        }
    </script>
"""

if "</body>" in content and "vistaPerfil" not in content:
    content = content.replace("</body>", profile_code + "\n</body>")
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("¡Perfil integrado correctamente en index.html!")
else:
    print("El perfil ya estaba integrado o no se encontró el cierre del body.")
