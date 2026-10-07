# Herramientas de evidencias

Apoyo para las sesiones de medición grabadas. No cambian el código de medición:
`evidencias.py` mide con `ivy_rssi.registrador.medir_punto` y guarda con
`ivy_rssi.sesion.guardar_punto`, así que los CSV/JSON quedan en `datos/` con el formato
de siempre.

- `evidencias.py`: crea `evidencias/AAAA-MM-DD_sesionN/` (datos, pantalla, camara,
  celular, figuras, bitacora.md), mide puntos, escribe la bitácora sola y graba pantalla
  (gdigrab) y webcam + micrófono (dshow) con ffmpeg en segundo plano.
- `punto.ps1`: mide un punto en una ventana visible (sale en la grabación de pantalla).

Los videos (`evidencias/**/*.mp4`, `*.mov`, fotos del celular) no van a git: van a Google
Drive. Ver `.gitignore`.
