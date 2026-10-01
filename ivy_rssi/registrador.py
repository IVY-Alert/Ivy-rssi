"""Registrador de RSSI: escucha los anuncios BLE del llavero y guía el protocolo.

Uso:
    python -m ivy_rssi.registrador --experimento E1 [--simular] [--segundos 30]

Cada anuncio recibido es una muestra (timestamp, RSSI). El programa recorre
las condiciones del experimento, mide N segundos en cada una y guarda el
punto en disco apenas termina.
"""

import argparse
import asyncio
import platform
import statistics
import sys
import time

import numpy as np

from . import sesion
from .experimentos import EXPERIMENTOS, condicion_e5

NOMBRE_LLAVERO = "GEOEXPO-ALERT"
AVISO_SIN_MUESTRAS_S = 10


# --- Escaneo BLE real -------------------------------------------------------

def _crear_escaner(al_detectar):
    """Crea el BleakScanner con las opciones correctas para cada sistema.

    - Escaneo ACTIVO (el valor por defecto de bleak). El firmware pone el
      nombre "GEOEXPO-ALERT" en la *respuesta de escaneo* (scan response),
      no en el anuncio. Un escaneo pasivo nunca pide esa respuesta, así que
      jamás vería el nombre. En activo el portátil manda un SCAN_REQ y el
      llavero contesta; las dos cosas traen RSSI y ambas sirven de muestra.
    - En Linux, BlueZ descarta por defecto los anuncios repetidos del mismo
      dispositivo y llegan poquísimas muestras. El filtro de descubrimiento
      DuplicateData=True le pide que los entregue todos.
    - En Windows los repetidos llegan solos; el argumento bluez= se ignora.
    """
    from bleak import BleakScanner

    return BleakScanner(
        detection_callback=al_detectar,
        scanning_mode="active",
        bluez={"filters": {"DuplicateData": True}},
    )


async def _medir_ble(segundos, direccion=None):
    """Escucha durante `segundos` y devuelve la lista de (timestamp, rssi)."""
    muestras = []
    conocidas = set()       # direcciones que ya mostraron el nombre del llavero
    if direccion:
        conocidas.add(direccion.upper())

    def al_detectar(dispositivo, anuncio):
        dir_ = dispositivo.address.upper()
        if not direccion:
            # El nombre solo viene en algunos paquetes (la respuesta de
            # escaneo). Recordamos la dirección para aceptar también los
            # anuncios que llegan sin nombre.
            nombre = anuncio.local_name or dispositivo.name
            if nombre == NOMBRE_LLAVERO:
                conocidas.add(dir_)
        if dir_ in conocidas:
            muestras.append((time.time(), anuncio.rssi))

    inicio = time.time()
    avisado = False
    async with _crear_escaner(al_detectar):
        while (transcurrido := time.time() - inicio) < segundos:
            await asyncio.sleep(1)
            _mostrar_en_vivo(transcurrido, muestras)
            if not muestras and transcurrido >= AVISO_SIN_MUESTRAS_S and not avisado:
                print("\n  ⚠ No llega ninguna muestra. ¿El llavero está encendido "
                      "y SIN conectar al celular? (conectado deja de anunciar)")
                avisado = True
    print()
    return muestras


def _mostrar_en_vivo(transcurrido, muestras):
    if muestras:
        media = statistics.fmean(r for _, r in muestras)
        texto = f"{len(muestras):5d} muestras | RSSI medio {media:6.1f} dBm"
    else:
        texto = "    0 muestras"
    print(f"\r  {transcurrido:4.0f} s | {texto}   ", end="", flush=True)


# --- Un punto de medición ---------------------------------------------------

def medir_punto(experimento, etiqueta, valor, segundos, simular, direccion, rng):
    """Mide un punto (real o simulado) y devuelve (muestras, resumen)."""
    t_inicio = time.time()
    if simular:
        from .simulador import simular_punto
        muestras = simular_punto(experimento, etiqueta, valor, segundos, rng, t_inicio)
        _mostrar_en_vivo(segundos, muestras)
        print()
        t_fin = t_inicio + segundos
    else:
        muestras = asyncio.run(_medir_ble(segundos, direccion))
        t_fin = time.time()

    rssi = [r for _, r in muestras]
    duracion = t_fin - t_inicio
    resumen = {
        "condicion": etiqueta,
        "valor": valor,
        "n_muestras": len(rssi),
        "duracion_s": round(duracion, 2),
        "tasa_hz": round(len(rssi) / duracion, 2),
        "mediana_dbm": statistics.median(rssi) if rssi else None,
        "promedio_dbm": round(statistics.fmean(rssi), 2) if rssi else None,
        # Ventana de tiempo del punto (con 1 ms de margen por el redondeo del
        # CSV), para poder descartarlo si el usuario lo repite.
        "t_inicio": round(t_inicio, 3) - 0.001,
        "t_fin": round(t_fin, 3) + 0.001,
        "descartado": False,
    }
    return muestras, resumen


def _imprimir_resumen(r):
    if r["n_muestras"] == 0:
        print("  → 0 muestras en este punto.")
        return
    print(f"  → {r['n_muestras']} muestras | tasa {r['tasa_hz']:.1f} muestras/s | "
          f"mediana {r['mediana_dbm']:.0f} dBm | promedio {r['promedio_dbm']:.1f} dBm")
    # Tasa baja con señal FUERTE = problema del escáner, no de la física
    # (con señal débil es normal: es justo lo que mide E5).
    if r["tasa_hz"] < 2 and r["mediana_dbm"] > -85:
        print("  ⚠ Pocas muestras con señal fuerte. En Linux revisa que BlueZ acepte "
              "DuplicateData (ver README) y que no haya otro programa escaneando.")


# --- Metadatos --------------------------------------------------------------

def _preguntar(texto, defecto=""):
    r = input(f"  {texto} [{defecto}]: ").strip()
    return r or defecto


def _preguntar_numero(texto, defecto, tipo=float):
    """Pide un número; acepta coma decimal ("1,0") y vuelve a preguntar si no es válido."""
    while True:
        r = _preguntar(texto, defecto).replace(",", ".")
        try:
            return tipo(r)
        except ValueError:
            print(f"  '{r}' no es un número válido.")


def pedir_metadatos(auto, extra=None):
    """Datos de la sesión. En modo --auto usa valores por defecto sin preguntar."""
    meta = {
        "fecha": time.strftime("%Y-%m-%d %H:%M:%S"),
        "sistema_operativo": platform.platform(),
        "python": platform.python_version(),
        "portatil": "",
        "fuente_alimentacion": "",
        "altura_portatil_m": 1.0,
        "altura_llavero_m": 1.0,
        "repeticion": 1,
        "lugar": "pasillo",
        "interferencias": "",
        "notas": "",
    }
    if not auto:
        print("\nDatos de la sesión (Enter = valor entre corchetes):")
        meta["portatil"] = _preguntar("Portátil (marca/modelo)")
        meta["fuente_alimentacion"] = _preguntar(
            "Fuente del llavero (power bank / batería / cargador)", "batería")
        meta["altura_portatil_m"] = _preguntar_numero("Altura del portátil (m)", "1.0")
        meta["altura_llavero_m"] = _preguntar_numero("Altura del llavero (m)", "1.0")
        meta["repeticion"] = _preguntar_numero("Número de repetición", "1", int)
        meta["lugar"] = _preguntar("Lugar (pasillo / espacio abierto)", "pasillo")
        meta["interferencias"] = _preguntar("Wi-Fi o microondas cerca (anotar)", "")
        meta["notas"] = _preguntar("Notas libres", "")
    meta.update(extra or {})
    return meta


# --- Protocolo guiado -------------------------------------------------------

def registrar(experimento, carpeta="datos", segundos=30, simular=False,
              direccion=None, auto=False, metadatos=None, rng=None,
              pedir_datos=True):
    """Recorre las condiciones del experimento y guarda la sesión.

    Devuelve la ruta del CSV. Con auto=True no pregunta nada (útil para el
    modo simulado y los tests). Con pedir_datos=False usa `metadatos` tal
    cual, sin preguntarlos (la pasada única los pide una sola vez).
    """
    from .simulador import SEMILLA
    if rng is None:
        rng = np.random.default_rng(SEMILLA)

    exp = EXPERIMENTOS[experimento]
    meta = pedir_metadatos(auto or not pedir_datos, metadatos)
    meta.update({"simulado": simular, "segundos_por_punto": segundos,
                 "nombre_buscado": NOMBRE_LLAVERO, "direccion": direccion})
    ruta = sesion.nueva_sesion(carpeta, experimento, meta)
    print(f"\n{experimento}: {exp['nombre']}  →  {ruta}")

    abierto = exp.get("abierto", False)
    i = 0
    while True:
        if abierto:
            etiqueta, valor, instruccion = condicion_e5(i)
        elif i < len(exp["condiciones"]):
            etiqueta, valor, instruccion = exp["condiciones"][i]
        else:
            break

        print(f"\n[{i + 1}] {instruccion}.")
        if not auto:
            r = input("  Enter = medir · s = saltar · t = terminar: ").strip().lower()
            if r == "t":
                break
            if r == "s":
                i += 1
                continue
            print("  (Apártate de la línea de vista)")

        muestras, resumen = medir_punto(experimento, etiqueta, valor, segundos,
                                        simular, direccion, rng)
        sesion.guardar_punto(ruta, experimento, etiqueta, valor, muestras, resumen)
        _imprimir_resumen(resumen)

        senal_perdida = abierto and resumen["n_muestras"] == 0
        if auto:
            if senal_perdida:
                print("  Señal perdida: fin de E5.")
                break
            i += 1
            continue

        if senal_perdida:
            r = input("  ¿Se perdió la señal? Enter = terminar E5 · c = continuar "
                      "· r = repetir: ").strip().lower()
            if r == "":
                break
        else:
            r = input("  Enter = siguiente · r = repetir este punto · t = terminar: ").strip().lower()
        if r == "r":
            sesion.descartar_ultimo_punto(ruta)
            print("  Punto descartado; se repite.")
            continue
        if r == "t":
            break
        i += 1

    print(f"\nSesión guardada en {ruta} (+ {sesion.ruta_json(ruta).name})")
    return ruta


def preparar_consola():
    """En Windows, si la salida va a un archivo, los símbolos (σ, →, ⚠) podrían
    romper el programa; con errors="replace" se cambian por '?' y sigue."""
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(errors="replace")


def main(argv=None):
    preparar_consola()
    p = argparse.ArgumentParser(description="Registra el RSSI del llavero Ivy.")
    p.add_argument("--experimento", required=True, choices=sorted(EXPERIMENTOS))
    p.add_argument("--simular", action="store_true", help="datos sintéticos, sin Bluetooth")
    p.add_argument("--segundos", type=float, default=30, help="duración de cada punto")
    p.add_argument("--direccion", help="filtrar por dirección MAC en vez de por nombre")
    p.add_argument("--carpeta", default="datos")
    p.add_argument("--auto", action="store_true",
                   help="no preguntar nada (útil con --simular)")
    p.add_argument("--repeticion", type=int, help="número de repetición (con --auto)")
    p.add_argument("--semilla", type=int, help="semilla del simulador")
    args = p.parse_args(argv)

    extra = {"repeticion": args.repeticion} if args.repeticion else None
    rng = np.random.default_rng(args.semilla) if args.semilla is not None else None
    try:
        registrar(args.experimento, args.carpeta, args.segundos, args.simular,
                  args.direccion, args.auto, extra, rng)
    except KeyboardInterrupt:
        print("\nInterrumpido. Los puntos ya terminados están guardados.")
    except Exception as e:  # errores típicos de Bluetooth apagado o sin permisos
        # En Linux sin BlueZ corriendo, dbus da FileNotFoundError/ConnectionRefusedError.
        if type(e).__name__.startswith("Bleak") or isinstance(e, (FileNotFoundError, ConnectionError)):
            print(f"\nError de Bluetooth: {e}\n¿Está encendido el Bluetooth del portátil? "
                  "En Linux: `bluetoothctl power on`.", file=sys.stderr)
            sys.exit(1)
        raise


if __name__ == "__main__":
    main()
