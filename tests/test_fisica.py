import numpy as np
import pytest

from ivy_rssi import fisica
from ivy_rssi.simulador import N_SIM, RSSI_1M, SIGMA_SOMBRA, generar_ejemplo
from ivy_rssi import analisis


def test_longitud_onda():
    assert fisica.longitud_onda() == pytest.approx(0.1229, abs=1e-3)


def test_fspl_1m():
    # 20·log10(4π·1 m / 0.1229 m) = 40.2 dB
    assert fisica.fspl_db(1.0) == pytest.approx(40.2, abs=0.05)


def test_fspl_crece_6db_al_duplicar_distancia():
    # n = 2: duplicar d suma 20·log10(2) ≈ 6.02 dB
    assert fisica.fspl_db(2.0) - fisica.fspl_db(1.0) == pytest.approx(6.02, abs=0.01)


def test_profundidad_penetracion_musculo():
    # Literatura: músculo a 2.45 GHz, δ (campo) ≈ 2.2 cm (base de datos IT'IS).
    delta_cm = 100 * fisica.profundidad_penetracion()
    assert 2.0 < delta_cm < 2.5
    assert delta_cm == pytest.approx(2.23, abs=0.05)


def test_no_es_buen_conductor():
    # Tangente de pérdidas ≈ 0.24 < 1: la aproximación de buen conductor no aplica.
    tan = fisica.tangente_perdidas(fisica.MUSCULO_EPS_R, fisica.MUSCULO_SIGMA,
                                   fisica.FRECUENCIA_MICROONDAS_HZ)
    assert tan == pytest.approx(0.24, abs=0.01)
    buen_conductor = np.sqrt(2 / (2 * np.pi * 2.45e9 * fisica.MU_0 * fisica.MUSCULO_SIGMA))
    assert buen_conductor < 0.5 * fisica.profundidad_penetracion()


def test_atenuacion_por_cm():
    assert fisica.atenuacion_db_por_cm() == pytest.approx(3.9, abs=0.1)


def test_promedio_potencia_mayor_o_igual():
    x = np.array([-60, -70, -80])
    assert fisica.promedio_potencia_dbm(x) >= fisica.promedio_dbm(x)
    # Si todos son iguales, los dos promedios coinciden.
    assert fisica.promedio_potencia_dbm([-65, -65]) == pytest.approx(-65)


def test_ajuste_exacto_sin_ruido():
    d = np.array([0.5, 1, 2, 4, 8])
    a = fisica.ajustar_log_distancia(d, fisica.rssi_log_distancia(d, -50, 2.7))
    assert a["n"] == pytest.approx(2.7)
    assert a["rssi_d0"] == pytest.approx(-50)
    assert a["r2"] == pytest.approx(1)


def test_ajuste_recupera_n_con_datos_simulados(tmp_path):
    rutas = generar_ejemplo(tmp_path, segundos=30)
    res = analisis.analizar_archivos([r for r in rutas if r.stem.startswith("E1")],
                                     guardar=False)["E1"]
    a = res["ajuste"]
    assert a["n"] == pytest.approx(N_SIM, abs=0.15)
    assert a["rssi_d0"] == pytest.approx(RSSI_1M, abs=2)
    assert a["sigma_db"] == pytest.approx(SIGMA_SOMBRA, abs=1)
    assert res["repeticiones"] == 3


def test_ajuste_sin_sesgo_en_muchas_semillas(tmp_path):
    # Con una sola semilla podría pasar "de suerte": comprobamos que en
    # promedio el estimador de n no tiene sesgo y que el IC 95 % acierta.
    ns, aciertos = [], 0
    for semilla in range(20):
        rutas = generar_ejemplo(tmp_path / str(semilla), semilla=semilla, segundos=5)
        e1 = [r for r in rutas if r.stem.startswith("E1")]
        a = analisis.analizar_archivos(e1, guardar=False)["E1"]["ajuste"]
        ns.append(a["n"])
        aciertos += abs(a["n"] - N_SIM) <= a["n_ic95"]
    assert np.mean(ns) == pytest.approx(N_SIM, abs=0.06)
    assert aciertos >= 16   # ~95 % de 20
