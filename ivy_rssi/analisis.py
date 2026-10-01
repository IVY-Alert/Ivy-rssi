"""Análisis de las sesiones: un resultado por experimento.

Uso:
    python -m ivy_rssi.analisis datos/<sesion>.csv [otra.csv ...]
    python -m ivy_rssi.analisis --todo            # todas las sesiones de datos/

Si llegan varias sesiones del mismo experimento (repeticiones), se combinan.
"""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from . import fisica, sesion
from .experimentos import EXPERIMENTOS


# --- Estadística por punto --------------------------------------------------

def resumen_por_punto(df, por_repeticion=True):
    """Una fila por (repetición, condición) con mediana, cuartiles y promedios.

    La mediana es nuestro "valor del punto": no la mueven los picos o nulos
    aislados del desvanecimiento rápido.
    """
    claves = (["repeticion"] if por_repeticion else []) + ["condicion", "valor_condicion"]
    g = df.groupby(claves, sort=False, dropna=False)["rssi_dbm"]
    tabla = g.agg(
        n="size",
        mediana="median",
        p25=lambda x: x.quantile(0.25),
        p75=lambda x: x.quantile(0.75),
        desv="std",
        promedio_dbm=fisica.promedio_dbm,
        promedio_potencia_dbm=fisica.promedio_potencia_dbm,
    )
    return tabla.reset_index()


def _por_condicion(df, orden):
    """Mediana por condición juntando todas las repeticiones, en el orden dado."""
    t = resumen_por_punto(df, por_repeticion=False).set_index("condicion")
    return t.reindex([c for c in orden if c in t.index])


# --- Un análisis por experimento --------------------------------------------

def _exigir(tabla, condicion, experimento):
    if condicion not in tabla.index:
        raise ValueError(f"{experimento} necesita la condición de referencia "
                         f"'{condicion}' y no se midió (¿se saltó?).")


def analizar_e1(df):
    """Ajuste log-distancia sobre las medianas de cada (repetición, distancia)."""
    puntos = resumen_por_punto(df)
    # Una recta con 2 puntos pasa exacto por ellos: no hay residuos ni IC.
    if puntos["valor_condicion"].nunique() < 3:
        raise ValueError("E1 necesita al menos 3 distancias distintas para el ajuste.")
    ajuste = fisica.ajustar_log_distancia(puntos["valor_condicion"], puntos["mediana"])
    puntos["residuo"] = ajuste["residuos"]
    # Friis "absoluto": con +9 dBm y antenas ideales de 0 dBi esperaríamos
    # 9 − 40.2 ≈ −31 dBm a 1 m. Lo que falte son pérdidas reales del sistema
    # (antenas pequeñas, el cuerpo del portátil, desacople, cables...).
    rssi_ideal_1m = fisica.POTENCIA_TX_DBM - fisica.fspl_db(1.0)

    # ¿Sirve el RSSI como regla? Estimamos la distancia de cada punto con el
    # propio modelo y comparamos con la distancia real (en %).
    d_est, _, _ = fisica.distancia_desde_rssi(puntos["mediana"], ajuste["rssi_d0"], ajuste["n"])
    puntos["distancia_estimada_m"] = d_est
    error_rel = np.abs(d_est / puntos["valor_condicion"] - 1)

    # Presupuesto de enlace: hasta dónde llegaría según este modelo. Con un
    # margen de 1.28σ, el 90 % de las posiciones a esa distancia aún tienen señal.
    margen = 1.28 * ajuste["sigma_db"]
    return {
        "puntos": puntos,
        "error_distancia_mediano": float(np.median(error_rel)),
        "factor_incertidumbre_distancia": 10 ** (ajuste["sigma_db"] / (10 * ajuste["n"])),
        "alcance_predicho_m": fisica.alcance_predicho(ajuste["rssi_d0"], ajuste["n"]),
        "alcance_predicho_90_m": fisica.alcance_predicho(ajuste["rssi_d0"], ajuste["n"],
                                                         margen_db=margen),
        "ajuste": ajuste,
        "interpretacion_n": fisica.interpretar_n(ajuste["n"]),
        "rssi_friis_ideal_1m": rssi_ideal_1m,
        "perdidas_sistema_db": rssi_ideal_1m - ajuste["rssi_d0"],
        "repeticiones": int(df["repeticion"].nunique()),
    }


def analizar_e2(df):
    """Atenuación de cada obstáculo respecto a la línea de vista."""
    orden = [c[0] for c in EXPERIMENTOS["E2"]["condiciones"]]
    t = _por_condicion(df, orden)
    _exigir(t, "linea_de_vista", "E2")
    referencia = t.loc["linea_de_vista", "mediana"]
    t["atenuacion_db"] = referencia - t["mediana"]
    t["cm_musculo_equivalentes"] = fisica.cm_equivalentes_de_musculo(t["atenuacion_db"])
    # Factor K de Rice de cada condición (mediana entre repeticiones): al
    # tapar el camino directo la señal "tiembla" más y K baja.
    k = df.groupby(["condicion", "repeticion"])["rssi_dbm"].apply(fisica.factor_k_rice)
    t["k_rice"] = k.groupby("condicion").median().reindex(t.index)
    return {"tabla": t, "referencia_dbm": referencia,
            # Dos modelos para "persona en medio": la onda la RODEA
            # (difracción por sus costados) o la ATRAVIESA (25 cm de músculo).
            "prediccion_difraccion_db": fisica.perdida_persona_db(),
            "prediccion_atravesar_db": 25 * fisica.atenuacion_db_por_cm(),
            "radio_fresnel_cm": 100 * fisica.radio_fresnel(1.0, 1.0),
            "muestras": df[["condicion", "rssi_dbm"]],
            "db_por_cm_musculo": fisica.atenuacion_db_por_cm(),
            "profundidad_penetracion_cm": 100 * fisica.profundidad_penetracion()}


def analizar_e3(df):
    """Patrón de radiación: RSSI relativo al máximo (0 dB = mejor dirección)."""
    t = resumen_por_punto(df, por_repeticion=False).sort_values("valor_condicion")
    t["relativo_db"] = t["mediana"] - t["mediana"].max()
    peor = t.loc[t["relativo_db"].idxmin()]
    return {"tabla": t, "rango_db": -t["relativo_db"].min(),
            "angulo_peor": float(peor["valor_condicion"]),
            "angulo_mejor": float(t.loc[t["relativo_db"].idxmax(), "valor_condicion"])}


def analizar_e4(df):
    """Diferencia de cada posición de la antena contra el diseño final."""
    orden = [c[0] for c in EXPERIMENTOS["E4"]["condiciones"]]
    t = _por_condicion(df, orden)
    _exigir(t, "antena_sobresale", "E4")
    t["diferencia_db"] = t["mediana"] - t.loc["antena_sobresale", "mediana"]
    return {"tabla": t}


def analizar_e5(df, metas):
    """Tasa de paquetes y RSSI contra la distancia; alcance máximo.

    La tasa sale de los resúmenes del JSON, que incluyen también los puntos
    con 0 muestras (que en el CSV no dejan ni una fila).
    """
    filas = []
    for m in metas:
        for p in m.get("puntos", []):
            filas.append({"repeticion": m.get("repeticion", 1), "distancia_m": p["valor"],
                          "n_muestras": p["n_muestras"], "duracion_s": p["duracion_s"]})
    if not filas or not any(f["n_muestras"] for f in filas):
        raise ValueError("E5 no tiene ningún punto con señal.")
    t = pd.DataFrame(filas).groupby("distancia_m", as_index=False)[["n_muestras", "duracion_s"]].sum()
    t["tasa_hz"] = fisica.tasa_paquetes(t["n_muestras"], t["duracion_s"])
    # Normalizamos respecto al punto más cercano CON señal (si el primero
    # se midió con 0 muestras, dividir por él daría infinito).
    t["tasa_normalizada"] = t["tasa_hz"] / t.loc[t["n_muestras"] > 0, "tasa_hz"].iloc[0]

    medianas = df.groupby("valor_condicion")["rssi_dbm"].median()
    t["mediana_dbm"] = t["distancia_m"].map(medianas)

    con_senal = t[t["n_muestras"] > 0]
    alcance = float(con_senal["distancia_m"].max()) if len(con_senal) else 0.0
    # Distancia donde se recibe menos de la mitad de los paquetes de cerca.
    bajo_mitad = t[t["tasa_normalizada"] < 0.5]
    d50 = float(bajo_mitad["distancia_m"].min()) if len(bajo_mitad) else None
    return {"tabla": t, "alcance_max_m": alcance, "distancia_tasa_50_m": d50}


def analizar(df, metas):
    """Despacha según el experimento (todas las filas deben ser del mismo)."""
    if df.empty and not any(m.get("puntos") for m in metas):
        raise ValueError("la sesión no tiene ninguna muestra.")
    experimentos = df["experimento"].unique() if not df.empty else [metas[0]["experimento"]]
    if len(experimentos) != 1:
        raise ValueError(f"Se mezclaron experimentos: {list(experimentos)}")
    exp = experimentos[0]
    funciones = {"E1": analizar_e1, "E2": analizar_e2, "E3": analizar_e3, "E4": analizar_e4}
    resultado = analizar_e5(df, metas) if exp == "E5" else funciones[exp](df)
    resultado["experimento"] = exp
    resultado["sesiones"] = [m["sesion"] for m in metas]
    resultado["metadatos"] = {k: v for k, v in metas[0].items() if k != "puntos"}
    return resultado


# --- Calibración para el buscador y la calculadora --------------------------

CALIBRACION_POR_DEFECTO = {"rssi_d0": -55.0, "n": 2.2, "sigma_db": 3.0, "medida": False}


def calibracion(carpeta="datos"):
    """Parámetros del modelo log-distancia: los de E1 si ya se analizó
    (datos/analisis_E1.json); si no, valores típicos."""
    ruta = Path(carpeta) / "analisis_E1.json"
    if not ruta.exists():
        return dict(CALIBRACION_POR_DEFECTO)
    with open(ruta, encoding="utf-8") as f:
        a = json.load(f)["ajuste"]
    return {"rssi_d0": a["rssi_d0"], "n": a["n"], "sigma_db": a["sigma_db"], "medida": True}


# --- Agrupar archivos por experimento ---------------------------------------

def agrupar_sesiones(rutas):
    """{experimento: [rutas]} a partir del prefijo del nombre (E1_..., E2_...)."""
    grupos = {}
    for r in sorted(map(Path, rutas)):
        exp = r.stem.split("_")[0]
        if exp in EXPERIMENTOS:
            grupos.setdefault(exp, []).append(r)
    return grupos


def sesiones_en(carpeta):
    return [r for r in Path(carpeta).glob("*.csv")]


# --- Salida -----------------------------------------------------------------

def imprimir(res):
    exp = res["experimento"]
    print(f"\n=== {exp}: {EXPERIMENTOS[exp]['nombre']}  ({len(res['sesiones'])} sesión/es)")
    if exp == "E1":
        a = res["ajuste"]
        print(f"  n = {a['n']:.2f} ± {a['n_ic95']:.2f} (IC 95 %)  →  {res['interpretacion_n']}")
        print(f"  RSSI(1 m) = {a['rssi_d0']:.1f} ± {a['rssi_d0_ic95']:.1f} dBm")
        print(f"  R² = {a['r2']:.3f}   σ (sombreado) = {a['sigma_db']:.1f} dB   "
              f"puntos = {a['n_puntos']} ({res['repeticiones']} repeticiones)")
        print(f"  Friis ideal a 1 m (+9 dBm, 0 dBi): {res['rssi_friis_ideal_1m']:.1f} dBm "
              f"→ pérdidas del sistema ≈ {res['perdidas_sistema_db']:.1f} dB")
        print(f"  Como regla: error típico de distancia {100 * res['error_distancia_mediano']:.0f} %, "
              f"incertidumbre ×/÷ {res['factor_incertidumbre_distancia']:.2f}")
        print(f"  Alcance predicho (RSSI = {fisica.SENSIBILIDAD_TIPICA_DBM:.0f} dBm): "
              f"{res['alcance_predicho_m']:.0f} m  (90 % de posiciones: "
              f"{res['alcance_predicho_90_m']:.0f} m)")
    elif exp == "E2":
        print(f"  Línea de vista: {res['referencia_dbm']:.1f} dBm. Músculo a 2.45 GHz: "
              f"δ = {res['profundidad_penetracion_cm']:.2f} cm, "
              f"{res['db_por_cm_musculo']:.1f} dB/cm")
        for c, f in res["tabla"].iterrows():
            print(f"  {c:18s} {f['mediana']:6.1f} dBm  atenuación {f['atenuacion_db']:5.1f} dB  "
                  f"K de Rice {f['k_rice']:4.1f}")
        print(f"  Persona en medio, teoría: rodeándola (difracción) ≈ "
              f"{res['prediccion_difraccion_db']:.0f} dB; atravesándola ≈ "
              f"{res['prediccion_atravesar_db']:.0f} dB. Zona de Fresnel en la mitad: "
              f"r1 = {res['radio_fresnel_cm']:.0f} cm")
    elif exp == "E3":
        print(f"  Variación con el ángulo: {res['rango_db']:.1f} dB "
              f"(mejor {res['angulo_mejor']:.0f}°, peor {res['angulo_peor']:.0f}°)")
        for _, f in res["tabla"].iterrows():
            print(f"  {f['valor_condicion']:5.0f}°  {f['relativo_db']:6.1f} dB")
    elif exp == "E4":
        for c, f in res["tabla"].iterrows():
            print(f"  {c:18s} {f['mediana']:6.1f} dBm  ({f['diferencia_db']:+.1f} dB vs. diseño final)")
    elif exp == "E5":
        print(f"  Alcance máximo (último punto con señal): {res['alcance_max_m']:.0f} m")
        if res["distancia_tasa_50_m"]:
            print(f"  La tasa cae bajo el 50 % a partir de {res['distancia_tasa_50_m']:.0f} m")
        if res.get("alcance_predicho_e1_m"):
            print(f"  Predicho con el modelo de E1: {res['alcance_predicho_e1_m']:.0f} m "
                  f"(quiebre de dos rayos: {fisica.distancia_quiebre(1, 1):.0f} m)")


def _a_json(x):
    """Convierte DataFrames y tipos de numpy a algo que json.dump entienda."""
    if isinstance(x, pd.DataFrame):
        return json.loads(x.reset_index().to_json(orient="records", force_ascii=False))
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, dict):
        return {k: _a_json(v) for k, v in x.items()}
    if isinstance(x, (np.floating, np.integer)):
        return x.item()
    if isinstance(x, Path):
        return str(x)
    return x


def guardar_json(res, carpeta):
    ruta = Path(carpeta) / f"analisis_{res['experimento']}.json"
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(_a_json(res), f, ensure_ascii=False, indent=2)
    return ruta


def analizar_archivos(rutas, guardar=True, mostrar=True):
    """Analiza una lista de CSV; devuelve {experimento: resultado}.

    Si están E1 y E5, cruza los dos: el modelo ajustado en E1 predice el
    alcance, y E5 lo pone a prueba. Ese cruce es la prueba fuerte del modelo.
    """
    resultados = {}
    salida = print if mostrar else (lambda *a, **k: None)
    for exp, grupo in agrupar_sesiones(rutas).items():
        df, metas = sesion.cargar(grupo)
        try:
            res = analizar(df, metas)
        except ValueError as e:
            # Un experimento incompleto no debe impedir analizar los demás.
            salida(f"\n=== {exp}: no se puede analizar: {e}")
            continue
        resultados[exp] = res
        res["carpeta"] = grupo[0].parent

    if "E1" in resultados and "E5" in resultados:
        e1 = resultados["E1"]
        resultados["E5"]["alcance_predicho_e1_m"] = e1["alcance_predicho_m"]
        resultados["E5"]["modelo_e1"] = {"rssi_d0": e1["ajuste"]["rssi_d0"], "n": e1["ajuste"]["n"]}

    for res in resultados.values():
        if mostrar:
            imprimir(res)
        if guardar:
            salida(f"  → {guardar_json(res, res['carpeta'])}")
    return resultados


def main(argv=None):
    from .registrador import preparar_consola
    preparar_consola()
    p = argparse.ArgumentParser(description="Analiza sesiones de RSSI.")
    p.add_argument("csv", nargs="*", help="uno o varios CSV de sesión")
    p.add_argument("--todo", action="store_true", help="todas las sesiones de --carpeta")
    p.add_argument("--carpeta", default="datos")
    args = p.parse_args(argv)
    rutas = sesiones_en(args.carpeta) if args.todo else args.csv
    if not rutas:
        p.error("Indica uno o más CSV, o usa --todo")
    analizar_archivos(rutas)


if __name__ == "__main__":
    main()
