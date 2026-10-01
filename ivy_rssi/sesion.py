"""Lectura y escritura de sesiones: un CSV crudo + un JSON de metadatos.

Lo usan el registrador, el simulador y el análisis, para que todos hablen
el mismo formato.
"""

import csv
import json
from datetime import datetime
from pathlib import Path

import pandas as pd

COLUMNAS = ["timestamp", "experimento", "condicion", "valor_condicion", "rssi_dbm"]


def nueva_sesion(carpeta, experimento, metadatos):
    """Crea el CSV (solo encabezado) y el JSON de una sesión nueva.

    Devuelve la ruta del CSV. El JSON tiene el mismo nombre con extensión .json.
    """
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    rep = metadatos.get("repeticion", 1)
    nombre = f"{experimento}_r{rep}_{datetime.now():%Y%m%d-%H%M%S}"
    ruta_csv = carpeta / f"{nombre}.csv"
    # Si ya existe (dos sesiones en el mismo segundo), se agrega un sufijo.
    i = 2
    while ruta_csv.exists():
        ruta_csv = carpeta / f"{nombre}-{i}.csv"
        i += 1

    with open(ruta_csv, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(COLUMNAS)

    metadatos = {**metadatos, "experimento": experimento, "puntos": []}
    guardar_metadatos(ruta_csv, metadatos)
    return ruta_csv


def ruta_json(ruta_csv):
    return Path(ruta_csv).with_suffix(".json")


def guardar_metadatos(ruta_csv, metadatos):
    with open(ruta_json(ruta_csv), "w", encoding="utf-8") as f:
        json.dump(metadatos, f, ensure_ascii=False, indent=2)


def leer_metadatos(ruta_csv):
    ruta = ruta_json(ruta_csv)
    if not ruta.exists():
        return {}
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def guardar_punto(ruta_csv, experimento, etiqueta, valor, muestras, resumen):
    """Agrega al CSV las muestras de UN punto y su resumen al JSON.

    Se llama apenas termina cada punto (escritura incremental): si el
    programa se cae en el punto 7, los 6 anteriores ya están en disco.
    `muestras` es una lista de (timestamp, rssi_dbm).
    """
    valor_txt = "" if valor is None else valor
    with open(ruta_csv, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for t, rssi in muestras:
            w.writerow([f"{t:.3f}", experimento, etiqueta, valor_txt, rssi])

    metadatos = leer_metadatos(ruta_csv)
    metadatos.setdefault("puntos", []).append(resumen)
    guardar_metadatos(ruta_csv, metadatos)


def descartar_ultimo_punto(ruta_csv):
    """Marca el último punto como descartado (cuando el usuario lo repite).

    Las muestras siguen en el CSV (nunca se borra nada medido), pero
    `cargar()` las ignora usando la ventana de tiempo guardada en el JSON.
    """
    metadatos = leer_metadatos(ruta_csv)
    if metadatos.get("puntos"):
        metadatos["puntos"][-1]["descartado"] = True
        guardar_metadatos(ruta_csv, metadatos)


def _quitar_descartados(df, meta):
    for p in meta.get("puntos", []):
        if p.get("descartado"):
            dentro = (df["condicion"] == p["condicion"]) & df["timestamp"].between(p["t_inicio"], p["t_fin"])
            df = df[~dentro]
    return df


def cargar(rutas_csv):
    """Lee una o varias sesiones y devuelve un único DataFrame.

    Agrega las columnas `sesion` (nombre del archivo) y `repeticion`
    (tomada del JSON), para poder combinar repeticiones en el análisis.
    Ignora los puntos descartados. También devuelve la lista de metadatos
    de cada sesión (sin los puntos descartados).
    """
    if isinstance(rutas_csv, (str, Path)):
        rutas_csv = [rutas_csv]
    tablas, metas = [], []
    for ruta in rutas_csv:
        df = pd.read_csv(ruta)
        meta = leer_metadatos(ruta)
        df = _quitar_descartados(df, meta)
        df["sesion"] = Path(ruta).stem
        df["repeticion"] = meta.get("repeticion", 1)
        tablas.append(df)
        puntos = [p for p in meta.get("puntos", []) if not p.get("descartado")]
        metas.append({**meta, "puntos": puntos, "sesion": Path(ruta).stem})
    return pd.concat(tablas, ignore_index=True), metas
