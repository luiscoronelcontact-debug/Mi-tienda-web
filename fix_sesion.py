import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

nuevo_inicio = """async function cargarDatosIniciales() {
            actualizarContadorFavoritos();
            
            // Escuchar automáticamente los cambios de sesión (ej. al volver de Google)
            supabaseClient.auth.onAuthStateChange((event, session) => {
                if (event === 'SIGNED_IN' || event === 'SIGNED_OUT') {
                    verificarSesionGoogle();
                }
            });
            
            await verificarSesionGoogle();
            await consultarSupabase();
        }"""

# Reemplazar la función cargarDatosIniciales actual por la nueva que tiene el escuchador
content = re.sub(r'async function cargarDatosIniciales\(\)\s*\{[^\}]+\}', nuevo_inicio, content)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("¡Escuchador de sesión de Google instalado con éxito!")
