# Índice de evidencias para el video final

Proyecto Ivy · Física, Calor y Ondas · Universidad del Norte. Entrega: 14 de octubre de 2026.

Todo lo de aquí está en esta carpeta del portátil (`ivy-rssi/evidencias/`). Los videos y
fotos pesados **no van a git** (1.5 GB): hay que subirlos a Google Drive (el **tuyo**).
Vista rápida de todo: [`hoja_contacto.jpg`](hoja_contacto.jpg).

Leyenda: ✅ buena toma · ⚠️ usar con cuidado · ⛔ tramo que no se usa.

## Resumen para el guion (5 líneas)

1. Medimos la señal Bluetooth (RSSI, 2.4 GHz) del llavero Ivy en un apartamento, con tres repeticiones de 0.25 a 8 m, giros de 30° y el cuerpo como obstáculo.
2. La señal cae con la distancia siguiendo RSSI = RSSI(1 m) − 10·n·log₁₀(d): en el pasillo **n = 1.28 ± 0.20**, menor que el 2 del espacio libre, porque las paredes guían la onda.
3. Moverse solo 7 cm (media longitud de onda) cambia el RSSI hasta 8 dB: es el multitrayecto, la interferencia entre la onda directa y los rebotes.
4. La antena no irradia igual hacia todos lados (**14 dB** entre la mejor y la peor orientación); el cuerpo pegado al llavero atenúa más (**bolsillo −8 dB**) que una persona en medio (−3 dB) o un morral (−1 dB), y la batería debajo de la antena le quita **5 dB**.
5. Para el llavero: funciona de sobra dentro de una casa, la antena debe ir siempre por fuera de la batería, conviene llevarlo en la mano o en el morral antes que en el bolsillo, y la app avisa sola (SMS y llamada) sin sacar el teléfono.

## Sesión 1 · 5 oct 2026 · E1 (RSSI vs. distancia)

| Archivo | Hora | Duración | Qué muestra | Uso |
|---|---|---|---|---|
| `2026-10-05_sesion1/celular/1319_reconocimiento_lugar.MOV` | 13:19 | 23 s | Recorrido del apartamento para elegir el lugar | ⚠️ sale una persona de la casa en el sofá: recortar |
| `…/celular/IMG_3529_E1_025m_detalle_llavero.mov` | 16:07 | 6 s | Detalle del llavero (ESP32 + power bank) junto al portátil | ✅ (vertical) |
| `…/celular/IMG_3530_E1_05m.mov` | 16:11 | 5 s | Montaje a 0.5 m | ✅ (vertical) |
| `…/celular/IMG_3531_E1_1m_montaje_video.MOV` | 16:12 | 6 s | Montaje a 1 m | ✅ |
| `…/celular/IMG_3532_E1_1m_montaje_general` (.HEIC/.jpg) | 16:14 | foto | **Plano general**: portátil, silla y llavero | ✅ la mejor foto del montaje |
| `…/celular/IMG_3533_E1_1m_silla_girada` (.HEIC/.jpg) | 16:20 | foto | Silla girada para tapar el rebote de la pared y la matera | ✅ |
| `…/celular/IMG_3534_E1_mover_a_2m.mov` | 16:22 | 12 s | Mover el llavero de 1.5 a 2 m con la cinta en el piso | ✅ (vertical) |
| `…/celular/foto_E1_r2_025m_montaje.jpg` | 16:44 | foto | Montaje de la repetición 2 a 0.25 m | ✅ |
| `…/camara/E1_r1_distancia.mp4` | 16:05–16:40 | 35 min | Webcam, repetición 1 | ✅ 01:40–02:30 (ESP32 de cerca); ⛔ 17:35–18:35 (otra persona) |
| `…/camara/E1_r2_distancia.mp4` | 16:45–17:02 | 18 min | Webcam, repetición 2 | ✅ 04:10–05:10; ⛔ **16:15–16:50** |
| `…/camara/E1_r3_distancia.mp4` | 17:07–17:46 | 39 min | Webcam, repetición 3 | ✅ 14:20–15:00, 30:00–30:20; ⛔ 20:00–20:10 y 28:35–29:15 (otra persona) |
| `…/pantalla/E1_r1…r3_distancia.mp4` | igual que la webcam | 18–39 min | Pantalla del portátil con el RSSI en vivo | ✅ |
| `…/figuras/E1_*_video.png` | — | — | RSSI vs. distancia (log y lineal), residuos, el RSSI como regla | ✅ |

Detalle de tramos «evitar» (primeros planos poco favorecedores) en
[`2026-10-05_sesion1/revision_videos.md`](2026-10-05_sesion1/revision_videos.md).

## Sesión 2 · 6 oct 2026 · E3 (patrón) y E2 (cuerpo)

| Archivo | Hora | Duración | Qué muestra | Uso |
|---|---|---|---|---|
| `2026-10-06_sesion2/rosa_angulos_E3.pdf` / `.png` | — | — | Rosa de ángulos para girar el llavero | ✅ gráfico |
| `…/celular/IMG_3544_E3_como_se_gira.mov` | 18:14 | 16 s | Cómo se gira el llavero de 30° en 30° | ✅ |
| `…/camara/E3_patron.mp4` | 18:09–18:32 | 22 min | Webcam durante E3 (piernas y llavero) | ✅ |
| `…/celular/IMG_3547_E2_mano_bolsillo_persona_7m50s.MOV` | 18:43 | 7 min 50 s | Plano bajo desde la mesa | ✅ mano 1:29–1:59 · bolsillo 2:44–3:15 · persona en medio 6:22–6:53 |
| `…/camara/E2_cuerpo.mp4` | 18:35–18:54 | 19 min | Webcam durante E2 | ✅ persona en medio 12:40–14:30 · morral 18:10–18:50 |
| `…/pantalla/E2_cuerpo.mp4`, `E3_patron.mp4` | igual que la webcam | 19–22 min | RSSI en vivo | ✅ |
| `…/figuras/E2_*_video.png`, `E3_*_video.png` | — | — | Atenuación del cuerpo, desvanecimiento, patrón polar | ✅ |


## Sesión 2 (cont.) · 6 oct 2026 · E4 (antena vs. batería)

LiPo Turnigy 750 mAh desconectada; el ESP32 con el power bank. 3 repeticiones (marca de 2 m, +7 cm, −7 cm).

| Archivo | Hora | Qué muestra | Uso |
|---|---|---|---|
| `2026-10-06_sesion2/celular/foto_E4_sistema_bateria_piezas.jpg` | 21:45 | Sistema de batería del ingeniero por piezas: LiPo, TP4056, MT3608, interruptor | ✅ |
| `…/celular/foto_E4_r1_antena_encima*.jpg`, `foto_E4_r2_antena_encima.jpg` | 21:49–22:06 | Batería debajo de la antena (de lado) | ✅ |
| `…/celular/foto_E4_r1/r2/r3_antena_sobresale.jpg` | 21:56–22:11 | Antena por fuera, batería sobre la mitad del USB (desde arriba) | ✅ la que justifica la carcasa |
| `…/celular/foto_E4_r1_sin_bateria.jpg` | 22:00 | Sin batería cerca | ✅ |
| `…/camara/E4_r1/r2/r3_antena_bateria.mp4`, `…/pantalla/…` | 21:45–22:13 | Webcam y pantalla durante E4 | ✅ (sin revisar cuadro a cuadro: solo manos y banquito) |
| `…/figuras/E4_antena_vs_bateria_video.png` | — | Barras: sobresale −63, sin batería −66, encima −68 dBm | ✅ |

## Hardware · soldadura del llavero (del ingeniero, por WhatsApp)

| Archivo | Hora del envío | Qué muestra |
|---|---|---|
| `hardware_soldadura/WhatsApp Image 2026-10-05 at 2.48.27 PM.jpeg` | 5 oct 14:48 | Componentes sueltos: elevador de voltaje, cargador TP4056 (USB-C) y LiPo 750 mAh |
| `…/WhatsApp Image 2026-10-06 at 8.25.54 AM.jpeg` | 6 oct 08:25 | Conector JST en la mano |
| `…/WhatsApp Image 2026-10-06 at 8.38.58 AM.jpeg` | 6 oct 08:38 | **«Ya quedó el sistema de la batería»**: cargador TP4056 + LiPo 750 mAh |
| `…/WhatsApp Video 2026-10-06 at 8.59.34 AM.mp4` | 6 oct 08:59 | Video de la soldadura (2:49) |
| `…/WhatsApp Image 2026-10-06 at 8.59.35 AM.jpeg` | 6 oct 08:59 | Placa perforada con el interruptor y los cables |
| `…/WhatsApp Video 2026-10-06 at 9.03.29 AM.mp4` | 6 oct 09:03 | «De cómo se hizo el resto» (4:50): módulo de carga y conectores |
| `…/WhatsApp Image 2026-10-06 at 9.06.35 / 9.06.54 AM.jpeg` | 6 oct 09:06 | Medición de la placa con calibrador |
| `…/WhatsApp Image 2026-10-06 at 9.13.18 AM.jpeg` | 6 oct 09:13 | Llavero en bolsa lista para entregar |

El comprobante de pago al ingeniero (también estaba en el chat) se sacó de aquí a
`Desktop/ivy-privado/`: tiene datos bancarios y no va en el video ni en git.


## Prototipo · fotos y videos del celular (sept–oct 2026)

`prototipo_celular/`, tomados de la galería del iPhone (solo lo del proyecto).

| Archivo | Qué muestra | Uso |
|---|---|---|
| `2026-09-22_video_primer_prototipo_boton.MP4` | Primer prototipo: ESP32 en protoboard, pulsando el botón | ✅ muy bueno para la historia del proyecto |
| `2026-09_componentes_bateria.JPG` | LiPo, cargador TP4056 y elevador MT3608 recién comprados | ✅ |
| `2026-09_impresora_carcasa_gcode.JPG` | Pantalla de la impresora 3D: «carcasa.gcode», 1 h 30 min, 59 g | ✅ |
| `2026-09_impresora_filamento_rojo.JPG`, `2026-09_impresora_3d.JPG` | Impresora 3D imprimiendo la carcasa | ✅ |
| `2026-09-30_video_carcasa_roja.MP4` | La carcasa roja impresa | ✅ |
| `2026-10_filamento_blanco.JPG` | Rollo de filamento blanco | ✅ |
| `2026-10-02_video_impresora_piezas_1/2.MOV` | Impresión de piezas blancas | ✅ |
| `2026-10-05_video_multimetro_lipo.MP4` | Multímetro midiendo el voltaje de la LiPo | ✅ |

## Código escribiéndose (para la parte de desarrollo)

`2026-10-05_sesion1/codigo/`: 6 clips de 19–38 s (1080p) con 3 capturas cada uno.

| Clip | Qué se escribe |
|---|---|
| `01_ivy-firmware_main.mp4` | El ESP32 inicia el BLE y se anuncia como `GEOEXPO-ALERT` a +9 dBm |
| `02_ivy-app_vincular.mp4` | La app lista los llaveros cercanos por RSSI (+ `git log`) |
| `03_ivy-app_KeychainLink.mp4` | Escaneo BLE de la app |
| `04_ivy-app_alertMachine.mp4` | Máquina de estados de la alerta |
| `05_ivy-rssi_registrador.mp4` | Cada anuncio es una muestra (+ medición real: 371 muestras, −43 dBm) |
| `06_ivy-rssi_fisica.mp4` | Ajuste log-distancia con n e IC 95 % (+ 32 pruebas en verde) |

## Pendiente

- **E5** (alcance máximo): afuera, con el internet del celular compartido al portátil.
- Prueba real de la app (SMS y llamada automáticos) en un teléfono **con SIM**.
