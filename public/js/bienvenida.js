/* Bienvenida de la primera visita. No modifica productos ni envía datos. */
(() => {
    'use strict';
    const CLAVE_VISTA = 'cellzone_bienvenida_v1';
    let yaVista = false;
    try { yaVista = localStorage.getItem(CLAVE_VISTA) === '1'; } catch (_) { /* La tienda sigue accesible sin almacenamiento. */ }
    if (yaVista) return;

    const dialogo = document.getElementById('bienvenida');
    const video = document.getElementById('bienvenida-video');
    const entrar = document.getElementById('bienvenida-entrar');
    const sonido = document.getElementById('bienvenida-sonido');
    if (!dialogo || !video || !entrar || !sonido) return;

    let fuentesCargadas = false;
    let terminada = false;
    const etiquetaSonido = sonido.querySelector('span');

    function prepararVideo() {
        if (fuentesCargadas) return;
        fuentesCargadas = true;
        for (const fuente of video.querySelectorAll('source[data-src]')) fuente.src = fuente.dataset.src;
        video.preload = 'auto';
        video.load();
    }
    function estadoSonido(activo) {
        video.muted = !activo;
        sonido.setAttribute('aria-pressed', String(activo));
        if (etiquetaSonido) etiquetaSonido.textContent = activo ? 'Silenciar' : 'Activar sonido';
    }
    function entrarATienda() {
        if (terminada) return;
        terminada = true;
        try { localStorage.setItem(CLAVE_VISTA, '1'); } catch (_) { /* El botón funciona incluso si el navegador bloquea almacenamiento. */ }
        video.pause();
        if (typeof dialogo.close === 'function' && dialogo.open) dialogo.close();
        else dialogo.removeAttribute('open');
        document.body.classList.remove('bienvenida-abierta');
        const principal = document.querySelector('main');
        if (principal) principal.focus({ preventScroll: true });
    }

    entrar.addEventListener('click', entrarATienda);
    dialogo.addEventListener('cancel', evento => { evento.preventDefault(); entrarATienda(); });
    sonido.addEventListener('click', async () => {
        if (!video.muted) { estadoSonido(false); return; }
        prepararVideo();
        estadoSonido(true);
        try {
            if (video.ended) video.currentTime = 0;
            await video.play(); // Un clic del visitante permite activar el audio.
        } catch (_) {
            estadoSonido(false);
            if (etiquetaSonido) etiquetaSonido.textContent = 'Sonido no disponible';
        }
    });

    try {
        if (typeof dialogo.showModal === 'function') dialogo.showModal();
        else dialogo.setAttribute('open', '');
    } catch (_) {
        // Si el navegador no puede abrir el diálogo, nunca se bloquea la tienda.
        return;
    }
    document.body.classList.add('bienvenida-abierta');
    video.poster = video.dataset.poster || '';
    const reducirMovimiento = typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (!reducirMovimiento) {
        prepararVideo();
        // Autoplay silenciado: si está bloqueado, queda la imagen y el botón sigue funcionando.
        const reproduccion = video.play();
        if (reproduccion && typeof reproduccion.catch === 'function') reproduccion.catch(() => {});
    }
})();
