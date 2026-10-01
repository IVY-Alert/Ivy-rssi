"""Modelos físicos de propagación de la onda de 2.4 GHz del llavero.

Todo está en unidades del SI salvo donde se dice (dB, dBm, cm).
"""

import numpy as np
from scipy import stats

# --- Constantes -------------------------------------------------------------

C = 299_792_458.0            # velocidad de la luz en el vacío (m/s)
EPSILON_0 = 8.8541878128e-12  # permitividad del vacío (F/m)
MU_0 = 4e-7 * np.pi           # permeabilidad del vacío (H/m), aprox. exacta

# BLE anuncia en tres canales: 37 (2402 MHz), 38 (2426 MHz) y 39 (2480 MHz).
# Usamos el centro de la banda como frecuencia representativa.
FRECUENCIA_BLE_HZ = 2.44e9

# Frecuencia del horno microondas y de las tablas de tejidos.
FRECUENCIA_MICROONDAS_HZ = 2.45e9

# Músculo a 2.45 GHz (Gabriel et al., 1996, modelo paramétrico; base de datos IT'IS):
# εr = 52.73, σ = 1.739 S/m.
MUSCULO_EPS_R = 52.73
MUSCULO_SIGMA = 1.739

# Potencia de transmisión configurada en el firmware (ESP_PWR_LVL_P9).
POTENCIA_TX_DBM = 9.0


# --- 1. Longitud de onda ----------------------------------------------------

def longitud_onda(f_hz=FRECUENCIA_BLE_HZ):
    """λ = c / f. A 2.44 GHz da ≈ 0.123 m (12.3 cm)."""
    return C / f_hz


# --- 2. Pérdida en espacio libre (Friis) ------------------------------------

def fspl_db(d_m, f_hz=FRECUENCIA_BLE_HZ):
    """Pérdida en espacio libre: FSPL(d) = 20·log10(4πd/λ)  [dB].

    Sale de la fórmula de Friis, Pr/Pt = Gt·Gr·(λ/4πd)², con antenas
    isotrópicas (Gt = Gr = 1). La potencia se reparte sobre una esfera de
    área 4πd², por eso cae con d² (n = 2). A 1 m y 2.44 GHz: ≈ 40.2 dB.
    """
    return 20 * np.log10(4 * np.pi * np.asarray(d_m, dtype=float) / longitud_onda(f_hz))


def rssi_friis(d_m, rssi_d0, d0=1.0):
    """Curva de espacio libre (n = 2) que pasa por RSSI(d0).

    La anclamos al RSSI medido a d0 porque no conocemos las ganancias reales
    de las antenas: así se compara solo la *pendiente*, que es la física.
    """
    return rssi_d0 - 20 * np.log10(np.asarray(d_m, dtype=float) / d0)


# --- 3. Modelo log-distancia ------------------------------------------------

def rssi_log_distancia(d_m, rssi_d0, n, d0=1.0):
    """RSSI(d) = RSSI(d0) − 10·n·log10(d/d0)   (sin el término aleatorio X_σ)."""
    return rssi_d0 - 10 * n * np.log10(np.asarray(d_m, dtype=float) / d0)


def ajustar_log_distancia(d_m, rssi_dbm, d0=1.0):
    """Ajusta RSSI(d) = RSSI(d0) − 10·n·log10(d/d0) + X_σ.

    Truco: con x = log10(d/d0) el modelo es una RECTA, y = a + b·x, con
    a = RSSI(d0) y b = −10·n. Así que basta una regresión lineal.

    Devuelve un diccionario con:
    - n, rssi_d0: los parámetros ajustados.
    - n_ic95: semiancho del intervalo de confianza del 95 % de n
      (t de Student con N − 2 grados de libertad).
    - r2: coeficiente de determinación.
    - sigma_db: desviación estándar de los residuos. Es el "sombreado
      log-normal" X_σ: variación lenta por obstáculos y multitrayecto,
      que en dB se distribuye aproximadamente normal.
    - residuos, n_puntos.
    """
    d = np.asarray(d_m, dtype=float)
    y = np.asarray(rssi_dbm, dtype=float)
    x = np.log10(d / d0)
    r = stats.linregress(x, y)
    n_puntos = len(x)
    t = stats.t.ppf(0.975, n_puntos - 2)
    residuos = y - (r.intercept + r.slope * x)
    return {
        "n": -r.slope / 10,
        "n_ic95": t * r.stderr / 10,
        "rssi_d0": r.intercept,
        "rssi_d0_ic95": t * r.intercept_stderr,
        "r2": r.rvalue ** 2,
        # ddof=2 porque la recta "gastó" dos parámetros.
        "sigma_db": float(np.std(residuos, ddof=2)),
        "residuos": residuos,
        "n_puntos": n_puntos,
        "d0": d0,
    }


def interpretar_n(n):
    """Frase corta que ubica el exponente medido en los rangos típicos.

    Rangos de Rappaport (2002), tabla 4.2: espacio libre 2; edificio con
    línea de vista 1.6–1.8 (el pasillo guía la onda como un tubo);
    fábricas con obstáculos 2–3; edificio con obstáculos 4–6.
    """
    if n < 1.9:
        return "menor que 2: el pasillo guía la onda (efecto guía de onda)"
    if n <= 2.2:
        return "cercano a 2: casi espacio libre"
    if n <= 3.0:
        return "entre 2 y 3: interior con reflexiones y algunos obstáculos"
    return "mayor que 3: interior con muchos obstáculos"


# --- 4. Profundidad de penetración en tejido --------------------------------

def constante_atenuacion(eps_r, sigma, f_hz):
    """Constante de atenuación α (Np/m) de un medio con pérdidas.

    La onda dentro del tejido es E(z) = E0·e^(−αz)·cos(ωt − βz). Fórmula
    completa (Griffiths, sec. 9.4.1), válida para cualquier medio:

        α = ω·√(με/2) · [ √(1 + (σ/ωε)²) − 1 ]^(1/2)

    con ε = εr·ε0 y μ ≈ μ0 (el tejido no es magnético). El cociente σ/ωε
    (tangente de pérdidas) dice si el medio es "buen conductor" (≫ 1) o
    "dieléctrico con pérdidas" (≪ 1). Para el músculo a 2.45 GHz vale ≈ 0.24:
    no es buen conductor, por eso NO sirve la aproximación δ = √(2/ωμσ).
    """
    w = 2 * np.pi * f_hz
    eps = eps_r * EPSILON_0
    tangente = sigma / (w * eps)
    return w * np.sqrt(MU_0 * eps / 2) * np.sqrt(np.sqrt(1 + tangente**2) - 1)


def tangente_perdidas(eps_r, sigma, f_hz):
    """σ / (ω·ε0·εr): corriente de conducción sobre corriente de desplazamiento."""
    return sigma / (2 * np.pi * f_hz * eps_r * EPSILON_0)


def profundidad_penetracion(eps_r=MUSCULO_EPS_R, sigma=MUSCULO_SIGMA,
                            f_hz=FRECUENCIA_MICROONDAS_HZ):
    """δ = 1/α (m): distancia a la que el CAMPO cae a 1/e (≈ 37 %).

    Para músculo a 2.45 GHz da ≈ 2.2 cm. Ojo: la POTENCIA cae como e^(−2αz),
    así que la potencia cae a 1/e en δ/2 ≈ 1.1 cm. Las tablas de IT'IS
    reportan la del campo.
    """
    return 1 / constante_atenuacion(eps_r, sigma, f_hz)


def atenuacion_db_por_cm(eps_r=MUSCULO_EPS_R, sigma=MUSCULO_SIGMA,
                         f_hz=FRECUENCIA_MICROONDAS_HZ):
    """Atenuación de potencia por cm de tejido: 20·log10(e)·α·(0.01 m) ≈ 8.686·α/100.

    Para músculo a 2.45 GHz: ≈ 3.9 dB por cada cm.
    """
    return 20 * np.log10(np.e) * constante_atenuacion(eps_r, sigma, f_hz) / 100


def cm_equivalentes_de_musculo(atenuacion_db):
    """¿Cuántos cm de músculo producirían esta atenuación si la onda lo atravesara?

    Sirve para comparar con E2. Una persona entera (~20–30 cm de tejido)
    atenuaría ~80–120 dB y el llavero sería invisible; si medimos 15–20 dB
    es porque la onda llega RODEANDO el cuerpo (difracción y reflexiones en
    paredes), no atravesándolo.
    """
    return atenuacion_db / atenuacion_db_por_cm()


# --- 5. Promedios: dBm vs. mW -----------------------------------------------

def dbm_a_mw(dbm):
    """P(mW) = 10^(P(dBm)/10)."""
    return 10 ** (np.asarray(dbm, dtype=float) / 10)


def mw_a_dbm(mw):
    """P(dBm) = 10·log10(P(mW))."""
    return 10 * np.log10(mw)


def promedio_dbm(rssi_dbm):
    """Promedio aritmético de los valores en dBm (media geométrica de la potencia).

    ¿Por qué promediar en dBm? Porque el sombreado y el desvanecimiento se
    distribuyen aproximadamente normal EN dB, y el modelo log-distancia es
    lineal en dB: la regresión necesita valores en dB. La MEDIANA en dBm es
    todavía mejor para el informe porque ignora picos y nulos raros.
    """
    return float(np.mean(rssi_dbm))


def promedio_potencia_dbm(rssi_dbm):
    """Promedio en potencia lineal (mW) y luego convertido a dBm.

    Se usa cuando importa la ENERGÍA recibida (p. ej. un presupuesto de
    enlace o comparar con Friis, que es una ley de potencias). Siempre da
    un valor ≥ promedio en dBm (desigualdad de Jensen): los picos fuertes
    pesan más. La diferencia crece con la dispersión de los datos.
    """
    return float(mw_a_dbm(np.mean(dbm_a_mw(rssi_dbm))))


# --- 6. Tasa de paquetes recibidos ------------------------------------------

def tasa_paquetes(n_muestras, duracion_s):
    """Muestras recibidas por segundo en un punto."""
    return np.asarray(n_muestras, dtype=float) / np.asarray(duracion_s, dtype=float)


def tasa_normalizada(tasas):
    """Tasa de cada punto dividida por la del primer punto (el más cercano).

    1.0 = se reciben tantos anuncios como de cerca; 0 = señal perdida. El
    llavero siempre emite igual: lo que baja es la fracción de paquetes
    que el portátil logra decodificar cuando el RSSI se acerca a su
    sensibilidad (≈ −95 dBm).
    """
    tasas = np.asarray(tasas, dtype=float)
    return tasas / tasas[0]


# --- 7. Zonas de Fresnel y difracción (por qué el cuerpo se "rodea") ---------

def radio_fresnel(d1_m, d2_m, f_hz=FRECUENCIA_BLE_HZ, n_zona=1):
    """Radio de la n-ésima zona de Fresnel en un punto del enlace (m).

        r_n = √( n·λ·d1·d2 / (d1 + d2) )

    La zona de Fresnel es el elipsoide alrededor de la línea de vista donde
    viaja la mayor parte de la energía. A 2 m de enlace, en la mitad,
    r1 ≈ 25 cm: ¡del tamaño de un torso! Por eso una persona en medio
    importa tanto, y por eso las alturas del montaje (~1 m) deben anotarse.
    """
    return np.sqrt(n_zona * longitud_onda(f_hz) * d1_m * d2_m / (d1_m + d2_m))


def parametro_fresnel_kirchhoff(h_m, d1_m, d2_m, f_hz=FRECUENCIA_BLE_HZ):
    """v = h·√( 2(d1 + d2) / (λ·d1·d2) ).

    h es cuánto sobresale el obstáculo por encima (o al lado) de la línea de
    vista: h > 0 la tapa, h < 0 la deja libre. v = √2 · h / r1.
    """
    return h_m * np.sqrt(2 * (d1_m + d2_m) / (longitud_onda(f_hz) * d1_m * d2_m))


def perdida_filo_cuchillo_db(v):
    """Pérdida por difracción en un filo de cuchillo, J(v) en dB.

    Aproximación de la Recomendación UIT-R P.526 (ec. 31), válida para
    v > −0.78 (para v menores la pérdida es ≈ 0):

        J(v) = 6.9 + 20·log10( √((v − 0.1)² + 1) + v − 0.1 )

    En v = 0 (el borde justo en la línea de vista) da 6 dB: la mitad del
    frente de onda está tapado y llega 1/4 de la potencia.
    """
    v = np.asarray(v, dtype=float)
    j = 6.9 + 20 * np.log10(np.sqrt((v - 0.1) ** 2 + 1) + v - 0.1)
    return np.where(v > -0.78, j, 0.0)


def perdida_persona_db(distancia_m=2.0, semiancho_m=0.22, f_hz=FRECUENCIA_BLE_HZ):
    """Pérdida estimada por una persona de pie en la mitad del enlace.

    Modelo: el cuerpo es una pantalla opaca (absorbe todo lo que le llega,
    ver profundidad_penetracion) y la onda pasa por sus DOS costados, cada
    uno un filo de cuchillo a `semiancho_m` de la línea de vista (hombros
    ≈ 44 cm de ancho). Sumamos en potencia las dos ondas difractadas (fases
    aleatorias), así que la pérdida es la de un filo menos 3 dB.

    Para 2 m da ≈ 12 dB. Comparar con ~100 dB si la onda ATRAVESARA 25 cm de
    músculo: la difracción, no la transmisión, explica E2.
    """
    d1 = d2 = distancia_m / 2
    v = parametro_fresnel_kirchhoff(semiancho_m, d1, d2, f_hz)
    return float(perdida_filo_cuchillo_db(v) - 10 * np.log10(2))


# --- 8. El agua y el horno microondas: modelo de Debye -----------------------

# Agua pura a 25 °C (Kaatze, 1989): permitividad estática, a alta frecuencia
# y tiempo de relajación de los dipolos.
AGUA_EPS_S = 78.36
AGUA_EPS_INF = 5.2
AGUA_TAU_S = 8.27e-12


def permitividad_debye(f_hz, eps_s=AGUA_EPS_S, eps_inf=AGUA_EPS_INF, tau=AGUA_TAU_S):
    """Permitividad compleja ε = ε' − jε'' del modelo de relajación de Debye.

        ε(ω) = ε∞ + (εs − ε∞) / (1 + jωτ)

    Los dipolos del agua intentan girar con el campo; τ es lo que tardan en
    "seguirlo". ε'' (pérdidas, lo que calienta) es máxima cuando ωτ = 1.
    Devuelve (ε', ε'').
    """
    eps = eps_inf + (eps_s - eps_inf) / (1 + 1j * 2 * np.pi * np.asarray(f_hz) * tau)
    return eps.real, -eps.imag


def frecuencia_pico_perdidas(tau=AGUA_TAU_S):
    """f = 1/(2πτ) ≈ 19 GHz para el agua a 25 °C: NO es 2.45 GHz."""
    return 1 / (2 * np.pi * tau)


# --- 9. Reflexión en el piso: modelo de dos rayos ----------------------------

def distancia_quiebre(h_tx_m, h_rx_m, f_hz=FRECUENCIA_BLE_HZ):
    """d_c = 4·h_t·h_r / λ: más allá, el rayo reflejado cancela al directo y
    la pérdida pasa de n ≈ 2 a n ≈ 4. Con ambos a 1 m: ≈ 33 m."""
    return 4 * h_tx_m * h_rx_m / longitud_onda(f_hz)


def perdida_dos_rayos_db(d_m, h_tx_m=1.0, h_rx_m=1.0, gamma=-1.0, f_hz=FRECUENCIA_BLE_HZ):
    """Pérdida (dB) con el rayo directo más el reflejado en el piso.

    Rayo directo: r1 = √(d² + (ht − hr)²). Reflejado: r2 = √(d² + (ht + hr)²).
    El campo total es la suma de dos ondas esféricas:

        E ∝ e^(−jk·r1)/r1 + Γ·e^(−jk·r2)/r2

    con Γ ≈ −1 (reflexión rasante). Cerca hay interferencia constructiva y
    destructiva (oscilaciones); lejos, PL ≈ 40·log10(d) − 20·log10(ht·hr).
    """
    d = np.asarray(d_m, dtype=float)
    lam = longitud_onda(f_hz)
    k = 2 * np.pi / lam
    r1 = np.sqrt(d**2 + (h_tx_m - h_rx_m) ** 2)
    r2 = np.sqrt(d**2 + (h_tx_m + h_rx_m) ** 2)
    campo = np.exp(-1j * k * r1) / r1 + gamma * np.exp(-1j * k * r2) / r2
    # Normalizado como Friis: |E|² · (λ/4π)².
    return -20 * np.log10(np.abs(campo) * lam / (4 * np.pi))


# --- 10. El RSSI como regla: estimar distancia --------------------------------

def distancia_desde_rssi(rssi_dbm, rssi_d0, n, sigma_db=0.0, d0=1.0):
    """Invierte el modelo log-distancia: d = d0 · 10^((RSSI(d0) − RSSI)/(10·n)).

    Devuelve (d, d_min, d_max). El intervalo ±1σ sale de que el sombreado
    X_σ, en dB, se convierte en un factor MULTIPLICATIVO sobre la distancia:

        factor = 10^(σ / (10·n))

    Con σ = 3 dB y n = 2.2 el factor es ≈ 1.37: decir "5 m" significa "entre
    3.7 y 6.9 m". Por eso el RSSI sirve para "frío/caliente", no como regla.
    """
    d = d0 * 10 ** ((rssi_d0 - np.asarray(rssi_dbm, dtype=float)) / (10 * n))
    factor = 10 ** (sigma_db / (10 * n))
    return d, d / factor, d * factor


# --- 11. Presupuesto de enlace y alcance -------------------------------------

SENSIBILIDAD_TIPICA_DBM = -95.0


def alcance_predicho(rssi_d0, n, sensibilidad_dbm=SENSIBILIDAD_TIPICA_DBM,
                     margen_db=0.0, d0=1.0):
    """Distancia a la que el RSSI del modelo toca la sensibilidad (+ un margen).

        d_max = d0 · 10^((RSSI(d0) − S − M) / (10·n))

    Con margen M = σ·1.28 se cubre el 90 % de las posiciones (sombreado normal).
    """
    return d0 * 10 ** ((rssi_d0 - sensibilidad_dbm - margen_db) / (10 * n))


# --- 12. Desvanecimiento rápido: factor K de Rice ----------------------------

def factor_k_rice(rssi_dbm):
    """Estima el factor K de Rice a partir de las muestras de UN punto.

    Con línea de vista llega una onda dominante más muchas dispersas: la
    amplitud sigue una distribución de Rice, K = P_directa / P_dispersa.
    K → 0 es Rayleigh (sin camino directo); K grande, señal estable.

    Método de momentos (Greenstein et al., 1999) sobre la potencia P en mW:
        γ = Var(P) / E[P]²,   K = √(1 − γ) / (1 − √(1 − γ))   (si γ < 1)
    Si γ ≥ 1 la variabilidad es la de Rayleigh o mayor: K = 0.
    """
    p = dbm_a_mw(rssi_dbm)
    gamma = np.var(p) / np.mean(p) ** 2
    if gamma >= 1:
        return 0.0
    raiz = np.sqrt(1 - gamma)
    return float(raiz / (1 - raiz))


# --- 13. Seguridad: cota de SAR ---------------------------------------------

def sar_cota_w_kg(potencia_dbm=POTENCIA_TX_DBM, masa_kg=0.010):
    """Cota superior de la SAR (tasa de absorción específica, W/kg).

    Peor caso imposible: TODA la potencia del llavero se absorbe en 10 g de
    tejido (la masa de promedio de las normas). SAR ≤ P / m.
    Con +9 dBm (≈ 8 mW): ≤ 0.8 W/kg, por debajo del límite de 2 W/kg
    (ICNIRP 2020, cabeza y tronco). Y el llavero transmite solo ráfagas de
    microsegundos, así que la potencia media es muchísimo menor.
    """
    return float(dbm_a_mw(potencia_dbm) / 1000 / masa_kg)
