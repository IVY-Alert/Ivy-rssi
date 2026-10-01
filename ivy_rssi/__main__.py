"""Todo de una sola pasada: medir → analizar → graficar.

Uso:
    python -m ivy_rssi                      # los 5 experimentos, uno tras otro
    python -m ivy_rssi E1 E2                # solo esos
    python -m ivy_rssi --simular --auto     # demo sin Bluetooth ni preguntas

Los datos quedan en datos/ y las figuras en figuras/<fecha-hora>/.
"""

import argparse
import time
from pathlib import Path

import numpy as np

from . import analisis, graficas
from .experimentos import EXPERIMENTOS
from .registrador import pedir_metadatos, preparar_consola, registrar


def main(argv=None):
    preparar_consola()
    p = argparse.ArgumentParser(description="Mide, analiza y grafica de una sola pasada.")
    p.add_argument("experimentos", nargs="*", help="E1 ... E5 (por defecto, todos)")
    p.add_argument("--simular", action="store_true", help="datos sintéticos, sin Bluetooth")
    p.add_argument("--auto", action="store_true", help="no preguntar nada")
    p.add_argument("--segundos", type=float, default=30, help="duración de cada punto")
    p.add_argument("--direccion", help="filtrar por dirección MAC en vez de por nombre")
    p.add_argument("--carpeta", default="datos")
    args = p.parse_args(argv)
    experimentos = [e.upper() for e in args.experimentos] or sorted(EXPERIMENTOS)
    for e in experimentos:
        if e not in EXPERIMENTOS:
            p.error(f"experimento desconocido: {e} (usa E1 ... E5)")

    # Los datos de la sesión (portátil, alturas...) se piden UNA vez para todo.
    meta = pedir_metadatos(args.auto)
    rng = np.random.default_rng() if args.simular else None

    rutas = []
    try:
        for exp in experimentos:
            rutas.append(registrar(exp, args.carpeta, args.segundos, args.simular,
                                   args.direccion, args.auto, meta, rng, pedir_datos=False))
    except KeyboardInterrupt:
        print("\nMedición interrumpida: se analiza lo que alcanzó a guardarse.")

    if not rutas:
        print("No se midió nada.")
        return
    print("\n" + "=" * 60 + "\nRESULTADOS")
    analisis.analizar_archivos(rutas)
    salida = Path("figuras") / time.strftime("%Y%m%d-%H%M%S")
    creadas = graficas.graficar_archivos(rutas, salida)
    print(f"\n{len(creadas)} figuras en {salida}/  (miren las *_video.png)")


if __name__ == "__main__":
    main()
