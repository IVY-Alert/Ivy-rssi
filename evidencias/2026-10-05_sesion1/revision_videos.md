# Revisión de los videos de la webcam (E1)

Revisados con un fotograma cada 10 s (cada 2 s en la zona marcada). Los tiempos son
**dentro de cada video** (mm:ss). Además se cruzó la ventana de cada punto medido con el
video para ver si alguien cruzó la línea durante una medición.

## NO USAR

| Video | Tramo | Motivo |
|---|---|---|
| `camara/E1_r2_distancia.mp4` | **16:15 – 16:50** | Tramo personal (anotado a las 17:01 en la bitácora). |
| `camara/E1_r1_distancia.mp4` | 17:35 – 18:35 | Pasa otra persona de la casa con el perro. Solo con su permiso. |
| `camara/E1_r3_distancia.mp4` | 20:00 – 20:10, 28:35 – 29:15 | Pasa otra persona de la casa, de cerca. Solo con su permiso. |

## Evitar (primeros planos poco favorecedores, no vergonzosos)

Tomas de muy cerca de la cara o de las piernas al acercarse al portátil. Se ven mal en el video.

- `E1_r1`: 00:00 – 00:25, 29:15 – 29:25, 31:00, 33:10
- `E1_r2`: 01:20 – 01:45, 06:40 – 06:55, 09:00, 12:20 – 13:05, 14:40, 15:30, 16:20 – 16:45, 17:30
- `E1_r3`: 07:50, 11:30, 12:30, 13:00 – 13:10, 14:00, 34:20, 37:30

## Buenas tomas recomendadas

| Video | Tramo | Qué se ve |
|---|---|---|
| `E1_r1` | 01:40 – 02:30 | Primer plano del ESP32 con el power bank sobre el banquito (0.25 m). |
| `E1_r1` | 09:40 – 10:00, 12:20 – 13:00 | Mover la silla a la siguiente marca (plano entero, sin cara). |
| `E1_r2` | 04:10 – 05:10 | El llavero se aleja por la sala; buena profundidad. |
| `E1_r2` | 10:00 – 10:40 | Pegando las marcas de cinta en el piso. |
| `E1_r3` | 14:20 – 15:00 | Llevar la silla con el llavero a la siguiente marca. |
| `E1_r3` | 30:00 – 30:20 | Cambio de luz (se enciende una lámpara): plano bonito del pasillo. |

## Interferencias durante los puntos (datos)

Cruce de las ventanas de medición (t_inicio, t_fin del JSON) con el video:

- Todos los puntos de E1 r1 y r2: nadie en la línea durante los 30 s.
- **E1 r3, 3 m (20:25 – 20:55 del video): el perro está en el piso, cerca de la línea,
  durante la medición.** Valor −65 dBm (r1: −64, r2: −70): coherente, pero conviene repetirlo
  si hay tiempo.
- E1 r3, 4 m: se encendió una lámpara justo antes (30:00); la luz no afecta 2.4 GHz.
