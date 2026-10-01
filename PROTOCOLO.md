# Protocolo de mediciones

Guía para el día de las mediciones. Lee todo una vez antes de salir.

## Material

- Cinta métrica (mínimo 10 m; para E5, una de 30 m o un decámetro).
- Cinta de enmascarar y marcador para marcar las distancias en el piso.
- Una **caja de cartón o un banco no metálico** para el llavero, a ~1 m de altura.
- El portátil sobre otra superficie no metálica, **a la misma altura** (~1 m).
- Fuente para el llavero: power bank, la batería del llavero o un cargador con extensión.
  Anótala: cambia la masa metálica cerca de la antena.
- Un transportador o una hoja con los ángulos cada 30° dibujados (para E3).
- Un morral y una persona voluntaria (para E2).
- El celular de pruebas, para verificar al final que la alerta llega (opcional).

## Lugar

- Un **pasillo de al menos 10 m** para E1–E4. Anota si es pasillo o espacio abierto, el
  ancho del pasillo y de qué son las paredes. En un pasillo, n puede salir menor que 2: las
  paredes guían la onda.
- Para **E5** probablemente necesites más de 10 m: el llavero transmite a +9 dBm y puede
  llegar a varias decenas de metros con línea de vista. Un pasillo largo o una cancha.
- Lejos de mesas metálicas, neveras y casilleros.

## Antes de empezar

1. Carga el llavero y el portátil.
2. **Desconecta el celular del llavero** (o apaga su Bluetooth). Mientras está conectado, el
   ESP32 deja de anunciar y el portátil no recibe nada.
3. Prueba rápida: `python -m ivy_rssi.registrador --experimento E2 --segundos 10`. Mide un
   punto y mira la tasa. Con el llavero a 1–2 m deberían ser varias muestras por segundo.
   Si sale 0, revisa el paso 2. Si sale muy baja en Linux, mira el README.
4. Marca las distancias en el piso con cinta: 0.25, 0.5, 1, 1.5, 2, 3, 4, 5, 6, 8 y 10 m,
   medidas desde la antena del portátil (normalmente bajo el teclado, cerca de una bisagra).

## Buenas prácticas (todas las mediciones)

- **Quien opera se aparta de la línea de vista** durante los 30 s de cada punto. Lo ideal es
  quedarse detrás del portátil, a 1–2 m. Tu cuerpo es agua y absorbe 2.4 GHz (eso es E2).
- **El celular desconectado** del llavero.
- **Anota Wi-Fi y microondas cercanos**: comparten la banda de 2.4 GHz. El programa lo
  pregunta al inicio.
- **Misma orientación del llavero en E1, E2, E4 y E5**: marca una flecha en la caja y
  apúntala siempre al portátil.
- Que nadie camine por el pasillo durante una medición. Si alguien pasa, repite el punto (`r`).
- **No toques el portátil** mientras mide (la mano cerca de la antena cambia el RSSI).

## Los experimentos

| # | Comando | Puntos | Tiempo aprox. |
|---|---|---|---|
| E1 | `--experimento E1` (×3) | 11 distancias | 12–15 min por repetición |
| E2 | `--experimento E2` | 5 condiciones | 8 min |
| E3 | `--experimento E3` | 12 ángulos | 12 min |
| E4 | `--experimento E4` | 3 posiciones | 10 min (hay que reacomodar la batería) |
| E5 | `--experimento E5 --segundos 15` | hasta perder la señal | 20–30 min |

Total: unas 2 horas y media con pausas. Hazlo en dos sesiones si hace falta.

### E1 — RSSI vs. distancia (tres repeticiones)

1. Llavero en la caja sobre la marca, antena apuntando al portátil.
2. El programa pide cada distancia; mueve la caja, apártate y presiona Enter.
3. Haz **tres repeticiones**. En cada una pon el número (1, 2, 3) cuando el programa lo pida.
4. **Entre repeticiones corre la línea completa unos 5–10 cm de lado** (más o menos media
   longitud de onda, λ/2 ≈ 6 cm). Así cada repetición cae en otro punto del patrón de
   interferencia del multitrayecto, y el promedio de las tres es más representativo. Si
   repites exactamente en el mismo sitio, las tres repeticiones repiten el mismo error.

### E2 — El cuerpo como obstáculo (a 2 m)

Llavero siempre en el mismo sitio, a 2 m: línea de vista, en la mano (de pie sobre la marca),
en el bolsillo del pantalón, una persona de pie en la mitad del camino, dentro del morral
cerrado sobre la caja. Si hay tiempo, repítelo en otro punto del pasillo.

### E3 — Patrón de radiación (a 2 m)

1. Dibuja una rosa de ángulos cada 30° en una hoja y pégala en la caja.
2. 0° = la antena del ESP32 apuntando al portátil. Gira **en sentido horario** visto desde
   arriba, sobre el propio eje del llavero, sin desplazarlo.
3. Ojo al interpretar: en un pasillo el patrón medido mezcla la antena con las reflexiones
   de las paredes. No es el patrón de una cámara anecoica (ver FISICA.md).

### E4 — Antena vs. batería (a 2 m)

Las tres posiciones: antena sobresaliendo de la batería (diseño final), antena encima de la
batería y sin batería cerca (alimentado por cable o con el power bank a más de 30 cm). No
muevas la caja entre condiciones. Si hay tiempo, repítelo (`--repeticion 2`) en otro
punto del pasillo: las diferencias esperadas (6–10 dB) son comparables al multitrayecto.

### E5 — Alcance máximo

1. Empieza a 2 m. El programa pide 2, 4, 6... m.
2. Usa `--segundos 15` para que no se haga eterno.
3. Cuando un punto tenga 0 muestras, el programa pregunta si se perdió la señal. Confirma
   caminando 2 m más cerca: si vuelve, ese era el límite.
4. A partir de unos 30 m con el llavero y el portátil a 1 m de altura, la reflexión en el
   piso empieza a pesar y la señal cae más rápido. Es normal.

## Fotos y videos para el video final

- **Plano general** del montaje: pasillo, cinta métrica en el piso, caja con el llavero y el
  portátil a la misma altura.
- **Primer plano de la pantalla** mostrando las muestras en vivo y el RSSI promedio
  (grábala con el celular o con la grabación de pantalla).
- **E1:** timelapse moviendo el llavero de marca en marca.
- **E2:** una toma de cada condición, sobre todo "persona en medio" y "bolsillo", con la cifra
  de dBm en pantalla.
- **E3:** la rosa de ángulos desde arriba, girando el llavero.
- **E4:** primer plano de las tres posiciones de la antena respecto a la batería (la foto
  justifica la regla de diseño de la carcasa).
- **E5:** toma larga alejándose; el momento en que el contador deja de subir.
- Foto del ESP32 con la antena de PCB visible y de la batería LiPo (la bolsa de aluminio).

## Después

```bash
python -m ivy_rssi.analisis --todo
python -m ivy_rssi.graficas --todo
```

Copia la carpeta `datos/` a un lugar seguro (o haz commit) el mismo día.
