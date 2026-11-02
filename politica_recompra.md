# POLÍTICA DE RECOMPRA — BTC y SOL

- **Versión:** 1.0
- **Aprobada por:** Miguel, el ____2 de Noviembre del 2026________ (fecha)
- **Entrada en vigor:** 7 días después de la fecha de aprobación (regla de la sección 9)
- **Sustituye a:** v0.1 provisional, aprobada por chat el 30-oct-2026 sin documento escrito

Este documento manda sobre cualquier criterio de los agentes. Ningún agente puede
modificarlo ni interpretarlo de forma distinta a como está escrito. Solo Miguel lo cambia.

---

## 1. Objetivo y alcance

**Objetivo del sistema:** la posición de SOL vendida en el de-risk se reconstruye por tramos
durante el ciclo bajista, de forma que el valor total de lo recomprado, en USD y en
SOL-equivalente, acabe por encima de lo que valdría hoy aquella posición. La moneda en que
se recupere ese valor es secundaria. La medida de éxito la calcula Chief of Staff cada mes
(sección 7 de su prompt); la cantidad de referencia está en su ledger, no en este
documento público.

- Aplica a cinco activos, en contado y con firma manual:
  - **Activos señal: BTC y SOL.** Tienen familias de señales y probabilidades de Toro y Oso,
    y sus tramos se desbloquean por sus propias condiciones.
  - **Activos cesta: HYPE, SUI y PUMP.** No tienen señales de valoración propias: sus tramos
    siguen a los de SOL (sección 10).
- Esta política es válida cuando lleva fecha de aprobación y ha entrado en vigor. Los
  importes no figuran aquí: Chief of Staff los registra en su ledger privado el día de
  entrada en vigor; hasta que lo haga, Estrategia puede emitir cards pero Chief of Staff no
  emite tickets.
- Ningún agente ejecuta operaciones ni accede a wallets. Las órdenes las firma Miguel.

## 2. Capital

**Este documento es público: no contiene importes.** El capital se define por referencia y
los importes viven solo en el ledger privado de Chief of Staff.

- **Capital de recompra del ciclo** = el USDC de la wallet (en Jupiter Lend y líquido) el día de entrada en vigor
de esta política, menos la reserva mínima intocable (10 % del patrimonio). Chief of
  Staff lo registra ese día como "capital inicial" y a partir de ahí descuenta lo ejecutado.
- **Reparto por activo** (porcentaje del capital de recompra):

| Activo | % del capital | Tipo |
|---|---|---|
| SOL | 25 % | señal |
| BTC | 20 % | señal |
| HYPE | 20 % | cesta |
| SUI | 20 % | cesta |
| PUMP | 15 % | cesta, menor peso por mayor riesgo |

  Propuesta pendiente de confirmación de Miguel: ☐ confirmado ☐ cambia a: ______

- **DCA de fondo**: ____ % del capital de recompra a la semana (recomendado: el equivalente
  al 15 % del capital repartido en el ciclo), comprado con el mismo reparto por activo.
- El capital de recompra no incluye los holds de largo plazo (2Z) ni el capital de la fase de
  test del sistema de trading, que son bolsas separadas.

## 3. Cuándo una familia de señales cuenta como ACTIVA

Esta es la regla que faltaba. El archivo de señales publica, por familia, cuántas
condiciones se cumplen y cuántas son medibles. Las condiciones que salen `SIN DATO`
**no cuentan ni a favor ni en contra**.

> **Una familia está ACTIVA cuando el número de condiciones cumplidas es igual o mayor
> que `mínimo(2, condiciones medibles)`.**

En la práctica:

| Condiciones medibles | Cumplidas necesarias |
|---|---|
| 4 | 2 |
| 3 | 2 |
| 2 | 2 |
| 1 | 1 |
| 0 | La familia NO está activa, y se declara NO EVALUABLE |

El principio es que **nunca se desbloquea un tramo por una sola señal** cuando hay más
de una disponible. Si solo hay una medible, se acepta, pero Estrategia debe señalarlo
en la card como base débil.

**Evento de capitulación confirmado** (lo que pide RT2) significa que la familia
*capitulación* del activo está ACTIVA según la regla anterior.

**Limitación conocida:** la familia *capitulación* de SOL solo tiene hoy una condición
medible (TVL), porque no hay fuente gratuita de unstaking. Mientras siga así, RT2 de SOL
puede abrirse con una sola señal. Lo compensan las dos puertas que ya existen: P_final
≥ 50 % y que BTC tenga RT2 desbloqueado antes. Revisar cuando haya datos de staking.

## 4. Tramos de recompra

Los tramos se desbloquean **en orden**, como máximo uno nuevo por semana y por activo.
"No desbloquear nada" es el resultado esperado la mayoría de las semanas.

Las condiciones se evalúan **por activo**: la P_final y las familias son las del propio
activo (BTC con las de BTC, SOL con las de SOL). Para SOL se exige además que BTC tenga
ya ese mismo tramo desbloqueado.

| Tramo | % del capital del activo | Condiciones (todas a la vez) |
|---|---|---|
| **RT1** | 20 % | P_final del activo ≥ 35 % **y** su familia *valoración* ACTIVA |
| **RT2** | 30 % | P_final del activo ≥ 50 % **y** su familia *capitulación* ACTIVA |
| **RT3** | 30 % | P_final del activo ≥ 60 % **y** su familia *confirmación* ACTIVA |
| **RT4** | 20 % | Retest del mínimo, **o** los tramos anteriores ejecutados y rebote > 25 % sin haber abierto RT3 |

Definiciones de RT4, con campos del archivo de señales:
- **Retest del mínimo**: un cierre semanal que queda a menos de un 3 % por encima de
  `ciclo.minimo_tras_maximo_usd`, o por debajo de él.
- **Rebote > 25 %**: `ciclo.rebote_desde_minimo_pct` mayor que 25, medido desde ese mismo
  mínimo registrado.

Reglas fijas:
- **Orden de entrada: BTC → SOL → cesta.** SOL solo puede desbloquear un tramo si BTC ya
  tiene ese mismo tramo desbloqueado. HYPE, SUI y PUMP desbloquean su parte de un tramo en
  el momento en que SOL desbloquea ese tramo (sección 10): nunca antes.
- Si el desacuerdo entre Bull y Bear supera los 40 puntos, se marca INCERTIDUMBRE ALTA
  y solo se desbloquea la mitad del tramo.
- Las familias *derivados* y *sentimiento* no desbloquean tramos por sí solas. Sirven
  como contexto en la card.
- **Interacción con el de-risk:** mientras el plan de de-risk esté reduciendo un activo,
  no se desbloquean tramos de recompra de ese activo. Vender y recomprar lo mismo a la
  vez no es una estrategia, es un error de coordinación.

## 5. Escalera de órdenes

Cada tramo desbloqueado se reparte en 3 o 4 órdenes límite escalonadas, en porcentajes
sobre el precio de referencia del archivo de señales: `resumen.precio_referencia_usd` para
BTC y SOL, y `otras_monedas.<activo>.tendencia.precio_referencia_usd` para HYPE, SUI y
PUMP (precio de perpetuo: Chief of Staff lo contrasta con el spot del mercado donde se
compre).

- Escalera por defecto: **−3 %, −6 %, −10 %**
- Validez: **14 días**. Lo que no se ejecute se cancela y el tramo sigue abierto.
- No hay stop loss. El control de riesgo es el tamaño máximo y la condición de pausa.

## 6. Condición de pausa

Es **una sola condición del sistema**, calculada sobre BTC, y congela RT3 y RT4 en los
dos activos.

- **Se activa** si BTC cierra una semana por debajo del *realized price* con una caída
  semanal superior al 15 %.
- **Se levanta** tras dos cierres semanales consecutivos por encima del *realized price*.
- Si `pausa_sistema_activa` llega como `SIN DATO`, no se desbloquean RT3 ni RT4 esa
  semana, en ningún activo.

## 7. DCA de fondo

- Importe fijo semanal, independiente de cualquier señal: el porcentaje del capital de
  recompra fijado en la sección 2, con el mismo reparto por activo. El importe en USDC lo
  calcula y registra Chief of Staff en privado.
- Día de compra: ____________ (día de la semana)
- **No se modifica según la opinión de mercado de la semana.** Esa opinión es
  precisamente lo que está delegado en Bull y Bear para poder puntuarla.
- Se suspende solo si Miguel lo decide por escrito, no por una lectura de los agentes.

## 8. Qué no pueden hacer los agentes

- Cambiar esta política, sus umbrales o sus porcentajes.
- Desbloquear un tramo sin el archivo de señales del día o con estado `FALLO`.
- Usar cifras que no estén en el archivo de señales. Si Bull o Bear lo hacen,
  Estrategia descarta ese argumento y lo anota.
- Saltarse el orden de los tramos o abrir dos en la misma semana.
- Ejecutar órdenes o acceder a wallets.

## 9. Cómo se cambia esta política

1. Miguel escribe el cambio, con el motivo, en el registro de abajo.
2. El cambio entra en vigor **7 días después** de escribirse.
3. Hasta entonces sigue vigente la versión anterior, y los agentes la citan por número.

El periodo de enfriamiento existe para evitar reescribir las reglas en mitad de una
capitulación, que es cuando más tentador resulta.

## 10. Activos cesta: HYPE, SUI y PUMP

Entran en la recompra con el reparto de la sección 2. No tienen las señales on-chain de BTC
(realized price, MVRV, NUPL) ni probabilidades de Toro y Oso, así que **no tienen desbloqueo
propio: su tramo RT_n se abre cuando SOL abre RT_n**. Pero sí tienen datos propios en el
archivo de señales (bloque `otras_monedas`), y esos datos ponen condiciones:

**Qué publica el archivo para cada uno:** precio y tendencia, ciclo desde su listado, ratio
frente a BTC con su percentil de 52 semanas, TVL (SUI y HYPE), comisiones e ingresos,
capitalización, FDV y oferta circulante, funding y open interest, y tres familias de
hechos: *valoracion_relativa*, *actividad* y *riesgo_oferta*. Las fuentes y sus límites están
en el propio archivo (`*_fuente`); el precio es de perpetuo, con contraste spot cuando existe.

**Condiciones para que la parte de un activo cesta entre en un tramo:**
1. **SOL ha desbloqueado ese mismo tramo** esta semana o antes.
2. **Techo relativo:** `techo_ratio_btc.supera` es false, es decir, su ratio frente a BTC no
   está por encima del percentil 80 de 52 semanas. Si lo supera, está caro respecto a BTC y
   su parte se **aplaza** hasta que baje del techo.
3. **Para RT1 y RT2** (los tramos de "comprar barato"): su familia *valoracion_relativa* debe
   estar ACTIVA según la regla de la sección 3. RT3 y RT4 (los de confirmación y reserva)
   no lo exigen.
4. **Veto estructural:** si OSO documenta un evento estructural confirmado (hackeo, parada de
   red, insolvencia o incidente grave de plataforma, deslistado), su parte se aplaza y la
   decide Miguel.
5. **Presión de oferta:** si la familia *riesgo_oferta* cumple (FDV más del doble de la
   capitalización), la parte de ese activo en el tramo se reduce a la **mitad**; el resto
   queda para el tramo siguiente.
El capital aplazado o reducido **no se reasigna** a otro activo.

**Riesgos que Miguel asume al incluirlos**, por escrito para que consten: beta muy superior a
BTC y SOL; en HYPE, concentración en una sola plataforma, que es además la fuente de su dato
de funding y open interest; en PUMP, dependencia del ciclo de memecoins; en SUI, competencia
entre L1 y calendario de desbloqueos (que la familia *riesgo_oferta* intenta medir).

Toro y Oso los analizan con sus familias en la sección de otras monedas; Estrategia aplica
estas cinco condiciones en la card y escribe el resultado por activo; Chief of Staff comprueba
antes de cada ticket que el activo se puede comprar desde la wallet con liquidez suficiente
(el archivo trae `volumen_24h_usd`); si hace falta un puente a otra red, el ticket lo indica
como paso previo y Miguel decide.

## 11. Registro de cambios

| Versión | Fecha | Cambio | Motivo | En vigor desde |
|---|---|---|---|---|
| 1.0 | ___2 noviembre 2026_______ | Versión inicial escrita y firmada. Define la regla de familia ACTIVA, que faltaba en la v0.1; define el retest y el rebote de RT4; escribe la interacción con el de-risk; define el objetivo del sistema (superar el valor de la posición de SOL vendida); incorpora HYPE, SUI y PUMP como activos cesta que siguen al tramo de SOL, con reparto por activo, techo relativo frente a BTC, familia de valoración propia para RT1–RT2, veto estructural y reducción por presión de oferta; el capital pasa a definirse por referencia para no publicar importes. No cambia los umbrales de P_final ni los porcentajes RT1–RT4 de la v0.1. | Sin la regla de familia, RT1 y RT3 no podían desbloquearse nunca; decisión de Miguel del 2-nov sobre la cesta y el objetivo. | Firma + 7 días |

---

*Este documento es un marco de proceso propio de Miguel, no una recomendación de
inversión ni asesoramiento financiero.*

