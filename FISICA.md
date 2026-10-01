# La física de la señal de Ivy

Teoría para un curso de física general, con lo que esperamos medir y una frase para el guion
del video en cada sección. Los números salen de `ivy_rssi/fisica.py`.

---

## 1. Una onda electromagnética de 2.4 GHz

El llavero se comunica por **Bluetooth Low Energy (BLE)**: una onda electromagnética, es
decir, campos eléctrico y magnético que oscilan y se propagan a la velocidad de la luz. Para
anunciarse, BLE usa tres canales: el 37 (2402 MHz), el 38 (2426 MHz) y el 39 (2480 MHz)
[1]. Tomamos el centro de la banda, *f* = 2.44 GHz.

$$\lambda = \frac{c}{f} = \frac{3.00\times10^{8}\ \text{m/s}}{2.44\times10^{9}\ \text{Hz}} \approx 12.3\ \text{cm}$$

**La misma banda que el horno microondas.** El horno trabaja a 2.45 GHz, dentro de la banda
ISM de 2.4–2.5 GHz, que se puede usar sin licencia. Por eso Wi-Fi, Bluetooth y los hornos la
comparten. El horno calienta porque las moléculas de agua son dipolos: el campo las hace
girar y la fricción entre ellas disipa energía. Mito común: 2.45 GHz **no** es una
"frecuencia de resonancia del agua". La absorción del agua líquida es máxima cerca de 20 GHz
[2]. Se usa 2.45 GHz porque la banda está libre y porque la onda penetra unos centímetros en
la comida en vez de calentar solo la superficie.

**Esperamos:** ninguna medición directa. Es el número que explica todo lo demás (por qué la
antena mide ~3 cm, por qué el cuerpo absorbe).

> 🎬 *"Nuestro llavero habla con ondas de 12 centímetros, las mismas del horno microondas;
> solo que con una potencia cien mil veces menor."*
> (+9 dBm ≈ 8 mW contra unos 800 W de un horno: ~10⁵.)

---

## 2. Espacio libre: la fórmula de Friis

Una antena ideal reparte su potencia sobre una esfera de área 4π*d*². Por eso la intensidad
cae como 1/*d*². Friis lo escribió para dos antenas [3]:

$$\frac{P_r}{P_t} = G_t\,G_r\left(\frac{\lambda}{4\pi d}\right)^2
\quad\Rightarrow\quad
\text{FSPL}(d) = 20\log_{10}\!\left(\frac{4\pi d}{\lambda}\right)\ \text{dB}$$

A 1 m y 2.44 GHz: **FSPL = 40.2 dB**. En decibeles, la ley 1/*d*² dice que **cada vez que
se duplica la distancia la señal cae 6 dB**.

Con +9 dBm y antenas ideales (0 dBi), a 1 m llegarían 9 − 40.2 ≈ **−31 dBm**. En la práctica
esperamos 15–25 dB menos: la antena de PCB del ESP32 y la del portátil no son ideales, y hay
desacople de polarización. `analisis.py` reporta esa diferencia como "pérdidas del sistema".

> 🎬 *"Cada vez que alejamos el llavero al doble de distancia, la señal pierde tres cuartas
> partes de su potencia."*

---

## 3. El modelo log-distancia

En un edificio real hay paredes, piso y techo que reflejan. Se generaliza el exponente 2
por un exponente *n* que se mide [4]:

$$\text{RSSI}(d) = \text{RSSI}(d_0) - 10\,n\,\log_{10}\!\left(\frac{d}{d_0}\right) + X_\sigma,
\qquad d_0 = 1\ \text{m}$$

- **RSSI** (*Received Signal Strength Indicator*): la potencia que recibe el portátil, en
  dBm (decibeles respecto a 1 mW: −60 dBm = 10⁻⁶ mW).
- ***n***: exponente de pérdida. Valores típicos (Rappaport, tabla 4.2 [4]):

  | Ambiente | *n* |
  |---|---|
  | Espacio libre | 2 |
  | Edificio, con línea de vista (pasillos) | 1.6–1.8 |
  | Fábrica, con obstáculos | 2–3 |
  | Área urbana (celular) | 2.7–3.5 |
  | Edificio, con obstáculos | 4–6 |

  En un pasillo, *n* < 2 se explica porque las paredes reflejan la onda y la "guían" como un
  tubo (efecto guía de onda): la energía no se dispersa en una esfera completa.
- ***X*σ**: el **sombreado** (*shadowing*). Variación lenta de un lugar a otro por obstáculos
  y reflexiones, que en dB se distribuye aproximadamente normal (de ahí "log-normal").

**Cómo se ajusta.** Con *x* = log₁₀(*d*/*d*₀) el modelo es una recta, *y* = *a* + *b·x*, con
*b* = −10*n*. Una regresión lineal da *n*, su **intervalo de confianza del 95 %** (con la *t* de
Student de *N* − 2 grados de libertad), R² y σ = desviación estándar de los residuos.
Ajustamos sobre la **mediana** de cada punto de cada repetición, así que σ mide el sombreado
entre posiciones y no el ruido entre paquetes.

**Esperamos:** *n* entre 1.6 y 2.5 en el pasillo, σ de 2–5 dB y R² > 0.9.

### ¿Promediar en dBm o en mW?

El dBm es logarítmico. Promediar dBm equivale a la media *geométrica* de la potencia;
promediar en mW y convertir de vuelta es la media *aritmética* de la potencia. Esta última
siempre es mayor o igual, y la diferencia crece con la dispersión.

- Reportamos **mediana y promedio en dBm**: el sombreado y el ruido son aproximadamente
  normales *en dB*, el modelo log-distancia es lineal *en dB* y la mediana ignora los picos
  y nulos raros.
- Se promedia **en potencia (mW)** cuando importa la energía total recibida, por ejemplo en
  un presupuesto de enlace. `fisica.promedio_potencia_dbm()` hace ese cálculo, y
  `resumen_por_punto()` reporta los dos.

> 🎬 *"Medimos la señal a once distancias, tres veces. La recta nos dice cuánto 'cuesta'
> alejarse: un exponente de 2 es el vacío; nuestro pasillo da n = …"*

---

## 4. El cuerpo humano absorbe la onda

El músculo es ~75 % agua con sales disueltas: un **dieléctrico con pérdidas**. Dentro de él
el campo se amortigua exponencialmente, *E*(*z*) = *E*₀ e^(−α*z*), con [5]

$$\alpha = \omega\sqrt{\frac{\mu\varepsilon}{2}}\left[\sqrt{1+\left(\frac{\sigma}{\omega\varepsilon}\right)^2}-1\right]^{1/2},
\qquad \delta = \frac{1}{\alpha}$$

Valores del músculo a 2.45 GHz (modelo paramétrico de Gabriel et al. [6], tal como los da la
base de datos IT'IS [7]): **ε_r = 52.73 y σ = 1.739 S/m**.

- Tangente de pérdidas σ/(ωε) ≈ **0.24**. No es ≫ 1, así que el músculo **no** es un "buen
  conductor" y la aproximación δ ≈ √(2/ωμσ) no sirve: daría ≈ 0.8 cm. Por eso usamos la
  fórmula completa.
- **δ ≈ 2.2 cm**: profundidad a la que el *campo* cae a 1/e (37 %). La *potencia* cae a 1/e
  en δ/2 ≈ 1.1 cm. Las tablas de IT'IS reportan la del campo.
- En decibeles: **≈ 3.9 dB por cada centímetro de músculo**.

**Comparación con E2 (importante).** Un torso tiene 20–30 cm de tejido. Si la onda lo
atravesara, perdería 80–120 dB y el llavero sería invisible. En cambio esperamos medir
**15–20 dB** con una persona en medio. La diferencia es la conclusión: la señal no atraviesa
el cuerpo, **lo rodea**. Llega por difracción en los bordes del cuerpo y por reflexiones en
paredes y piso. El análisis traduce cada atenuación a "cm de músculo equivalentes" solo para
hacer visible esa diferencia. No significa que la onda atraviese esos centímetros.

**Esperamos:** mano ≈ 2–5 dB, morral ≈ 5–10 dB, bolsillo ≈ 8–15 dB, persona en medio
≈ 15–20 dB.

> 🎬 *"El cuerpo es casi todo agua, y el agua se come los 2.4 GHz: en apenas dos centímetros
> de músculo la onda pierde más de la mitad de su amplitud. Por eso la alerta sale
> mejor del bolsillo de la chaqueta que del bolsillo del pantalón."*

---

## 5. Patrón de radiación

Ninguna antena real irradia igual hacia todos lados. El ESP32 DevKit V1 usa una antena de
PCB tipo F invertida (la pista en zigzag del extremo del módulo). Su patrón, que es la
ganancia en función de la dirección, tiene lóbulos y nulos. Además, el plano de tierra de la
placa, el regulador, los cables y la batería lo deforman [8].

En E3 giramos el llavero y graficamos el RSSI relativo al máximo en un diagrama polar.
Advertencia honesta: en un pasillo el patrón medido es la antena **por** el ambiente, porque
al girar también cambian las reflexiones. Un patrón "puro" se mide en una cámara anecoica.
Aun así, una diferencia de ~10 dB entre la mejor y la peor dirección es un resultado real y
útil para el diseño.

**Esperamos:** variación de 5–15 dB, con el peor ángulo donde la batería o la placa quedan
entre la antena y el portátil.

> 🎬 *"Al girar el llavero, la señal cambia hasta diez veces en potencia: la antena tiene
> direcciones 'ciegas', y diseñamos la carcasa para que no apunten hacia el cuerpo."*

---

## 6. Metal cerca de la antena: la batería

La batería LiPo viene en una **bolsa de aluminio laminado**. Un conductor cerca de la antena
causa tres efectos:

1. **Reflexión y bloqueo:** el campo no penetra en el metal (δ del aluminio a 2.4 GHz ≈ 1.7 µm).
   Lo que queda detrás de la batería está "a la sombra".
2. **Corrientes imagen:** las cargas del metal se reacomodan y crean una "antena imagen"
   (método de imágenes [8]). Si el metal está paralelo y a una distancia mucho menor que λ/4
   (≈ 3 cm), la imagen está casi en contrafase y cancela buena parte de la radiación.
3. **Desintonía:** el metal cambia la impedancia de la antena. Parte de la potencia rebota
   hacia el transmisor en lugar de irradiarse.

Por eso Espressif recomienda dejar una zona libre de metal alrededor de la antena del módulo
[9], y de ahí sale nuestra regla de diseño: **la antena sobresale de la batería**.

**Esperamos:** antena encima de la batería ≈ 6–10 dB peor que el diseño final. "Sin batería"
casi igual o ligeramente mejor que el diseño final.

> 🎬 *"La batería está envuelta en aluminio, que para esta onda es un espejo. Con la antena
> encima de la batería perdemos más de tres cuartas partes de la potencia; con la antena por fuera, casi
> nada."*

---

## 7. Alcance y tasa de paquetes (E5)

El llavero siempre emite igual. Lo que cambia con la distancia es la fracción de anuncios
que el portátil logra **decodificar**. Mientras el RSSI está muy por encima de la
sensibilidad del receptor (≈ −90 a −100 dBm en portátiles), llegan casi todos. Cerca de la
sensibilidad, el ruido gana y la tasa se desploma en pocos dB.

**Sesgo del sobreviviente:** cerca del límite, el RSSI promedio que medimos es *mayor* que el
real, porque solo registramos los paquetes que tuvieron suerte (un pico de desvanecimiento a
favor). Por eso la curva de RSSI en E5 se "aplana" cerca de −95 dBm en lugar de seguir
bajando. La tasa de paquetes es la medida honesta del alcance.

**Reflexión en el piso:** con antenas a altura *h* ≈ 1 m, más allá de *d* ≈ 4*h*²/λ ≈ 33 m la
onda directa y la reflejada en el piso se cancelan cada vez más. La pérdida pasa de *n* ≈ 2 a
*n* ≈ 4 (modelo de dos rayos [4]).

> 🎬 *"Alejándonos de dos en dos metros, el portátil fue recibiendo cada vez menos avisos,
> hasta perderlos a … metros: ese es el radio de cobertura del llavero."*

---

## Referencias

1. Bluetooth SIG. *Bluetooth Core Specification* v5.4 (2023), Vol. 6 (Low Energy Controller),
   Part B, §1.4.1 "Advertising and data channel indices".
2. Kaatze, U. (1989). "Complex permittivity of water as a function of frequency and
   temperature". *Journal of Chemical & Engineering Data*, 34(4), 371–374.
3. Friis, H. T. (1946). "A note on a simple transmission formula". *Proceedings of the IRE*,
   34(5), 254–256.
4. Rappaport, T. S. (2002). *Wireless Communications: Principles and Practice* (2.ª ed.).
   Prentice Hall. Cap. 4: modelo de dos rayos (§4.6), log-distancia y tabla 4.2 (§4.9),
   sombreado log-normal (§4.9.2).
5. Griffiths, D. J. (2017). *Introduction to Electrodynamics* (4.ª ed.). Cambridge University
   Press. §9.4.1 "Electromagnetic waves in conductors".
6. Gabriel, S., Lau, R. W., & Gabriel, C. (1996). "The dielectric properties of biological
   tissues: III. Parametric models for the dielectric spectrum of tissues". *Physics in
   Medicine & Biology*, 41(11), 2271–2293. (Partes I y II: 41(11), 2231–2249 y 2251–2269.)
7. IT'IS Foundation. *Tissue Properties Database — Dielectric Properties* (músculo, 2450 MHz:
   ε_r = 52.73, σ = 1.739 S/m). https://itis.swiss/virtual-population/tissue-properties/
8. Balanis, C. A. (2016). *Antenna Theory: Analysis and Design* (4.ª ed.). Wiley. Cap. 4
   (efectos de un plano conductor, teoría de imágenes) y cap. 2 (patrón de radiación).
9. Espressif Systems. *ESP32 Hardware Design Guidelines*, sección de diseño de la antena de
   PCB (zona libre de metal). https://docs.espressif.com/projects/esp-hardware-design-guidelines/
