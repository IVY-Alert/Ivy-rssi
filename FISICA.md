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

**El modelo de Debye lo demuestra con números.** Los dipolos del agua tardan un tiempo
τ en girar para seguir al campo. Eso da una permitividad compleja [2]:

$$\varepsilon(\omega) = \varepsilon_\infty + \frac{\varepsilon_s - \varepsilon_\infty}{1 + j\omega\tau},
\qquad \varepsilon_s = 78.36,\ \varepsilon_\infty = 5.2,\ \tau = 8.27\ \text{ps (25 °C)}$$

La parte imaginaria ε″ mide la absorción y es máxima cuando ωτ = 1, es decir, en
*f* = 1/(2πτ) ≈ **19 GHz**. A 2.45 GHz, ε″ ≈ 9: absorbe bastante, pero muy lejos del máximo
(≈ 37). No hay ninguna "resonancia": es una relajación, una curva ancha y sin pico agudo.
Figura `T1_agua_debye`.

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

### 4.1 Zonas de Fresnel y difracción por filo de cuchillo

¿Por dónde rodea la onda al cuerpo? La energía no viaja por una línea sino por la **primera
zona de Fresnel**: el elipsoide alrededor de la línea de vista donde los caminos difieren del
directo en menos de λ/2 [4]. Su radio a distancias *d*₁ y *d*₂ de los extremos es

$$r_1 = \sqrt{\frac{\lambda\, d_1 d_2}{d_1 + d_2}}$$

En la mitad de un enlace de 2 m, **r₁ ≈ 25 cm**: casi el ancho de un torso. Una persona tapa
casi toda la zona, pero no toda. Modelamos sus costados como dos **filos de cuchillo**. El
parámetro de Fresnel-Kirchhoff *v* = *h*·√(2(*d*₁+*d*₂)/(λ*d*₁*d*₂)) mide cuánto tapa cada
borde (*h* ≈ 22 cm, medio ancho de hombros). La pérdida por difracción sigue la aproximación
de la UIT-R P.526 [10]:

$$J(v) = 6.9 + 20\log_{10}\!\left(\sqrt{(v-0.1)^2+1} + v - 0.1\right)\ \text{dB}$$

Con *v* ≈ 1.26 cada borde da ≈ 15.5 dB. Las dos ondas que rodean el cuerpo por cada lado se
suman en potencia (−3 dB), así que el total es **≈ 12 dB**. Las reflexiones en paredes y
piso, y el cuerpo real (más ancho, con brazos), lo suben hacia lo que esperamos medir.
**Conclusión física: la difracción predice ~12 dB; atravesar el cuerpo predeciría ~97 dB.**
La medición decide.

**Esperamos:** mano ≈ 2–5 dB, morral ≈ 5–10 dB, bolsillo ≈ 8–15 dB, persona en medio
≈ 12–20 dB.

> 🎬 *"El cuerpo es casi todo agua, y el agua se come los 2.4 GHz: en apenas dos centímetros
> de músculo la onda pierde más de la mitad de su amplitud. Por eso la alerta sale
> mejor del bolsillo de la chaqueta que del bolsillo del pantalón."*

> 🎬 *"Si la onda tuviera que atravesar a una persona, su potencia se dividiría entre
> miles de millones. No la atraviesa: la rodea, igual que el sonido dobla una esquina."*
> (97 dB = 10^9.7 ≈ 5 000 millones.)

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

**Validación cruzada.** Con *n* y RSSI(1 m) de E1 se predice el alcance antes de medirlo:

$$d_{\max} = d_0 \cdot 10^{(\text{RSSI}(d_0) - S)/(10n)}, \qquad S \approx -95\ \text{dBm}$$

E5 pone a prueba esa predicción. Que un modelo calibrado hasta 10 m prediga el alcance a
50–70 m es la prueba más fuerte de que la física funciona. Si falla, dice dónde: dos rayos,
otro ambiente u otra sensibilidad. La calculadora del programa da esta ficha para cualquier
distancia.

---

## 8. Desvanecimiento rápido: la distribución de Rice

Con el llavero quieto, el RSSI igual "tiembla" de un paquete a otro. Al receptor llegan
muchas ondas a la vez: la directa y decenas de reflejadas, con fases distintas. Además, BLE
salta entre 3 frecuencias, y cada una ve otro patrón de interferencia. Por el teorema del
límite central, la suma de las ondas dispersas es una gaussiana compleja. Si además hay una
onda directa dominante, la **amplitud** sigue una distribución de **Rice** [11], con

$$K = \frac{\text{potencia de la onda directa}}{\text{potencia de las dispersas}}$$

- *K* grande (≥ 10): línea de vista, la señal es estable (~2 dB de dispersión).
- *K* → 0: sin camino directo, distribución de **Rayleigh**, con nulos profundos de −10 a
  −20 dB.

Lo estimamos por momentos (Greenstein et al. [11]): con γ = Var(*P*)/E[*P*]², sobre la
potencia en mW, *K* = √(1−γ)/(1−√(1−γ)).

**Esperamos:** *K* alto en línea de vista y bajo con una persona en medio. Es una segunda
evidencia, independiente de la atenuación, de que el cuerpo tapa el camino directo
(figura `E2_desvanecimiento`).

> 🎬 *"Cuando alguien se interpone, la señal no solo baja: empieza a temblar, porque ya no
> llega directo sino rebotando por todos lados."*

---

## 9. ¿Sirve el RSSI como regla?

Invirtiendo el modelo log-distancia se estima la distancia:

$$\hat d = d_0 \cdot 10^{(\text{RSSI}(d_0) - \text{RSSI})/(10n)}$$

Pero el sombreado de σ dB se vuelve un error **multiplicativo**: la distancia real está, con
68 % de probabilidad, entre *d̂*/F y *d̂*·F, con F = 10^(σ/(10*n*)). Con σ = 3 dB y *n* = 2.2,
F ≈ 1.37: "5 m" significa "entre 3.7 y 6.9 m". El error crece en proporción a la distancia.

Por eso el **modo buscador** del programa muestra una barra de "frío/caliente" y una
distancia con su intervalo, no un número exacto. Es la física honesta de buscar un llavero
perdido (figura `E1_rssi_como_regla`).

> 🎬 *"El RSSI no es una cinta métrica: es un juego de frío o caliente. Y la física nos dice
> exactamente qué tan caliente."*

---

## 10. ¿Es seguro llevarlo encima? (SAR)

La **tasa de absorción específica** (SAR, W/kg) es la potencia absorbida por kilogramo de
tejido. La norma limita la SAR localizada a **2 W/kg** promediada en 10 g de tejido (cabeza y
tronco, ICNIRP 2020 [12]). Cota del peor caso imposible: que *toda* la potencia del llavero
(+9 dBm ≈ 8 mW) se absorba en 10 g de tejido:

$$\text{SAR} \le \frac{P}{m} = \frac{0.008\ \text{W}}{0.010\ \text{kg}} = 0.8\ \text{W/kg} < 2\ \text{W/kg}$$

Y el llavero no transmite todo el tiempo: emite ráfagas de menos de un milisegundo por
anuncio, así que su potencia media es mucho menor.

> 🎬 *"Aun suponiendo que el cuerpo se tragara toda la señal, el llavero queda por debajo de
> la mitad del límite internacional de exposición."*

---

## Referencias

1. Bluetooth SIG. *Bluetooth Core Specification* v5.4 (2023), Vol. 6 (Low Energy Controller),
   Part B, §1.4.1 "Advertising and data channel indices".
2. Kaatze, U. (1989). "Complex permittivity of water as a function of frequency and
   temperature". *Journal of Chemical & Engineering Data*, 34(4), 371–374.
3. Friis, H. T. (1946). "A note on a simple transmission formula". *Proceedings of the IRE*,
   34(5), 254–256.
4. Rappaport, T. S. (2002). *Wireless Communications: Principles and Practice* (2.ª ed.).
   Prentice Hall. Cap. 4: modelo de dos rayos (§4.6), zonas de Fresnel y filo de cuchillo
   (§4.7), log-distancia y tabla 4.2 (§4.9), sombreado log-normal (§4.9.2).
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
10. UIT-R (2019). *Recomendación UIT-R P.526-15: Propagación por difracción*. Unión
    Internacional de Telecomunicaciones, ec. (31) (filo de cuchillo).
11. Greenstein, L. J., Michelson, D. G., & Erceg, V. (1999). "Moment-method estimation of the
    Ricean K-factor". *IEEE Communications Letters*, 3(6), 175–176.
12. ICNIRP (2020). "Guidelines for limiting exposure to electromagnetic fields (100 kHz to
    300 GHz)". *Health Physics*, 118(5), 483–524.
