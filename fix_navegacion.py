with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Asegurar que el logo tenga un enlace/onclick para volver al inicio
# Buscamos la etiqueta del logo y le agregamos el evento onclick
old_logo = '<a class="flex items-center gap-3 cursor-pointer">'
new_logo = '<a onclick="irAInicio()" class="flex items-center gap-3 cursor-pointer">'

if old_logo in content:
    content = content.replace(old_logo, new_logo)
else:
    # Si la clase es un poco diferente, buscamos por partes clave del logo
    content = content.replace('class="flex items-center gap-3', 'onclick="irAInicio()" class="flex items-center gap-3')

# 2. Reemplazar las funciones de navegación en el script para usar irAInicio correctamente
script_nuevo = """    <script>
        function irAInicio() {
            const perfilDiv = document.getElementById('vistaPerfil');
            if (perfilDiv) perfilDiv.classList.add('hidden');
            
            // Restaurar el contenido principal limpiando el style display para que recupere flex/grid
            const mainContent = document.querySelector('main') || document.getElementById('productosContainer') || document.querySelector('.max-w-7xl');
            if (mainContent) mainContent.style.display = '';
            
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        async function mostrarPerfil() {
            const mainContent = document.querySelector('main') || document.getElementById('productosContainer') || document.querySelector('.max-w-7xl');
            if (mainContent) mainContent.style.display = 'none';
            
            const perfilDiv = document.getElementById('vistaPerfil');
            if (perfilDiv) perfilDiv.classList.remove('hidden');
            
            // Ocultar form de edición al abrir por defecto
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

# Reemplazar el bloque de script antiguo del perfil
if '<script>' in content and 'async function mostrarPerfil()' in content:
    start_pos = content.find('<script>\n        async function mostrarPerfil()')
    if start_pos == -1:
        start_pos = content.find('<script>')
        # Buscamos el script que contenga mostrarPerfil
        for part in content.split('<script>'):
            if 'mostrarPerfil' in part:
                start_pos = content.find('<script>' + part)
                end_pos = start_pos + len('<script>' + part)
                # Buscamos el cierre de ese script </script>
                end_script = content.find('</script>', start_pos) + len('</script>')
                content = content[:start_pos] + script_nuevo + content[end_script:]
                break

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("¡Navegación corregida con éxito!")
