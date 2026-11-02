# Borrador: organización de Cellzone

**No desplegar ni fusionar todavía.** Esta rama partió de `main`, que no es idéntico a la tienda activa. Posteriormente se incorporaron para revisión el HTML y logo aportados desde la notebook y correcciones locales. Las pruebas de navegador fueron simuladas; faltan las pruebas reales indicadas en [`REVISION_CELLZONE.md`](REVISION_CELLZONE.md).

## Carpetas

- `public/`: sitio web para futuros despliegues; verificar todos los recursos de la versión buena.
- `herramientas/`: scripts de trabajo y sincronización de la copia de GitHub. **No ejecutar todavía `sincronizar.py` ni scripts de limpieza**; requieren revisión.
- `datos/`: catálogo y archivos de trabajo tal como estaban en GitHub.
- `respaldos/`: copias históricas de HTML.
- Archivos como `src/` y `productos.js` permanecen sin clasificar hasta verificar sus dependencias.

Hay enlaces simbólicos en la raíz para conservar las rutas antiguas de páginas, CSS, JS, scripts y datos. Las rutas relativas de los scripts se esperan desde la raíz del proyecto; los enlaces y todos los flujos deben probarse en la notebook antes de usarlos. Si el sistema de archivos no admite enlaces simbólicos, será necesario adaptarlos.

## Despliegue futuro

`vercel.json` conserva la regla de reescritura anterior, propone `public` como salida y deshabilita el despliegue Git automático de esta rama. `.vercelignore` contiene una lista permitida para Vercel CLI. Son medidas propuestas para despliegues futuros: deben probarse, no modifican la tienda activa ni eliminan archivos de despliegues anteriores. Un despliegue manual todavía podría realizarse; no hacerlo con este borrador.

## Seguridad

El repositorio sigue siendo público: las carpetas `herramientas`, `datos`, `respaldos`, los enlaces y el historial siguen visibles en GitHub. No guardar secretos en este repositorio. `.gitignore` no elimina archivos que ya están seguidos. `herramientas/asistente.mjs` usa `OPENROUTER_API_KEY` desde el entorno en lugar de una clave literal; esto no borra la clave del historial ni de despliegues antiguos.

## Antes de dar por terminada la migración

1. Completar las pruebas de las rutas y dependencias de la notebook; el cotejo de huellas y los archivos web aportados ya se incorporaron para revisión.
2. Revisar las referencias a catálogo y datos, reparar la sincronización sin ejecutarla hasta autorización y comprobar permisos.
3. Probar localmente y luego en una vista previa autorizada: tienda, productos, carrito, Google/Supabase y WhatsApp.
4. Revisar que solo se publiquen los recursos previstos, y que los archivos administrativos no se devuelvan como contenido. La reescritura existente podría responder HTML para rutas inexistentes.
