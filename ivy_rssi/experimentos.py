"""Los cinco experimentos, definidos en un solo lugar.

Cada condición es una tupla (etiqueta, valor, instrucción):
- etiqueta: texto corto que va a la columna `condicion` del CSV.
- valor: número que va a `valor_condicion` (distancia en m o ángulo en °),
  o None cuando la condición no es numérica (por ejemplo "en_la_mano").
- instrucción: lo que el registrador le pide al usuario antes de medir.
"""

# Distancia fija (m) a la que se hacen E2, E3 y E4.
DISTANCIA_FIJA_M = 2.0

# Paso (m) con el que se aleja el llavero en E5.
PASO_E5_M = 2.0


def _distancias(lista_m):
    return [(f"{d:g} m", d, f"Pon el llavero a {d:g} m del portátil") for d in lista_m]


EXPERIMENTOS = {
    "E1": {
        "nombre": "RSSI vs. distancia",
        "unidad": "m",
        "condiciones": _distancias([0.25, 0.5, 1, 1.5, 2, 3, 4, 5, 6, 8, 10]),
    },
    "E2": {
        "nombre": "El cuerpo como obstáculo",
        "unidad": None,
        "condiciones": [
            ("linea_de_vista", None, "Llavero a 2 m, en línea de vista, sin nadie en medio"),
            ("en_la_mano", None, "Llavero a 2 m, sostenido en la mano (brazo extendido al lado)"),
            ("bolsillo", None, "Llavero a 2 m, dentro del bolsillo del pantalón"),
            ("persona_en_medio", None, "Llavero a 2 m, con una persona de pie entre el llavero y el portátil"),
            ("morral", None, "Llavero a 2 m, dentro de un morral cerrado"),
        ],
    },
    "E3": {
        "nombre": "Patrón de radiación",
        "unidad": "°",
        "condiciones": [
            (f"{a}°", a, f"Llavero a 2 m, girado {a}° respecto a la marca de 0°")
            for a in range(0, 360, 30)
        ],
    },
    "E4": {
        "nombre": "Antena vs. batería",
        "unidad": None,
        "condiciones": [
            ("antena_sobresale", None, "Llavero a 2 m, antena sobresaliendo de la batería (diseño final)"),
            ("antena_encima", None, "Llavero a 2 m, antena encima de la batería"),
            ("sin_bateria", None, "Llavero a 2 m, sin batería cerca (alimentado por cable o power bank lejos)"),
        ],
    },
    "E5": {
        "nombre": "Alcance máximo",
        "unidad": "m",
        # E5 no tiene lista fija: el registrador genera 2, 4, 6... con
        # condicion_e5() hasta que se pierde la señal.
        "condiciones": [],
        "abierto": True,
    },
}


def condicion_e5(indice):
    """Condición número `indice` (0, 1, 2...) de E5: 2 m, 4 m, 6 m..."""
    d = PASO_E5_M * (indice + 1)
    return _distancias([d])[0]
