"""Gráficas con la identidad visual de Ivy.

Uso:
    python -m ivy_rssi.graficas datos/<sesion>.csv [otra.csv ...]
    python -m ivy_rssi.graficas --todo                 # todas las sesiones de datos/
    python -m ivy_rssi.graficas --ejemplo              # datos simulados → figuras/ejemplo/

Cada figura se exporta dos veces: <nombre>_video.png (1920×1080) y
<nombre>_informe.png (300 dpi, tamaño de media página).
"""

import argparse
import re
import tempfile
import urllib.request
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # sin ventanas: solo archivos PNG
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter, MaxNLocator
from scipy import stats

from . import analisis, fisica

# --- Identidad visual -------------------------------------------------------

CREMA = "#FFF6E6"         # fondo
AMBAR = "#FFA928"         # color principal
AMBAR_OSCURO = "#E98A10"
TINTA = "#2E2437"         # texto y ejes
DURAZNO = "#FFD5BE"
MANTEQUILLA = "#FFE8A3"
ARENA = "#EDE3D3"
MIEL = "#F6D9A8"

CARPETA_FUENTES = Path(__file__).parent / "fuentes"
# Instancias estáticas que sirve la API CSS de Google Fonts (licencia OFL).
URL_CSS_FUENTES = ("https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@700"
                   "&family=Instrument+Sans:wght@400;600")

FUENTE_TITULOS = "Bricolage Grotesque"
FUENTE_TEXTO = "Instrument Sans"

# Dos formatos de salida. `escala` agranda letras y trazos para el video,
# que se ve de lejos y en pantalla completa.
FORMATOS = {
    "video": {"figsize": (16, 9), "dpi": 120, "escala": 1.9},     # 1920×1080
    "informe": {"figsize": (6.5, 4.2), "dpi": 300, "escala": 0.85},
}

# Nombres bonitos para las condiciones.
ETIQUETAS = {
    "linea_de_vista": "Línea de vista",
    "en_la_mano": "En la mano",
    "bolsillo": "Bolsillo del pantalón",
    "persona_en_medio": "Persona en medio",
    "morral": "Dentro de un morral",
    "antena_sobresale": "Antena sobresale\n(diseño final)",
    "antena_encima": "Antena encima\nde la batería",
    "sin_bateria": "Sin batería cerca",
}


# --- Fuentes ----------------------------------------------------------------

def descargar_fuentes():
    """Baja Bricolage Grotesque 700 e Instrument Sans 400/600 a ivy_rssi/fuentes/."""
    CARPETA_FUENTES.mkdir(exist_ok=True)
    css = urllib.request.urlopen(URL_CSS_FUENTES, timeout=15).read().decode()
    patron = r"font-family: '([^']+)';.*?font-weight: (\d+);.*?url\((.+?)\)"
    for familia, peso, url in re.findall(patron, css, re.S):
        destino = CARPETA_FUENTES / f"{familia.replace(' ', '')}-{peso}.ttf"
        destino.write_bytes(urllib.request.urlopen(url, timeout=30).read())


def registrar_fuentes():
    """Registra las fuentes en matplotlib. Si faltan, las descarga.

    Sin red y sin archivos, se usa DejaVu Sans (viene con matplotlib) y se avisa.
    """
    global FUENTE_TITULOS, FUENTE_TEXTO
    archivos = sorted(CARPETA_FUENTES.glob("*.ttf"))
    if len(archivos) < 3:
        try:
            descargar_fuentes()
            archivos = sorted(CARPETA_FUENTES.glob("*.ttf"))
        except OSError as e:
            warnings.warn(f"No se pudieron descargar las fuentes ({e}); uso DejaVu Sans.")
            FUENTE_TITULOS = FUENTE_TEXTO = "DejaVu Sans"
            return
    for a in archivos:
        font_manager.fontManager.addfont(str(a))


def estilo(escala):
    """rcParams del estilo Ivy: fondo crema, tinta, sin marco arriba ni a la derecha."""
    return {
        "figure.facecolor": CREMA,
        "axes.facecolor": CREMA,
        "savefig.facecolor": CREMA,
        # DejaVu Sans de respaldo para los símbolos que Instrument Sans no
        # trae (σ, ≈): matplotlib busca cada glifo en la lista, en orden.
        "font.family": [FUENTE_TEXTO, "DejaVu Sans"],
        "figure.constrained_layout.use": True,
        "font.size": 11 * escala,
        "text.color": TINTA,
        "axes.labelcolor": TINTA,
        "axes.edgecolor": TINTA,
        "axes.linewidth": 0.8 * escala,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.labelsize": 11 * escala,
        "axes.labelpad": 6 * escala,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": ARENA,          # rejilla muy suave
        "grid.linewidth": 0.8 * escala,
        "xtick.color": TINTA,
        "ytick.color": TINTA,
        "xtick.labelsize": 10 * escala,
        "ytick.labelsize": 10 * escala,
        "xtick.major.width": 0.8 * escala,
        "ytick.major.width": 0.8 * escala,
        "xtick.major.size": 4 * escala,
        "ytick.major.size": 4 * escala,
        "lines.linewidth": 2 * escala,
        "lines.markersize": 7 * escala,
        "legend.frameon": False,
        "legend.fontsize": 10 * escala,
        "axes.unicode_minus": True,
    }


def _titulo(ax, texto):
    """Título a la izquierda en Bricolage Grotesque: dice el hallazgo, no el eje."""
    ax.set_title(texto, loc="left", fontfamily=FUENTE_TITULOS, fontweight="bold",
                 fontsize=plt.rcParams["font.size"] * 1.45, pad=plt.rcParams["font.size"])


def _nota(ax, texto, x=0.97, y=0.95, ha="right"):
    """Recuadro de anotación con fondo mantequilla."""
    ax.text(x, y, texto, transform=ax.transAxes, ha=ha, va="top",
            bbox={"boxstyle": "round,pad=0.5", "facecolor": MANTEQUILLA, "edgecolor": "none"})


def _formato_metros(x, _):
    return f"{x:g}"


# --- Una función por figura -------------------------------------------------
# Cada una recibe el resultado de analisis.analizar() y devuelve la figura.

def _medianas_e1(res):
    """Por distancia: mediana de las repeticiones y el rango que cubren sus
    cuartiles (p25 más bajo y p75 más alto). Con una sola repetición, las
    barras son el rango intercuartil de las muestras."""
    g = res["puntos"].groupby("valor_condicion")
    med = g["mediana"].median()
    return med.index.values, med.values, g["p25"].min().values, g["p75"].max().values


def fig_e1_log(res):
    a = res["ajuste"]
    fig, ax = plt.subplots()
    d, med, lo, hi = _medianas_e1(res)
    dd = np.geomspace(d.min() * 0.85, d.max() * 1.15, 100)

    ax.plot(dd, fisica.rssi_friis(dd, a["rssi_d0"]), ls="--", color=TINTA, lw=plt.rcParams["lines.linewidth"] * 0.6,
            label="Espacio libre, Friis (n = 2)")
    ax.plot(dd, fisica.rssi_log_distancia(dd, a["rssi_d0"], a["n"]), color=AMBAR_OSCURO,
            label=f"Ajuste log-distancia (n = {a['n']:.2f})")
    ax.errorbar(d, med, yerr=[med - lo, hi - med], fmt="o", color=AMBAR, mec=CREMA,
                ecolor=AMBAR_OSCURO, elinewidth=plt.rcParams["lines.linewidth"] * 0.6,
                capsize=0, label="Medido (mediana; barras: 50 % central de las muestras)")

    ax.set_xscale("log")
    ax.set_xticks(d)
    ax.xaxis.set_major_formatter(FuncFormatter(_formato_metros))
    ax.minorticks_off()
    ax.set_xlabel("Distancia entre el llavero y el portátil (m, escala logarítmica)")
    ax.set_ylabel("RSSI (dBm)")
    _titulo(ax, "La señal pierde potencia con la distancia")
    _nota(ax, f"n = {a['n']:.2f} ± {a['n_ic95']:.2f} (IC 95 %)\n"
              f"R² = {a['r2']:.3f}   σ = {a['sigma_db']:.1f} dB")
    ax.legend(loc="lower left")
    return fig


def fig_e1_lineal(res):
    a = res["ajuste"]
    fig, ax = plt.subplots()
    d, med, lo, hi = _medianas_e1(res)
    dd = np.linspace(d.min() * 0.8, d.max() * 1.03, 200)
    curva = fisica.rssi_log_distancia(dd, a["rssi_d0"], a["n"])

    # Banda ±σ: dónde cae ~68 % de los puntos por el sombreado.
    ax.fill_between(dd, curva - a["sigma_db"], curva + a["sigma_db"], color=MIEL, lw=0,
                    label=f"± σ de sombreado ({a['sigma_db']:.1f} dB)")
    ax.plot(dd, curva, color=AMBAR_OSCURO, label="Modelo ajustado")
    ax.plot(d, med, "o", color=AMBAR, mec=CREMA, label="Medido (mediana)")
    ax.set_xlim(0, d.max() * 1.05)
    ax.set_xlabel("Distancia entre el llavero y el portátil (m)")
    ax.set_ylabel("RSSI (dBm)")
    _titulo(ax, "Cae rápido cerca, despacio lejos")
    ax.legend(loc="upper right")
    return fig


def fig_e1_residuos(res):
    a = res["ajuste"]
    r = np.asarray(a["residuos"])
    fig, ax = plt.subplots()
    ax.hist(r, bins="auto", density=True, color=DURAZNO, edgecolor=CREMA,
            linewidth=plt.rcParams["lines.linewidth"], label="Residuos medidos")
    x = np.linspace(-4 * a["sigma_db"], 4 * a["sigma_db"], 200)
    ax.plot(x, stats.norm.pdf(x, 0, a["sigma_db"]), color=AMBAR_OSCURO,
            label=f"Normal, σ = {a['sigma_db']:.1f} dB")
    ax.axvline(0, color=TINTA, lw=plt.rcParams["lines.linewidth"] * 0.4)
    ax.set_xlabel("Residuo: medido − modelo (dB)")
    ax.set_ylabel("Densidad de probabilidad (1/dB)")
    _titulo(ax, "El sombreado sigue una campana en dB")
    ax.legend(loc="upper right")
    return fig


def fig_e2(res):
    t = res["tabla"].drop("linea_de_vista").sort_values("atenuacion_db")
    fig, ax = plt.subplots()
    nombres = [ETIQUETAS.get(c, c) for c in t.index]
    barras = ax.barh(nombres, t["atenuacion_db"], color=AMBAR, height=0.6)
    ax.bar_label(barras, labels=[f"{v:.0f} dB" for v in t["atenuacion_db"]],
                 padding=6, color=TINTA)
    # Predicción teórica para "persona en medio": la onda rodea el cuerpo.
    if "persona_en_medio" in t.index:
        y = list(t.index).index("persona_en_medio")
        pred = res["prediccion_difraccion_db"]
        ax.plot([pred, pred], [y - 0.38, y + 0.38], color=TINTA,
                lw=plt.rcParams["lines.linewidth"], zorder=3)
        ax.annotate(f"teoría de difracción: {pred:.0f} dB", (pred, y - 0.38),
                    xytext=(0, -4), textcoords="offset points", ha="center", va="top",
                    fontsize=plt.rcParams["font.size"] * 0.85)
    _nota(ax, f"Si la onda ATRAVESARA 25 cm de músculo:\n≈ {res['prediccion_atravesar_db']:.0f} dB "
              "(no llegaría nada).\nLa onda rodea el cuerpo.", y=0.62)
    ax.yaxis.get_label().set_visible(False)
    ax.grid(axis="y", visible=False)
    ax.set_xlim(0, t["atenuacion_db"].max() * 1.18)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlabel("Atenuación respecto a la línea de vista (dB)")
    _titulo(ax, "El cuerpo bloquea los 2.4 GHz: la onda lo rodea")
    return fig


def fig_e3(res):
    t = res["tabla"]
    ang = np.radians(np.append(t["valor_condicion"], t["valor_condicion"].iloc[0]))
    rel = np.append(t["relativo_db"], t["relativo_db"].iloc[0])  # cerrar el contorno
    piso = min(-15, np.floor(rel.min() / 5) * 5 - 5)

    fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)              # ángulos en sentido horario, como al girar
    ax.fill(ang, rel, color=DURAZNO, zorder=1)
    ax.plot(ang, rel, "o-", color=AMBAR_OSCURO, mec=CREMA, zorder=2)
    ax.set_ylim(piso, 1)                    # el centro es `piso` dB, no cero
    anillos = np.arange(piso, 1, 5)
    ax.set_yticks(anillos)
    ax.set_yticklabels([])
    # Etiquetas de los anillos a mano, encima del relleno (zorder alto).
    for v in anillos[1:]:
        ax.text(np.radians(105), v, f"{v:.0f} dB", ha="center", va="center", zorder=5,
                fontsize=plt.rcParams["font.size"] * 0.8,
                bbox={"boxstyle": "round,pad=0.15", "facecolor": CREMA, "edgecolor": "none"})
    ax.set_xticks(np.radians(np.arange(0, 360, 30)))
    ax.set_xticklabels([f"{a}°" for a in range(0, 360, 30)])
    ax.spines["polar"].set_color(ARENA)
    _titulo(ax, "La antena no irradia igual hacia todos lados")
    ax.text(1.02, 0.02, f"0 dB = dirección más fuerte\nnulo de {res['rango_db']:.0f} dB "
            f"hacia {res['angulo_peor']:.0f}°", transform=ax.transAxes, va="bottom")
    return fig


def fig_e4(res):
    t = res["tabla"]
    # Las barras miden el MARGEN sobre la sensibilidad del receptor: cuánto
    # sobra antes de perder la señal. Así son longitudes positivas con un
    # cero físico, cosa que no pasa con los dBm negativos.
    margen = t["mediana"] - SENSIBILIDAD_DBM
    fig, ax = plt.subplots()
    nombres = [ETIQUETAS.get(c, c) for c in t.index]
    colores = [AMBAR_OSCURO if c == "antena_sobresale" else AMBAR for c in t.index]
    barras = ax.bar(nombres, margen, color=colores, width=0.55)
    textos = [f"{m:.0f} dBm" + ("" if c == "antena_sobresale" else f"\n({d:+.0f} dB)")
              for c, m, d in zip(t.index, t["mediana"], t["diferencia_db"])]
    ax.bar_label(barras, labels=textos, padding=6, color=TINTA)
    ax.grid(axis="x", visible=False)
    ax.set_ylim(0, margen.max() * 1.3)
    ax.set_ylabel(f"Margen sobre la sensibilidad, {SENSIBILIDAD_DBM:.0f} dBm (dB)")
    _titulo(ax, "El metal de la batería tapa la antena")
    return fig


def fig_e5(res):
    t = res["tabla"]
    alcance = res["alcance_max_m"]
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True,
                                   gridspec_kw={"height_ratios": [1, 1]})
    ax1.plot(t["distancia_m"], 100 * t["tasa_normalizada"], "o-", color=AMBAR, mec=CREMA)
    ax1.set_ylabel("Paquetes recibidos\n(% del más cercano)")
    ax1.set_ylim(0, 115)

    con = t.dropna(subset=["mediana_dbm"])
    ax2.plot(con["distancia_m"], con["mediana_dbm"], "o-", color=AMBAR_OSCURO, mec=CREMA,
             label="Medido en E5 (mediana)")
    if "modelo_e1" in res:
        m = res["modelo_e1"]
        dd = np.linspace(t["distancia_m"].min(), t["distancia_m"].max(), 200)
        ax2.plot(dd, fisica.rssi_log_distancia(dd, m["rssi_d0"], m["n"]), ls="--", color=TINTA,
                 lw=plt.rcParams["lines.linewidth"] * 0.6, label=f"Modelo de E1 (n = {m['n']:.2f})")
        ax2.legend(loc="upper right")
    ax2.axhline(SENSIBILIDAD_DBM, ls="--", color=TINTA, lw=plt.rcParams["lines.linewidth"] * 0.5)
    ax2.text(t["distancia_m"].min(), SENSIBILIDAD_DBM + 1.5,
             f"sensibilidad típica ≈ {SENSIBILIDAD_DBM:.0f} dBm", va="bottom")
    ax2.set_ylabel("RSSI (dBm)")
    ax2.set_xlabel("Distancia entre el llavero y el portátil (m)")

    for ax in (ax1, ax2):
        ax.axvline(alcance, color=AMBAR_OSCURO, lw=plt.rcParams["lines.linewidth"] * 0.6)
    ax1.text(alcance, 108, f" alcance máximo: {alcance:.0f} m ", ha="right", va="center",
             bbox={"boxstyle": "round,pad=0.3", "facecolor": MANTEQUILLA, "edgecolor": "none"})
    if res.get("alcance_predicho_e1_m"):
        pred = res["alcance_predicho_e1_m"]
        for ax in (ax1, ax2):
            ax.axvline(pred, ls=":", color=TINTA, lw=plt.rcParams["lines.linewidth"] * 0.6)
        ax1.text(pred, 8, f" predicho por E1: {pred:.0f} m ", ha="right", va="bottom",
                 bbox={"boxstyle": "round,pad=0.3", "facecolor": CREMA, "edgecolor": "none"})
    _titulo(ax1, "Hasta dónde llega la alerta")
    return fig


def fig_e1_regla(res):
    """¿Sirve el RSSI como regla? Distancia estimada vs. distancia real."""
    p = res["puntos"]
    factor = res["factor_incertidumbre_distancia"]
    fig, ax = plt.subplots()
    dd = np.geomspace(p["valor_condicion"].min() * 0.8, p["valor_condicion"].max() * 1.25, 50)
    ax.fill_between(dd, dd / factor, dd * factor, color=MIEL, lw=0,
                    label=f"Incertidumbre ±1σ (×/÷ {factor:.2f})")
    ax.plot(dd, dd, color=TINTA, lw=plt.rcParams["lines.linewidth"] * 0.6, ls="--",
            label="Estimación perfecta")
    ax.plot(p["valor_condicion"], p["distancia_estimada_m"], "o", color=AMBAR, mec=CREMA,
            label="Estimada con el RSSI de cada punto")
    ax.set_xscale("log")
    ax.set_yscale("log")
    for eje in (ax.xaxis, ax.yaxis):
        eje.set_major_formatter(FuncFormatter(_formato_metros))
    ax.set_xticks([0.25, 0.5, 1, 2, 5, 10])
    ax.set_yticks([0.25, 0.5, 1, 2, 5, 10])
    ax.minorticks_off()
    ax.set_xlabel("Distancia real (m)")
    ax.set_ylabel("Distancia estimada con el RSSI (m)")
    _titulo(ax, "El RSSI dice «frío o caliente», no los centímetros")
    _nota(ax, f"Error típico: {100 * res['error_distancia_mediano']:.0f} %", x=0.97, y=0.08)
    ax.legend(loc="upper left")
    return fig


def fig_e2_desvanecimiento(res):
    """Distribución acumulada de la potencia: Rice con y sin camino directo."""
    m = res["muestras"]
    fig, ax = plt.subplots()
    x = np.linspace(-25, 8, 300)
    estilos = [("linea_de_vista", AMBAR), ("persona_en_medio", AMBAR_OSCURO)]
    for cond, color in estilos:
        rssi = m.loc[m["condicion"] == cond, "rssi_dbm"].to_numpy(dtype=float)
        if len(rssi) < 10:
            continue
        # Potencia relativa a su media (en mW), en dB.
        rel = rssi - fisica.promedio_potencia_dbm(rssi)
        orden = np.sort(rel)
        ax.step(orden, np.arange(1, len(orden) + 1) / len(orden), where="post", color=color,
                label=f"{ETIQUETAS[cond]} (medido)")
        # Teoría: amplitud de Rice con potencia media 1.
        k = res["tabla"].loc[cond, "k_rice"]
        sigma = np.sqrt(1 / (2 * (k + 1)))
        cdf = stats.rice.cdf(10 ** (x / 20), np.sqrt(2 * k), scale=sigma)
        ax.plot(x, cdf, ls="--", color=color, lw=plt.rcParams["lines.linewidth"] * 0.6,
                label=f"Rice, K = {k:.1f}")
    ax.set_xlim(-25, 8)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("Potencia de cada paquete respecto a su media (dB)")
    ax.set_ylabel("Fracción de paquetes (acumulada)")
    _titulo(ax, "Sin camino directo, la señal tiembla más")
    ax.legend(loc="upper left")
    return fig


def fig_teoria_debye():
    """Permitividad del agua (Debye): el horno NO usa la resonancia del agua."""
    f = np.geomspace(0.1e9, 300e9, 400)
    e1, e2 = fisica.permitividad_debye(f)
    pico = fisica.frecuencia_pico_perdidas()
    fig, ax = plt.subplots()
    ax.plot(f / 1e9, e1, color=AMBAR, label="ε′: cuánto se polariza (almacena)")
    ax.plot(f / 1e9, e2, color=AMBAR_OSCURO, label="ε″: cuánto absorbe (calienta)")
    for fx, texto in [(2.45, "BLE y horno\n2.45 GHz"), (pico / 1e9, f"máximo de\nabsorción\n{pico / 1e9:.0f} GHz")]:
        ax.axvline(fx, color=TINTA, ls=":", lw=plt.rcParams["lines.linewidth"] * 0.6)
        ax.text(fx * 1.08, 60, texto, va="top")
    ax.set_xscale("log")
    ax.xaxis.set_major_formatter(FuncFormatter(_formato_metros))
    ax.set_xlabel("Frecuencia (GHz, escala logarítmica)")
    ax.set_ylabel("Permitividad relativa del agua a 25 °C")
    _titulo(ax, "El horno no usa la «resonancia» del agua")
    ax.legend(loc="center left")
    return fig


def fig_teoria_dos_rayos():
    """Espacio libre vs. dos rayos (reflexión en el piso), antenas a 1 m."""
    d = np.geomspace(1, 300, 2000)
    dc = fisica.distancia_quiebre(1.0, 1.0)
    fig, ax = plt.subplots()
    ax.plot(d, -fisica.perdida_dos_rayos_db(d), color=AMBAR,
            label="Dos rayos: directo + reflejado en el piso")
    ax.plot(d, -fisica.fspl_db(d), color=TINTA, ls="--", lw=plt.rcParams["lines.linewidth"] * 0.6,
            label="Espacio libre (n = 2)")
    ax.axvline(dc, color=AMBAR_OSCURO, ls=":", lw=plt.rcParams["lines.linewidth"] * 0.6)
    ax.text(dc * 1.08, -45, f"quiebre\n4·h·h/λ = {dc:.0f} m\n(de n = 2 a n = 4)", va="top")
    ax.set_xscale("log")
    ax.xaxis.set_major_formatter(FuncFormatter(_formato_metros))
    ax.set_ylim(-120, -35)
    ax.set_xlabel("Distancia (m, escala logarítmica), llavero y portátil a 1 m del piso")
    ax.set_ylabel("Ganancia del canal (dB)")
    _titulo(ax, "El piso también refleja: lejos, la señal cae el doble de rápido")
    ax.legend(loc="lower left")
    return fig


SENSIBILIDAD_DBM = -95.0

# Figuras que solo dependen de la teoría (no de mediciones).
FIGURAS_TEORIA = [("T1_agua_debye", fig_teoria_debye), ("T2_dos_rayos", fig_teoria_dos_rayos)]

FIGURAS = {
    "E1": [("E1_rssi_vs_distancia_log", fig_e1_log),
           ("E1_rssi_vs_distancia_lineal", fig_e1_lineal),
           ("E1_residuos", fig_e1_residuos),
           ("E1_rssi_como_regla", fig_e1_regla)],
    "E2": [("E2_cuerpo_obstaculo", fig_e2),
           ("E2_desvanecimiento", fig_e2_desvanecimiento)],
    "E3": [("E3_patron_radiacion", fig_e3)],
    "E4": [("E4_antena_vs_bateria", fig_e4)],
    "E5": [("E5_alcance", fig_e5)],
}


# --- Exportar ---------------------------------------------------------------

def exportar(funcion, res, nombre, carpeta):
    """Dibuja la figura en los dos formatos y la guarda. Devuelve las rutas."""
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    rutas = []
    for formato, f in FORMATOS.items():
        with plt.rc_context({**estilo(f["escala"]), "figure.figsize": f["figsize"]}):
            # constrained_layout acomoda los márgenes sin cambiar el tamaño
            # (bbox="tight" lo cambiaría y el video no saldría de 1920×1080).
            fig = funcion(res) if res is not None else funcion()
            ruta = carpeta / f"{nombre}_{formato}.png"
            fig.savefig(ruta, dpi=f["dpi"])
            plt.close(fig)
            rutas.append(ruta)
    return rutas


def graficar_archivos(rutas_csv, carpeta_salida):
    """Analiza los CSV (combinando repeticiones) y exporta sus figuras."""
    registrar_fuentes()
    creadas = []
    # analizar_archivos cruza E1 con E5 (alcance predicho vs. medido).
    resultados = analisis.analizar_archivos(rutas_csv, guardar=False, mostrar=False)
    for exp, res in resultados.items():
        for nombre, funcion in FIGURAS[exp]:
            creadas += exportar(funcion, res, nombre, carpeta_salida)
    return creadas


def graficar_teoria(carpeta_salida):
    """Figuras de teoría pura (no necesitan datos)."""
    registrar_fuentes()
    creadas = []
    for nombre, funcion in FIGURAS_TEORIA:
        creadas += exportar(funcion, None, nombre, carpeta_salida)
    return creadas


def main(argv=None):
    p = argparse.ArgumentParser(description="Genera las figuras de las sesiones.")
    p.add_argument("csv", nargs="*", help="uno o varios CSV de sesión")
    p.add_argument("--todo", action="store_true", help="todas las sesiones de --carpeta")
    p.add_argument("--ejemplo", action="store_true",
                   help="simula los 5 experimentos y grafica en figuras/ejemplo/")
    p.add_argument("--carpeta", default="datos")
    p.add_argument("--salida", default="figuras")
    args = p.parse_args(argv)

    if args.ejemplo:
        from .simulador import generar_ejemplo
        with tempfile.TemporaryDirectory() as tmp:
            rutas = generar_ejemplo(tmp)
            salida = Path(args.salida) / "ejemplo" if args.salida == "figuras" else args.salida
            creadas = graficar_archivos(rutas, salida) + graficar_teoria(salida)
    else:
        rutas = analisis.sesiones_en(args.carpeta) if args.todo else args.csv
        if not rutas:
            p.error("Indica uno o más CSV, o usa --todo / --ejemplo")
        creadas = graficar_archivos(rutas, args.salida) + graficar_teoria(args.salida)
    for r in creadas:
        print(r)


if __name__ == "__main__":
    main()
