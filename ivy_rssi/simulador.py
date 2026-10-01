"""Datos sintéticos, pero físicamente realistas, para probar todo sin hardware.

El RSSI de cada muestra se arma con tres capas, de la más lenta a la más rápida:

    RSSI = modelo determinista (distancia, obstáculo, ángulo)
         + sombreado X_σ (fijo en cada punto; σ = 3 dB)
         + desvanecimiento rápido (cambia en cada paquete; ~2 dB)

y luego se redondea a entero, porque el radio del portátil reporta dBm enteros.
Un paquete solo "llega" si su RSSI supera la sensibilidad del receptor:
así aparece la caída de la tasa de paquetes en E5.
"""

import time

import numpy as np

from . import fisica
from .experimentos import DISTANCIA_FIJA_M

SEMILLA = 2026

# Parámetros del "mundo" simulado.
RSSI_1M = -55.0          # dBm a 1 m
N_SIM = 2.2              # exponente de pérdida
SIGMA_SOMBRA = 3.0       # dB, sombreado log-normal (por punto) en E1 y E5
# En E2, E3 y E4 el llavero NO cambia de sitio: el multitrayecto del pasillo
# es casi el mismo en todas las condiciones y se cancela al comparar. Solo
# queda una variación pequeña (mover la mano, girar el llavero unos cm).
SIGMA_SOMBRA_FIJO = 1.0
SIGMA_RAPIDO = 2.0       # dB, desvanecimiento rápido (por muestra)
TASA_ANUNCIOS = 8.0      # anuncios recibidos por segundo cuando la señal es buena
SENSIBILIDAD = -95.0     # dBm; por debajo de esto el paquete se pierde

# Atenuación extra (dB) de cada condición de E2 y E4.
ATENUACION_E2 = {
    "linea_de_vista": 0.0,
    "en_la_mano": 3.0,
    "bolsillo": 10.0,
    "persona_en_medio": 17.0,
    "morral": 8.0,
}
ATENUACION_E4 = {
    "antena_sobresale": 0.0,
    "antena_encima": 8.0,
    "sin_bateria": -1.0,   # sin el metal cerca, un poco mejor que el diseño final
}

# E3: nulo suave de ~10 dB centrado en este ángulo (detrás de la batería).
ANGULO_NULO = 210.0


def ganancia_patron_db(angulo_grados):
    """Patrón de radiación simulado: 0 dB casi siempre y un nulo de 10 dB.

    Forma gaussiana en el ángulo (ancho ~50°) más un pequeño rizado de ±1 dB,
    como el de una antena de PCB real afectada por la placa y la batería.
    """
    delta = (np.asarray(angulo_grados, dtype=float) - ANGULO_NULO + 180) % 360 - 180
    return -10 * np.exp(-(delta / 50) ** 2) + 1.0 * np.cos(np.radians(2 * angulo_grados))


def rssi_esperado(experimento, etiqueta, valor):
    """RSSI medio (sin aleatoriedad) de una condición."""
    if experimento in ("E1", "E5"):
        return fisica.rssi_log_distancia(valor, RSSI_1M, N_SIM)
    base = fisica.rssi_log_distancia(DISTANCIA_FIJA_M, RSSI_1M, N_SIM)
    if experimento == "E2":
        return base - ATENUACION_E2[etiqueta]
    if experimento == "E3":
        return base + ganancia_patron_db(valor)
    if experimento == "E4":
        return base - ATENUACION_E4[etiqueta]
    raise ValueError(f"Experimento desconocido: {experimento}")


def simular_punto(experimento, etiqueta, valor, segundos, rng, t_inicio=None):
    """Muestras de UN punto: lista de (timestamp, rssi_dbm).

    Los anuncios llegan como un proceso de Poisson (intervalos aleatorios),
    que es lo que se ve en un escáner real: el ESP32 anuncia periódicamente,
    pero el portátil salta entre los 3 canales y no oye todos.
    """
    if t_inicio is None:
        t_inicio = time.time()
    media = rssi_esperado(experimento, etiqueta, valor)
    sigma = SIGMA_SOMBRA if experimento in ("E1", "E5") else SIGMA_SOMBRA_FIJO
    sombra = rng.normal(0, sigma)             # una sola vez por punto

    n_intentos = rng.poisson(TASA_ANUNCIOS * segundos)
    tiempos = np.sort(rng.uniform(0, segundos, n_intentos)) + t_inicio
    rssi = media + sombra + rng.normal(0, SIGMA_RAPIDO, n_intentos)

    # Recepción: cerca de la sensibilidad el paquete se pierde con más
    # probabilidad (curva suave de ~2 dB de ancho, no un corte brusco).
    p_recibir = 1 / (1 + np.exp(-(rssi - SENSIBILIDAD) / 1.0))
    llega = rng.uniform(size=n_intentos) < p_recibir
    return [(float(t), int(round(r))) for t, r in zip(tiempos[llega], rssi[llega])]


def generar_ejemplo(carpeta, semilla=SEMILLA, segundos=30, repeticiones_e1=3):
    """Genera sesiones de los cinco experimentos (E1 con varias repeticiones).

    Devuelve la lista de rutas CSV creadas.
    """
    from .registrador import registrar  # aquí para evitar importación circular

    rng = np.random.default_rng(semilla)
    rutas = []
    for exp in ["E1", "E2", "E3", "E4", "E5"]:
        reps = repeticiones_e1 if exp == "E1" else 1
        for rep in range(1, reps + 1):
            meta = {"repeticion": rep, "notas": "Datos SIMULADOS"}
            rutas.append(registrar(exp, carpeta, segundos, simular=True,
                                   auto=True, metadatos=meta, rng=rng))
    return rutas


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Genera sesiones simuladas de los 5 experimentos.")
    p.add_argument("--carpeta", default="datos/simulados")
    p.add_argument("--semilla", type=int, default=SEMILLA)
    args = p.parse_args()
    for r in generar_ejemplo(args.carpeta, args.semilla):
        print(r)
