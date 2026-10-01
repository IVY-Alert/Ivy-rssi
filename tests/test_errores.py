"""Casos que antes rompían el programa (encontrados al depurar)."""

import asyncio
from types import SimpleNamespace

from ivy_rssi import analisis, registrador


def test_coma_decimal_en_las_preguntas(tmp_path, monkeypatch):
    respuestas = iter(["HP", "bateria", "1,0", "abc", "0,8", "2", "pasillo", "", ""])
    monkeypatch.setattr("builtins.input", lambda *_: next(respuestas))
    meta = registrador.pedir_metadatos(auto=False)
    assert meta["altura_portatil_m"] == 1.0
    assert meta["altura_llavero_m"] == 0.8      # "abc" se rechazó y se volvió a preguntar
    assert meta["repeticion"] == 2


def _sesion_saltando(tmp_path, experimento, saltar, monkeypatch):
    """Sesión interactiva simulada que salta la condición en la posición `saltar`."""
    datos = [""] * 8                                 # metadatos por defecto
    respuestas = iter(datos + sum((["s"] if i == saltar else ["", ""] for i in range(12)), []))
    monkeypatch.setattr("builtins.input", lambda *_: next(respuestas, "t"))
    return registrador.registrar(experimento, tmp_path, segundos=3, simular=True)


def test_e2_sin_linea_de_vista_avisa_sin_romper(tmp_path, monkeypatch, capsys):
    ruta = _sesion_saltando(tmp_path, "E2", 0, monkeypatch)
    assert analisis.analizar_archivos([ruta], guardar=False) == {}
    assert "linea_de_vista" in capsys.readouterr().out


def test_e1_con_pocas_distancias_avisa(tmp_path, monkeypatch, capsys):
    respuestas = iter([""] * 8 + ["", "", "", "t"])  # mide 2 puntos y termina
    monkeypatch.setattr("builtins.input", lambda *_: next(respuestas, "t"))
    ruta = registrador.registrar("E1", tmp_path, segundos=3, simular=True)
    assert analisis.analizar_archivos([ruta], guardar=False) == {}
    assert "3 distancias" in capsys.readouterr().out


def test_sesion_vacia_avisa(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda *_: "t" if "Enter = medir" in _[0] else "")
    ruta = registrador.registrar("E4", tmp_path, segundos=3, simular=True)
    assert analisis.analizar_archivos([ruta], guardar=False) == {}
    assert "ninguna muestra" in capsys.readouterr().out


class EscanerFalso:
    """Imita a BleakScanner: emite paquetes del llavero y de otro aparato.

    Como en el firmware real, el nombre solo viene en algunos paquetes (la
    respuesta de escaneo); el resto llega sin nombre.
    """

    def __init__(self, al_detectar):
        self.al_detectar = al_detectar

    async def __aenter__(self):
        llavero = SimpleNamespace(address="aa:bb:cc:dd:ee:ff", name=None)
        otro = SimpleNamespace(address="11:22:33:44:55:66", name=None)
        paquetes = [
            (llavero, None, -60),            # anuncio sin nombre ANTES de ver el nombre
            (llavero, "GEOEXPO-ALERT", -61),  # respuesta de escaneo con el nombre
            (llavero, None, -62),            # anuncio sin nombre: ya se reconoce
            (otro, "Audifonos", -40),
            (otro, None, -41),
        ]
        for disp, nombre, rssi in paquetes:
            self.al_detectar(disp, SimpleNamespace(local_name=nombre, rssi=rssi))
        return self

    async def __aexit__(self, *_):
        return False


def test_filtro_ble_por_nombre(monkeypatch):
    monkeypatch.setattr(registrador, "_crear_escaner", EscanerFalso)
    muestras = asyncio.run(registrador._medir_ble(1))
    assert [r for _, r in muestras] == [-61, -62]


def test_filtro_ble_por_direccion(monkeypatch):
    monkeypatch.setattr(registrador, "_crear_escaner", EscanerFalso)
    muestras = asyncio.run(registrador._medir_ble(1, direccion="11:22:33:44:55:66"))
    assert [r for _, r in muestras] == [-40, -41]


def test_escaner_real_se_construye():
    # Verifica que bleak acepta nuestros argumentos (no necesita Bluetooth).
    registrador._crear_escaner(lambda d, a: None)


def test_pasada_unica_simulada(tmp_path, monkeypatch):
    from ivy_rssi.__main__ import main
    monkeypatch.chdir(tmp_path)
    main(["E1", "e4", "--simular", "--auto", "--segundos", "3"])
    figuras = list((tmp_path / "figuras").rglob("*.png"))
    assert len(figuras) == 8          # (3 de E1 + 1 de E4) × 2 formatos
