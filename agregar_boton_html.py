import os

if os.path.exists("index.html"):
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    selector_html = """
        <div class="flex items-center gap-1 bg-card-bg neon-border p-1 rounded-xl">
            <button id="btn-usd" onclick="cambiarMoneda('USD')" class="px-2.5 py-1 rounded-lg text-xs font-extrabold bg-neon-green text-black transition-all">USD</button>
            <button id="btn-ars" onclick="cambiarMoneda('ARS')" class="px-2.5 py-1 rounded-lg text-xs font-extrabold text-gray-400 hover:text-white transition-all">ARS</button>
        </div>
    """

    if "btn-usd" in html:
        print("⚠️ El selector de moneda ya estaba agregado en el HTML.")
    else:
        # Intentar ubicarlo antes del botón de perfil o login de Google
        if 'onclick="loginConGoogle()"' in html:
            html = html.replace('onclick="loginConGoogle()"', selector_html + '\n    <button onclick="loginConGoogle()"')
            print("✅ Selector insertado correctamente junto al botón de perfil.")
        elif 'id="perfil"' in html:
            html = html.replace('id="perfil"', selector_html + '\n    <div id="perfil"')
            print("✅ Selector insertado cerca del perfil.")
        else:
            # Si no encuentra el botón exacto, lo agregamos al final del body o header
            html = html.replace('</body>', selector_html + '\n</body>')
            print("✅ Selector agregado al final de la página.")

        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html)
else:
    print("⚠️ No se encontró el archivo index.html en esta ruta.")
