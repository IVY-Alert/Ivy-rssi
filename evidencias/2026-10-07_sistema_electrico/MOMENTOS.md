# Sistema eléctrico · 7 oct 2026 · momentos clave

**Resumen:** se montó el llavero con su batería (LiPo 750 mAh → cargador TP4056 → interruptor
→ elevador MT3608 a 5 V → ESP32). El elevador se ajustó a 5 V, el llavero disparó la alerta en
el celular con la batería, hubo un **corto entre VIN y OUT del elevador** (el ESP32 estaba
desconectado y no se dañó) y en la tarde se volvió a soldar todo y funcionó.

## Clips (`clips/`)

| Clip | Duración | Qué muestra |
|---|---|---|
| `00_RESUMEN_para_el_grupo_conexion_y_alerta.mp4` | 2:09 | Conexión + alerta disparándose (el que se mandó al grupo) |
| `01_bateria_conectada_elevador_11V.mp4` | 0:25 | Se conecta la batería: el elevador sale a ~11 V |
| `02_ajuste_elevador_11V_a_5V.mp4` | 2:05 | Girando la perilla: el multímetro baja de 11 V a **5.00 V** |
| `03_conexion_al_ESP32.mp4` | 0:42 | Conexión del sistema al ESP32 |
| `04_ALERTA_con_bateria_pantalla_roja.mp4` | 1:27 | ⭐ Se pulsa el llavero y el celular muestra la **alerta roja con la cuenta atrás** |
| `05_IMPORTANTE_corto_circuito.mp4` | 0:32 | ⚠️ El momento del corto al manipular los cables. El multímetro está en modo temperatura (termopar): marca 44 °C y baja a 35 °C. No se ve chispa. |

## Segundo exacto en los videos completos (`videos_originales/`)

**1 · `1_1007_ajuste_elevador_5V.mp4`** (7:00, grabado 10:07)

| Minuto | Qué pasa |
|---|---|
| 01:25 | Se conecta la batería: el multímetro pasa de 0 a **~11 V** |
| 03:10 | Empieza el ajuste de la perilla del elevador |
| 03:30 | 8.9 V |
| 04:00 | 7.4 V |
| 04:20 | 5.2 V |
| **04:50 – 05:10** | **5.00 V**: elevador listo para el ESP32 |
| 06:20 | Revisión con el celular |

**2 · `2_1018_conexion_y_alerta_funcionando.mp4`** (15:06, grabado 10:18)

| Minuto | Qué pasa |
|---|---|
| 00:00 – 04:00 | Revisión con el multímetro |
| 10:58 – 11:40 | Conexión del sistema al ESP32 |
| 12:00 | Celular en mano, app abierta |
| **13:10** | ⭐ **Llavero pulsado: pantalla roja de alerta** con la cuenta atrás |
| 13:20 – 13:45 | Cuenta atrás (6… 5… 2…) |
| 13:50 – 14:15 | Alerta confirmada en la app |

**3 · `3_1207_corto_circuito.mp4`** (13:09, grabado 12:07)

| Minuto | Qué pasa |
|---|---|
| 09:09 – 11:55 | Sistema conectado; el multímetro (UNI-T UT33C+) está en modo temperatura con el termopar |
| 12:04 – 12:40 | Se reacomodan los cables del sistema |
| 12:44 | Pasa una persona por detrás (recortar si hace falta) |
| **12:46 – 12:52** | ⚠️ **Manipulación de los cables donde ocurre el corto VIN–OUT** |
| 12:53 | Se pone un frasco para sostener los cables |
| 13:07 | Se levanta la cámara: fin |

**Lección:** aislar cada unión con termoencogible y medir siempre 5.0 V en la salida del
elevador antes de conectar el ESP32.
