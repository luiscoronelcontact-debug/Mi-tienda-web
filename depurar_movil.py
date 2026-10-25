with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

error_catcher = """<script>
window.onerror = function(msg, url, lineNo, columnNo, error) {
    alert("ERROR JS: " + msg + "\\nLínea: " + lineNo);
    return false;
};
window.onunhandledrejection = function(event) {
    alert("PROMESA FALLIDA: " + (event.reason ? event.reason.message : "Error en Supabase"));
};
</script>
</head>"""

if "window.onerror" not in content:
    content = content.replace("</head>", error_catcher)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("¡Detector de errores activado!")
else:
    print("El detector ya estaba activado.")
