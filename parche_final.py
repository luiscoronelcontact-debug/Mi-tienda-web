with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

script_parche = """
<!-- PARCHE FORZADO DE NAVEGACION Y SESION -->
<script>
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
</script>
"""

# Limpiar parche anterior si existiera para no duplicar
if "PARCHE FORZADO DE NAVEGACION Y SESION" in content:
    print("El parche ya estaba instalado.")
else:
    # Insertar justo antes del cierre del body
    content = content.replace("</body>", script_parche + "\n</body>")
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("¡Parche forzado inyectado con éxito!")
