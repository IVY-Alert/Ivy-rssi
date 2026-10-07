# Bitácora — 2026-10-05_sesion1

Inicio: 2026-10-05 16:04:55

## Montaje y condiciones

| Dato | Valor |
|---|---|
| portatil | Lenovo ThinkPad L14 Gen 3 (Bluetooth RZ616), antenas en el borde superior de la pantalla |
| fuente_alimentacion | power bank |
| altura_portatil_m | 0.695 |
| altura_llavero_m | 0.695 |
| lugar | apartamento: sala + pasillo interior recto (~1 m de ancho, paredes lisas pintadas, puertas de madera, piso de baldosa) |
| longitud_disponible_m | 8 |
| referencia_distancias | borde superior de la pantalla; desfase hasta el borde del asiento a = 17.5 ± 0.5 cm |
| llavero_mac | 3C:8A:1F:A7:31:DA |
| interferencias | Wi-Fi del portatil en 5 GHz (DJ TORRES 5G, canal 52); BLE de varios televisores y una nevera en el edificio; sin microondas encendido |
| notas | E1 de 0.25 a 8 m (no hay 10 m). Se retiraron bancos metalicos de la linea; matera desplazada; perro fuera durante las mediciones. Prueba previa de 30 s pegado al portatil: 371 muestras, 12.2 muestras/s, mediana -43 dBm. |

## Registro

Formato de puntos: `hora · experimento · condición · muestras · mediana · tasa`.
🎥/📸 = toma pedida al celular (emparejar por hora).

- 16:04:55 · 📝 Video de reconocimiento del lugar con el celular a las 13:19 (celular/1319_reconocimiento_lugar.MOV). Prueba real de 30 s en la mesa: 371 muestras, 12.2/s, mediana -43 dBm.
- 16:04:55 · 📝 Encuadre de webcam ajustado en 4 pruebas (camara/encuadre_prueba1-4.jpg). Clips de codigo generados en codigo/.
- 16:04:56 · 📸 FOTO pedida: cinta en el piso con las marcas (toma 3) y plano general del montaje (toma 1)

### 16:05:05 — E1 repetición 1 (`E1_r1_20261005-160505.csv`)

- 16:05:12 · ⏺ inicia grabación `E1_r1_distancia`
- 16:07:45 · 🎥 VIDEO pedido: detalle del llavero en su soporte junto al portatil (toma 2)
- 16:08:18 · E1 · 0.25 m · n=107 · mediana -44 dBm · 3.5 muestras/s
- 16:09:17 · 📝 Recibido video del celular IMG_3529 (detalle del llavero a 0.25 m) -> celular/IMG_3529_E1_025m_detalle_llavero.mov
- 16:10:47 · ↺ último punto de E1 descartado (llavero estaba al lado del portatil, no sobre la linea; se coloca delante de la pantalla); se repite
- 16:11:20 · E1 · 0.25 m · n=119 · mediana -47 dBm · 3.9 muestras/s
- 16:12:23 · 📝 Recibido video del celular IMG_3530 (montaje a 0.5 m) -> celular/IMG_3530_E1_05m.mov
- 16:12:55 · E1 · 0.5 m · n=107 · mediana -54 dBm · 3.5 muestras/s
- 16:14:12 · E1 · 1 m · n=97 · mediana -54 dBm · 3.2 muestras/s
- 16:16:14 · 📝 Foto del montaje a 1 m (celular/foto_E1_1m_montaje_general.jpg). El punto de 1 m dio igual que 0.5 m (-54 dBm): matera y pared a ~20-30 cm detras del llavero; se retira la matera y se repite.
- 16:18:48 · ↺ último punto de E1 descartado (1 m dio igual que 0.5 m; se gira la silla para que el respaldo tape la matera y la pared (la matera no se puede mover)); se repite
- 16:19:21 · E1 · 1 m · n=89 · mediana -60 dBm · 2.9 muestras/s
- 16:21:18 · E1 · 1.5 m · n=69 · mediana -62 dBm · 2.3 muestras/s
- 16:23:21 · 🎥 VIDEO pedido y recibido: mover la silla de 1.5 m a 2 m con la cinta a la vista (toma 3) -> celular/IMG_3534_E1_mover_a_2m.mov
- 16:24:30 · E1 · 2 m · n=81 · mediana -67 dBm · 2.7 muestras/s
- 16:26:49 · E1 · 3 m · n=69 · mediana -66 dBm · 2.3 muestras/s
- 16:28:27 · ↺ último punto de E1 descartado (3 m dio 1 dB por encima de 2 m; se repite para comprobar); se repite
- 16:29:00 · E1 · 3 m · n=69 · mediana -64 dBm · 2.3 muestras/s
- 16:33:29 · E1 · 4 m · n=77 · mediana -67 dBm · 2.5 muestras/s
- 16:35:16 · E1 · 5 m · n=99 · mediana -64 dBm · 3.3 muestras/s
- 16:36:52 · E1 · 6 m · n=115 · mediana -66 dBm · 3.8 muestras/s
- 16:40:00 · E1 · 8 m · n=89 · mediana -69 dBm · 2.9 muestras/s
- 16:40:13 · ⏹ fin grabación `E1_r1_distancia` (pantalla 17.3 MB, camara 99.7 MB)

### 16:44:59 — E1 repetición 2 (`E1_r2_20261005-164459.csv`)

- 16:45:00 · 📝 Repeticion 2: linea corrida ~7 cm a la derecha de cada marca (~lambda/2). Foto: celular/foto_E1_r2_025m_montaje.jpg
- 16:45:06 · ⏺ inicia grabación `E1_r2_distancia`
- 16:45:38 · E1 · 0.25 m · n=115 · mediana -49 dBm · 3.8 muestras/s
- 16:47:36 · E1 · 0.5 m · n=101 · mediana -54 dBm · 3.3 muestras/s
- 16:50:03 · E1 · 1 m · n=97 · mediana -59 dBm · 3.2 muestras/s
- 16:51:09 · E1 · 1.5 m · n=91 · mediana -62 dBm · 3.0 muestras/s
- 16:52:41 · E1 · 2 m · n=95 · mediana -61 dBm · 3.1 muestras/s
- 16:54:50 · E1 · 3 m · n=61 · mediana -70 dBm · 2.0 muestras/s
- 16:57:10 · E1 · 4 m · n=53 · mediana -63 dBm · 1.8 muestras/s · ⚠ RSSI +7 dB respecto a 3 m (debería bajar con la distancia)
- 16:58:48 · E1 · 5 m · n=89 · mediana -67 dBm · 2.9 muestras/s
- 17:00:25 · E1 · 6 m · n=69 · mediana -72 dBm · 2.3 muestras/s
- 17:01:53 · 📝 NO USAR: tramo de ~1 min antes de esta hora en camara/E1_r2_distancia.mp4 (tramo personal). Recortar al editar.
- 17:02:26 · E1 · 8 m · n=111 · mediana -67 dBm · 3.7 muestras/s
- 17:02:38 · ⏹ fin grabación `E1_r2_distancia` (pantalla 8.1 MB, camara 63.5 MB)

### 17:07:01 — E1 repetición 3 (`E1_r3_20261005-170701.csv`)

- 17:07:02 · 📝 Repeticion 3: linea corrida ~7 cm a la IZQUIERDA de cada marca (no habia espacio para 14 cm a la derecha)
- 17:07:08 · ⏺ inicia grabación `E1_r3_distancia`
- 17:07:41 · E1 · 0.25 m · n=111 · mediana -50 dBm · 3.7 muestras/s
- 17:17:13 · E1 · 0.5 m · n=109 · mediana -54 dBm · 3.6 muestras/s
- 17:19:21 · E1 · 1 m · n=95 · mediana -62 dBm · 3.1 muestras/s
- 17:21:00 · E1 · 1.5 m · n=83 · mediana -61 dBm · 2.7 muestras/s
- 17:23:03 · E1 · 2 m · n=91 · mediana -59 dBm · 3.0 muestras/s
- 17:27:56 · E1 · 3 m · n=83 · mediana -65 dBm · 2.7 muestras/s
- 17:38:15 · E1 · 4 m · n=65 · mediana -65 dBm · 2.1 muestras/s
- 17:41:03 · E1 · 5 m · n=81 · mediana -65 dBm · 2.7 muestras/s
- 17:42:59 · E1 · 6 m · n=91 · mediana -71 dBm · 3.0 muestras/s
- 17:46:03 · E1 · 8 m · n=107 · mediana -68 dBm · 3.5 muestras/s
- 17:46:09 · ⏹ fin grabación `E1_r3_distancia` (pantalla 11.5 MB, camara 235.3 MB)
- 18:09:12 · 📝 PAUSA despues de E1 (3 repeticiones completas). n = 1.28 +/- 0.20, R2 = 0.862, sigma = 2.5 dB. Pendientes: E2, E4, E3, E5.
- 18:12:39 · 📝 Revision de videos de webcam E1 hecha (revision_videos.md). Unico punto con interferencia: E1 r3 3 m, el perro estuvo cerca de la linea durante la medicion (-65 dBm, coherente). Repetir si hay tiempo.
