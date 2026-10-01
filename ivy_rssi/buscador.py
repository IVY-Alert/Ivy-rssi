"""Modo buscador: ¿dónde está el llavero? RSSI en vivo, distancia estimada
y una barra de "frío/caliente".

Uso:
    python -m ivy_rssi.buscador [--simular] [--direccion AA:BB:...]

La distancia sale de invertir el modelo log-distancia calibrado en E1. Su
incertidumbre es grande (ver FISICA.md): sirve para guiarse, no para medir.
"""

import argparse
import asyncio
import statistics
import time

import numpy as np

from . import fisica
from .analisis import calibracion

VENTANA_S = 2.0      # se usa la mediana de los últimos 2 s (suaviza el desvanecimiento)
PISO_DBM, TECHO_DBM = -95.0, -40.0
ANCHO_BARRA = 30


def barra(rssi):
    """Barra de texto: llena = muy cerca, vacía = en el límite de alcance."""
    llenas = round(ANCHO_BARRA * np.clip((rssi - PISO_DBM) / (TECHO_DBM - PISO_DBM), 0, 1))
    return "█" * llenas + "·" * (ANCHO_BARRA - llenas)


def linea_estado(muestras, ahora, cal, rssi_antes=None):
    """Texto de una actualización a partir de las muestras recientes.

    Devuelve (texto, rssi_suavizado) o (None, None) si no hay muestras.
    """
    recientes = [r for t, r in muestras if ahora - t <= VENTANA_S]
    if not recientes:
        return None, None
    rssi = statistics.median(recientes)
    d, d_min, d_max = fisica.distancia_desde_rssi(rssi, cal["rssi_d0"], cal["n"], cal["sigma_db"])
    tendencia = ""
    if rssi_antes is not None:
        # Más de 3 dB de cambio es más que el temblor normal de la señal.
        if rssi - rssi_antes > 3:
            tendencia = "  ▲ más caliente"
        elif rssi_antes - rssi > 3:
            tendencia = "  ▼ más frío"
    texto = (f"{barra(rssi)} {rssi:5.0f} dBm  ≈ {d:4.1f} m "
             f"({d_min:.1f}–{d_max:.1f} m){tendencia}")
    return texto, rssi


async def _escuchar(muestras, direccion, simular, duracion, al_actualizar):
    """Recibe muestras (reales o simuladas) y llama al_actualizar cada 0.5 s."""
    inicio = time.time()
    rng = np.random.default_rng()
    if not simular:
        from .registrador import _crear_escaner, crear_filtro
        escaner = _crear_escaner(crear_filtro(muestras, direccion))
        await escaner.start()
    try:
        while duracion is None or time.time() - inicio < duracion:
            await asyncio.sleep(0.5)
            if simular:
                # Alguien camina hacia el llavero: de 12 m a 0.5 m en ~40 s.
                d = max(0.5, 12 - 0.3 * (time.time() - inicio))
                for _ in range(4):
                    rssi = (fisica.rssi_log_distancia(d, -55, 2.2) + rng.normal(0, 2))
                    muestras.append((time.time(), int(round(rssi))))
            al_actualizar(time.time())
    finally:
        if not simular:
            await escaner.stop()


def buscar(direccion=None, simular=False, duracion=None, carpeta="datos"):
    """Bucle principal del buscador. Ctrl+C para salir."""
    cal = calibracion(carpeta)
    origen = "calibrado con tu E1" if cal["medida"] else "valores típicos (aún no hay E1)"
    print(f"\nBUSCADOR — modelo: RSSI(1 m) = {cal['rssi_d0']:.0f} dBm, "
          f"n = {cal['n']:.2f}, σ = {cal['sigma_db']:.1f} dB ({origen})")
    print("Camina con el portátil; la barra se llena al acercarte. Ctrl+C para salir.\n")

    muestras = []
    historial = []          # (tiempo, rssi suavizado) para la tendencia
    ultimo_dato = [time.time()]

    def al_actualizar(ahora):
        antes = [r for t, r in historial if ahora - t >= VENTANA_S]
        texto, rssi = linea_estado(muestras, ahora, cal, antes[-1] if antes else None)
        if texto is None:
            if ahora - ultimo_dato[0] > 10:
                texto = "Sin señal hace 10 s: ¿llavero encendido y sin conectar al celular?"
            else:
                texto = "Buscando..."
        else:
            ultimo_dato[0] = ahora
            historial.append((ahora, rssi))
            del historial[:-20]
        print(f"\r{texto:<80}", end="", flush=True)

    try:
        asyncio.run(_escuchar(muestras, direccion, simular, duracion, al_actualizar))
    except KeyboardInterrupt:
        pass
    print("\nBuscador terminado.")
    return muestras


def main(argv=None):
    from .registrador import preparar_consola
    preparar_consola()
    p = argparse.ArgumentParser(description="Busca el llavero con el RSSI en vivo.")
    p.add_argument("--simular", action="store_true")
    p.add_argument("--direccion")
    p.add_argument("--carpeta", default="datos")
    args = p.parse_args(argv)
    buscar(args.direccion, args.simular, carpeta=args.carpeta)


if __name__ == "__main__":
    main()
