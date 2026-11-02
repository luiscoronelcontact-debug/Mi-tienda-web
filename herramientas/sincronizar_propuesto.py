#!/usr/bin/env python3
"""Borrador NO HABILITADO del sincronizador Cellzone.

La ejecución normal solo valida un catálogo local y simula cálculos. No conecta
con NeoImport ni con Supabase y no escribe nada. La función de envío permanece
bloqueada en código hasta revisar el origen real de precios, el caso de ARS=0,
la autenticación, las políticas y una prueba separada autorizada.

El 20 % se conserva como hipótesis del script original: se aplica una sola vez
a los precios del catálogo de entrada. Nunca se debe ejecutar sobre precios que
ya tengan el margen. No se infiere una tasa USD/ARS.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from urllib.parse import urlsplit

# Interruptor de seguridad: NO cambiar sin revisión y autorización explícita.
ESCRITURA_DESHABILITADA = True
PROYECTO_ESPERADO = 'otnjxfzttdjihjcoximm.supabase.co'
FACTOR = Decimal('1.20')
CENTAVO = Decimal('0.01')


class CatalogoInvalido(ValueError):
    """El catálogo debe corregirse antes de cualquier posible escritura."""


def _texto_no_vacio(valor):
    return str(valor).strip() if valor is not None else ''


def _identificador(producto):
    presentes = [_texto_no_vacio(producto.get(k)) for k in ('id', 'codigo', 'sku')]
    presentes = [v for v in presentes if v]
    if not presentes:
        raise CatalogoInvalido('Un producto no tiene identificador.')
    if len(set(presentes)) > 1:
        raise CatalogoInvalido('Un producto tiene identificadores diferentes; revisar la correspondencia.')
    return presentes[0]


def _precio_base(valor, moneda):
    if valor is None or isinstance(valor, bool):
        raise CatalogoInvalido(f'Falta el precio de origen en {moneda}.')
    try:
        numero = Decimal(str(valor))
        if not numero.is_finite() or numero <= 0 or numero > Decimal('1000000000000'):
            raise CatalogoInvalido(f'El precio de origen en {moneda} no es positivo y válido.')
        return numero
    except (InvalidOperation, TypeError, ValueError) as exc:
        if isinstance(exc, CatalogoInvalido):
            raise
        raise CatalogoInvalido(f'El precio de origen en {moneda} no es válido.') from exc


def _stock(valor):
    if valor is None or isinstance(valor, bool):
        raise CatalogoInvalido('Falta un stock entero válido.')
    try:
        numero = Decimal(str(valor))
        if not numero.is_finite() or numero != numero.to_integral_value() or numero < 0 or numero > 2147483647:
            raise CatalogoInvalido('El stock debe ser un entero no negativo válido.')
        return int(numero)
    except (InvalidOperation, TypeError, ValueError) as exc:
        if isinstance(exc, CatalogoInvalido):
            raise
        raise CatalogoInvalido('El stock no es válido.') from exc


def preparar_productos(datos):
    """Valida todo el catálogo y prepara filas sin efectuar ninguna E/S de red."""
    if not isinstance(datos, list) or not datos:
        raise CatalogoInvalido('El catálogo debe ser una lista no vacía.')
    resultado = []
    ids = set()
    errores = []
    for indice, producto in enumerate(datos, start=1):
        try:
            if not isinstance(producto, dict):
                raise CatalogoInvalido('La fila no es un objeto.')
            identificador = _identificador(producto)
            if identificador in ids:
                raise CatalogoInvalido('Identificador repetido.')
            ids.add(identificador)
            # Solo precio USD puede usar los alias USD históricos; ARS requiere dato propio.
            origen_usd = producto.get('precio_usd', producto.get('precio', producto.get('costo', producto.get('price'))))
            origen_ars = producto.get('precio_ars')
            usd = (_precio_base(origen_usd, 'USD') * FACTOR).quantize(CENTAVO, rounding=ROUND_HALF_UP)
            ars = (_precio_base(origen_ars, 'ARS') * FACTOR).quantize(CENTAVO, rounding=ROUND_HALF_UP)
            stock = _stock(producto.get('stock', producto.get('quantity')))
            resultado.append({
                'id': identificador,
                'nombre': str(producto.get('nombre') or producto.get('title') or producto.get('name') or 'Sin nombre'),
                'categoria': str(producto.get('categoria') or 'General'),
                'precio': float(usd),
                'precio_usd': float(usd),
                'precio_ars': float(ars),
                'imagen': str(producto.get('imagen') or ''),
                'descripcion': str(producto.get('descripcion') or 'Sin descripción disponible.'),
                'stock': stock,
            })
        except (CatalogoInvalido, InvalidOperation) as exc:
            errores.append(f'fila {indice}: {exc}')
    if errores:
        vista = '; '.join(errores[:5])
        raise CatalogoInvalido(f'{len(errores)} fila(s) inválida(s). {vista}')
    return resultado


def cargar_catalogo(ruta):
    with Path(ruta).open('r', encoding='utf-8') as archivo:
        return json.load(archivo)


def enviar_lotes_bloqueado(productos, sesion=None):
    """Propuesta para revisión: el interruptor impide cualquier envío real.

    En una futura versión autorizada, la clave de escritura se obtendría solo
    del entorno privado, no del repositorio ni de la carpeta pública. No hay
    reintentos automáticos: si falla un lote, los anteriores podrían haber sido
    aplicados y habría que conciliar antes de continuar.
    """
    if ESCRITURA_DESHABILITADA:
        raise RuntimeError('Escritura deshabilitada: este borrador nunca envía datos.')
    # Además del cambio de código revisado, se exigiría una confirmación de entorno.
    if os.environ.get('CELLZONE_CONFIRMAR_ESCRITURA') != 'SI':
        raise RuntimeError('Falta confirmación explícita de escritura.')
    url = os.environ.get('SUPABASE_URL', '').rstrip('/')
    partes = urlsplit(url)
    if (partes.scheme != 'https' or partes.hostname != PROYECTO_ESPERADO
            or partes.port not in (None, 443) or partes.username or partes.password
            or partes.path or partes.query or partes.fragment):
        raise RuntimeError('La URL de Supabase no coincide con el proyecto esperado.')
    clave = os.environ.get('SUPABASE_WRITE_KEY', '')
    if not clave:
        raise RuntimeError('Falta la credencial privada de escritura en el entorno.')
    cabeceras = {
        'apikey': clave,
        'Content-Type': 'application/json',
        'Prefer': 'resolution=merge-duplicates,return=minimal',
    }
    # Las claves sb_secret_ no son JWT; para un JWT legado solo si está revisado.
    if clave.startswith('eyJ'):
        cabeceras['Authorization'] = f'Bearer {clave}'
    elif not clave.startswith('sb_secret_'):
        raise RuntimeError('La credencial no tiene un formato de escritura reconocido.')
    if sesion is None:
        import requests
        sesion = requests.Session()
    for indice in range(0, len(productos), 500):
        lote = productos[indice:indice + 500]
        try:
            respuesta = sesion.post(
                f'{url}/rest/v1/productos', headers=cabeceras, json=lote,
                timeout=30, allow_redirects=False,
            )
        except Exception as exc:
            raise RuntimeError('Falló la conexión; no se reintenta automáticamente y debe revisarse la conciliación.') from exc
        if respuesta.status_code not in (200, 201, 204):
            raise RuntimeError(f'Falló el lote {indice // 500 + 1} (HTTP {respuesta.status_code}); detener y conciliar.')
    return len(productos)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Simulación local: valida y prepara precios; no escribe ni hace conexiones.')
    parser.add_argument('catalogo', help='Ruta a un catálogo JSON para simular, preferentemente datos ficticios.')
    args = parser.parse_args(argv)
    try:
        productos = preparar_productos(cargar_catalogo(args.catalogo))
    except (OSError, json.JSONDecodeError, CatalogoInvalido) as exc:
        print(f'Simulación detenida: {exc}', file=sys.stderr)
        return 1
    print(f'Simulación válida: {len(productos)} producto(s). No se realizó ninguna conexión ni escritura.')
    print('El envío continúa bloqueado y la fuente de precios debe revisarse antes de una sincronización real.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
