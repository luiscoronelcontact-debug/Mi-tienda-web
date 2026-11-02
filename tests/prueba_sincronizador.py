"""Pruebas sin red del borrador: solo datos y credenciales ficticios."""
import contextlib
import importlib.util
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

RUTA = Path(__file__).resolve().parents[1] / 'herramientas' / 'sincronizar_propuesto.py'
spec = importlib.util.spec_from_file_location('sync_borrador', RUTA)
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


def producto(**cambios):
    base = {'id': 'id-ficticio', 'nombre': 'Producto ficticio', 'precio_usd': 100,
            'precio_ars': 160000, 'stock': 3, 'categoria': 'Ejemplo'}
    base.update(cambios)
    return base


class RespuestaFalsa:
    def __init__(self, status):
        self.status_code = status


class SesionFalsa:
    def __init__(self, status=204):
        self.requests = []
        self.status = status

    def post(self, url, **kwargs):
        self.requests.append((url, kwargs))
        return RespuestaFalsa(self.status)


class PruebasSimuladas(unittest.TestCase):
    def test_margen_una_vez_y_monedas(self):
        filas = sync.preparar_productos([producto()])
        self.assertEqual(filas[0]['precio'], 120)
        self.assertEqual(filas[0]['precio_usd'], 120)
        self.assertEqual(filas[0]['precio_ars'], 192000)
        self.assertEqual(filas[0]['stock'], 3)

    def test_no_calcula_tipo_de_cambio_si_falta_ars(self):
        with self.assertRaisesRegex(sync.CatalogoInvalido, 'ARS'):
            sync.preparar_productos([producto(precio_ars=0)])

    def test_datos_faltantes_duplicados_y_dudosos_detienen(self):
        for datos in ([producto(precio_usd=-1)], [producto(stock=None)],
                      [producto(), producto()], [producto(codigo='otro-id')]):
            with self.subTest(datos=datos), self.assertRaises(sync.CatalogoInvalido):
                sync.preparar_productos(datos)

    def test_envio_bloqueado_incluso_si_se_entrega_sesion_falsa(self):
        sesion = SesionFalsa()
        with self.assertRaisesRegex(RuntimeError, 'deshabilitada'):
            sync.enviar_lotes_bloqueado([producto()], sesion)
        self.assertEqual(sesion.requests, [])

    def test_codigo_de_envio_solo_con_mocks_no_efectua_red(self):
        sesion = SesionFalsa()
        entorno = {'CELLZONE_CONFIRMAR_ESCRITURA': 'SI',
                   'SUPABASE_URL': 'https://otnjxfzttdjihjcoximm.supabase.co',
                   'SUPABASE_WRITE_KEY': 'sb_' + 'secret_' + 'credencial-ficticia'}
        with patch.object(sync, 'ESCRITURA_DESHABILITADA', False), patch.dict(os.environ, entorno, clear=True):
            cantidad = sync.enviar_lotes_bloqueado(sync.preparar_productos([producto()]), sesion)
        self.assertEqual(cantidad, 1)
        self.assertEqual(len(sesion.requests), 1)
        url, pedido = sesion.requests[0]
        self.assertTrue(url.startswith(entorno['SUPABASE_URL'] + '/rest/'))
        self.assertFalse(pedido['allow_redirects'])
        self.assertEqual(pedido['headers']['apikey'], entorno['SUPABASE_WRITE_KEY'])
        self.assertNotIn('Authorization', pedido['headers'])  # sb_secret no es JWT.
        self.assertEqual(pedido['json'][0]['precio_ars'], 192000)

    def test_url_incorrecta_detiene_antes_del_envio_simulado(self):
        sesion = SesionFalsa()
        entorno = {'CELLZONE_CONFIRMAR_ESCRITURA': 'SI', 'SUPABASE_URL': 'https://otro.invalid',
                   'SUPABASE_WRITE_KEY': 'sb_' + 'secret_' + 'credencial-ficticia'}
        with patch.object(sync, 'ESCRITURA_DESHABILITADA', False), patch.dict(os.environ, entorno, clear=True):
            with self.assertRaisesRegex(RuntimeError, 'URL'):
                sync.enviar_lotes_bloqueado(sync.preparar_productos([producto()]), sesion)
        self.assertEqual(sesion.requests, [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
