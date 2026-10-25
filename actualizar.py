with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

start_str = "async function verificarSesionGoogle() {"
end_str = "async function loginConGoogle() {"

new_func = """async function verificarSesionGoogle() {
            const { data: { session } } = await supabaseClient.auth.getSession();
            if (session && session.user) {
                const user = session.user;
                const avatar = user.user_metadata?.avatar_url || 'https://via.placeholder.com/40';
                const nombre = user.user_metadata?.full_name || user.email;

                document.getElementById('authContainer').innerHTML = `
                    <div class="flex items-center gap-2 bg-card-bg neon-border px-3 py-1.5 rounded-xl">
                        <img src="${avatar}" alt="Avatar" class="w-7 h-7 rounded-full object-cover border border-neon-green">
                        <span class="text-xs font-bold text-white hidden sm:inline max-w-[100px] truncate">${nombre}</span>
                        <a href="/perfil" class="text-[10px] text-neon-green hover:underline ml-1 cursor-pointer font-bold" title="Mi Perfil">Perfil</a>
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

        """

if start_str in content and end_str in content:
    start_idx = content.find(start_str)
    end_idx = content.find(end_str)
    content = content[:start_idx] + new_func + content[end_idx:]
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("¡Index actualizado con éxito!")
else:
    print("Error: No se encontraron los puntos de referencia en index.html")
