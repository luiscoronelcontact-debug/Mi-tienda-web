import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Buscamos el punto de inicio (después de las variables globales) y el punto final (antes de Gestión de Favoritos)
start_match = re.search(r'let todosLosResultadosActuales = \[\];', content)
end_match = re.search(r'// Gestión de Favoritos', content)

if start_match and end_match:
    start_idx = start_match.end()
    end_idx = end_match.start()
    
    # Insertamos el bloque limpio, sin duplicados y con la navegación correcta
    nuevo_codigo = """
        
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
            
            const prodContainer = document.getElementById('productosContainer');
            if (prodContainer) prodContainer.style.display = '';

            const buscador = document.getElementById('buscadorContainer') || document.querySelector('.max-w-7xl');
            if (buscador) buscador.style.display = '';

            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
        
        """
    
    # Reemplazamos toda la sección sucia por el código limpio
    content = content[:start_idx] + nuevo_codigo + content[end_idx:]
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("¡Duplicados eliminados y código JS reparado con éxito!")
else:
    print("No se encontraron las marcas de inicio/fin. Revisa el archivo.")
