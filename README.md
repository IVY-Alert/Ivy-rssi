# ivy-rssi

Mediciones de la señal BLE (2.4 GHz) del llavero **Ivy** y su análisis físico, para el
proyecto de Física, Calor y Ondas (Universidad del Norte).

El portátil escucha los anuncios del llavero (`GEOEXPO-ALERT`), registra el RSSI en cinco
experimentos, ajusta modelos de propagación de ondas y genera gráficas listas para el video.

- **[PROTOCOLO.md](PROTOCOLO.md)**: qué hacer el día de las mediciones.
- **[FISICA.md](FISICA.md)**: la teoría, con frases para el guion.
- **[figuras/ejemplo/](figuras/ejemplo/)**: todas las figuras hechas con datos simulados.

## Instalación

Python 3.11 o más reciente.

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Linux:    source .venv/bin/activate
pip install -r requirements.txt
```

## El programa

```bash
python -m ivy_rssi              # con el llavero
python -m ivy_rssi --simular    # sin llavero, para practicar
```

Al entrar pide los datos de la sesión (portátil, alturas, lugar...) una sola vez y muestra
un menú:

```
  1) E1  RSSI vs. distancia
  2) E2  El cuerpo como obstáculo
  3) E3  Patrón de radiación
  4) E4  Antena vs. batería
  5) E5  Alcance máximo
  ─────
  6) Resultados, figuras e INFORME de todo lo medido
  7) Buscador: ¿dónde está el llavero? (RSSI en vivo)
  8) Calculadora física para una distancia
  9) Cambiar segundos por punto
  0) Salir
```

- **1–5:** corre la prueba guiada. Al terminar muestra sus resultados y genera sus figuras,
  combinando las repeticiones que ya haya en `datos/`.
- **6:** analiza todo, cruza E1 con E5 (alcance predicho contra medido) y escribe
  `figuras/INFORME.md`, con estructura de trabajo de grado: resumen, marco teórico,
  metodología, resultados, discusión, conclusiones y limitaciones, con tus números.
- **7, buscador:** RSSI en vivo con una barra de frío/caliente, la distancia estimada con su
  intervalo y si te estás acercando. Usa el modelo calibrado en tu E1.
- **8, calculadora:** ficha física para una distancia: λ, Friis, dos rayos, zona de Fresnel,
  RSSI y margen esperados, alcance, penetración en tejido, difracción por una persona y SAR.

Ejemplo de informe completo con datos simulados: [figuras/ejemplo/INFORME.md](figuras/ejemplo/INFORME.md).

## Uso por partes

```bash
# 1. Registrar (real, con el llavero encendido y SIN conectar al celular)
python -m ivy_rssi.registrador --experimento E1
python -m ivy_rssi.registrador --experimento E5 --segundos 15

# 1b. Probar todo sin Bluetooth
python -m ivy_rssi.registrador --experimento E1 --simular
python -m ivy_rssi.registrador --experimento E1 --simular --auto   # sin preguntas

# 2. Analizar (si das varias repeticiones del mismo experimento, se combinan)
python -m ivy_rssi.analisis datos/E1_r1_20261005-101500.csv
python -m ivy_rssi.analisis --todo

# 3. Graficar
python -m ivy_rssi.graficas datos/E2_r1_20261005-103000.csv
python -m ivy_rssi.graficas --todo          # todas las sesiones de datos/ → figuras/
python -m ivy_rssi.graficas --ejemplo       # simula y grafica en figuras/ejemplo/

# 4. Informe, buscador y calculadora sueltos
python -m ivy_rssi.informe --todo           # figuras/INFORME.md
python -m ivy_rssi.informe --ejemplo        # figuras/ejemplo/ con datos simulados
python -m ivy_rssi.buscador [--simular]
python -m ivy_rssi.calculadora 5            # ficha física a 5 m

# Tests
python -m pytest
```

Opciones del registrador: `--segundos N` (30 por defecto), `--direccion AA:BB:...` (filtrar
por MAC en vez de por nombre), `--carpeta`, `--auto`, `--repeticion`, `--semilla`.

Durante la medición: **Enter** mide, **s** salta el punto, **t** termina. Al final de cada
punto: **Enter** sigue, **r** repite (el intento anterior queda en el CSV pero marcado como
descartado en el JSON, y el análisis lo ignora).

## Archivos de una sesión

`datos/E1_r2_20261005-101500.csv` — una fila por anuncio recibido:

| timestamp | experimento | condicion | valor_condicion | rssi_dbm |
|---|---|---|---|---|
| 1791216900.123 | E1 | 1.5 m | 1.5 | -58 |

`datos/E1_r2_20261005-101500.json` — metadatos (fecha, sistema operativo, portátil, fuente
del llavero, alturas, repetición, lugar, interferencias, notas) y un resumen por punto
(muestras, tasa, mediana, promedio). Se escriben **después de cada punto**, así que un
fallo a mitad de la sesión no borra lo ya medido.

El análisis escribe `datos/analisis_E1.json`, etc.

## Estructura

```
ivy_rssi/
  __main__.py      # el programa con menú
  experimentos.py  # los 5 experimentos y sus condiciones, en un solo lugar
  registrador.py   # escaneo BLE y protocolo guiado
  simulador.py     # datos sintéticos realistas (semilla fija)
  sesion.py        # leer/escribir CSV + JSON
  fisica.py        # λ, Friis, log-distancia, tejido, Fresnel, difracción, Debye,
                   # dos rayos, Rice, estimación de distancia, alcance, SAR
  analisis.py      # un análisis por experimento
  graficas.py      # estilo Ivy + una función por figura (datos y teoría)
  informe.py       # INFORME.md con estructura de trabajo de grado
  buscador.py      # modo buscador: RSSI en vivo y distancia estimada
  calculadora.py   # ficha física para una distancia
  fuentes/         # Bricolage Grotesque e Instrument Sans (licencia OFL)
```

## Bluetooth en cada sistema

**El escaneo es activo, no pasivo.** El firmware pone el nombre `GEOEXPO-ALERT` en la
*respuesta de escaneo* (scan response), no en el anuncio. Un escaneo pasivo nunca la pide y
no vería el nombre. Con escaneo activo el portátil manda un `SCAN_REQ` y el llavero
contesta. Los dos paquetes traen RSSI, y el registrador cuenta ambos como muestras.
El registrador recuerda la dirección del llavero apenas ve el nombre, así que también acepta
los anuncios que llegan sin nombre.

**Windows 11:** no requiere nada especial; los anuncios repetidos llegan solos. Bluetooth
encendido en Configuración.

**Linux (Fedora/Arch, BlueZ):** por defecto BlueZ junta los anuncios repetidos y llegan
poquísimas muestras. El registrador pide `DuplicateData=True` en el filtro de descubrimiento.
Si aun así la tasa sale baja con señal fuerte (el programa avisa):

- `bluetoothctl power on` y que no haya otro programa escaneando (cierra el applet de
  Bluetooth del escritorio si está buscando dispositivos).
- BlueZ junta en una sola notificación los cambios que llegan muy seguidos. Por eso en Linux
  puede haber menos muestras/s que en Windows aunque el filtro funcione. Para la física no
  importa, mientras haya decenas de muestras por punto.

Mira siempre la **tasa de muestras/s** que se imprime al final de cada punto. Con el
llavero cerca deberían ser varias por segundo.

## Qué está probado y qué no

| Parte | Probado aquí (sin hardware) | Requiere el llavero |
|---|---|---|
| Física (λ, FSPL, δ, ajuste, IC) | ✅ tests numéricos | — |
| Simulador, análisis, combinación de repeticiones | ✅ | — |
| Gráficas (11 figuras × 2 formatos) e informe | ✅ | — |
| Buscador y calculadora | ✅ en modo `--simular` y con un escáner BLE falso | el buscador real |
| Protocolo guiado, guardado incremental, repetir/saltar | ✅ en modo `--simular` | — |
| Escaneo BLE real, filtro por nombre/MAC, DuplicateData en BlueZ, tasa real | ❌ | ✅ en tu portátil |
