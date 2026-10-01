import json

import pandas as pd

from ivy_rssi import graficas, registrador, sesion
from ivy_rssi.experimentos import EXPERIMENTOS
from ivy_rssi.simulador import generar_ejemplo


def test_registrador_simulado_crea_csv_y_json(tmp_path, capsys):
    registrador.main(["--experimento", "E1", "--simular", "--auto",
                      "--carpeta", str(tmp_path), "--segundos", "10"])
    csvs = list(tmp_path.glob("E1_*.csv"))
    assert len(csvs) == 1
    df = pd.read_csv(csvs[0])
    assert list(df.columns) == sesion.COLUMNAS
    assert len(df) > 100
    assert df["rssi_dbm"].between(-110, -20).all()
    assert set(df["valor_condicion"]) == {c[1] for c in EXPERIMENTOS["E1"]["condiciones"]}

    meta = json.loads(csvs[0].with_suffix(".json").read_text(encoding="utf-8"))
    for clave in ["fecha", "sistema_operativo", "portatil", "fuente_alimentacion",
                  "altura_portatil_m", "altura_llavero_m", "repeticion", "notas"]:
        assert clave in meta
    assert meta["simulado"] is True
    assert len(meta["puntos"]) == len(EXPERIMENTOS["E1"]["condiciones"])
    assert all(p["tasa_hz"] > 4 for p in meta["puntos"])


def test_e5_termina_al_perder_la_senal(tmp_path):
    ruta = registrador.registrar("E5", tmp_path, segundos=5, simular=True, auto=True)
    meta = sesion.leer_metadatos(ruta)
    assert meta["puntos"][-1]["n_muestras"] == 0
    assert meta["puntos"][0]["n_muestras"] > 0


def test_punto_descartado_se_ignora(tmp_path):
    ruta = registrador.registrar("E4", tmp_path, segundos=5, simular=True, auto=True)
    antes = len(sesion.cargar(ruta)[0])
    sesion.descartar_ultimo_punto(ruta)
    df, metas = sesion.cargar(ruta)
    assert "sin_bateria" not in set(df["condicion"])
    assert len(df) < antes
    assert len(metas[0]["puntos"]) == 2


def test_graficas_se_generan(tmp_path):
    rutas = generar_ejemplo(tmp_path / "datos", segundos=5)
    creadas = graficas.graficar_archivos(rutas, tmp_path / "figuras")
    # 9 figuras de datos × 2 formatos
    assert len(creadas) == 18
    from PIL import Image
    video = [r for r in creadas if r.name.endswith("_video.png")]
    assert all(Image.open(r).size == (1920, 1080) for r in video)
