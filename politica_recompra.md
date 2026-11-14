# POLÍTICA DE RECOMPRA — SOL, con BTC como guía y HYPE, SUI y PUMP como cesta

- **Versión:** 1.1
- **Aprobada por:** Miguel, el 14 de noviembre de 2026
- **Entrada en vigor:** 21 de noviembre de 2026, 7 días después de la aprobación (sección
  11.3). El script de señales v2.0 ya está en el repositorio (anexo A). Hasta esa fecha sigue
  vigente la v1.0.
- **Sustituye a:** v1.0, aprobada el 2-nov-2026

Este documento manda sobre cualquier criterio de los agentes. Ningún agente puede
modificarlo ni interpretarlo de forma distinta a como está escrito. Solo Miguel lo cambia.

**Este documento es público: no contiene importes.**

---

## 1. Objetivo y alcance

**Objetivo del sistema:** la posición de SOL vendida en el de-risk se reconstruye por tramos
durante el ciclo bajista, de forma que el valor total de lo recomprado, en USD y en
SOL-equivalente, acabe por encima de lo que valdría aquella posición en la fecha de cada
medición. La medida la calcula Chief of Staff cada mes; la cantidad de referencia está en su
ledger privado.

**Cómo lo persigue:** el sistema hace dos cosas distintas y esta política las separa.

1. **Definir el suelo** (secciones 3 a 5). Es el trabajo del flujo: Toro, Oso y Estrategia
   determinan cada semana en qué fase de suelo está el mercado. Eso decide **cuándo** se
   compra y **cuánto** capital se libera.
2. **Elegir el destino** (sección 6). No hay reparto fijo por activo. El sistema está
   especializado en SOL: SOL es el destino por defecto de cada tramo, y Miguel decide en
   cada ticket si una parte va a otro activo elegible.

Papel de cada activo:

- **SOL:** activo principal. Su fase de suelo desbloquea los tramos.
- **BTC:** guía del mercado. SOL no puede alcanzar una fase que BTC no haya alcanzado. Es
  además un destino elegible.
- **HYPE, SUI y PUMP (cesta):** destinos opcionales, sin fase de suelo propia. Solo entran
  si cumplen las condiciones de la sección 10.

Todas las compras son en contado y con firma manual de Miguel. Ningún agente ejecuta
operaciones ni accede a wallets.

## 2. Capital

Los importes viven solo en el ledger privado de Chief of Staff.

- **Capital de recompra del ciclo** = el USDC de la wallet (en Jupiter Lend y líquido) el
  día de entrada en vigor, menos la reserva mínima intocable (10 % del patrimonio total de
  la wallet, holds de largo plazo incluidos). Si Chief of Staff ya registró el capital
  inicial con la v1.0, ese registro se mantiene.
- **Es una sola bolsa**, sin reparto previo por activo. Se divide así:

| Parte | % del capital de recompra | Regla |
|---|---|---|
| DCA de fondo | 15 % | Sección 9 |
| Tramos RT1–RT4 | 85 % | Secciones 5 y 6 |

  Los porcentajes de los tramos (sección 5) se aplican sobre ese 85 %. Así la suma es 100 %.

- Quedan fuera: los holds de largo plazo (2Z) y el capital de la fase de test.
- **Incidente de custodia:** si Chief of Staff u Oso documentan un incidente en Jupiter Lend
  o una pérdida de paridad de USDC, Chief of Staff avisa, no emite tickets nuevos y Miguel
  decide. Ningún agente propone mover el capital.
- **Órdenes de otra bolsa:** las órdenes límite de compra de SOL que Miguel tiene abiertas
  en otra plataforma se pagan con dinero ajeno a este capital. No se descuentan de los
  tramos ni del DCA y no cuentan en la medida del objetivo. Chief of Staff las anota solo
  como información (precio, en privado) y avisa en el ticket si un escalón de una escalera
  nueva queda a menos de un 3 % de una de ellas. Mantenerlas o cancelarlas es decisión de
  Miguel; los agentes pueden opinar en la card, nada más.

## 3. Cuándo una familia de señales cuenta como ACTIVA

El archivo de señales publica, por familia, las condiciones y si se cumplen.

> **Una familia está ACTIVA cuando el número de condiciones cumplidas es igual o mayor
> que `mínimo(2, condiciones con fuente)`.**

Tres reglas para contar:

1. **Sin fuente y fuente caída no son lo mismo.**
   - *Sin fuente* (no existe dato gratuito): la condición no cuenta ni a favor ni en contra.
     Hoy son: liquidaciones (BTC); pico de unstaking y liquidaciones (SOL). El archivo las
     marca con `sin_dato_motivo: sin_fuente`.
   - *Fuente caída* (existe, pero hoy falló y aparece en `fallos`): la condición cuenta como
     **no cumplida**. Un fallo de datos nunca puede hacer más fácil un desbloqueo. Excepción
     acotada: si falla LTH-SOPR, vale el último valor guardado de los 7 días anteriores.
2. **Un mismo hecho cuenta una sola vez.** "MVRV Z < 0", "precio bajo realized price" y
   "NUPL < 0" son la misma condición matemática (capitalización por debajo de la
   capitalización realizada). Cuentan como **una** condición, en la familia *valoración*
   de BTC, y NUPL no cuenta en *capitulación*.
3. **Con una sola condición con fuente**, la familia puede activarse con ella, pero
   Estrategia lo escribe en la card como BASE DÉBIL. Con cero, la familia es NO EVALUABLE.

El archivo de señales ya aplica esta regla y publica el resultado en el campo `activa` de
cada familia. Los agentes leen ese campo: no recalculan la regla.

Familias que desbloquean, tal como quedan en esta versión:

| Activo | Familia | Condiciones |
|---|---|---|
| BTC | valoración | precio bajo realized price (incluye MVRV Z y NUPL) · precio hasta un 10 % sobre la media de 200 semanas · caída desde el máximo de al menos 50 % |
| BTC | capitulación | LTH-SOPR < 1 · Puell < 0,5 · hash ribbons en capitulación |
| BTC | confirmación | cierre semanal sobre la media de 20 semanas · RSI semanal saliendo de sobreventa · hash ribbons recuperadas en los últimos 30 días |
| SOL | valoración | precio bajo la media de 200 semanas · ratio SOL/BTC en el 10 % inferior de 52 semanas · capitalización / comisiones de red en el 20 % más bajo de 12 meses |
| SOL | capitulación | TVL en USD cae y TVL en SOL estable · pico de unstaking (sin fuente) |
| SOL | confirmación | cierre semanal sobre la media de 20 semanas · RSI semanal saliendo de sobreventa · familia *confirmación* de BTC ACTIVA |

Las familias *derivados* y *sentimiento* no desbloquean nada. Sirven como contexto.

**Limitación conocida:** la *capitulación* de SOL solo tiene una condición con fuente (TVL).
Mientras siga así, su fase 2 se apoya en una sola señal propia; lo compensan P_final ≥ 55 %
y que BTC tenga que estar ya en fase 2.

## 4. Cómo define el flujo el suelo

### 4.1 P_final

**P_final de un activo** es la probabilidad, combinada por Estrategia, del evento
`evento_8s` del archivo de señales: *el cierre semanal más bajo de las próximas 26 semanas
ocurre dentro de las próximas 8*. Es decir, la probabilidad de que el suelo esté aquí o a
menos de dos meses.

- Toro y Oso dan cada uno su probabilidad para BTC y para SOL. Estrategia las pondera por
  su Brier score.
- `evento_8s` tarda hasta 26 semanas en resolverse y se resuelve antes cuando sale "no", lo
  que al principio favorece a quien predice bajo. Por eso los pesos son **50/50 hasta tener
  10 predicciones de `evento_8s` resueltas**, de las que al menos 3 resueltas en "sí".
  Mientras tanto, el Brier de `evento_4s` se publica como información y no pondera.
- `evento_4s` no entra en P_final. Es contexto y calibración.
- **Referencia de "sin información":** el archivo publica en
  `frecuencia_historica_eventos` cuántas veces ha ocurrido `evento_8s` en la historia de
  cada activo (a 14-nov-2026: 57 % de las semanas en BTC desde 2010 y 44 % en SOL desde 2020). Una P_final igual o
  inferior a esa frecuencia no aporta información: Estrategia lo escribe en la card.
- Si el desacuerdo entre Toro y Oso supera los 40 puntos, la semana se marca
  INCERTIDUMBRE ALTA (sección 5).

### 4.2 Fases de suelo

Estrategia publica cada semana la fase de BTC y la de SOL. Las fases se alcanzan en orden y
una fase alcanzada no se pierde, salvo por invalidación (4.4).

| Fase | Nombre | Condiciones del activo (todas a la vez) |
|---|---|---|
| 0 | SIN SUELO | No se cumple la fase 1 |
| 1 | ZONA DE VALOR | P_final ≥ 45 % **y** familia *valoración* ACTIVA |
| 2 | CAPITULACIÓN | Fase 1 alcanzada, P_final ≥ 55 % **y** familia *capitulación* ACTIVA |
| 3 | SUELO CONFIRMADO | Fase 2 alcanzada, P_final ≥ 65 %, familia *confirmación* ACTIVA **y** suelo de referencia VALIDADO |

**Regla de guía:** SOL solo puede alcanzar la fase *n* si BTC ya está en la fase *n* o
superior, esa misma semana o antes.

### 4.3 Suelo de referencia

Es el precio que el flujo declara como suelo. Se define con campos del archivo, no con la
opinión de un agente.

- **Suelo provisional:** `ciclo.minimo_tras_maximo_usd`, el cierre semanal más bajo desde
  el máximo.
- **Suelo VALIDADO:** ese mínimo tiene al menos **4 semanas** de antigüedad y desde él ha
  habido un rebote de al menos el **15 %** en cierre semanal.

Estrategia escribe en cada card, para BTC y para SOL: fase, suelo de referencia (precio y
fecha), si es provisional o validado, y el nivel de invalidación.

### 4.4 Invalidación

Si un cierre semanal queda **por debajo del suelo validado**:

- el suelo vuelve a ser provisional, con el nuevo mínimo;
- el activo vuelve a la fase 2 si estaba en la 3;
- las órdenes de RT3 y RT4 aún no ejecutadas se cancelan; lo no ejecutado vuelve a su tramo;
- lo ya comprado no se toca. Esta política no vende.

La invalidación de BTC arrastra a SOL por la regla de guía.

### 4.5 Escenarios de ciclo

Además de P_final, Toro y Oso dan cada semana, para BTC y para SOL, la probabilidad de tres
escenarios excluyentes que suman 100 %. La referencia es `suelo.minimo_usd` de esa semana.

| Escenario | Se cumple si |
|---|---|
| **A. El suelo ya está hecho** | Ningún cierre semanal por debajo de la referencia hasta el 26-sep-2027 |
| **B. Suelo nuevo pronto** | El cierre semanal más bajo hasta el 26-sep-2027 queda por debajo de la referencia y ocurre el 28-mar-2027 o antes |
| **C. Ciclo largo** | Queda por debajo de la referencia y ocurre después del 28-mar-2027 |

- El archivo resuelve cada predicción en `resolucion_ciclo`. Se puntúa con el Brier de tres
  categorías y Estrategia combina las probabilidades con los mismos pesos que en 4.1.
- **No desbloquean tramos ni cambian fases.** Sirven para dos cosas: la propuesta semanal
  de inicio del DCA (sección 9) y dar a Miguel el contexto de cuánto puede durar el ciclo.
- Son opiniones que se calibran con el tiempo, no probabilidades medidas. Estrategia las
  presenta así en la card.

## 5. Tramos de recompra

Un tramo se desbloquea **cuando SOL alcanza la fase correspondiente**. Como máximo se
desbloquea un tramo nuevo por semana. "No desbloquear nada" es el resultado esperado la
mayoría de las semanas.

| Tramo | % de la parte de tramos | Se desbloquea cuando |
|---|---|---|
| **RT1** | 20 % | SOL alcanza la fase 1 |
| **RT2** | 30 % | SOL alcanza la fase 2 |
| **RT3** | 30 % | SOL alcanza la fase 3 |
| **RT4** (reserva) | 20 % | Una de las dos vías de abajo |

**RT4 es el único tramo que puede abrirse sin RT3.** Tiene dos vías:

- **Vía retest:** RT2 desbloqueado, suelo de SOL VALIDADO y un cierre semanal de SOL a menos
  de un 3 % por encima de ese suelo, sin perderlo. Un mínimo nuevo no es un retest: es una
  invalidación.
- **Vía rebote:** RT1 y RT2 desbloqueados, RT3 sin abrir y
  `ciclo.rebote_desde_minimo_pct` de SOL mayor que 25. Evita quedarse fuera si el mercado
  se gira sin dar la confirmación completa.

Reglas fijas:

- **INCERTIDUMBRE ALTA:** solo se libera la mitad del tramo. La otra mitad se libera la
  primera semana posterior en que el desacuerdo sea de 40 puntos o menos y las condiciones
  de la fase sigan cumpliéndose. Si el tramo siguiente se desbloquea antes, la mitad
  pendiente se suma a RT4.
- **Interacción con el de-risk:** mientras el plan de de-risk esté reduciendo un activo, no
  se compra ese activo.
- Sin archivo de señales del día, con estado `FALLO` o caducado, no se desbloquea nada.

## 6. Destino de cada tramo

No hay reparto fijo. Cada tramo desbloqueado se asigna así:

1. **Por defecto, el 100 % del tramo va a SOL.**
2. Estrategia escribe en la card qué otros activos son **elegibles** esa semana y por qué,
   con las cifras del archivo. No propone porcentajes.
   - **BTC** es elegible si está en la misma fase o superior (por la regla de guía, lo
     estará casi siempre).
   - **HYPE, SUI y PUMP** son elegibles si cumplen la sección 10.
3. **Miguel decide el reparto del tramo** y lo escribe. Chief of Staff emite los tickets
   con ese reparto. Si Miguel no dice nada, se aplica el punto 1.
4. **Sin tope para la cesta.** Miguel puede asignar cualquier parte del tramo a los activos
   elegibles. Chief of Staff solo comprueba que cada activo del reparto sea elegible esa
   semana; si no lo es, no emite su ticket y se lo dice a Miguel.
5. **Aviso de riesgo de oferta:** si un activo de la cesta tiene la familia *riesgo_oferta*
   cumplida (FDV más del doble de la capitalización), Estrategia lo marca como ALERTA DE
   OFERTA en la card y Chief of Staff lo repite en el ticket. No limita ni excluye: decide
   Miguel.

Un activo no elegible no recibe nada y su parte no queda "pendiente": el tramo se reparte
entre los elegibles. No hay capital aplazado por activo.

## 7. Escalera de órdenes

Cada tramo se reparte en órdenes límite sobre el precio de referencia del archivo:
`resumen.precio_referencia_usd` para BTC y SOL, y
`otras_monedas.<activo>.tendencia.precio_referencia_usd` para la cesta (precio de perpetuo:
Chief of Staff lo contrasta con el spot del mercado donde se compre).

| Tramo | BTC y SOL | Cesta |
|---|---|---|
| RT1, RT2 y RT4 vía retest (comprar debilidad) | −3 %, −6 %, −10 % | −5 %, −10 %, −15 % |
| RT3 y RT4 vía rebote (comprar confirmación) | la mitad al precio de referencia; el resto a −3 % y −6 % | la mitad al precio de referencia; el resto a −5 % y −10 % |

- Validez: **14 días**. Lo no ejecutado se cancela y vuelve a su tramo; Chief of Staff
  emite una escalera nueva sobre el precio de referencia vigente si la fase se mantiene.
- No hay stop loss. El control de riesgo es el tamaño, la invalidación (4.4) y la pausa.

## 8. Condición de pausa

Es **una sola condición del sistema**, calculada sobre BTC. Congela RT3 y RT4 en **todos**
los activos, incluidas las órdenes pendientes de esos tramos.

- **Se activa** si BTC cierra una semana por debajo del *realized price* con una caída
  semanal superior al 15 %.
- **Se levanta** tras dos cierres semanales consecutivos por encima del *realized price*.
- Si `pausa_sistema_activa` llega como `SIN DATO`, no se desbloquean RT3 ni RT4 esa semana.

## 9. DCA de fondo

- **Destino: solo SOL.** Es el activo en el que el sistema está especializado y en el que
  se mide el objetivo.
- **Importe:** el 15 % del capital de recompra repartido en **26 semanas** a partes
  iguales. Chief of Staff calcula y registra el importe en privado.
- **Inicio: lo propone el flujo y lo decide Miguel.** Cada semana, mientras el DCA no haya
  empezado, Estrategia escribe en la card una línea "DCA: INICIAR" o "DCA: ESPERAR", con las
  cifras del archivo que la apoyan y la probabilidad de cada escenario de ciclo. Chief of
  Staff no emite ninguna compra de DCA hasta que Miguel escriba que empieza.
- **Una vez empezado, no se para por la opinión de la semana:** sigue los 26 lunes, también
  durante la condición de pausa.
- Si no ha empezado cuando salta la revisión de fin de ciclo (11.1), Miguel decide qué
  hacer con el 15 % reservado.
- **Día de compra:** lunes, con el cierre semanal ya publicado.
- Se suspende solo si Miguel lo decide por escrito, o mientras el de-risk esté reduciendo
  SOL.
- Al acabar las 26 semanas, lo que quede sin usar se suma a RT4.

## 10. Activos cesta: HYPE, SUI y PUMP

No tienen fase de suelo ni probabilidades de Toro y Oso. Son destinos opcionales de un
tramo ya desbloqueado por SOL. Un activo de la cesta es **elegible** en un tramo si cumple
todo esto:

1. **Techo relativo:** `techo_ratio_btc.supera` es false (su ratio frente a BTC no está por
   encima del percentil 80 de 52 semanas).
2. **Para RT1 y RT2:** su familia *valoracion_relativa* está ACTIVA según la sección 3. En
   esa familia, las tres condiciones derivadas del precio (ratio frente a BTC, media de 200
   días, caída desde su máximo) cuentan como **una sola**: para activarse hace falta además
   la de capitalización / ingresos. Un precio castigado no basta si el negocio no lo
   respalda.
3. **Sin veto estructural:** Oso no ha documentado un evento estructural confirmado
   (hackeo, parada de red, insolvencia o incidente grave de plataforma, deslistado). Con
   veto, el activo no es elegible hasta que Miguel lo levante por escrito.
4. **Liquidez:** Chief of Staff comprueba que se puede comprar desde la wallet con liquidez
   suficiente (`volumen_24h_usd`). Si hace falta un puente a otra red, el ticket lo indica
   como paso previo y Miguel decide.

La familia *riesgo_oferta* no excluye ni limita: genera la ALERTA DE OFERTA de la sección 6.

**Riesgos que Miguel asume al incluirlos:** beta muy superior a BTC y SOL; ausencia de
señales de suelo propias; en HYPE, concentración en una sola plataforma, que es además la
fuente de su dato de funding y open interest; en PUMP, dependencia del ciclo de memecoins;
en SUI, competencia entre L1 y calendario de desbloqueos.

## 11. Fin de ciclo, límites de los agentes y cambios

### 11.1 Revisión obligatoria

Chief of Staff avisa y Miguel decide por escrito qué hacer con el capital restante cuando
ocurra lo primero de esto:

- La familia *confirmación* de BTC lleva **8 semanas seguidas** ACTIVA
  (`btc.resumen.confirmacion_semanas_seguidas_activa`, medida en cada cierre semanal) y RT1
  no se ha desbloqueado (el mercado se ha girado sin pasar por la zona de valor).
- Han pasado **52 semanas** desde la entrada en vigor.
- El capital de tramos se ha agotado.

Ningún agente decide el cierre del ciclo ni propone desplegar el capital por su cuenta.

### 11.2 Qué no pueden hacer los agentes

- Cambiar esta política, sus umbrales o sus porcentajes.
- Declarar una fase o un suelo con cifras que no estén en el archivo de señales. Si Toro u
  Oso lo hacen, Estrategia descarta ese argumento y lo anota.
- Saltarse el orden de las fases o desbloquear dos tramos en la misma semana.
- Decidir el reparto de un tramo entre activos, o emitir tickets para un activo no elegible.
- Iniciar el DCA sin la orden escrita de Miguel, o mantener o cancelar sus órdenes de otra bolsa.
- Ejecutar órdenes o acceder a wallets.

### 11.3 Cómo se cambia esta política

1. Miguel escribe el cambio, con el motivo, en el registro de abajo.
2. El cambio entra en vigor **7 días después** de escribirse.
3. Hasta entonces sigue vigente la versión anterior, y los agentes la citan por número.

El periodo de enfriamiento existe para evitar reescribir las reglas en mitad de una
capitulación, que es cuando más tentador resulta.

## 12. Valores confirmados al firmar

Miguel confirmó todos estos valores al firmar el 14-nov-2026.

| Valor | Confirmado | Sección |
|---|---|---|
| Caída desde máximo que cuenta en la valoración de BTC | 50 % | 3 |
| Suelo validado: antigüedad y rebote | 4 semanas y 15 % | 4.3 |
| Máximo de la cesta por tramo | Sin tope (decidido por Miguel el 14-nov) | 6 |
| *riesgo_oferta* en la cesta | Solo alerta en card y ticket (decidido el 14-nov) | 6 |
| Escalera de la cesta | −5 %, −10 %, −15 % | 7 |
| Parte al precio de referencia en RT3 | 50 % | 7 |
| Umbrales de P_final por fase | 45 / 55 / 65 % (antes 35 / 50 / 60; decidido el 14-nov) | 4.2 |
| Condiciones de precio que cuentan en la cesta | 1 de 3 (decidido el 14-nov) | 10 |
| DCA: parte del capital, duración y día | 15 %, 26 semanas, lunes | 9 |
| DCA: inicio | Lo propone Estrategia cada semana; lo decide Miguel (decidido el 14-nov) | 9 |
| Escenarios de ciclo: fecha de corte y horizonte | 28-mar-2027 y 26-sep-2027 (decidido el 14-nov) | 4.5 |
| Revisión de fin de ciclo | 8 semanas de confirmación sin RT1, o 52 semanas (confirmado el 14-nov) | 11.1 |

No cambian respecto a la v1.0: los porcentajes
RT1–RT4 (20 / 30 / 30 / 20), la validez de 14 días, la condición de pausa y el enfriamiento
de 7 días.

## 13. Registro de cambios

| Versión | Fecha | Cambio | Motivo | En vigor desde |
|---|---|---|---|---|
| 1.0 | 2 noviembre 2026 | Versión inicial escrita y firmada. | Sin la regla de familia, RT1 y RT3 no podían desbloquearse. | 9 noviembre 2026 |
| 1.1 | 14 noviembre 2026 | Elimina el reparto fijo por activo: una sola bolsa, SOL como destino por defecto y reparto decidido por Miguel en cada tramo, sin tope para la cesta (riesgo de oferta solo como alerta). Separa "definir el suelo" de "elegir destino": define P_final, las fases de suelo, el suelo de referencia validado y su invalidación. Sube los umbrales de P_final a 45 / 55 / 65 %. Añade los tres escenarios de ciclo (4.5). Corrige el doble conteo del realized price en BTC y añade una condición independiente. Distingue condición sin fuente de fuente caída. Redefine el retest de RT4 y aclara que RT4 puede abrirse sin RT3. Cuadra el capital (15 % DCA + 85 % tramos). DCA solo en SOL, con duración, día e inicio propuesto por el flujo y decidido por Miguel. Deja fuera del capital las órdenes límite de otra bolsa. Da destino a las mitades por incertidumbre. Escalera distinta para tramos de confirmación y para la cesta. En la cesta, las condiciones de precio cuentan como una sola. Añade revisión de fin de ciclo e incidente de custodia. La pausa cubre todos los activos. | Decisiones de Miguel del 13-nov (sin reparto fijo, que el flujo defina el suelo) y del 14-nov (cesta sin tope, inicio del DCA, órdenes de otra bolsa, fin de ciclo). Revisión de coherencia de la v1.0 contra `senales.py`. | 21 noviembre 2026 |

---

## Anexo A. Cambios que esta versión exige fuera de la política

La v1.1 no puede entrar en vigor hasta que el script publique lo que la política nombra.

**En `senales.py` (hecho en la v2.0.0 y la v2.0.1):**

1. Cada condición sin evaluar lleva `sin_dato_motivo` (`sin_fuente` o `fuente_caida`) y cada
   familia publica `con_fuente`, `activa` y `base_debil`.
2. BTC *valoración*: una sola condición para el realized price y nueva condición "caída desde
   el máximo ≥ 50 %". NUPL sale de *capitulación* (sigue publicado como dato). LTH-SOPR
   guarda su último valor (válido 7 días).
3. SOL *confirmación*: añade "RSI semanal saliendo de sobreventa"; "BTC en confirmación"
   pasa a exigir la familia ACTIVA.
4. Bloque `suelo` en BTC y SOL: mínimo, fecha, antigüedad, rebote máximo, `validado`,
   nivel de invalidación, `retest` e invalidaciones.
5. Cesta: en *valoracion_relativa* solo cuenta una de las tres condiciones de precio (v2.0.1).
6. `resolucion_ciclo` (tres escenarios), `frecuencia_historica_eventos` y
   `confirmacion_semanas_seguidas_activa`.
7. Umbrales nuevos en `UMBRALES`, incluidas las fechas de los escenarios.

**En los prompts:**

- Estrategia: publicar fase y suelo de referencia de BTC y SOL; marcar ALERTA DE OFERTA; línea semanal "DCA: INICIAR / ESPERAR"; definir P_final como
  `evento_8s`; listar elegibles sin proponer porcentajes; nueva regla de pesos de Brier; leer `activa` y `suelo`
  del archivo; combinar los escenarios de ciclo.
- Chief of Staff: bolsa única 15/85; comprobar elegibilidad (sin tope de cesta) y repetir la
  ALERTA DE OFERTA; anotar las órdenes de otra bolsa solo como información; DCA solo en SOL los
  lunes desde que Miguel lo ordene por escrito;
  avisos de fin de ciclo y de custodia; reemisión de escaleras caducadas.
- Toro y Oso: quitar la frase de que SUI, HYPE y PUMP son "solo informativos"; dar cada
  semana las probabilidades de los escenarios A, B y C para BTC y SOL.

---

*Este documento es un marco de proceso propio de Miguel, no una recomendación de
inversión ni asesoramiento financiero.*
