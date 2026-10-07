"""Evidencias de una sesión de mediciones: grabación, bitácora y puntos.

No toca el código de medición: mide con `registrador.medir_punto` y guarda con
`sesion.guardar_punto`, así los CSV/JSON quedan en el formato de siempre en
datos/ y `analisis`/`graficas` los leen sin cambios.

Uso (desde la raíz del repo, con el .venv):
    python herramientas/evidencias.py sesion --carpeta evidencias/2026-10-05_sesion1 --meta meta.json
    python herramientas/evidencias.py experimento --exp E1 --rep 1         # crea el CSV/JSON
    python herramientas/evidencias.py grabar-inicio --nombre E1_r1_distancia
    python herramientas/evidencias.py medir --exp E1 --cond "1 m" --valor 1 --instr "..."
    python herramientas/evidencias.py descartar --exp E1                   # repite el último punto
    python herramientas/evidencias.py grabar-fin --nombre E1_r1_distancia
    python herramientas/evidencias.py nota "pasó alguien"
    python herramientas/evidencias.py toma "📸 FOTO: plano general"
    python herramientas/evidencias.py fotograma --salida camara/encuadre.jpg
"""

import argparse
import json
import os
import statistics
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

ESTADO = RAIZ / "evidencias" / ".sesion_actual.json"
FFMPEG = os.environ.get("IVY_FFMPEG", "ffmpeg")
CAMARA = "Integrated Camera"
MICROFONO = "Microphone Array (Realtek(R) Audio)"


# --- Estado de la sesión ----------------------------------------------------

def _estado():
    return json.loads(ESTADO.read_text(encoding="utf-8")) if ESTADO.exists() else {}


def _guardar_estado(e):
    ESTADO.parent.mkdir(parents=True, exist_ok=True)
    ESTADO.write_text(json.dumps(e, ensure_ascii=False, indent=2), encoding="utf-8")


def _carpeta():
    return RAIZ / _estado()["carpeta"]


def _hora():
    return datetime.now().strftime("%H:%M:%S")


def bitacora(linea):
    with open(_carpeta() / "bitacora.md", "a", encoding="utf-8") as f:
        f.write(linea + "\n")


# --- Subcomandos ------------------------------------------------------------

def cmd_sesion(a):
    carpeta = RAIZ / a.carpeta
    for sub in ("datos", "pantalla", "camara", "celular", "figuras"):
        (carpeta / sub).mkdir(parents=True, exist_ok=True)
    meta = json.loads(Path(a.meta).read_text(encoding="utf-8-sig"))
    _guardar_estado({"carpeta": a.carpeta, "meta": meta, "csv": {}})
    b = carpeta / "bitacora.md"
    if not b.exists():
        filas = "\n".join(f"| {k} | {v} |" for k, v in meta.items())
        b.write_text(
            f"# Bitácora — {carpeta.name}\n\n"
            f"Inicio: {datetime.now():%Y-%m-%d %H:%M:%S}\n\n"
            f"## Montaje y condiciones\n\n| Dato | Valor |\n|---|---|\n{filas}\n\n"
            "## Registro\n\n"
            "Formato de puntos: `hora · experimento · condición · muestras · mediana · tasa`.\n"
            "🎥/📸 = toma pedida al celular (emparejar por hora).\n\n",
            encoding="utf-8")
    print(f"Sesión lista en {carpeta}")


def cmd_experimento(a):
    from ivy_rssi import sesion
    from ivy_rssi.registrador import NOMBRE_LLAVERO
    e = _estado()
    meta = {**e["meta"], "fecha": time.strftime("%Y-%m-%d %H:%M:%S"),
            "repeticion": a.rep, "simulado": a.simular,
            "segundos_por_punto": a.segundos, "nombre_buscado": NOMBRE_LLAVERO,
            "direccion": None, "carpeta_evidencias": e["carpeta"]}
    ruta = sesion.nueva_sesion(RAIZ / "datos", a.exp, meta)
    e["csv"][a.exp] = str(ruta.relative_to(RAIZ))
    _guardar_estado(e)
    bitacora(f"\n### {_hora()} — {a.exp} repetición {a.rep} (`{ruta.name}`)\n")
    print(ruta)


def _imprimir_cabecera(exp, cond, instr):
    print("=" * 60)
    print(f"  IVY RSSI · {exp} · {cond}")
    print(f"  {instr}")
    print("=" * 60)


def cmd_medir(a):
    """Mide UN punto y lo guarda. Pensado para correr en una ventana visible."""
    from ivy_rssi import sesion
    from ivy_rssi.registrador import _imprimir_resumen, medir_punto, preparar_consola
    import numpy as np
    preparar_consola()
    e = _estado()
    ruta = RAIZ / e["csv"][a.exp]
    valor = None if a.valor in (None, "") else float(a.valor)
    _imprimir_cabecera(a.exp, a.cond, a.instr or "")
    rng = np.random.default_rng() if a.simular else None
    try:
        muestras, r = medir_punto(a.exp, a.cond, valor, a.segundos, a.simular, None, rng)
    except Exception as err:  # Bluetooth apagado, etc.
        r = {"error": f"{type(err).__name__}: {err}"}
        print("ERROR:", r["error"])
        Path(a.resultado).write_text(json.dumps(r), encoding="utf-8")
        time.sleep(4)
        return
    sesion.guardar_punto(ruta, a.exp, a.cond, valor, muestras, r)
    _imprimir_resumen(r)

    # Comparación con los puntos anteriores de esta sesión (para avisar en el momento).
    meta = sesion.leer_metadatos(ruta)
    previos = [p for p in meta["puntos"][:-1] if not p.get("descartado") and p["mediana_dbm"] is not None]
    avisos = []
    if r["n_muestras"] < 0.5 * a.segundos and a.exp != "E5":
        avisos.append(f"pocas muestras ({r['n_muestras']} en {a.segundos:g} s)")
    if a.exp == "E1" and previos and r["mediana_dbm"] is not None:
        ant = previos[-1]
        if r["mediana_dbm"] - ant["mediana_dbm"] > 6:
            avisos.append(f"RSSI {r['mediana_dbm'] - ant['mediana_dbm']:+.0f} dB respecto a {ant['condicion']} "
                          "(debería bajar con la distancia)")
    r["avisos"] = avisos
    r["mediana_previas"] = [(p["condicion"], p["mediana_dbm"]) for p in previos]
    for x in avisos:
        print("  ⚠", x)

    med = "—" if r["mediana_dbm"] is None else f"{r['mediana_dbm']:.0f} dBm"
    bitacora(f"- {_hora()} · {a.exp} · {a.cond} · n={r['n_muestras']} · mediana {med} · "
             f"{r['tasa_hz']:.1f} muestras/s" + (f" · ⚠ {'; '.join(avisos)}" if avisos else ""))
    Path(a.resultado).write_text(json.dumps(r, ensure_ascii=False), encoding="utf-8")
    time.sleep(3)   # que se alcance a ver el resultado en la grabación


def cmd_descartar(a):
    from ivy_rssi import sesion
    ruta = RAIZ / _estado()["csv"][a.exp]
    sesion.descartar_ultimo_punto(ruta)
    bitacora(f"- {_hora()} · ↺ último punto de {a.exp} descartado ({a.motivo}); se repite")
    print("Descartado.")


def cmd_nota(a):
    bitacora(f"- {_hora()} · 📝 {a.texto}")


def cmd_toma(a):
    bitacora(f"- {_hora()} · {a.texto}")


# --- Grabación ---------------------------------------------------------------

def _args_pantalla(salida):
    return [FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
            "-f", "gdigrab", "-framerate", "15", "-draw_mouse", "1", "-i", "desktop",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "28", "-pix_fmt", "yuv420p",
            "-movflags", "+frag_keyframe+empty_moov", str(salida)]


def _args_camara(salida, audio=True):
    entrada = f"video={CAMARA}" + (f":audio={MICROFONO}" if audio else "")
    args = [FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
            "-f", "dshow", "-rtbufsize", "256M", "-vcodec", "mjpeg",
            "-video_size", "1280x720", "-framerate", "30", "-i", entrada,
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "26", "-pix_fmt", "yuv420p"]
    if audio:
        args += ["-c:a", "aac", "-b:a", "96k"]
    return args + ["-movflags", "+frag_keyframe+empty_moov", str(salida)]


def _mantener_despierto():
    """Pide a Windows no apagar la pantalla ni suspender mientras este proceso viva
    (como un reproductor de video). No cambia ninguna configuración."""
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000002 | 0x00000001)


def cmd_despierto(a):
    """Proceso de fondo que mantiene la pantalla encendida hasta que exista .despierto.stop."""
    stop = _carpeta() / ".grabando" / "despierto.stop"
    stop.parent.mkdir(exist_ok=True)
    stop.unlink(missing_ok=True)
    _mantener_despierto()
    while not stop.exists():
        time.sleep(2)
    stop.unlink(missing_ok=True)


def cmd_grabar_daemon(a):
    """Proceso en segundo plano: lanza los ffmpeg y los cierra con 'q' al ver el .stop."""
    carpeta = _carpeta()
    control = carpeta / ".grabando"
    control.mkdir(exist_ok=True)
    stop, listo = control / f"{a.nombre}.stop", control / f"{a.nombre}.listo"
    log = open(control / f"{a.nombre}.log", "w", encoding="utf-8")
    procs = {}

    def lanzar(clave, args):
        return subprocess.Popen(args, stdin=subprocess.PIPE, stdout=log, stderr=log,
                                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))

    procs["pantalla"] = lanzar("pantalla", _args_pantalla(carpeta / "pantalla" / f"{a.nombre}.mp4"))
    if a.camara:
        cam = carpeta / "camara" / f"{a.nombre}.mp4"
        procs["camara"] = lanzar("camara", _args_camara(cam))
        time.sleep(3)
        if procs["camara"].poll() is not None:     # sin micrófono, solo video
            procs["camara"] = lanzar("camara", _args_camara(cam, audio=False))
    time.sleep(2)
    caidos = [k for k, p in procs.items() if p.poll() is not None]
    if caidos:
        bitacora(f"- {_hora()} · ⚠ grabación {a.nombre}: falló {', '.join(caidos)} (ver .grabando/{a.nombre}.log)")
    (control / f"{a.nombre}.estado").write_text(json.dumps({"caidos": caidos}), encoding="utf-8")

    _mantener_despierto()
    parte = 1
    while not stop.exists():
        time.sleep(0.5)
        # gdigrab se cae si Windows bloquea la pantalla: se relanza en otro archivo.
        if procs["pantalla"].poll() is not None and parte < 20:
            time.sleep(2)
            parte += 1
            procs["pantalla"] = lanzar("pantalla", _args_pantalla(
                carpeta / "pantalla" / f"{a.nombre}_parte{parte}.mp4"))
            bitacora(f"- {_hora()} · ⚠ la grabación de pantalla se cortó (¿pantalla bloqueada?); "
                     f"sigue en `{a.nombre}_parte{parte}.mp4`")
    for p in procs.values():
        if p.poll() is None:
            try:
                p.stdin.write(b"q")
                p.stdin.flush()
            except OSError:
                pass
    for p in procs.values():
        try:
            p.wait(timeout=20)
        except subprocess.TimeoutExpired:
            p.kill()
    stop.unlink(missing_ok=True)
    listo.write_text("ok", encoding="utf-8")


def cmd_grabar_inicio(a):
    carpeta = _carpeta()
    control = carpeta / ".grabando"
    control.mkdir(exist_ok=True)
    for x in ("listo", "estado", "stop"):
        (control / f"{a.nombre}.{x}").unlink(missing_ok=True)
    args = [sys.executable, str(Path(__file__).resolve()), "grabar-daemon", "--nombre", a.nombre]
    if not a.sin_camara:
        args.append("--camara")
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(subprocess, "DETACHED_PROCESS", 0)
    subprocess.Popen(args, cwd=RAIZ, creationflags=flags, close_fds=True)
    est = control / f"{a.nombre}.estado"
    for _ in range(40):
        if est.exists():
            break
        time.sleep(0.25)
    caidos = json.loads(est.read_text())["caidos"] if est.exists() else ["(sin respuesta)"]
    bitacora(f"- {_hora()} · ⏺ inicia grabación `{a.nombre}`" + (f" · ⚠ falló {caidos}" if caidos else ""))
    print("Grabando" if not caidos else f"⚠ Falló: {caidos}")


def cmd_grabar_fin(a):
    control = _carpeta() / ".grabando"
    (control / f"{a.nombre}.stop").write_text("", encoding="utf-8")
    listo = control / f"{a.nombre}.listo"
    for _ in range(120):
        if listo.exists():
            break
        time.sleep(0.25)
    tam = {}
    for sub in ("pantalla", "camara"):
        f = _carpeta() / sub / f"{a.nombre}.mp4"
        if f.exists():
            tam[sub] = f"{f.stat().st_size / 1e6:.1f} MB"
    bitacora(f"- {_hora()} · ⏹ fin grabación `{a.nombre}` ({', '.join(f'{k} {v}' for k, v in tam.items()) or 'sin archivos'})")
    print(tam)


def cmd_fotograma(a):
    salida = _carpeta() / a.salida
    salida.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-f", "dshow",
                    "-vcodec", "mjpeg", "-video_size", "1280x720", "-framerate", "30",
                    "-i", f"video={CAMARA}", "-t", str(a.segundos), "-update", "1",
                    "-q:v", "3", str(salida)], check=True)
    print(salida)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="cmd", required=True)
    x = s.add_parser("sesion"); x.add_argument("--carpeta", required=True); x.add_argument("--meta", required=True)
    x = s.add_parser("experimento"); x.add_argument("--exp", required=True); x.add_argument("--rep", type=int, default=1)
    x.add_argument("--segundos", type=float, default=30); x.add_argument("--simular", action="store_true")
    x = s.add_parser("medir"); x.add_argument("--exp", required=True); x.add_argument("--cond", required=True)
    x.add_argument("--valor"); x.add_argument("--instr"); x.add_argument("--segundos", type=float, default=30)
    x.add_argument("--simular", action="store_true"); x.add_argument("--resultado", required=True)
    x = s.add_parser("descartar"); x.add_argument("--exp", required=True); x.add_argument("--motivo", default="")
    x = s.add_parser("nota"); x.add_argument("texto")
    x = s.add_parser("toma"); x.add_argument("texto")
    x = s.add_parser("grabar-inicio"); x.add_argument("--nombre", required=True); x.add_argument("--sin-camara", action="store_true")
    s.add_parser("despierto")
    x = s.add_parser("grabar-daemon"); x.add_argument("--nombre", required=True); x.add_argument("--camara", action="store_true")
    x = s.add_parser("grabar-fin"); x.add_argument("--nombre", required=True)
    x = s.add_parser("fotograma"); x.add_argument("--salida", required=True); x.add_argument("--segundos", type=float, default=3)
    a = p.parse_args()
    globals()["cmd_" + a.cmd.replace("-", "_")](a)


if __name__ == "__main__":
    main()
