"""Reconstruye E5: asigna a cada muestra la distancia según la posición vista en la webcam.

Paso = 0.41 m (5 pasos medidos = 2.05 m). El video empieza a las 15:30:16 (hora local).
Tramos (segundos del video -> pasos), sacados de la altura de la cabeza en la imagen;
se descartan 3 s después de cada cambio (caminando) y la vuelta al portátil (110-139 s).
"""
import csv, sys
from datetime import datetime

T0 = datetime(2026, 10, 9, 15, 30, 16).timestamp()
TRAMOS = [(50, 84, 10), (88, 105, 15), (140, 171, 20), (175, 202, 25), (206, 229, 30),
          (233, 261, 35), (265, 294, 40), (298, 329, 45), (333, 349, 50), (353, 374, 55),
          (378, 419, 60), (423, 495, 65)]
PASO = 0.41

crudo, r1, salida = sys.argv[1:4]
filas = []
with open(r1, encoding="utf-8") as f:
    for r in csv.DictReader(f):
        filas.append([r["timestamp"], "E5", "5 pasos (2.05 m)", "2.05", r["rssi_dbm"]])
cuenta = {}
with open(crudo, encoding="utf-8") as f:
    for r in csv.DictReader(f):
        t = float(r["timestamp"]) - T0
        for a, b, p in TRAMOS:
            if a <= t <= b:
                d = round(p * PASO, 2)
                filas.append([r["timestamp"], "E5", f"{p} pasos ({d} m)", str(d), r["rssi_dbm"]])
                cuenta[p] = cuenta.get(p, 0) + 1
with open(salida, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["timestamp", "experimento", "condicion", "valor_condicion", "rssi_dbm"])
    w.writerows(filas)
for a, b, p in TRAMOS:
    print(f"{p:3d} pasos  {p*PASO:5.2f} m  {cuenta.get(p,0):3d} muestras en {b-a} s")
