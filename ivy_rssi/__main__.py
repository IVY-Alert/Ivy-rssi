"""Programa principal de Ivy RSSI: entras, eliges una prueba y la ejecutas.

Uso:
    python -m ivy_rssi            # con el llavero
    python -m ivy_rssi --simular  # sin Bluetooth, con datos simulados

Después de cada prueba muestra los resultados y genera las figuras. Si una
prueba ya tiene repeticiones anteriores en datos/, las combina. También trae
el modo buscador y, para los curiosos de la física, una calculadora.
"""

import argparse
from pathlib import Path

import numpy as np

from . import analisis, buscador, calculadora, graficas
from .experimentos import EXPERIMENTOS
from .registrador import pedir_metadatos, preparar_consola, registrar


def _menu(simular, segundos):
    print("\n" + "=" * 52)
    print("  IVY RSSI — pruebas de señal" + ("   [SIMULADO]" if simular else ""))
    print("=" * 52)
    for i, (clave, exp) in enumerate(sorted(EXPERIMENTOS.items()), start=1):
        print(f"  {i}) {clave}  {exp['nombre']}")
    print("  ─────")
    print("  6) Resultados y figuras de todo lo medido")
    print("  7) Buscador: ¿dónde está el llavero? (RSSI en vivo)")
    print("  8) Para curiosos: calculadora física a una distancia")
    print(f"  9) Cambiar segundos por punto (ahora {segundos:g} s)")
    print("  0) Salir")
    return input("\nElige una opción: ").strip()


def _resultados(rutas, carpeta_figuras):
    """Analiza las sesiones dadas, imprime los resultados y genera las figuras."""
    if not rutas:
        print("Todavía no hay mediciones.")
        return
    analisis.analizar_archivos(rutas)
    creadas = graficas.graficar_archivos(rutas, carpeta_figuras)
    if creadas:
        print(f"\nFiguras en {carpeta_figuras}/ (las *_video.png son para el video)")


def main(argv=None):
    preparar_consola()
    p = argparse.ArgumentParser(description="Menú de pruebas de señal del llavero Ivy.")
    p.add_argument("--simular", action="store_true", help="datos sintéticos, sin Bluetooth")
    p.add_argument("--segundos", type=float, default=30, help="duración de cada punto")
    p.add_argument("--direccion", help="filtrar por dirección MAC en vez de por nombre")
    p.add_argument("--carpeta", default="datos")
    args = p.parse_args(argv)

    claves = sorted(EXPERIMENTOS)
    segundos = args.segundos
    rng = np.random.default_rng() if args.simular else None
    carpeta = Path(args.carpeta)

    # Los datos de la sesión (portátil, alturas...) se piden UNA vez al entrar.
    meta = pedir_metadatos(auto=False)

    while True:
        opcion = _menu(args.simular, segundos)
        if opcion == "0":
            print("Hasta luego.")
            break

        if opcion in {"1", "2", "3", "4", "5"}:
            exp = claves[int(opcion) - 1]
            try:
                registrar(exp, carpeta, segundos, args.simular, args.direccion,
                          metadatos=meta, rng=rng, pedir_datos=False)
            except KeyboardInterrupt:
                print("\nPrueba interrumpida; los puntos terminados quedaron guardados.")
            # Resultados de esta prueba, junto con sus repeticiones anteriores.
            rutas = [r for r in analisis.sesiones_en(carpeta) if r.stem.startswith(exp + "_")]
            _resultados(rutas, Path("figuras"))

        elif opcion == "6":
            rutas = analisis.sesiones_en(carpeta)
            if not rutas:
                print("Todavía no hay mediciones.")
                continue
            _resultados(rutas, Path("figuras"))
            graficas.graficar_teoria(Path("figuras"))

        elif opcion == "7":
            buscador.buscar(args.direccion, args.simular, carpeta=carpeta)

        elif opcion == "8":
            r = input("Distancia en metros: ").strip().replace(",", ".")
            try:
                print("\n" + calculadora.ficha(float(r), carpeta))
            except ValueError:
                print("No es un número.")

        elif opcion == "9":
            r = input("Segundos por punto: ").strip().replace(",", ".")
            try:
                segundos = float(r)
            except ValueError:
                print("No es un número; sigue igual.")

        else:
            print("Opción no válida.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nHasta luego.")
