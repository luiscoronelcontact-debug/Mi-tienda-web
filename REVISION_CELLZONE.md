# Revisión de la versión de la notebook

**Rama de revisión: no fusionar ni desplegar sin las pruebas y autorización pendientes.** No se ejecutó el sincronizador original ni se actualizaron datos de Supabase para preparar este borrador.

## Qué incluye

- `public/index.html` parte del HTML enviado por el propietario desde su notebook y conserva `public/img/logo.png`, también recibido de la notebook. `public/css/styles.css` se mantuvo sin cambios.
- El catálogo y el detalle muestran precios **USD y ARS** por separado. El selector establece la moneda del carrito y del mensaje. Se usan los valores de la base sin sumar un segundo 20 % y sin inventar una tasa de conversión. Si falta un precio, el total queda a confirmar.
- Los enlaces y mensajes de WhatsApp usan el número comercial confirmado por el propietario. El HTML del selector, el formateador y las referencias del carrito fueron corregidos.
- El catálogo, modal, carrito, perfil y detalle utilizan elementos DOM y texto para datos no confiables; las URL de imágenes se validan. Se reemplazaron alertas técnicas y funciones duplicadas.
- `vercel.json` conserva `outputDirectory: public`, la regla de reescritura y la desactivación del despliegue Git automático de esta rama. Propone las cabeceras `X-Content-Type-Options: nosniff` y `Referrer-Policy: strict-origin-when-cross-origin`. Esto **no impide un despliegue manual**, no cambia la web activa y no se ha probado en Vercel.
- `herramientas/sincronizar_propuesto.py` es una propuesta de simulación con la escritura **deshabilitada en código**. El original `herramientas/sincronizar.py` y sus rutas antiguas no se reemplazaron y no deben ejecutarse hasta revisar el flujo NeoImport y la autenticación.

## Precios y sincronización

Se compararon por ID 24.022 productos de la base con el `catalogo_real.json` que coincide con el mapa de la notebook: todos los USD de la base eran el 120 % de los USD del catálogo, con tolerancia de aproximadamente un centavo. Para ARS coincidieron 24.021; uno tenía ARS cero en el catálogo y un precio en la base, pendiente de revisar. Esa relación **no prueba** el costo actual de NeoImport ni qué proceso alimentó la base.

El sincronizador original envía `precio`, pero no `precio_usd` ni `precio_ars`. El frontend propuesto necesita las dos columnas: hay que revisar el origen, la escritura y el efecto sobre las demás columnas antes de volver a sincronizar. Nunca colocar claves privadas en el navegador, el repositorio ni la carpeta `public/`.

## Pruebas y límites

- En Chromium se probaron búsqueda, favoritos, ambos precios, carrito, totales, modal, mensajes interceptados y perfil simulado con datos ficticios y red externa bloqueada. También se probaron cadenas hostiles y ausencia de precio. En el entorno local se comprobó el encabezado en móviles de 320 y 375 px.
- Una comprobación adicional de solo lectura renderizó 60 productos públicos reales y comparó sus precios con la base, con sesión y red del navegador simuladas. No hubo escrituras ni pedidos reales.
- `tests/prueba_sincronizador.py` comprueba el cálculo y el bloqueo de escritura con datos y sesión HTTP ficticios. `tests/prueba_navegador.cjs` usa Playwright y respuestas simuladas. Instalar las dependencias de `tests/package.json` y el navegador de Playwright solo si se desea repetir las pruebas; no ejecutan el sincronizador original.
- Falta probar Google OAuth y perfiles con cuentas de prueba, WhatsApp real en dispositivos, los encabezados y reescrituras reales de Vercel, la política CSP, la sincronización en un entorno seguro y una revisión completa de seguridad. La vista ficticia interactiva permanece en el espacio de revisión local, no en esta rama.

La separación de carpetas no vuelve privado el repositorio público ni borra claves o archivos de su historial o de despliegues anteriores.
