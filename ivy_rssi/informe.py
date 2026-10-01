"""Informe automático con la estructura de un trabajo de grado.

Toma los resultados del análisis y escribe INFORME.md junto a las figuras:
resumen, introducción, marco teórico, metodología, resultados, discusión,
conclusiones y limitaciones, con los números de TUS mediciones.

Uso:
    python -m ivy_rssi.informe --todo          # datos/ → figuras/INFORME.md
"""

import argparse
from pathlib import Path

from . import analisis, fisica, graficas


def _fig(nombre, pie):
    return f"![{pie}]({nombre}_informe.png)\n\n*{pie}*\n"


def _tabla(encabezado, filas):
    lineas = ["| " + " | ".join(encabezado) + " |", "|" + "---|" * len(encabezado)]
    lineas += ["| " + " | ".join(str(c) for c in f) + " |" for f in filas]
    return "\n".join(lineas) + "\n"


def _resultados_e1(r):
    a = r["ajuste"]
    return f"""### 4.1 Atenuación con la distancia (E1)

Se ajustó el modelo log-distancia a {a['n_puntos']} puntos ({r['repeticiones']} repeticiones):

{_tabla(["Parámetro", "Valor"], [
    ["Exponente de pérdida *n*", f"{a['n']:.2f} ± {a['n_ic95']:.2f} (IC 95 %)"],
    ["RSSI(1 m)", f"{a['rssi_d0']:.1f} ± {a['rssi_d0_ic95']:.1f} dBm"],
    ["R²", f"{a['r2']:.3f}"],
    ["σ del sombreado", f"{a['sigma_db']:.1f} dB"],
    ["Pérdidas del sistema frente a Friis ideal", f"{r['perdidas_sistema_db']:.1f} dB"],
])}
Interpretación de *n*: {r['interpretacion_n']}.

{_fig("E1_rssi_vs_distancia_log", "Figura 1. RSSI contra distancia (escala logarítmica), ajuste y referencia de Friis.")}
{_fig("E1_rssi_vs_distancia_lineal", "Figura 2. La misma caída en escala lineal, con la banda de ±σ del sombreado.")}
{_fig("E1_residuos", "Figura 3. Residuos del ajuste y la normal con σ medida: el sombreado es log-normal.")}
**El RSSI como estimador de distancia.** Invirtiendo el modelo, el error típico fue de
{100 * r['error_distancia_mediano']:.0f} % y la incertidumbre de ±1σ equivale a un factor ×/÷
{r['factor_incertidumbre_distancia']:.2f} sobre la distancia.

{_fig("E1_rssi_como_regla", "Figura 4. Distancia estimada con el RSSI contra distancia real.")}"""


def _resultados_e2(r):
    t = r["tabla"]
    filas = [[graficas.ETIQUETAS.get(c, c).replace("\n", " "), f"{f['mediana']:.0f}",
              f"{f['atenuacion_db']:.0f}", f"{f['k_rice']:.1f}"] for c, f in t.iterrows()]
    return f"""### 4.2 El cuerpo como obstáculo (E2)

{_tabla(["Condición", "RSSI (dBm)", "Atenuación (dB)", "K de Rice"], filas)}
{_fig("E2_cuerpo_obstaculo", "Figura 5. Atenuación de cada obstáculo y predicción por difracción.")}
{_fig("E2_desvanecimiento", "Figura 6. Distribución de la potencia de los paquetes y ajuste de Rice.")}"""


def _resultados_e3(r):
    return f"""### 4.3 Patrón de radiación (E3)

La señal varió {r['rango_db']:.1f} dB con la orientación: máxima hacia {r['angulo_mejor']:.0f}°
y mínima hacia {r['angulo_peor']:.0f}°.

{_fig("E3_patron_radiacion", "Figura 7. Patrón de radiación medido (0 dB = dirección más fuerte).")}"""


def _resultados_e4(r):
    filas = [[graficas.ETIQUETAS.get(c, c).replace("\n", " "), f"{f['mediana']:.0f}",
              f"{f['diferencia_db']:+.0f}"] for c, f in r["tabla"].iterrows()]
    return f"""### 4.4 Antena y batería (E4)

{_tabla(["Posición", "RSSI (dBm)", "Diferencia (dB)"], filas)}
{_fig("E4_antena_vs_bateria", "Figura 8. Margen de enlace en cada posición de la antena.")}"""


def _resultados_e5(r):
    extra = ""
    if r.get("alcance_predicho_e1_m"):
        extra = (f" El modelo de E1 predecía {r['alcance_predicho_e1_m']:.0f} m "
                 f"(error de {100 * (r['alcance_max_m'] / r['alcance_predicho_e1_m'] - 1):+.0f} %).")
    d50 = (f" La tasa de paquetes cayó bajo el 50 % desde {r['distancia_tasa_50_m']:.0f} m."
           if r["distancia_tasa_50_m"] else "")
    return f"""### 4.5 Alcance máximo (E5)

El último punto con señal estuvo a **{r['alcance_max_m']:.0f} m**.{d50}{extra}

{_fig("E5_alcance", "Figura 9. Tasa de paquetes y RSSI contra distancia.")}"""


def _discusion(res):
    puntos = []
    if "E1" in res:
        a = res["E1"]["ajuste"]
        puntos.append(
            f"- **Exponente de pérdida.** *n* = {a['n']:.2f} ± {a['n_ic95']:.2f}. "
            + ("El intervalo incluye a 2: no se distingue del espacio libre."
               if abs(a["n"] - 2) <= a["n_ic95"] else
               "El intervalo excluye a 2: el ambiente sí modifica la propagación "
               + ("(el pasillo concentra la energía)." if a["n"] < 2 else "(reflexiones y obstáculos)."))
            + f" Las pérdidas del sistema (≈ {res['E1']['perdidas_sistema_db']:.0f} dB frente a Friis ideal)"
            " corresponden a antenas pequeñas, no ideales y con desacople de polarización.")
    if "E2" in res:
        r = res["E2"]
        t = r["tabla"]
        if "persona_en_medio" in t.index:
            med = t.loc["persona_en_medio", "atenuacion_db"]
            puntos.append(
                f"- **Difracción contra absorción.** Una persona en medio atenuó {med:.0f} dB. "
                f"Si la onda atravesara 25 cm de músculo (δ = {r['profundidad_penetracion_cm']:.2f} cm) "
                f"perdería ≈ {r['prediccion_atravesar_db']:.0f} dB; la difracción por los costados del "
                f"cuerpo predice ≈ {r['prediccion_difraccion_db']:.0f} dB. La medición es compatible con "
                "que la onda **rodea** el cuerpo, no que lo atraviesa. La zona de Fresnel en la mitad "
                f"del enlace (r₁ = {r['radio_fresnel_cm']:.0f} cm) es del tamaño de un torso: por eso "
                "una persona la tapa casi por completo.")
            puntos.append(
                f"- **Desvanecimiento.** El factor K de Rice bajó de "
                f"{t.loc['linea_de_vista', 'k_rice']:.1f} con línea de vista a "
                f"{t.loc['persona_en_medio', 'k_rice']:.1f} con una persona en medio: sin camino "
                "directo, la señal llega solo por caminos dispersos y fluctúa más (tiende a Rayleigh).")
    if "E1" in res and "E5" in res and res["E5"].get("alcance_predicho_e1_m"):
        pred, med = res["E5"]["alcance_predicho_e1_m"], res["E5"]["alcance_max_m"]
        puntos.append(
            f"- **Validación cruzada.** El modelo calibrado en E1 (hasta 10 m) predijo un alcance de "
            f"{pred:.0f} m y E5 midió {med:.0f} m. Extrapolar un factor ~{pred / 10:.0f} fuera del rango "
            "de calibración es exigente. "
            + (f"Que E5 se quede corto es coherente con el modelo de dos rayos: más allá del quiebre "
               f"({fisica.distancia_quiebre(1, 1):.0f} m) la reflexión en el piso sube el exponente hacia 4."
               if med < pred else
               "Que E5 llegue más lejos indica que su lugar propaga mejor que el de E1 (menos "
               "obstáculos) o que la sensibilidad real del portátil es mejor que −95 dBm."))
    if "E4" in res and "antena_encima" in res["E4"]["tabla"].index:
        dif = res["E4"]["tabla"].loc["antena_encima", "diferencia_db"]
        puntos.append(
            f"- **Regla de diseño.** Con la antena encima de la batería la señal cambió {dif:+.0f} dB "
            f"({100 * (1 - 10 ** (dif / 10)):.0f} % de la potencia perdida). La bolsa de aluminio de "
            "la LiPo refleja la onda y, por estar a menos de λ/4 de la antena, su corriente imagen "
            "cancela parte de la radiación. Se justifica que la antena sobresalga de la batería.")
    return "\n".join(puntos) + "\n"


def escribir_informe(resultados, carpeta):
    """Escribe <carpeta>/INFORME.md y devuelve su ruta."""
    simulado = any(r["metadatos"].get("simulado") for r in resultados.values())
    meta = next(iter(resultados.values()))["metadatos"] if resultados else {}
    secciones = {"E1": _resultados_e1, "E2": _resultados_e2, "E3": _resultados_e3,
                 "E4": _resultados_e4, "E5": _resultados_e5}
    resumen_n = ""
    if "E1" in resultados:
        a = resultados["E1"]["ajuste"]
        resumen_n = (f" El exponente de pérdida medido fue *n* = {a['n']:.2f} ± {a['n_ic95']:.2f} "
                     f"(R² = {a['r2']:.2f}).")
    aviso = ("> ⚠️ **Este informe usa datos SIMULADOS.** Sirve para ver la estructura; "
             "los números reales salen de las mediciones.\n\n" if simulado else "")

    texto = f"""# Propagación de la señal Bluetooth de 2.4 GHz del llavero de alerta Ivy

*Física, Calor y Ondas — Universidad del Norte*

{aviso}## Resumen

Se caracterizó experimentalmente la propagación de la onda electromagnética de 2.4 GHz
que emite el llavero de alerta personal Ivy (ESP32, Bluetooth Low Energy, +9 dBm), midiendo
la intensidad de señal recibida (RSSI) en un portátil en {len(resultados)} experimentos:
distancia, obstrucción por el cuerpo humano, orientación, posición de la antena respecto a
la batería y alcance máximo.{resumen_n} Los resultados se interpretan con la ecuación de
Friis, el modelo log-distancia con sombreado log-normal, la atenuación en dieléctricos con
pérdidas, la difracción por filo de cuchillo, el desvanecimiento de Rice y el modelo de dos
rayos, y justifican reglas concretas de diseño de la carcasa.

## 1. Introducción

Un llavero de alerta solo es útil si su señal llega al celular cuando más se necesita: con
el llavero en un bolsillo, en un morral o con el cuerpo de la persona en medio. Este trabajo
mide cómo se comporta la onda de 2.4 GHz en esas condiciones reales y usa la física de ondas
para explicar los resultados y tomar decisiones de diseño.

**Objetivo general.** Caracterizar la atenuación de la señal BLE del llavero y explicarla con
modelos físicos de propagación de ondas.

**Objetivos específicos.** (1) Medir el exponente de pérdida *n* del ambiente. (2) Cuantificar
la atenuación del cuerpo humano y contrastar absorción contra difracción. (3) Medir el patrón
de radiación. (4) Evaluar el efecto de la batería sobre la antena. (5) Determinar el alcance y
validar la predicción del modelo.

## 2. Marco teórico

El desarrollo completo, con fórmulas y referencias, está en `FISICA.md`. En síntesis:

{_tabla(["Fenómeno", "Modelo", "Resultado clave"], [
    ["Onda de 2.44 GHz", "λ = c/f", f"λ = {100 * fisica.longitud_onda():.1f} cm"],
    ["Espacio libre", "Friis: FSPL = 20·log10(4πd/λ)", f"{fisica.fspl_db(1.0):.1f} dB a 1 m"],
    ["Ambiente real", "Log-distancia + sombreado X_σ", "*n* y σ medidos"],
    ["Tejido", "Dieléctrico con pérdidas (Gabriel 1996)",
     f"δ = {100 * fisica.profundidad_penetracion():.2f} cm, {fisica.atenuacion_db_por_cm():.1f} dB/cm"],
    ["Obstáculo", "Fresnel-Kirchhoff, UIT-R P.526", f"persona: ≈ {fisica.perdida_persona_db():.0f} dB"],
    ["Agua", "Relajación de Debye",
     f"pico de absorción a {fisica.frecuencia_pico_perdidas() / 1e9:.0f} GHz, no a 2.45"],
    ["Piso", "Dos rayos", f"quiebre a {fisica.distancia_quiebre(1, 1):.0f} m"],
    ["Fluctuación", "Desvanecimiento de Rice", "factor K"],
    ["Seguridad", "SAR ≤ P/m", f"≤ {fisica.sar_cota_w_kg():.1f} W/kg (límite 2 W/kg)"],
])}
{_fig("T1_agua_debye", "Figura T1. Permitividad del agua (modelo de Debye).")}
{_fig("T2_dos_rayos", "Figura T2. Espacio libre contra el modelo de dos rayos.")}
## 3. Metodología

El portátil registró con escaneo BLE activo cada anuncio del llavero (`GEOEXPO-ALERT`) durante
{meta.get('segundos_por_punto', 30):g} s por punto, guardando marca de tiempo y RSSI. El valor
de cada punto es la **mediana** de sus muestras. Montaje: llavero sobre soporte no metálico a
{meta.get('altura_llavero_m', 1.0)} m y portátil a {meta.get('altura_portatil_m', 1.0)} m de
altura; lugar: {meta.get('lugar') or 'sin anotar'}; alimentación del llavero:
{meta.get('fuente_alimentacion') or 'sin anotar'}; sistema: {meta.get('sistema_operativo', '')}.
El protocolo completo está en `PROTOCOLO.md`; los datos crudos (CSV) y metadatos (JSON),
en `datos/`.

## 4. Resultados

{chr(10).join(secciones[e](resultados[e]) for e in sorted(resultados))}
## 5. Discusión

{_discusion(resultados)}
## 6. Conclusiones

- La señal del llavero sigue el modelo log-distancia; el ambiente queda resumido en *n* y σ.
- El cuerpo humano es prácticamente opaco a 2.4 GHz (δ ≈ 2 cm), pero la onda lo rodea por
  difracción: llevar el llavero pegado al cuerpo cuesta decenas de dB, no lo vuelve invisible.
- El RSSI permite saber si el llavero está "cerca o lejos", no medir la distancia con precisión.
- La antena debe sobresalir de la batería y apuntar hacia fuera del cuerpo.

## 7. Limitaciones y trabajo futuro

- El patrón de E3 mezcla la antena con las reflexiones del lugar; un patrón puro requiere
  cámara anecoica.
- El RSSI de cerca al límite de sensibilidad está sesgado hacia arriba (solo se registran los
  paquetes que llegan); la tasa de paquetes es la medida de alcance más honesta.
- El escáner no informa en cuál de los 3 canales llegó cada paquete; con esa información se
  podría estudiar la diversidad en frecuencia.

## Referencias

Ver la lista completa y verificada en `FISICA.md`.
"""
    ruta = Path(carpeta) / "INFORME.md"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(texto, encoding="utf-8")
    return ruta


def generar_todo(rutas_csv, carpeta):
    """Analiza, grafica (datos + teoría) y escribe el informe en `carpeta`."""
    resultados = analisis.analizar_archivos(rutas_csv, guardar=False, mostrar=False)
    figuras = graficas.graficar_archivos(rutas_csv, carpeta) + graficas.graficar_teoria(carpeta)
    return escribir_informe(resultados, carpeta), figuras


def main(argv=None):
    from .registrador import preparar_consola
    preparar_consola()
    p = argparse.ArgumentParser(description="Genera el informe tipo trabajo de grado.")
    p.add_argument("csv", nargs="*")
    p.add_argument("--todo", action="store_true")
    p.add_argument("--carpeta", default="datos")
    p.add_argument("--salida", default="figuras")
    p.add_argument("--ejemplo", action="store_true",
                   help="simula los 5 experimentos → figuras/ejemplo/ con su INFORME.md")
    args = p.parse_args(argv)
    if args.ejemplo:
        import tempfile
        from .simulador import generar_ejemplo
        with tempfile.TemporaryDirectory() as tmp:
            ruta, figuras = generar_todo(generar_ejemplo(tmp), Path(args.salida) / "ejemplo")
        print(f"{ruta}  (+ {len(figuras)} figuras)")
        return
    rutas = analisis.sesiones_en(args.carpeta) if args.todo else args.csv
    if not rutas:
        p.error("Indica uno o más CSV, o usa --todo")
    ruta, figuras = generar_todo(rutas, args.salida)
    print(f"{ruta}  (+ {len(figuras)} figuras)")


if __name__ == "__main__":
    main()
