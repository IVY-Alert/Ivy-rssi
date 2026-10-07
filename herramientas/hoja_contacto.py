"""Hoja de contacto: una imagen con miniaturas de los videos y fotos de las sesiones.

    python herramientas/hoja_contacto.py

Escribe evidencias/hoja_contacto.jpg. Los fotogramas de la webcam se toman en
momentos revisados (sin primeros planos ni tramos marcados como «no usar»).
"""

import os
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parent.parent
EV = RAIZ / "evidencias"
FFMPEG = os.environ.get("IVY_FFMPEG", "ffmpeg")
TW, TH, COLS, PAD, LAB = 384, 216, 5, 14, 44
FUENTE = RAIZ / "ivy_rssi/fuentes/InstrumentSans-600.ttf"

# (archivo relativo a evidencias/, segundo del fotograma o None para fotos, rótulo)
ITEMS = [
    ("2026-10-05_sesion1/celular/1319_reconocimiento_lugar.MOV", 1, "Reconocimiento del lugar"),
    ("2026-10-05_sesion1/celular/IMG_3532_E1_1m_montaje_general.jpg", None, "E1 · montaje general"),
    ("2026-10-05_sesion1/celular/IMG_3529_E1_025m_detalle_llavero.mov", 3, "E1 · llavero a 0.25 m"),
    ("2026-10-05_sesion1/celular/IMG_3534_E1_mover_a_2m.mov", 6, "E1 · moviendo a 2 m"),
    ("2026-10-05_sesion1/celular/IMG_3533_E1_1m_silla_girada.jpg", None, "E1 · silla girada (1 m)"),
    ("2026-10-05_sesion1/camara/E1_r1_distancia.mp4", 120, "E1 r1 · webcam (ESP32)"),
    ("2026-10-05_sesion1/camara/E1_r2_distancia.mp4", 270, "E1 r2 · webcam"),
    ("2026-10-05_sesion1/camara/E1_r3_distancia.mp4", 880, "E1 r3 · webcam"),
    ("2026-10-05_sesion1/pantalla/E1_r1_distancia.mp4", 1300, "E1 · pantalla (RSSI en vivo)"),
    ("2026-10-06_sesion2/celular/IMG_3544_E3_como_se_gira.mov", 8, "E3 · cómo se gira"),
    ("2026-10-06_sesion2/camara/E3_patron.mp4", 250, "E3 · webcam"),
    ("2026-10-06_sesion2/celular/IMG_3547_E2_mano_bolsillo_persona_7m50s.MOV", 100, "E2 · en la mano"),
    ("2026-10-06_sesion2/celular/IMG_3547_E2_mano_bolsillo_persona_7m50s.MOV", 395, "E2 · persona en medio"),
    ("2026-10-06_sesion2/camara/E2_cuerpo.mp4", 1110, "E2 · morral"),
    ("hardware_soldadura/WhatsApp Image 2026-10-06 at 8.38.58 AM.jpeg", None, "Hardware · sistema de batería"),
    ("hardware_soldadura/WhatsApp Video 2026-10-06 at 9.03.29 AM.mp4", 60, "Hardware · soldadura (4:50)"),
    ("hardware_soldadura/WhatsApp Video 2026-10-06 at 8.59.34 AM.mp4", 60, "Hardware · soldadura (2:49)"),
    ("hardware_soldadura/WhatsApp Image 2026-10-06 at 9.06.54 AM.jpeg", None, "Hardware · medición de la placa"),
    ("2026-10-05_sesion1/figuras/E1_rssi_vs_distancia_log_video.png", None, "Figura · E1 RSSI vs. distancia"),
    ("2026-10-06_sesion2/figuras/E3_patron_radiacion_video.png", None, "Figura · E3 patrón"),
]


def miniatura(ruta, seg, tmp):
    if seg is None and ruta.suffix.lower() in (".jpg", ".jpeg", ".png"):
        img = Image.open(ruta).convert("RGB")
    else:
        args = [FFMPEG, "-v", "error", "-y"] + (["-ss", str(seg)] if seg is not None else []) + [
            "-i", str(ruta), "-frames:v", "1", str(tmp)]
        subprocess.run(args, check=True)
        img = Image.open(tmp).convert("RGB")
    img.thumbnail((TW, TH))
    lienzo = Image.new("RGB", (TW, TH), (20, 18, 24))
    lienzo.paste(img, ((TW - img.width) // 2, (TH - img.height) // 2))
    return lienzo


def main():
    fuente = ImageFont.truetype(str(FUENTE), 19)
    filas = -(-len(ITEMS) // COLS)
    W = COLS * TW + (COLS + 1) * PAD
    H = filas * (TH + LAB) + (filas + 1) * PAD + 70
    hoja = Image.new("RGB", (W, H), (14, 12, 18))
    d = ImageDraw.Draw(hoja)
    d.text((PAD, 22), "Ivy · evidencias del proyecto (5 y 6 de octubre de 2026)", font=ImageFont.truetype(str(FUENTE), 30),
           fill=(255, 194, 71))
    tmp = EV / "_tmp_frame.jpg"
    for k, (rel, seg, rotulo) in enumerate(ITEMS):
        x = PAD + (k % COLS) * (TW + PAD)
        y = 70 + PAD + (k // COLS) * (TH + LAB + PAD)
        try:
            hoja.paste(miniatura(EV / rel, seg, tmp), (x, y))
        except Exception as e:  # que un archivo faltante no tumbe la hoja
            d.rectangle((x, y, x + TW, y + TH), outline=(120, 40, 40))
            rotulo += f" (falta: {type(e).__name__})"
        d.text((x + 4, y + TH + 8), rotulo, font=fuente, fill=(226, 220, 232))
    tmp.unlink(missing_ok=True)
    salida = EV / "hoja_contacto.jpg"
    hoja.save(salida, quality=88)
    print(salida)


if __name__ == "__main__":
    main()
