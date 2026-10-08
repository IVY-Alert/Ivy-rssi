# Bitácora — 2026-10-06_sesion2

Inicio: 2026-10-06 18:03:51

## Montaje y condiciones

| Dato | Valor |
|---|---|
| portatil | Lenovo ThinkPad L14 Gen 3 (Bluetooth RZ616), antenas en el borde superior de la pantalla |
| fuente_alimentacion | power bank (pegado al ESP32, gira con el llavero en E3) |
| altura_portatil_m | 0.695 |
| altura_llavero_m | 0.695 |
| lugar | mismo montaje de la sesion 1: sala del apartamento, sillas tapizadas, banquito plastico; marcas de cinta en el piso de la sesion 1 |
| referencia_distancias | borde superior de la pantalla; desfase hasta el borde del asiento a = 17.5 ± 0.5 cm |
| llavero_mac | 3C:8A:1F:A7:31:DA |
| interferencias | Wi-Fi del portatil en 5 GHz; BLE de televisores y nevera del edificio |
| notas | Sesion 2 (dia siguiente). Orden: E3 -> E2 -> E5; E4 al final cuando llegue la bateria LiPo. Perro con una pata lastimada: minima intervencion en la casa. |

## Registro

Formato de puntos: `hora · experimento · condición · muestras · mediana · tasa`.
🎥/📸 = toma pedida al celular (emparejar por hora).


### 18:09:46 — E3 repetición 1 (`E3_r1_20261006-180946.csv`)

- 18:09:47 · 📝 E3 a 2 m sobre la marca de la sesion 1 (sin desplazamiento lateral). Rosa de angulos impresa bajo el llavero; power bank gira con el llavero. Operador controla desde el iPad con Remote Control.
- 18:09:54 · ⏺ inicia grabación `E3_patron`
- 18:14:52 · 🎥 VIDEO recibido: como se gira el llavero en E3 (toma 6) -> celular/IMG_3544_E3_como_se_gira.mov
- 18:15:25 · E3 · 0° · n=67 · mediana -65 dBm · 2.2 muestras/s
- 18:16:53 · E3 · 30° · n=69 · mediana -62 dBm · 2.3 muestras/s
- 18:18:15 · E3 · 60° · n=63 · mediana -67 dBm · 2.1 muestras/s
- 18:19:24 · E3 · 90° · n=65 · mediana -68 dBm · 2.1 muestras/s
- 18:20:46 · E3 · 120° · n=83 · mediana -63 dBm · 2.7 muestras/s
- 18:22:01 · E3 · 150° · n=91 · mediana -62 dBm · 3.0 muestras/s
- 18:23:23 · E3 · 180° · n=95 · mediana -62 dBm · 3.1 muestras/s
- 18:24:54 · E3 · 210° · n=89 · mediana -60 dBm · 2.9 muestras/s
- 18:26:25 · E3 · 240° · n=95 · mediana -58 dBm · 3.1 muestras/s
- 18:27:39 · E3 · 270° · n=87 · mediana -60 dBm · 2.9 muestras/s
- 18:28:53 · E3 · 300° · n=79 · mediana -55 dBm · 2.6 muestras/s
- 18:30:10 · E3 · 330° · n=71 · mediana -54 dBm · 2.3 muestras/s
- 18:31:23 · 📝 Cierre de E3: se repite 0 grados. El operador gira el banquito usando el circulo central del banco como eje (el ESP32 puede no estar en el centro).
- 18:31:57 · E3 · 0° · n=99 · mediana -62 dBm · 3.3 muestras/s
- 18:32:11 · 📝 Cierre 0 grados: -62 dBm (inicio: -65). Repetible dentro de ~3 dB; el patron es real. Como el banquito se gira sobre su centro y el ESP32 puede no estar ahi, la antena se desplaza unos cm al girar: el patron mezcla antena + multitrayecto.
- 18:32:12 · ⏹ fin grabación `E3_patron` (pantalla 5.4 MB, camara 126.8 MB)

### 18:35:33 — E2 repetición 1 (`E2_r1_20261006-183533.csv`)

- 18:35:33 · 📝 E2 a 2 m (marca de la sesion 1, sin desplazamiento). El operador es tambien la persona/obstaculo; controla con el iPad en la mano contraria. Power bank va con el llavero.
- 18:35:39 · ⏺ inicia grabación `E2_cuerpo`
- 18:37:21 · E2 · linea_de_vista · n=99 · mediana -61 dBm · 3.3 muestras/s
- 18:44:44 · 🎥 Celular grabando desde la mesa, ~75 cm del portatil, durante E2 (mano en adelante)
- 18:45:17 · E2 · en_la_mano · n=113 · mediana -65 dBm · 3.7 muestras/s
- 18:46:32 · E2 · bolsillo · n=59 · mediana -69 dBm · 1.9 muestras/s
- 18:48:53 · E2 · persona_en_medio · n=71 · mediana -63 dBm · 2.4 muestras/s
- 18:49:38 · ↺ último punto de E2 descartado (persona en medio dio solo 2 dB; se repite comprobando que el cuerpo tapa el llavero desde la pantalla); se repite
- 18:50:11 · E2 · persona_en_medio · n=55 · mediana -64 dBm · 1.8 muestras/s
- 18:54:37 · E2 · morral · n=83 · mediana -62 dBm · 2.7 muestras/s
- 18:54:51 · 📝 Video del celular de E2 (mano/bolsillo/persona) supera 30 MB: se copiara al final por cable a celular/.
- 18:54:52 · ⏹ fin grabación `E2_cuerpo` (pantalla 3.5 MB, camara 116.5 MB)
- 18:58:12 · 📝 FIN de la sesion 2 (E3 y E2 completos). Pendientes: E5 (afuera) y E4 (al llegar la bateria LiPo), manana. Copiar los videos del celular por cable.
- 19:04:28 · 📝 Copiados del iPhone por cable: IMG_3547 (E2, 7 min 50 s, 675 MB; en_la_mano ~1:29-1:59, bolsillo ~2:44-3:15, persona_en_medio valida ~6:22-6:53 del video). Plano bajo desde la mesa.
- 21:45:26 · 📝 E4 antena vs bateria. Llego el sistema de bateria del ingeniero (LiPo Turnigy 750 mAh + TP4056 + MT3608 + interruptor, sin conectar al ESP32). El ESP32 sigue con el power bank en la misma posicion; la LiPo va desconectada (lo que importa es su bolsa de aluminio). Ivy cerrada en el Samsung para que el llavero anuncie. 3 repeticiones: marca 2 m, +7 cm derecha, 7 cm izquierda.

### 21:45:26 — E4 repetición 1 (`E4_r1_20261006-214526.csv`)

- 21:45:33 · ⏺ inicia grabación `E4_r1_antena_bateria`
- 21:49:18 · 📝 E4 r1: la primera colocacion dejo la LiPo debajo del extremo de la antena (contrario al USB): se mide como antena_encima. Fotos: celular/foto_E4_r1_antena_encima*.jpg
- 21:49:51 · E4 · antena_encima · n=71 · mediana -67 dBm · 2.4 muestras/s
- 21:56:10 · 📝 E4 r1 antena_sobresale: LiPo encima de la mitad del USB, pegada con cinta y papel; modulo y antena destapados. Foto: celular/foto_E4_r1_antena_sobresale.jpg
- 21:56:42 · E4 · antena_sobresale · n=83 · mediana -59 dBm · 2.7 muestras/s
- 21:59:33 · 📝 E4 r1 sin_bateria: LiPo retirada a mas de 30 cm; power bank debajo del banquito (en el asiento). Foto: celular/foto_E4_r1_sin_bateria.jpg
- 22:00:05 · E4 · sin_bateria · n=77 · mediana -61 dBm · 2.5 muestras/s
- 22:00:24 · ⏹ fin grabación `E4_r1_antena_bateria` (pantalla 2.7 MB, camara 90.7 MB)

### 22:00:25 — E4 repetición 2 (`E4_r2_20261006-220025.csv`)

- 22:00:26 · 📝 E4 r2: silla corrida ~7 cm a la derecha. Orden: sin_bateria, antena_sobresale, antena_encima.
- 22:00:32 · ⏺ inicia grabación `E4_r2_antena_bateria`
- 22:02:10 · E4 · sin_bateria · n=89 · mediana -68 dBm · 2.9 muestras/s
- 22:04:09 · E4 · antena_sobresale · n=75 · mediana -65 dBm · 2.5 muestras/s
- 22:07:38 · E4 · antena_encima · n=87 · mediana -69 dBm · 2.9 muestras/s
- 22:07:59 · ⏹ fin grabación `E4_r2_antena_bateria` (pantalla 1.5 MB, camara 48.6 MB)

### 22:08:00 — E4 repetición 3 (`E4_r3_20261006-220800.csv`)

- 22:08:01 · 📝 E4 r3: silla ~7 cm a la izquierda de la marca de 2 m. Orden: antena_encima, antena_sobresale, sin_bateria.
- 22:08:07 · ⏺ inicia grabación `E4_r3_antena_bateria`
- 22:10:39 · E4 · antena_encima · n=79 · mediana -69 dBm · 2.6 muestras/s
- 22:12:20 · E4 · antena_sobresale · n=59 · mediana -64 dBm · 1.9 muestras/s
- 22:13:34 · E4 · sin_bateria · n=53 · mediana -65 dBm · 1.8 muestras/s
- 22:13:40 · ⏹ fin grabación `E4_r3_antena_bateria` (pantalla 1.2 MB, camara 35.2 MB)
- 22:14:18 · 📝 FIN E4 (3 repeticiones). Combinado: antena_sobresale -63 dBm, sin_bateria -66 (-3 dB), antena_encima -68 (-5 dB). Encima fue la peor en las 3 repeticiones (-8, -4, -5 dB vs sobresale). Conclusion: antena siempre por fuera de la bateria.
- 12:47:21 · 📝 2026-10-07 ~12:19: corto entre VIN y OUT del sistema de bateria al manipular cables (video evidencias/IMPORTANTE/2026-10-07_IMPORTANTE_corto_circuito.mp4). El ESP32 estaba desconectado. Pendiente revisar MT3608, TP4056 y LiPo antes de volver a conectar.
