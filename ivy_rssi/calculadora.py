"""Calculadora física: toda la física del enlace para una distancia dada.

Uso:
    python -m ivy_rssi.calculadora 5        # ficha para 5 m
"""

import argparse

from . import fisica
from .analisis import calibracion


def ficha(d_m, carpeta="datos"):
    """Texto con lo que dice cada modelo físico a la distancia d_m."""
    cal = calibracion(carpeta)
    lam = fisica.longitud_onda()
    rssi = float(fisica.rssi_log_distancia(d_m, cal["rssi_d0"], cal["n"]))
    margen = rssi - fisica.SENSIBILIDAD_TIPICA_DBM
    eps1, eps2 = fisica.permitividad_debye(fisica.FRECUENCIA_MICROONDAS_HZ)
    origen = "tu E1" if cal["medida"] else "valores típicos"
    lineas = [
        f"FICHA FÍSICA A {d_m:g} m",
        "",
        "Onda",
        f"  λ = c/f = {100 * lam:.1f} cm  →  la distancia son {d_m / lam:.0f} longitudes de onda",
        f"  Antena de cuarto de onda λ/4 = {100 * lam / 4:.1f} cm",
        "",
        "Propagación",
        f"  Espacio libre (Friis): {float(fisica.fspl_db(d_m)):.1f} dB de pérdida",
        f"  Dos rayos (piso, alturas 1 m): {float(fisica.perdida_dos_rayos_db(d_m)):.1f} dB "
        f"(quiebre a {fisica.distancia_quiebre(1, 1):.0f} m)",
        f"  Zona de Fresnel en la mitad: r1 = {100 * fisica.radio_fresnel(d_m / 2, d_m / 2):.0f} cm "
        "(mantenla libre)",
        "",
        f"Modelo log-distancia ({origen}: RSSI(1 m) = {cal['rssi_d0']:.0f} dBm, n = {cal['n']:.2f})",
        f"  RSSI esperado: {rssi:.1f} dBm ± {cal['sigma_db']:.1f} dB",
        f"  Margen sobre la sensibilidad ({fisica.SENSIBILIDAD_TIPICA_DBM:.0f} dBm): {margen:.1f} dB",
        f"  Alcance predicho: {fisica.alcance_predicho(cal['rssi_d0'], cal['n']):.0f} m",
        "",
        "Cuerpo humano (músculo a 2.45 GHz)",
        f"  Profundidad de penetración δ = {100 * fisica.profundidad_penetracion():.2f} cm, "
        f"{fisica.atenuacion_db_por_cm():.1f} dB/cm",
        f"  Persona en la mitad (difracción por sus costados): ≈ "
        f"{fisica.perdida_persona_db(d_m):.0f} dB",
        f"  Agua a 2.45 GHz (Debye): ε' = {eps1:.1f}, ε'' = {eps2:.1f}; "
        f"pico de absorción a {fisica.frecuencia_pico_perdidas() / 1e9:.0f} GHz",
        "",
        "Seguridad",
        f"  SAR ≤ {fisica.sar_cota_w_kg():.2f} W/kg en el peor caso imposible "
        "(límite ICNIRP: 2 W/kg)",
    ]
    return "\n".join(lineas)


def main(argv=None):
    from .registrador import preparar_consola
    preparar_consola()
    p = argparse.ArgumentParser(description="Física del enlace a una distancia dada.")
    p.add_argument("distancia", type=float, help="distancia en metros")
    p.add_argument("--carpeta", default="datos")
    args = p.parse_args(argv)
    print(ficha(args.distancia, args.carpeta))


if __name__ == "__main__":
    main()
