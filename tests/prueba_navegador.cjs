// Pruebas de navegador con datos ficticios. Intercepta TODAS las conexiones externas.
// Requiere Playwright y Chromium. No usa ni modifica la base de Cellzone.
const assert = require('node:assert/strict');
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');

const root = path.resolve(__dirname, '../public');
const cssFile = process.env.CELLZONE_TEST_CSS;
if (!cssFile) throw new Error('Indicar CELLZONE_TEST_CSS con la hoja Tailwind compilada para pruebas.');
const css = fs.readFileSync(cssFile, 'utf8');
const fontDir = process.env.CELLZONE_TEST_MATERIAL_DIR;
const materialCss = fontDir ? fs.readFileSync(path.join(fontDir, 'material.css'), 'utf8') : null;
const materialFont = fontDir ? fs.readFileSync(path.join(fontDir, 'material.woff2')) : null;
const products = [
  { id: 'producto-1', nombre: 'Producto Uno', categoria: 'Tecnología', descripcion: 'Prueba de producto uno.', precio: 120, precio_usd: 120, precio_ars: 150000, imagen: '' },
  { id: 'producto-2', nombre: 'Producto Dos', categoria: 'Tecnología', descripcion: 'Prueba de producto dos.', precio: 30, precio_usd: 30, precio_ars: 45000, imagen: '' },
  { id: "x');window.__xss=1;//", nombre: '<img src=x onerror="window.__xss=1">', categoria: '<svg onload="window.__xss=2">', descripcion: '<script>window.__xss=3</script>', precio_usd: 7.5, precio_ars: 9500, imagen: 'javascript:window.__xss=4' },
  { id: 'sin-ars', nombre: 'Producto sin ARS', categoria: 'Otros', descripcion: 'No hay precio ARS.', precio_usd: 20, precio_ars: 0, imagen: '' }
];

const stub = `
window.__mock = {
  products: ${JSON.stringify(products)}, session: null, profile: null,
  callbacks: [], oauth: null, lastUpdate: null,
  emit() { this.callbacks.forEach(cb => cb('SIGNED_IN', this.session)); }
};
window.supabase = { createClient() { return {
  auth: {
    onAuthStateChange(cb) { window.__mock.callbacks.push(cb); return { data: { subscription: {} } }; },
    async getSession() { return { data: { session: window.__mock.session }, error: null }; },
    async signInWithOAuth(opts) { window.__mock.oauth = opts; return { error: null }; },
    async signOut() { window.__mock.session = null; return { error: null }; }
  },
  from(tabla) {
    if (tabla === 'productos') return { select() { return { async in(campo, ids) {
      return { data: window.__mock.products.filter(p => ids.includes(String(p.id))), error: null };
    } }; } };
    if (tabla === 'profiles') return {
      select() { return { eq() { return { async maybeSingle() { return { data: window.__mock.profile, error: null }; } }; } }; },
      async upsert(v) { window.__mock.lastUpdate = v; return { error: null }; }
    };
    throw new Error('Tabla no simulada: ' + tabla);
  }
}; } };`;

function testServer() {
  return http.createServer((req, res) => {
    const url = new URL(req.url, 'http://127.0.0.1');
    if (url.pathname === '/__prueba/material.woff2' && materialFont) {
      res.writeHead(200, { 'Content-Type': 'font/woff2' }).end(materialFont);
      return;
    }
    const name = decodeURIComponent(url.pathname === '/' ? '/index.html' : url.pathname);
    const file = path.resolve(root, '.' + name);
    if (!(file === root || file.startsWith(root + path.sep))) { res.writeHead(403).end(); return; }
    fs.readFile(file, (err, bytes) => {
      if (err) { res.writeHead(404).end(); return; }
      const type = ({ '.html': 'text/html; charset=utf-8', '.js': 'application/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.png': 'image/png', '.jpg': 'image/jpeg', '.mp4': 'video/mp4', '.webm': 'video/webm' })[path.extname(file)] || 'application/octet-stream';
      res.writeHead(200, { 'Content-Type': type }).end(bytes);
    });
  });
}

async function main() {
  const server = testServer();
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const origin = `http://127.0.0.1:${server.address().port}`;
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const pageErrors = [];
  let failCatalog = false;
  let externalIntercepted = 0;
  let blockedUnexpected = [];
  await context.addInitScript(() => {
    window.__opens = [];
    window.__alerts = [];
    window.open = (url, target, features) => { window.__opens.push({ url, target, features }); return null; };
    window.alert = text => window.__alerts.push(String(text));
    window.scrollTo = () => {};
  });
  await context.route('**/*', async route => {
    const url = new URL(route.request().url());
    if (url.origin === origin) return route.continue();
    externalIntercepted++;
    if (url.hostname === 'cdn.tailwindcss.com') {
      const js = `window.tailwind = {config:{}}; const style = document.createElement('style'); style.textContent = ${JSON.stringify(css)}; document.head.appendChild(style);`;
      return route.fulfill({ status: 200, contentType: 'application/javascript', body: js });
    }
    if (url.hostname === 'cdn.jsdelivr.net' && url.pathname.includes('supabase-js')) {
      return route.fulfill({ status: 200, contentType: 'application/javascript', body: stub });
    }
    if (materialCss && url.hostname === 'fonts.googleapis.com' && (url.searchParams.get('family') || '').startsWith('Material Symbols')) {
      return route.fulfill({ status: 200, contentType: 'text/css', body: materialCss });
    }
    if (materialFont && url.hostname === 'fonts.gstatic.com' && url.pathname.endsWith('.woff2')) {
      return route.fulfill({ status: 200, contentType: 'font/woff2', body: materialFont });
    }
    if (url.hostname === 'otnjxfzttdjihjcoximm.supabase.co' && url.pathname === '/rest/v1/productos') {
      if (failCatalog) return route.fulfill({ status: 500, contentType: 'application/json', body: '{}' });
      let result = products.slice();
      const id = url.searchParams.get('id');
      const nombre = url.searchParams.get('nombre');
      if (id && id.startsWith('eq.')) result = result.filter(p => p.id === id.slice(3));
      if (nombre && nombre.startsWith('ilike.*') && nombre.endsWith('*')) {
        const q = nombre.slice(7, -1).toLocaleLowerCase('es');
        result = result.filter(p => p.nombre.toLocaleLowerCase('es').includes(q));
      }
      return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(result) });
    }
    if (!['fonts.googleapis.com', 'fonts.gstatic.com'].includes(url.hostname)) blockedUnexpected.push(url.hostname);
    return route.abort();
  });
  const page = await context.newPage();
  const pedidosVideo = [];
  page.on('request', request => {
    const url = new URL(request.url());
    if (url.origin === origin && url.pathname.startsWith('/media/')) pedidosVideo.push(url.pathname);
  });
  page.on('pageerror', error => pageErrors.push(error.message));
  const step = text => console.log('OK:', text);
  try {
    await page.goto(origin + '/', { waitUntil: 'networkidle' });
    assert.equal(await page.locator('#bienvenida').evaluate(el => el.open), true, 'La primera visita abre la bienvenida.');
    await page.waitForFunction(() => {
      const v = document.getElementById('bienvenida-video');
      return v.readyState >= 2 && v.videoWidth === 720 && v.currentTime > 0.08;
    }, null, { timeout: 15000 });
    assert.equal(await page.locator('#bienvenida-video').evaluate(v => v.muted), true);
    assert.ok(pedidosVideo.length > 0);
    for (const viewport of [{ width: 320, height: 700 }, { width: 375, height: 812 }, { width: 1280, height: 900 }]) {
      await page.setViewportSize(viewport);
      const rect = await page.getByRole('button', { name: 'Entrar a la tienda' }).boundingBox();
      assert.ok(rect && rect.x >= 0 && rect.x + rect.width <= viewport.width && rect.y >= 0 && rect.y + rect.height <= viewport.height);
    }
    await page.getByRole('button', { name: 'Activar sonido' }).click();
    assert.equal(await page.locator('#bienvenida-sonido').getAttribute('aria-pressed'), 'true');
    await page.getByRole('button', { name: 'Silenciar' }).click();
    await page.getByRole('button', { name: 'Entrar a la tienda' }).click();
    assert.equal(await page.evaluate(() => localStorage.getItem('cellzone_bienvenida_v1')), '1');
    pedidosVideo.length = 0;
    await page.reload({ waitUntil: 'networkidle' });
    assert.equal(await page.locator('#bienvenida').evaluate(el => el.open), false, 'La segunda visita entra directamente.');
    assert.equal(pedidosVideo.length, 0, 'La segunda visita no descarga el video.');
    step('Bienvenida con video, acceso, sonido optativo y recuerdo; sin afectar la tienda.');
    await page.waitForSelector('#productGrid article');
    assert.equal(await page.locator('#productGrid article').count(), 4);
    assert.equal(await page.locator('#authContainer #btn-usd').count(), 0);
    assert.equal(await page.locator('header img').getAttribute('src'), 'img/logo.png');
    assert.equal(await page.locator('a[href="https://wa.me/595995677862"]').count(), 2);
    const card1 = page.locator('#productGrid article').nth(0);
    const cardText = await card1.textContent();
    assert.match(cardText, /USD 120,00/);
    assert.match(cardText, /ARS 150\.000,00/);
    assert.doesNotMatch(cardText, /144,00/);
    assert.equal(await page.locator('#btn-usd').getAttribute('aria-pressed'), 'true');
    await page.getByRole('button', { name: 'Ingresar con Google' }).click();
    const oauth = await page.evaluate(() => window.__mock.oauth);
    assert.equal(oauth.provider, 'google');
    assert.equal(oauth.options.redirectTo, origin);
    step('Logo, selector separado, enlaces, precios sin segundo recargo e inicio OAuth simulado.');

    if (process.env.CELLZONE_SCREENSHOT) await page.screenshot({ path: process.env.CELLZONE_SCREENSHOT, fullPage: false });
    if (materialFont) {
      await page.setViewportSize({ width: 375, height: 812 });
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), true, 'La portada no debe desbordar a 375px.');
      if (process.env.CELLZONE_SCREENSHOT_MOBILE) await page.screenshot({ path: process.env.CELLZONE_SCREENSHOT_MOBILE, fullPage: false });
      await page.setViewportSize({ width: 320, height: 700 });
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), true, 'La portada no debe desbordar a 320px.');
      await page.setViewportSize({ width: 1280, height: 900 });
      step('La portada se mantiene dentro del ancho de celular de 320 y 375 píxeles.');
    }
    await page.getByRole('button', { name: 'Agregar a favoritos' }).first().click();
    assert.equal(await page.locator('#favCountBadge').textContent(), '1');
    assert.equal(await page.locator('#productModalBackdrop').evaluate(el => el.classList.contains('hidden')), true);
    await page.locator('.cat-pill').filter({ hasText: 'Favoritos' }).click();
    await page.waitForFunction(() => document.querySelectorAll('#productGrid article').length === 1);
    assert.match(await page.locator('#productGrid').textContent(), /Producto Uno/);
    await page.locator('.cat-pill').filter({ hasText: 'TODOS' }).click();
    await page.waitForFunction(() => document.querySelectorAll('#productGrid article').length === 4);
    await page.locator('#buscador').fill('Producto Dos');
    await page.waitForFunction(() => document.querySelectorAll('#productGrid article').length === 1);
    assert.match(await page.locator('#productGrid').textContent(), /Producto Dos/);
    await page.locator('#buscador').fill('');
    await page.waitForFunction(() => document.querySelectorAll('#productGrid article').length === 4);
    step('Favoritos y búsqueda funcionan con respuestas simuladas.');

    await page.locator('#productGrid article').nth(2).click();
    assert.equal(await page.locator('#modalContentContainer h2').textContent(), products[2].nombre);
    assert.equal(await page.locator('#modalContentContainer p img').count(), 0);
    assert.match(await page.locator('#modalContentContainer img').getAttribute('src'), /^data:image\/svg\+xml/);
    assert.equal(await page.evaluate(() => window.__xss || 0), 0);
    await page.locator('#productModalDialog > button').click();
    step('Texto hostil y URL javascript: no se ejecutan en catálogo ni modal.');

    await page.locator('#productGrid article').nth(1).click();
    await page.getByRole('button', { name: 'Consultar por WhatsApp' }).click();
    let opens = await page.evaluate(() => window.__opens);
    let direct = new URL(opens.at(-1).url);
    assert.equal(direct.host, 'wa.me');
    assert.equal(direct.pathname, '/595995677862');
    assert.match(direct.searchParams.get('text'), /Producto Dos/);
    assert.match(direct.searchParams.get('text'), /USD 30,00/);
    await page.locator('#productModalDialog > button').click();
    await page.locator('#productGrid article').nth(0).getByRole('button', { name: /AGREGAR$/ }).click();
    await page.getByRole('button', { name: 'Agregar una unidad de Producto Uno' }).click();
    assert.equal(await page.locator('#headerCartCount').textContent(), '2');
    assert.equal(await page.locator('#cartTotal').textContent(), 'USD 240,00');
    await page.locator('#cartDrawerBackdrop button').filter({ hasText: '✕' }).click();
    await page.waitForTimeout(350);
    await page.locator('#productGrid article').nth(1).getByRole('button', { name: /AGREGAR$/ }).click();
    assert.equal(await page.locator('#cartTotal').textContent(), 'USD 270,00');
    await page.getByRole('group', { name: 'Moneda del pedido en el carrito' }).getByRole('button', { name: 'ARS' }).click();
    assert.equal(await page.locator('#cartTotal').textContent(), 'ARS 345.000,00');
    assert.equal(await page.locator('#btn-ars').getAttribute('aria-pressed'), 'true');
    await page.getByRole('button', { name: 'FINALIZAR PEDIDO VÍA WHATSAPP' }).click();
    opens = await page.evaluate(() => window.__opens);
    const order = new URL(opens.at(-1).url);
    const message = order.searchParams.get('text');
    assert.equal(order.pathname, '/595995677862');
    assert.match(message, /2 × Producto Uno \(ARS 150\.000,00 c\/u\)/);
    assert.match(message, /1 × Producto Dos \(ARS 45\.000,00 c\/u\)/);
    assert.match(message, /Total estimado: ARS 345\.000,00/);
    assert.doesNotMatch(message, /USD/);
    assert.match(opens.at(-1).features, /noopener/);
    step('Cantidades y totales correctos en USD/ARS; WhatsApp simulado usa la moneda y el número confirmados.');

    await page.getByRole('button', { name: 'Eliminar' }).first().click();
    await page.getByRole('button', { name: 'Eliminar' }).first().click();
    await page.locator('#cartDrawerBackdrop button').filter({ hasText: '✕' }).click();
    await page.waitForTimeout(350);
    await page.locator('#productGrid article').nth(3).getByRole('button', { name: /AGREGAR$/ }).click();
    assert.equal(await page.locator('#cartTotal').textContent(), 'ARS: consultar');
    await page.getByRole('button', { name: 'FINALIZAR PEDIDO VÍA WHATSAPP' }).click();
    opens = await page.evaluate(() => window.__opens);
    const missingPriceMessage = new URL(opens.at(-1).url).searchParams.get('text');
    assert.match(missingPriceMessage, /ARS: consultar/);
    assert.match(missingPriceMessage, /Total en ARS: a confirmar/);
    step('Un precio ausente no se convierte con una tasa inventada y el total queda a confirmar.');
    await page.locator('#cartDrawerBackdrop button').filter({ hasText: '✕' }).click();
    await page.waitForTimeout(350);

    await page.evaluate(() => {
      window.__mock.session = { user: { id: 'usuario-ficticio', email: 'falso@example.invalid', user_metadata: { full_name: '<img src=x onerror="window.__xss=5">', avatar_url: 'javascript:window.__xss=6' } } };
      window.__mock.profile = { full_name: 'Cliente de prueba', phone: '', province: '', city: '', address: '' };
      window.__mock.emit();
    });
    await page.waitForSelector('#authContainer button:has-text("Perfil")');
    assert.equal(await page.locator('#authContainer img').count(), 0);
    assert.equal(await page.locator('#btn-ars').count(), 1);
    assert.equal(await page.evaluate(() => window.__xss || 0), 0);
    await page.locator('#authContainer button').filter({ hasText: 'Perfil' }).click();
    await page.waitForFunction(() => !document.getElementById('vistaPerfil').classList.contains('hidden'));
    assert.equal(await page.locator('#perfilNombreTxt').textContent(), 'Cliente de prueba');
    await page.getByRole('button', { name: 'Editar perfil' }).click();
    await page.locator('#profFullName').fill('Nombre nuevo de prueba');
    await page.getByRole('button', { name: 'Guardar cambios' }).click();
    await page.waitForFunction(() => window.__mock.lastUpdate !== null);
    assert.equal(await page.evaluate(() => window.__mock.lastUpdate.full_name), 'Nombre nuevo de prueba');
    assert.equal(await page.evaluate(() => window.__mock.lastUpdate.id), 'usuario-ficticio');
    await page.getByRole('button', { name: 'Volver a la tienda' }).click();
    assert.equal(await page.locator('#vistaPerfil').evaluate(el => el.classList.contains('hidden')), true);
    assert.equal(await page.evaluate(() => window.__alerts.length), 0);
    step('Sesión y perfil simulados: selector conservado, texto seguro, guardado ficticio y vuelta a la tienda.');

    await page.goto(origin + '/detalle.html?id=producto-1', { waitUntil: 'networkidle' });
    assert.match(await page.locator('#app').textContent(), /USD 120,00/);
    assert.match(await page.locator('#app').textContent(), /ARS 150\.000,00/);
    assert.equal(await page.getByRole('button', { name: 'ARS' }).getAttribute('aria-pressed'), 'true');
    await page.getByRole('button', { name: 'Consultar / Pedir por WhatsApp' }).click();
    opens = await page.evaluate(() => window.__opens);
    assert.match(new URL(opens.at(-1).url).searchParams.get('text'), /ARS 150\.000,00/);
    await page.goto(origin + '/detalle.html?id=' + encodeURIComponent(products[2].id), { waitUntil: 'networkidle' });
    assert.equal(await page.locator('#app h1').textContent(), products[2].nombre);
    assert.equal(await page.locator('#app .descripcion script').count(), 0);
    assert.match(await page.locator('#app img').getAttribute('src'), /^data:image\/svg\+xml/);
    assert.equal(await page.evaluate(() => window.__xss || 0), 0);
    step('Detalle independiente muestra ambos precios, conserva la moneda y protege datos hostiles.');

    await page.goto(origin + '/', { waitUntil: 'networkidle' });
    await page.evaluate(() => localStorage.removeItem('cellzone_bienvenida_v1'));
    await context.route(origin + '/media/**', route => route.abort());
    await page.reload({ waitUntil: 'networkidle' });
    assert.equal(await page.locator('#bienvenida').evaluate(el => el.open), true);
    await page.getByRole('button', { name: 'Entrar a la tienda' }).click();
    assert.equal(await page.locator('#bienvenida').evaluate(el => el.open), false, 'Puede entrar aunque falle el video.');
    await page.evaluate(() => localStorage.removeItem('cellzone_bienvenida_v1'));
    await page.emulateMedia({ reducedMotion: 'reduce' });
    pedidosVideo.length = 0;
    await page.reload({ waitUntil: 'networkidle' });
    assert.equal(await page.locator('#bienvenida-video').evaluate(v => v.paused), true);
    assert.equal(pedidosVideo.length, 0, 'Movimiento reducido: no se descarga video automáticamente.');
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('#bienvenida').evaluate(el => el.open), false);
    await page.emulateMedia({ reducedMotion: 'no-preference' });
    step('Fallo del video, movimiento reducido y Escape no impiden entrar.');

    failCatalog = true;
    await page.goto(origin + '/', { waitUntil: 'networkidle' });
    await page.waitForFunction(() => document.getElementById('productCounter').textContent === 'No se pudo cargar el catálogo');
    assert.match(await page.locator('#productGrid').textContent(), /No se pudo conectar/);
    assert.equal(await page.evaluate(() => window.__alerts.length), 0);
    assert.deepEqual(pageErrors, []);
    assert.deepEqual(blockedUnexpected, []);
    step('Error del catálogo expresado sin alertas técnicas; cero errores no manejados.');
    console.log(`Sin red externa: ${externalIntercepted} solicitudes interceptadas o bloqueadas.`);
  } finally {
    await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
