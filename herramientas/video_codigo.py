"""Video "código en desarrollo": el código real de Ivy escribiéndose en un editor.

Cuatro escenas con fragmentos reales (firmware, app, registrador, física) y una
terminal con salidas reales de la sesión. Renderiza con Pillow + Pygments y
codifica con ffmpeg (1920x1080, 30 fps).

    python herramientas/video_codigo.py --salida evidencias/.../desarrollo_codigo.mp4 \
        --firmware ruta/a/main.cpp --app ../ivy-app
"""

import argparse
import os
import random
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pygments import lex
from pygments.lexers import get_lexer_by_name
from pygments.token import Token

RAIZ = Path(__file__).resolve().parent.parent
W, H, FPS = 1920, 1080, 30
FFMPEG = os.environ.get("IVY_FFMPEG", "ffmpeg")

# Paleta: editor oscuro con el ámbar de Ivy como acento.
C = {
    "fondo": (14, 12, 18), "ventana": (22, 19, 28), "barra": (30, 26, 38),
    "lateral": (26, 22, 33), "linea_act": (36, 31, 46), "numeros": (88, 80, 102),
    "num_act": (255, 194, 71), "texto": (226, 220, 232), "tenue": (140, 130, 155),
    "ambar": (255, 169, 40), "ambar_cl": (255, 194, 71), "crema": (255, 246, 230),
    "verde": (48, 209, 88), "terminal": (17, 15, 22),
}
SINTAXIS = [
    (Token.Comment, (120, 112, 138)),
    (Token.Literal.String.Doc, (150, 140, 120)),
    (Token.Literal.String, (166, 226, 140)),
    (Token.Literal.Number, (255, 160, 122)),
    (Token.Keyword, (255, 169, 40)),
    (Token.Name.Builtin, (130, 200, 255)),
    (Token.Name.Function, (255, 214, 120)),
    (Token.Name.Class, (255, 214, 120)),
    (Token.Name.Decorator, (255, 160, 122)),
    (Token.Name.Tag, (255, 169, 40)),
    (Token.Name.Attribute, (130, 200, 255)),
    (Token.Comment.Preproc, (255, 122, 26)),
    (Token.Operator, (200, 190, 215)),
    (Token.Punctuation, (170, 160, 185)),
]

FUENTES = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
F_MONO = ImageFont.truetype(str(FUENTES / "consola.ttf"), 25)
F_MONO_S = ImageFont.truetype(str(FUENTES / "consola.ttf"), 21)
F_TIT = ImageFont.truetype(str(RAIZ / "ivy_rssi/fuentes/BricolageGrotesque-700.ttf"), 120)
F_SUB = ImageFont.truetype(str(RAIZ / "ivy_rssi/fuentes/InstrumentSans-400.ttf"), 38)
F_UI = ImageFont.truetype(str(RAIZ / "ivy_rssi/fuentes/InstrumentSans-600.ttf"), 22)
F_UI_S = ImageFont.truetype(str(RAIZ / "ivy_rssi/fuentes/InstrumentSans-400.ttf"), 19)
CW = F_MONO.getlength("M")
LH = 34

# Geometría
X0, Y0 = 40, 30                     # ventana
WIN_W, WIN_H = W - 80, H - 60
TOP = Y0 + 44                       # bajo la barra de título
TABS_H = 42
SIDE_W = 300
ED_X, ED_Y = X0 + SIDE_W, TOP + TABS_H
TERM_H = 270
STATUS_H = 30
ED_H = WIN_H - 44 - TABS_H - TERM_H - STATUS_H
VISIBLES = ED_H // LH - 1


def color_de(tipo):
    for t, c in SINTAXIS:
        if tipo in t:
            return c
    return C["texto"]


def preparar(codigo, lenguaje):
    """Líneas del fragmento como listas de (texto, color)."""
    codigo = codigo.expandtabs(4).rstrip() + "\n"
    lineas, actual = [], []
    for tipo, valor in lex(codigo, get_lexer_by_name(lenguaje)):
        partes = valor.split("\n")
        for i, p in enumerate(partes):
            if i:
                lineas.append(actual)
                actual = []
            if p:
                actual.append((p, color_de(tipo)))
    return lineas[:-1] if lineas and not lineas[-1] else lineas


def linea_texto(runs):
    return "".join(t for t, _ in runs)


class Escena:
    def __init__(self, repo, archivo, arbol, codigo, lenguaje, rotulo, terminal, inicio_linea=1):
        self.repo, self.archivo, self.arbol = repo, archivo, arbol
        self.lineas = preparar(codigo, lenguaje)
        self.lenguaje, self.rotulo, self.terminal = lenguaje, rotulo, terminal
        self.inicio_linea = inicio_linea
        self.textos = [linea_texto(r) for r in self.lineas]

    def guion(self, rnd):
        """Momentos (en s) en que se escribe cada carácter: lista de (t, línea, col)."""
        t, pasos = 0.6, []
        for i, txt in enumerate(self.textos):
            sangria = len(txt) - len(txt.lstrip(" "))
            pasos.append((t, i, sangria))          # la sangría aparece de una (auto-indent)
            for col in range(sangria + 1, len(txt) + 1):
                t += rnd.uniform(0.008, 0.03)
                if txt[col - 1] in "(,:=":
                    t += rnd.uniform(0.0, 0.05)
                pasos.append((t, i, col))
            t += rnd.uniform(0.05, 0.2) if txt.strip() else 0.06
        return pasos, t + 0.6


# --- Dibujo -------------------------------------------------------------------

def redondeado(d, caja, r, color):
    d.rounded_rectangle(caja, r, fill=color)


def dibujar_ventana(img, d, esc, linea_cur, col_cur, top, cursor_on, term_lineas, term_cursor):
    redondeado(d, (X0, Y0, X0 + WIN_W, Y0 + WIN_H), 16, C["ventana"])
    # Barra de título
    d.rounded_rectangle((X0, Y0, X0 + WIN_W, Y0 + 44), 16, fill=C["barra"])
    d.rectangle((X0, Y0 + 30, X0 + WIN_W, Y0 + 44), fill=C["barra"])
    for i, c in enumerate([(255, 95, 87), (255, 189, 46), (40, 200, 64)]):
        d.ellipse((X0 + 20 + i * 26, Y0 + 15, X0 + 34 + i * 26, Y0 + 29), fill=c)
    titulo = f"{esc.repo} — {esc.archivo}"
    d.text((X0 + WIN_W / 2, Y0 + 22), titulo, font=F_UI_S, fill=C["tenue"], anchor="mm")

    # Barra lateral con el árbol del repo
    d.rectangle((X0, TOP, X0 + SIDE_W, Y0 + WIN_H - STATUS_H), fill=C["lateral"])
    d.text((X0 + 22, TOP + 18), esc.repo.upper(), font=F_UI, fill=C["ambar_cl"])
    y = TOP + 58
    for entrada in esc.arbol:
        nivel = (len(entrada) - len(entrada.lstrip(" "))) // 2
        nombre = entrada.strip()
        activo = esc.archivo.endswith(nombre) and not nombre.endswith("/")
        if activo:
            d.rectangle((X0, y - 4, X0 + SIDE_W, y + 26), fill=C["linea_act"])
            d.rectangle((X0, y - 4, X0 + 3, y + 26), fill=C["ambar"])
        xi = X0 + 22 + nivel * 18
        if nombre.endswith("/"):
            d.polygon([(xi, y + 7), (xi + 9, y + 12), (xi, y + 17)], fill=C["tenue"])
        d.text((xi + 18, y), nombre.rstrip("/"), font=F_UI_S,
               fill=C["crema"] if activo else C["tenue"])
        y += 31

    # Pestaña
    d.rectangle((ED_X, TOP, X0 + WIN_W, ED_Y), fill=C["barra"])
    nombre = esc.archivo.split("/")[-1]
    ancho = F_UI_S.getlength(nombre) + 56
    d.rectangle((ED_X, TOP, ED_X + ancho, ED_Y), fill=C["ventana"])
    d.rectangle((ED_X, TOP, ED_X + ancho, TOP + 2), fill=C["ambar"])
    d.text((ED_X + 20, TOP + 21), nombre, font=F_UI_S, fill=C["crema"], anchor="lm")
    d.ellipse((ED_X + ancho - 22, TOP + 17, ED_X + ancho - 14, TOP + 25), fill=C["ambar_cl"])

    # Editor
    gutter = 78
    yb = ED_Y + 14
    for k in range(VISIBLES + 1):
        i = top + k
        if i > linea_cur:
            break
        yy = yb + k * LH
        if i == linea_cur:
            d.rectangle((ED_X, yy - 4, X0 + WIN_W, yy + LH - 6), fill=C["linea_act"])
        num = str(esc.inicio_linea + i)
        d.text((ED_X + gutter - 22, yy), num, font=F_MONO_S,
               fill=C["num_act"] if i == linea_cur else C["numeros"], anchor="ra")
        limite = col_cur if i == linea_cur else 10 ** 6
        x, col = ED_X + gutter, 0
        for texto, color in esc.lineas[i]:
            if col >= limite:
                break
            trozo = texto[: max(0, limite - col)]
            d.text((x, yy), trozo, font=F_MONO, fill=color)
            x += CW * len(trozo)
            col += len(texto)
        if i == linea_cur and cursor_on:
            cx = ED_X + gutter + CW * col_cur
            d.rectangle((cx, yy - 1, cx + 2, yy + LH - 9), fill=C["ambar_cl"])

    # Rótulo de la escena (arriba a la derecha del editor)
    if esc.rotulo:
        tw = F_UI.getlength(esc.rotulo)
        caja = (X0 + WIN_W - tw - 70, ED_Y + 16, X0 + WIN_W - 24, ED_Y + 58)
        d.rounded_rectangle(caja, 21, fill=(46, 36, 22), outline=C["ambar"], width=2)
        d.text(((caja[0] + caja[2]) / 2, (caja[1] + caja[3]) / 2), esc.rotulo, font=F_UI,
               fill=C["ambar_cl"], anchor="mm")

    # Terminal
    ty = Y0 + WIN_H - STATUS_H - TERM_H
    d.rectangle((ED_X, ty, X0 + WIN_W, ty + TERM_H), fill=C["terminal"])
    d.line((ED_X, ty, X0 + WIN_W, ty), fill=C["barra"], width=2)
    d.text((ED_X + 24, ty + 14), "TERMINAL", font=F_UI_S, fill=C["tenue"])
    d.rectangle((ED_X + 24, ty + 40, ED_X + 110, ty + 42), fill=C["ambar"])
    visibles = term_lineas[-6:]
    for k, (texto, color) in enumerate(visibles):
        d.text((ED_X + 24, ty + 58 + k * 32), texto, font=F_MONO_S, fill=color)
    if term_cursor is not None:
        k = len(visibles) - 1
        cx = ED_X + 24 + F_MONO_S.getlength(visibles[-1][0])
        d.rectangle((cx + 2, ty + 58 + k * 32, cx + 13, ty + 58 + k * 32 + 24), fill=C["texto"])

    # Barra de estado
    sy = Y0 + WIN_H - STATUS_H
    d.rounded_rectangle((X0, sy, X0 + WIN_W, Y0 + WIN_H), 16, fill=C["ambar"])
    d.rectangle((X0, sy, X0 + WIN_W, sy + 14), fill=C["ambar"])
    tinta = (46, 36, 55)
    d.text((X0 + 22, sy + 15), f"main   ·   {esc.repo}", font=F_UI_S, fill=tinta, anchor="lm")
    lang = {"python": "Python", "tsx": "TypeScript React", "typescript": "TypeScript", "cpp": "C++ · ESP32"}[esc.lenguaje]
    estado = f"Ln {esc.inicio_linea + linea_cur}, Col {col_cur + 1}    UTF-8    {lang}"
    d.text((X0 + WIN_W - 22, sy + 15), estado, font=F_UI_S, fill=tinta, anchor="rm")


def fundido(img, a):
    if a >= 1:
        return img
    return Image.blend(Image.new("RGB", img.size, C["fondo"]), img, max(0.0, a))


def tarjeta(titulo, sub, extra, icono, t, dur):
    img = Image.new("RGB", (W, H), C["fondo"])
    d = ImageDraw.Draw(img)
    # Brillo ámbar suave detrás
    for r in range(520, 0, -20):
        a = int(18 * (1 - r / 520))
        d.ellipse((W / 2 - r * 1.6, H / 2 - r, W / 2 + r * 1.6, H / 2 + r), fill=(14 + a, 12 + a // 2, 18))
    yb = H / 2 - 40
    if icono is not None:
        img.paste(icono, (int(W / 2 - icono.width / 2), int(yb - 330)), icono)
    d.text((W / 2, yb), titulo, font=F_TIT, fill=C["crema"], anchor="mm")
    d.rectangle((W / 2 - 60, yb + 80, W / 2 + 60, yb + 84), fill=C["ambar"])
    d.text((W / 2, yb + 135), sub, font=F_SUB, fill=C["ambar_cl"], anchor="mm")
    if extra:
        d.text((W / 2, yb + 200), extra, font=F_UI, fill=C["tenue"], anchor="mm")
    a = min(1.0, t / 0.6, (dur - t) / 0.6)
    return fundido(img, a)


# --- Montaje -----------------------------------------------------------------

def _ffmpeg(salida):
    return subprocess.Popen([FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
                             "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                             "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "16",
                             "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(salida)],
                            stdin=subprocess.PIPE)


def generar(escenas, carpeta, rotulos=False):
    """Un clip MP4 por escena (sin portada ni fundidos) y 3 capturas PNG por escena."""
    rnd = random.Random(7)
    carpeta.mkdir(parents=True, exist_ok=True)
    for num, esc in enumerate(escenas, start=1):
        if not rotulos:
            esc.rotulo = ""
        base = f"{num:02d}_{esc.repo}_{Path(esc.archivo).stem}"
        pasos, t_codigo = esc.guion(rnd)
        eventos, t = [], t_codigo
        for cmd, salidas in esc.terminal:
            t += 0.3
            for k in range(1, len(cmd) + 1):
                eventos.append((t, "cmd", cmd[:k]))
                t += rnd.uniform(0.03, 0.06)
            t += 0.35
            for texto, color, espera in salidas:
                t += espera
                eventos.append((t, "out", (texto, C.get(color, C["texto"]))))
        dur = t + 2.5
        capturas = {int(t_codigo * 0.5 * FPS): "a_escribiendo", int((t_codigo + 0.3) * FPS): "b_codigo",
                    int((dur - 0.5) * FPS): "c_final"}
        ff = _ffmpeg(carpeta / f"{base}.mp4")
        top_suave, ip, ie, lin, col = 0.0, 0, 0, 0, 0
        term = [("$ ", C["ambar_cl"])]
        escribiendo_term = False
        for f in range(int(dur * FPS)):
            ts = f / FPS
            while ip < len(pasos) and pasos[ip][0] <= ts:
                _, lin, col = pasos[ip]
                ip += 1
            while ie < len(eventos) and eventos[ie][0] <= ts:
                _, tipo, val = eventos[ie]
                if tipo == "cmd":
                    term[-1] = ("$ " + val, C["ambar_cl"])
                    escribiendo_term = True
                else:
                    escribiendo_term = False
                    term.append(val)
                ie += 1
            fin_salida = bool(eventos) and ie >= len(eventos)
            objetivo = max(0, lin - (VISIBLES - 3))
            top_suave += (objetivo - top_suave) * 0.25
            escribiendo = ip < len(pasos) and ts > 0.6
            parpadeo = int(ts * 2) % 2 == 0
            img = Image.new("RGB", (W, H), C["fondo"])
            d = ImageDraw.Draw(img)
            term_vista = term + ([("$ ", C["ambar_cl"])] if fin_salida else [])
            dibujar_ventana(img, d, esc, lin, col, int(round(top_suave)), escribiendo or parpadeo,
                            term_vista, True if (escribiendo_term or fin_salida or not eventos) and parpadeo else None)
            ff.stdin.write(img.tobytes())
            if f in capturas:
                img.save(carpeta / f"{base}_{capturas[f]}.png")
        ff.stdin.close()
        ff.wait()
        print(f"  {base}.mp4 ({dur:.1f} s) + 3 capturas", flush=True)


def fragmento(ruta, desde, hasta):
    lineas = Path(ruta).read_text(encoding="utf-8").splitlines()
    return "\n".join(lineas[desde - 1:hasta])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--salida", required=True, help="carpeta de los clips")
    p.add_argument("--rotulos", action="store_true", help="dibujar el rótulo de cada escena")
    p.add_argument("--firmware", required=True, help="src/main.cpp de ivy-firmware")
    p.add_argument("--app", required=True, help="carpeta del repo ivy-app")
    a = p.parse_args()
    app = Path(a.app)

    escenas = [
        Escena("ivy-firmware", "src/main.cpp",
               ["lib/", "  nmea/", "  panic/", "lora/", "src/", "  main.cpp", "test/", "platformio.ini"],
               fragmento(a.firmware, 619, 646), "cpp",
               "Firmware · el llavero se anuncia por BLE", [], inicio_linea=619),
        Escena("ivy-app", "src/app/vincular.tsx",
               ["src/", "  app/", "    (tabs)/", "    _layout.tsx", "    alerta.tsx", "    vincular.tsx",
                "  ble/", "  components/", "  protocol/", "  theme/", "app.json"],
               fragmento(app / "src/app/vincular.tsx", 17, 40), "tsx",
               "App · llaveros cercanos ordenados por RSSI",
               [("git log --oneline -4", [
                   ("defdb10 La app pasa a su propio repositorio, IVY-Alert/ivy-app", "texto", 0.08),
                   ("41a4c68 El APK de Android tambien para moviles de 32 bits", "texto", 0.08),
                   ("675c760 Compilacion automatica del APK de Android en GitHub Actions", "texto", 0.08),
                   ("5a78477 Logo de Ivy (la hoja) en la app y en los iconos", "texto", 0.08)])],
               inicio_linea=17),
        Escena("ivy-app", "src/ble/KeychainLink.ts",
               ["src/", "  app/", "  ble/", "    KeychainLink.ts", "  components/", "  protocol/",
                "    alertMachine.ts", "    nus.ts", "  state/", "  theme/", "app.json"],
               fragmento(app / "src/ble/KeychainLink.ts", 185, 206), "typescript",
               "App · escaneo BLE con RSSI de cada llavero", [], inicio_linea=185),
        Escena("ivy-app", "src/protocol/alertMachine.ts",
               ["src/", "  app/", "  ble/", "    KeychainLink.ts", "  components/", "  protocol/",
                "    alertMachine.ts", "    nus.ts", "  state/", "  theme/", "app.json"],
               fragmento(app / "src/protocol/alertMachine.ts", 1, 31), "typescript",
               "App · máquina de estados de la alerta", [], inicio_linea=1),
        Escena("ivy-rssi", "ivy_rssi/registrador.py",
               ["ivy_rssi/", "  analisis.py", "  buscador.py", "  fisica.py", "  graficas.py",
                "  registrador.py", "  simulador.py", "tests/", "PROTOCOLO.md", "FISICA.md"],
               fragmento(RAIZ / "ivy_rssi/registrador.py", 51, 71), "python",
               "Registrador · cada anuncio es una muestra",
               [("python prueba_real.py 30", [
                   ("     5 s | llavero: 69 muestras", "texto", 0.5),
                   ("    15 s | llavero: 215 muestras", "texto", 0.6),
                   ("    30 s | llavero: 371 muestras", "texto", 0.6),
                   ("LLAVERO: 371 muestras en 30.4 s -> 12.19 muestras/s", "verde", 0.3),
                   ("  mediana -43 dBm, min -57, max -38", "ambar_cl", 0.2)])],
               inicio_linea=51),
        Escena("ivy-rssi", "ivy_rssi/fisica.py",
               ["ivy_rssi/", "  analisis.py", "  buscador.py", "  fisica.py", "  graficas.py",
                "  registrador.py", "  simulador.py", "tests/", "PROTOCOLO.md", "FISICA.md"],
               fragmento(RAIZ / "ivy_rssi/fisica.py", 61, 101), "python",
               "Física · RSSI(d) = RSSI(d0) − 10·n·log(d/d0)",
               [("python -m pytest -q", [
                   ("................................                    [100%]", "verde", 0.9),
                   ("32 passed in 87.27s", "verde", 0.2)])],
               inicio_linea=61),
    ]
    generar(escenas, Path(a.salida), a.rotulos)


if __name__ == "__main__":
    main()
