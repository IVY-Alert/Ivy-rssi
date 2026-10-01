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

from . import analisis, fisica, sesion

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
    ax.grid(axis="y", visible=False)
    ax.set_xlim(0, t["atenuacion_db"].max() * 1.18)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlabel("Atenuación respecto a la línea de vista (dB)")
    _titulo(ax, "El cuerpo absorbe la señal de 2.4 GHz")
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
    ax2.plot(con["distancia_m"], con["mediana_dbm"], "o-", color=AMBAR_OSCURO, mec=CREMA)
    ax2.axhline(SENSIBILIDAD_DBM, ls="--", color=TINTA, lw=plt.rcParams["lines.linewidth"] * 0.5)
    ax2.text(t["distancia_m"].min(), SENSIBILIDAD_DBM + 1.5,
             f"sensibilidad típica ≈ {SENSIBILIDAD_DBM:.0f} dBm", va="bottom")
    ax2.set_ylabel("RSSI (dBm)")
    ax2.set_xlabel("Distancia entre el llavero y el portátil (m)")

    for ax in (ax1, ax2):
        ax.axvline(alcance, color=AMBAR_OSCURO, lw=plt.rcParams["lines.linewidth"] * 0.6)
    ax1.text(alcance, 108, f" alcance máximo: {alcance:.0f} m ", ha="right", va="center",
             bbox={"boxstyle": "round,pad=0.3", "facecolor": MANTEQUILLA, "edgecolor": "none"})
    _titulo(ax1, "Hasta dónde llega la alerta")
    return fig


SENSIBILIDAD_DBM = -95.0

FIGURAS = {
    "E1": [("E1_rssi_vs_distancia_log", fig_e1_log),
           ("E1_rssi_vs_distancia_lineal", fig_e1_lineal),
           ("E1_residuos", fig_e1_residuos)],
    "E2": [("E2_cuerpo_obstaculo", fig_e2)],
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
            fig = funcion(res)
            ruta = carpeta / f"{nombre}_{formato}.png"
            fig.savefig(ruta, dpi=f["dpi"])
            plt.close(fig)
            rutas.append(ruta)
    return rutas


def graficar_archivos(rutas_csv, carpeta_salida):
    """Analiza los CSV (combinando repeticiones) y exporta sus figuras."""
    registrar_fuentes()
    creadas = []
    for exp, grupo in analisis.agrupar_sesiones(rutas_csv).items():
        df, metas = sesion.cargar(grupo)
        try:
            res = analisis.analizar(df, metas)
        except ValueError as e:
            print(f"{exp}: sin figuras ({e})")
            continue
        for nombre, funcion in FIGURAS[exp]:
            creadas += exportar(funcion, res, nombre, carpeta_salida)
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
            creadas = graficar_archivos(rutas, salida)
    else:
        rutas = analisis.sesiones_en(args.carpeta) if args.todo else args.csv
        if not rutas:
            p.error("Indica uno o más CSV, o usa --todo / --ejemplo")
        creadas = graficar_archivos(rutas, args.salida)
    for r in creadas:
        print(r)


if __name__ == "__main__":
    main()
