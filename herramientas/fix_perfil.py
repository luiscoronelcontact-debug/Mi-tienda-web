with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_func = """        async function mostrarPerfil() {
            // Ocultar sección principal de productos/buscador si existe
            const mainContent = document.querySelector('main') || document.getElementById('productosContainer') || document.querySelector('.max-w-7xl');
            // Ocultamos todo el contenido principal de la tienda y mostramos el perfil
            const perfilDiv = document.getElementById('vistaPerfil');
            perfilDiv.classList.remove('hidden');"""

new_func = """        async function mostrarPerfil() {
            // Ocultar el catálogo y mostrar el perfil
            const mainContent = document.querySelector('main') || document.getElementById('productosContainer') || document.querySelector('.max-w-7xl');
            if (mainContent) mainContent.style.display = 'none';
            
            const perfilDiv = document.getElementById('vistaPerfil');
            if (perfilDiv) perfilDiv.classList.remove('hidden');"""

old_close = """        function cerrarPerfil() {
            document.getElementById('vistaPerfil').classList.add('hidden');
        }"""

new_close = """        function cerrarPerfil() {
            document.getElementById('vistaPerfil').classList.add('hidden');
            const mainContent = document.querySelector('main') || document.getElementById('productosContainer') || document.querySelector('.max-w-7xl');
            if (mainContent) mainContent.style.display = 'block';
        }"""

if old_func in content:
    content = content.replace(old_func, new_func)
if old_close in content:
    content = content.replace(old_close, new_close)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("¡Arreglo aplicado con éxito!")
