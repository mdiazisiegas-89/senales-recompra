# Señales 2026-11-14

- Snapshot: `244aeab9c05d`
- Estado: **OK**
- Generado: 2026-11-14T12:41:06Z
- Válido hasta: 2026-11-16T00:41:06Z
- Aviso: Precio realizado tomado de Coin Metrics CapMVRVCur. Antes fallaron: Coin Metrics CapRealUSD: HTTPError: 403 Client Error: Forbidden for url: https://community-api.coinmetrics.io/v4/timeseries/as

## Cambios desde el archivo anterior

- btc.valoracion.precio bajo realized price (mismo hecho que MVRV Z < 0 y NUPL < 0): SIN DATO → False
- btc.valoracion.caída desde el máximo de al menos 50 % (último cierre semanal): SIN DATO → False
- btc.valoracion.ACTIVA: SIN DATO → False
- btc.capitulacion.ACTIVA: SIN DATO → False
- btc.derivados.ACTIVA: SIN DATO → False
- btc.sentimiento.ACTIVA: SIN DATO → False
- btc.confirmacion.ACTIVA: SIN DATO → False
- btc.suelo.validado: SIN DATO → True
- btc.suelo.fecha_minimo: SIN DATO → 2026-06-28
- sol.valoracion.ACTIVA: SIN DATO → False
- sol.capitulacion.ACTIVA: SIN DATO → False
- sol.derivados.ACTIVA: SIN DATO → False
- sol.sentimiento.ACTIVA: SIN DATO → False
- sol.confirmacion.RSI semanal saliendo de sobreventa: SIN DATO → False
- sol.confirmacion.familia confirmación de BTC ACTIVA: SIN DATO → False
- sol.confirmacion.ACTIVA: SIN DATO → False
- sol.suelo.validado: SIN DATO → True
- sol.suelo.fecha_minimo: SIN DATO → 2026-06-07

## Cambios en los últimos 7 días

- btc.valoracion.precio bajo realized price (mismo hecho que MVRV Z < 0 y NUPL < 0): SIN DATO → False
- btc.valoracion.precio cerca o bajo la media de 200 semanas: False → True
- btc.valoracion.caída desde el máximo de al menos 50 % (último cierre semanal): SIN DATO → False
- btc.valoracion.ACTIVA: SIN DATO → False
- btc.capitulacion.LTH-SOPR < 1: False → True
- btc.capitulacion.ACTIVA: SIN DATO → False
- btc.derivados.ACTIVA: SIN DATO → False
- btc.sentimiento.ACTIVA: SIN DATO → False
- btc.confirmacion.ACTIVA: SIN DATO → False
- btc.suelo.validado: SIN DATO → True
- btc.suelo.fecha_minimo: SIN DATO → 2026-06-28
- sol.valoracion.ACTIVA: SIN DATO → False
- sol.capitulacion.ACTIVA: SIN DATO → False
- sol.derivados.ACTIVA: SIN DATO → False
- sol.sentimiento.ACTIVA: SIN DATO → False
- sol.confirmacion.cierre semanal sobre la media de 20 semanas: True → False
- sol.confirmacion.RSI semanal saliendo de sobreventa: SIN DATO → False
- sol.confirmacion.familia confirmación de BTC ACTIVA: SIN DATO → False
- sol.confirmacion.ACTIVA: SIN DATO → False
- sol.suelo.validado: SIN DATO → True
- sol.suelo.fecha_minimo: SIN DATO → 2026-06-07

## BTC

### Resumen para Estrategia

| Dato | Valor |
|---|---|
| precio_referencia_usd | 68096.31 |
| precio_referencia_fecha | 2026-11-13 |
| dato_diario_al_dia | True |
| cierre_semanal_usd | 74967.72 |
| cierre_semanal_fecha | 2026-11-08 |
| cierre_semanal_al_dia | True |
| evento_4s_umbral_usd | 67470.95 |
| pausa_sistema_activa | False |
| semanas_desde_maximo | 57 |
| caida_desde_maximo_pct | -39.31 |
| rebote_desde_minimo_pct | 25.96 |
| confirmacion_semanas_seguidas_activa | 0 |

### Tendencia

| Dato | Valor |
|---|---|
| fecha_ultimo_dato | 2026-11-13 |
| fecha_ultimo_cierre_semanal | 2026-11-08 |
| precio_referencia_usd | 68096.31 |
| cierre_semanal_usd | 74967.72 |
| var_semanal_pct | -4.05 |
| var_7d_pct | -10.19 |
| var_30d_pct | -16.44 |
| sma50d | 80537.78 |
| sma200d | 73030.6 |
| sma50d_sobre_sma200d | True |
| sma20w | 73559.13 |
| ema21w | 76530.67 |
| sma200w | 67745.52 |
| cierre_sobre_sma20w | True |
| rsi14_diario | 23.76 |
| rsi14_semanal | 48.17 |
| macd_semanal | 1631.05 |
| macd_semanal_senal | 971.47 |
| ultimo_cierre_mensual_fecha | 2026-10-31 |
| ultimo_cierre_mensual_usd | 77401.02 |
| var_mensual_pct | -7.39 |
| ultimo_cierre_anual_fecha | 2025-12-31 |
| ultimo_cierre_anual_usd | 87516.98 |
| var_anual_pct | -6.29 |
| precio_kraken_contraste_usd | 67111.6 |

ultimos_30_cierres_semanales: 2026-04-19 = 73905.2, 2026-04-26 = 78538.77, 2026-05-03 = 78649.17, 2026-05-10 = 82256.78, 2026-05-17 = 77497.7, 2026-05-24 = 76950.99, 2026-05-31 = 73599.56, 2026-06-07 = 63158.25, 2026-06-14 = 65615.33, 2026-06-21 = 63365.44, 2026-06-28 = 59516.67, 2026-07-05 = 63619.88, 2026-07-12 = 63752.27, 2026-07-19 = 64653.05, 2026-07-26 = 65328.79, 2026-08-02 = 63445.68, 2026-08-09 = 64864.93, 2026-08-16 = 62818.41, 2026-08-23 = 77593.03, 2026-08-30 = 77689.19, 2026-09-06 = 80319.97, 2026-09-13 = 76759.26, 2026-09-20 = 81194.74, 2026-09-27 = 84392.47, 2026-10-04 = 86520.8, 2026-10-11 = 83636.61, 2026-10-18 = 81935.17, 2026-10-25 = 80038.91, 2026-11-01 = 78135.08, 2026-11-08 = 74967.72

ultimos_24_cierres_mensuales: 2024-11-30 = 96463.62, 2024-12-31 = 93389.73, 2025-01-31 = 102263.04, 2025-02-28 = 84243.78, 2025-03-31 = 82461.45, 2025-04-30 = 94236.73, 2025-05-31 = 104708.96, 2025-06-30 = 107153.1, 2025-07-31 = 115848.34, 2025-08-31 = 108316.45, 2025-09-30 = 113971.74, 2025-10-31 = 109554.24, 2025-11-30 = 90607.7, 2025-12-31 = 87516.98, 2026-01-31 = 78702.39, 2026-02-28 = 66965.64, 2026-03-31 = 68214.87, 2026-04-30 = 76299.62, 2026-05-31 = 73599.56, 2026-06-30 = 58525.08, 2026-07-31 = 62875.18, 2026-08-31 = 78533.89, 2026-09-30 = 83579.67, 2026-10-31 = 77401.02

ultimos_10_cierres_anuales: 2016-12-31 = 968.97, 2017-12-31 = 13921.48, 2018-12-31 = 3687.2, 2019-12-31 = 7167.4, 2020-12-31 = 29022.67, 2021-12-31 = 46355.12, 2022-12-31 = 16524.22, 2023-12-31 = 42217.16, 2024-12-31 = 93389.73, 2025-12-31 = 87516.98

### Ciclo

| Dato | Valor |
|---|---|
| maximo_cierre_semanal_usd | 123523.77 |
| fecha_maximo | 2025-10-05 |
| semanas_desde_maximo | 57 |
| minimo_tras_maximo_usd | 59516.67 |
| fecha_minimo | 2026-06-28 |
| caida_desde_maximo_pct | -39.31 |
| rebote_desde_minimo_pct | 25.96 |

### Suelo

| Dato | Valor |
|---|---|
| minimo_usd | 59516.67 |
| fecha_minimo | 2026-06-28 |
| semanas_antiguedad | 19 |
| rebote_maximo_desde_minimo_pct | 45.37 |
| validado | True |
| nivel_invalidacion_usd | 59516.67 |
| ultimo_cierre_sobre_suelo_pct | 25.96 |
| retest | False |
| invalidado_en_ultimo_cierre | False |
| ultima_invalidacion_fecha | 2026-06-07 |
| suelo_perdido_usd | 65733.52 |

### Onchain

| Dato | Valor |
|---|---|
| realized_price_usd | 53762.42 |
| realized_price_fecha | 2026-11-13 |
| precio_bajo_realized | False |
| mvrv | 1.267 |
| mvrv_z | 0.464 |
| nupl | 0.210494 |
| puell | 0.707379 |
| hash_ribbons_30_bajo_60 | False |
| hash_ribbons_dias_en_estado | 79 |
| lth_sopr | 0.9613 |
| lth_sopr_fecha | 2026-11-07 |
| realized_fuente | Coin Metrics CapMVRVCur |

### Derivados

| Dato | Valor |
|---|---|
| funding_medio_7d_pct_hora | 0.001017 |
| funding_medio_7d_anualizado_pct | 8.9 |
| funding_medio_14d_pct_hora | 0.001094 |
| horas_funding_negativo_7d | 9 |
| open_interest_usd | 2567058886.0 |
| volumen_24h_usd | 3728182223.0 |
| oi_var_7d_pct | -19.06 |
| oi_var_30d_pct | SIN DATO |
| fuente | Hyperliquid (un solo mercado, no agregado) |

### Fundamentales

| Dato | Valor |
|---|---|
| comisiones_media_7d_usd | 221387.0 |
| comisiones_var_vs_30d_previos_pct | 6.0 |
| comisiones_fuente | DefiLlama red bitcoin |
| mcap_usd | 1350951837628.0 |
| fdv_usd | 1350954793205.0 |
| oferta_circulante | 20111771.0 |
| fdv_sobre_mcap | 1.0 |
| mcap_var_30d_pct | SIN DATO |
| valoracion_base | comisiones de red (sin emisión) |
| mcap_sobre_base_anualizada | 16718.4 |
| mcap_sobre_base_percentil_365d | 14.3 |
| mcap_sobre_base_min_365d | 12124.7 |
| mcap_sobre_base_max_365d | 25376.0 |
| mercado_fuente | CoinGecko |
| nota | Informativo, no entra en ninguna familia: a los mineros les paga sobre todo la emisión. La métrica de valoración de BTC es el MVRV (sección onchain). |

### Familia valoracion: no activa · 1 cumplidas, 3 con fuente (3 en total)

- precio bajo realized price (mismo hecho que MVRV Z < 0 y NUPL < 0): no cumple
- precio cerca o bajo la media de 200 semanas: cumple
- caída desde el máximo de al menos 50 % (último cierre semanal): no cumple

### Familia capitulacion: no activa · 1 cumplidas, 3 con fuente (3 en total)

- LTH-SOPR < 1: cumple
- Puell < 0,5: no cumple
- hash ribbons en capitulación: no cumple

### Familia derivados: no activa · 0 cumplidas, 2 con fuente (3 en total)

- funding medio de 7 días negativo: no cumple
- open interest desplomado en 30 días: FUENTE CAÍDA (cuenta como no cumple)
- grandes liquidaciones de largos: SIN FUENTE (no cuenta)

### Familia sentimiento: no activa · 0 cumplidas, 1 con fuente (1 en total)

- Fear & Greed en miedo extremo 14 días o más: no cumple

### Familia confirmacion: no activa · 1 cumplidas, 3 con fuente (3 en total)

- cierre semanal sobre la media de 20 semanas: cumple
- RSI semanal saliendo de sobreventa: no cumple
- hash ribbons recuperadas en los últimos 30 días: no cumple

### Frecuencia histórica de los eventos (desde 2010-07-18)

- evento_4s: ocurrió el 69.6 % de 848 semanas resueltas
- evento_8s: ocurrió el 56.7 % de 830 semanas resueltas

### Resolución del evento de ciclo

| Semana | Mínimo de referencia | A | B | C |
|---|---|---|---|---|
| 2026-11-08 | 59516.67 | pendiente | pendiente | pendiente |

### Resolución de eventos (últimas 30 semanas)

| Cierre | USD | Evento 4 s | Evento 8 s |
|---|---|---|---|
| 2026-04-19 | 73905.2 | True | False |
| 2026-04-26 | 78538.77 | True | False |
| 2026-05-03 | 78649.17 | True | True |
| 2026-05-10 | 82256.78 | False | True |
| 2026-05-17 | 77497.7 | False | pendiente |
| 2026-05-24 | 76950.99 | False | pendiente |
| 2026-05-31 | 73599.56 | False | pendiente |
| 2026-06-07 | 63158.25 | True | pendiente |
| 2026-06-14 | 65615.33 | True | pendiente |
| 2026-06-21 | 63365.44 | True | pendiente |
| 2026-06-28 | 59516.67 | True | pendiente |
| 2026-07-05 | 63619.88 | True | pendiente |
| 2026-07-12 | 63752.27 | True | pendiente |
| 2026-07-19 | 64653.05 | True | pendiente |
| 2026-07-26 | 65328.79 | True | pendiente |
| 2026-08-02 | 63445.68 | True | pendiente |
| 2026-08-09 | 64864.93 | True | pendiente |
| 2026-08-16 | 62818.41 | True | False |
| 2026-08-23 | 77593.03 | True | False |
| 2026-08-30 | 77689.19 | True | False |
| 2026-09-06 | 80319.97 | True | False |
| 2026-09-13 | 76759.26 | True | pendiente |
| 2026-09-20 | 81194.74 | True | pendiente |
| 2026-09-27 | 84392.47 | True | pendiente |
| 2026-10-04 | 86520.8 | True | pendiente |
| 2026-10-11 | 83636.61 | False | pendiente |
| 2026-10-18 | 81935.17 | pendiente | pendiente |
| 2026-10-25 | 80038.91 | pendiente | pendiente |
| 2026-11-01 | 78135.08 | pendiente | pendiente |
| 2026-11-08 | 74967.72 | pendiente | pendiente |

## SOL

### Resumen para Estrategia

| Dato | Valor |
|---|---|
| precio_referencia_usd | 77.84 |
| precio_referencia_fecha | 2026-11-13 |
| dato_diario_al_dia | True |
| cierre_semanal_usd | 86.91 |
| cierre_semanal_fecha | 2026-11-08 |
| cierre_semanal_al_dia | True |
| evento_4s_umbral_usd | 78.22 |
| pausa_sistema_activa | False |
| semanas_desde_maximo | 102 |
| caida_desde_maximo_pct | -65.72 |
| rebote_desde_minimo_pct | 31.28 |

### Tendencia

| Dato | Valor |
|---|---|
| fecha_ultimo_dato | 2026-11-13 |
| fecha_ultimo_cierre_semanal | 2026-11-08 |
| precio_referencia_usd | 77.84 |
| cierre_semanal_usd | 86.91 |
| var_semanal_pct | -7.79 |
| var_7d_pct | -13.58 |
| var_30d_pct | -25.3 |
| sma50d | 103.84 |
| sma200d | 88.89 |
| sma50d_sobre_sma200d | True |
| sma20w | 93.1 |
| ema21w | 96.88 |
| sma200w | 113.62 |
| cierre_sobre_sma20w | False |
| rsi14_diario | 18.92 |
| rsi14_semanal | 43.92 |
| macd_semanal | 1.82 |
| macd_semanal_senal | 1.46 |
| ultimo_cierre_mensual_fecha | 2026-10-31 |
| ultimo_cierre_mensual_usd | 95.29 |
| var_mensual_pct | -19.3 |
| ultimo_cierre_anual_fecha | 2025-12-31 |
| ultimo_cierre_anual_usd | 124.58 |
| var_anual_pct | -34.21 |
| precio_kraken_contraste_usd | 75.65 |

ultimos_30_cierres_semanales: 2026-04-19 = 83.57, 2026-04-26 = 86.9, 2026-05-03 = 84.04, 2026-05-10 = 96.45, 2026-05-17 = 85.26, 2026-05-24 = 85.19, 2026-05-31 = 82.2, 2026-06-07 = 66.2, 2026-06-14 = 70.85, 2026-06-21 = 72.54, 2026-06-28 = 71.19, 2026-07-05 = 81.56, 2026-07-12 = 76.76, 2026-07-19 = 76.29, 2026-07-26 = 76.63, 2026-08-02 = 73.48, 2026-08-09 = 76.34, 2026-08-16 = 74.5, 2026-08-23 = 95.37, 2026-08-30 = 101.89, 2026-09-06 = 106.49, 2026-09-13 = 99.48, 2026-09-20 = 111.0, 2026-09-27 = 121.91, 2026-10-04 = 121.63, 2026-10-11 = 111.15, 2026-10-18 = 103.94, 2026-10-25 = 101.14, 2026-11-01 = 94.26, 2026-11-08 = 86.91

ultimos_24_cierres_mensuales: 2024-11-30 = 238.17, 2024-12-31 = 189.36, 2025-01-31 = 231.1, 2025-02-28 = 147.72, 2025-03-31 = 124.99, 2025-04-30 = 147.76, 2025-05-31 = 156.77, 2025-06-30 = 155.13, 2025-07-31 = 172.34, 2025-08-31 = 201.43, 2025-09-30 = 208.58, 2025-10-31 = 187.36, 2025-11-30 = 135.07, 2025-12-31 = 124.58, 2026-01-31 = 105.31, 2026-02-28 = 84.3, 2026-03-31 = 83.0, 2026-04-30 = 82.99, 2026-05-31 = 82.2, 2026-06-30 = 73.47, 2026-07-31 = 72.81, 2026-08-31 = 103.03, 2026-09-30 = 118.08, 2026-10-31 = 95.29

ultimos_10_cierres_anuales: 2020-12-31 = 1.51, 2021-12-31 = 170.53, 2022-12-31 = 9.96, 2023-12-31 = 101.14, 2024-12-31 = 189.36, 2025-12-31 = 124.58

### Ciclo

| Dato | Valor |
|---|---|
| maximo_cierre_semanal_usd | 253.53 |
| fecha_maximo | 2024-11-24 |
| semanas_desde_maximo | 102 |
| minimo_tras_maximo_usd | 66.2 |
| fecha_minimo | 2026-06-07 |
| caida_desde_maximo_pct | -65.72 |
| rebote_desde_minimo_pct | 31.28 |

### Suelo

| Dato | Valor |
|---|---|
| minimo_usd | 66.2 |
| fecha_minimo | 2026-06-07 |
| semanas_antiguedad | 22 |
| rebote_maximo_desde_minimo_pct | 84.15 |
| validado | True |
| nivel_invalidacion_usd | 66.2 |
| ultimo_cierre_sobre_suelo_pct | 31.28 |
| retest | False |
| invalidado_en_ultimo_cierre | False |
| ultima_invalidacion_fecha | 2026-06-07 |
| suelo_perdido_usd | 81.33 |

### Derivados

| Dato | Valor |
|---|---|
| funding_medio_7d_pct_hora | 0.000174 |
| funding_medio_7d_anualizado_pct | 1.5 |
| funding_medio_14d_pct_hora | 0.000517 |
| horas_funding_negativo_7d | 53 |
| open_interest_usd | 309826854.0 |
| volumen_24h_usd | 354065782.0 |
| oi_var_7d_pct | -38.61 |
| oi_var_30d_pct | SIN DATO |
| fuente | Hyperliquid (un solo mercado, no agregado) |

### Ratio_sol_btc

| Dato | Valor |
|---|---|
| ratio_sol_btc | 0.00114307869 |
| percentil_52s | 19.0 |
| minimo_52s | 0.00102131207 |
| maximo_52s | 0.00159251247 |

### Fundamentales

| Dato | Valor |
|---|---|
| tvl_usd | 4999238530.0 |
| tvl_fecha | 2026-11-13 |
| tvl_usd_var_90d_pct | 4.42 |
| tvl_en_sol_var_90d_pct | 1.0 |
| fees_media_7d_usd | 438324.0 |
| fees_var_vs_30d_previos_pct | -31.92 |
| fees_fuente | DefiLlama red solana |
| ingresos_red_media_7d_usd | 30249.0 |
| ingresos_red_var_vs_30d_previos_pct | -59.08 |
| ingresos_red_fuente | DefiLlama red solana |
| fees_apps_ecosistema_media_7d_usd | 8819090.0 |
| fees_apps_ecosistema_var_vs_30d_previos_pct | -26.13 |
| stablecoins_solana_usd | 14140939170.0 |
| stablecoins_solana_var_30d_pct | -6.36 |
| mcap_usd | 44820628718.0 |
| fdv_usd | 48304380125.0 |
| oferta_circulante | 591573846.0 |
| fdv_sobre_mcap | 1.08 |
| mcap_var_30d_pct | SIN DATO |
| valoracion_base | comisiones de red |
| mcap_sobre_base_anualizada | 280.1 |
| mcap_sobre_base_percentil_365d | 66.1 |
| mcap_sobre_base_min_365d | 138.3 |
| mcap_sobre_base_max_365d | 398.1 |
| mercado_fuente | CoinGecko |

### Familia valoracion: no activa · 1 cumplidas, 3 con fuente (3 en total)

- precio bajo la media de 200 semanas: cumple
- ratio SOL/BTC en mínimos del rango de 52 semanas: no cumple
- capitalización / comisiones de red en el 20 % más bajo de 12 meses: no cumple

### Familia capitulacion: no activa · 0 cumplidas, 1 con fuente (2 en total)

- TVL en USD cae y TVL en SOL estable: no cumple
- pico de unstaking: SIN FUENTE (no cuenta)

### Familia derivados: no activa · 0 cumplidas, 2 con fuente (3 en total)

- funding medio de 7 días negativo: no cumple
- open interest desplomado en 30 días: FUENTE CAÍDA (cuenta como no cumple)
- grandes liquidaciones de largos: SIN FUENTE (no cuenta)

### Familia sentimiento: no activa · 0 cumplidas, 1 con fuente (1 en total)

- Fear & Greed en miedo extremo 14 días o más: no cumple

### Familia confirmacion: no activa · 0 cumplidas, 3 con fuente (3 en total)

- cierre semanal sobre la media de 20 semanas: no cumple
- RSI semanal saliendo de sobreventa: no cumple
- familia confirmación de BTC ACTIVA: no cumple

### Frecuencia histórica de los eventos (desde 2020-04-12)

- evento_4s: ocurrió el 53.5 % de 342 semanas resueltas
- evento_8s: ocurrió el 43.8 % de 322 semanas resueltas

### Resolución del evento de ciclo

| Semana | Mínimo de referencia | A | B | C |
|---|---|---|---|---|
| 2026-11-08 | 66.2 | pendiente | pendiente | pendiente |

### Resolución de eventos (últimas 30 semanas)

| Cierre | USD | Evento 4 s | Evento 8 s |
|---|---|---|---|
| 2026-04-19 | 83.57 | True | True |
| 2026-04-26 | 86.9 | True | True |
| 2026-05-03 | 84.04 | True | True |
| 2026-05-10 | 96.45 | False | True |
| 2026-05-17 | 85.26 | False | pendiente |
| 2026-05-24 | 85.19 | False | pendiente |
| 2026-05-31 | 82.2 | False | pendiente |
| 2026-06-07 | 66.2 | True | pendiente |
| 2026-06-14 | 70.85 | True | pendiente |
| 2026-06-21 | 72.54 | True | pendiente |
| 2026-06-28 | 71.19 | True | pendiente |
| 2026-07-05 | 81.56 | True | pendiente |
| 2026-07-12 | 76.76 | True | pendiente |
| 2026-07-19 | 76.29 | True | pendiente |
| 2026-07-26 | 76.63 | True | pendiente |
| 2026-08-02 | 73.48 | True | pendiente |
| 2026-08-09 | 76.34 | True | pendiente |
| 2026-08-16 | 74.5 | True | False |
| 2026-08-23 | 95.37 | True | False |
| 2026-08-30 | 101.89 | True | False |
| 2026-09-06 | 106.49 | True | False |
| 2026-09-13 | 99.48 | True | pendiente |
| 2026-09-20 | 111.0 | True | pendiente |
| 2026-09-27 | 121.91 | False | pendiente |
| 2026-10-04 | 121.63 | False | pendiente |
| 2026-10-11 | 111.15 | False | pendiente |
| 2026-10-18 | 103.94 | False | pendiente |
| 2026-10-25 | 101.14 | False | pendiente |
| 2026-11-01 | 94.26 | pendiente | pendiente |
| 2026-11-08 | 86.91 | pendiente | pendiente |

### Pausa del sistema (calculada sobre BTC, aplica a BTC y SOL)

| Dato | Valor |
|---|---|
| activa | False |
| desde | SIN DATO |
| cierres_seguidos_sobre_realized | SIN DATO |
| ultimo_cierre_bajo_realized | False |

## Otras monedas

Activos cesta: sus tramos siguen a los de SOL según la política; aquí van sus hechos propios.

## SUI

Fuente de precio: Hyperliquid, perpetuo (no es precio spot). Datos desde 2023-05-03.

### SUI resumen

| Dato | Valor |
|---|---|
| precio_referencia_usd | 0.79569 |
| precio_referencia_fecha | 2026-11-13 |
| dato_diario_al_dia | True |
| cierre_semanal_usd | 0.82041 |
| cierre_semanal_fecha | 2026-11-08 |
| semanas_desde_maximo | 96 |
| caida_desde_maximo_pct | -84.37 |
| rebote_desde_minimo_pct | 22.29 |

Techo ratio/BTC: percentil 29.9 (umbral 80) → no supera

### SUI tendencia

| Dato | Valor |
|---|---|
| fecha_ultimo_dato | 2026-11-13 |
| fecha_ultimo_cierre_semanal | 2026-11-08 |
| precio_referencia_usd | 0.79569 |
| cierre_semanal_usd | 0.82041 |
| var_semanal_pct | -8.93 |
| var_7d_pct | -8.38 |
| var_30d_pct | -22.17 |
| sma50d | 1.0 |
| sma200d | 0.85881 |
| sma50d_sobre_sma200d | True |
| sma20w | 0.84551 |
| ema21w | 0.92414 |
| sma200w | SIN DATO |
| cierre_sobre_sma20w | False |
| rsi14_diario | 35.1 |
| rsi14_semanal | 44.91 |
| macd_semanal | -0.029339 |
| macd_semanal_senal | -0.059629 |
| ultimo_cierre_mensual_fecha | 2026-10-31 |
| ultimo_cierre_mensual_usd | 0.89897 |
| var_mensual_pct | -22.85 |
| ultimo_cierre_anual_fecha | 2025-12-31 |
| ultimo_cierre_anual_usd | 1.4 |
| var_anual_pct | -65.92 |
| precio_spot_contraste_usd | 0.769 |
| precio_spot_contraste_fuente | Kraken |

ultimos_30_cierres_semanales: 2026-04-19 = 0.9222, 2026-04-26 = 0.9449, 2026-05-03 = 0.91949, 2026-05-10 = 1.33, 2026-05-17 = 1.04, 2026-05-24 = 1.03, 2026-05-31 = 0.895, 2026-06-07 = 0.75876, 2026-06-14 = 0.80314, 2026-06-21 = 0.69321, 2026-06-28 = 0.68111, 2026-07-05 = 0.75645, 2026-07-12 = 0.73624, 2026-07-19 = 0.74977, 2026-07-26 = 0.72288, 2026-08-02 = 0.68937, 2026-08-09 = 0.68616, 2026-08-16 = 0.67086, 2026-08-23 = 0.85106, 2026-08-30 = 0.7116, 2026-09-06 = 0.81249, 2026-09-13 = 0.70156, 2026-09-20 = 0.89853, 2026-09-27 = 1.26, 2026-10-04 = 1.21, 2026-10-11 = 1.13, 2026-10-18 = 0.99663, 2026-10-25 = 0.91984, 2026-11-01 = 0.90083, 2026-11-08 = 0.82041

ultimos_24_cierres_mensuales: 2024-11-30 = 3.48, 2024-12-31 = 4.12, 2025-01-31 = 4.09, 2025-02-28 = 2.83, 2025-03-31 = 2.27, 2025-04-30 = 3.51, 2025-05-31 = 3.25, 2025-06-30 = 2.77, 2025-07-31 = 3.61, 2025-08-31 = 3.25, 2025-09-30 = 3.26, 2025-10-31 = 2.36, 2025-11-30 = 1.5, 2025-12-31 = 1.4, 2026-01-31 = 1.15, 2026-02-28 = 0.90317, 2026-03-31 = 0.87858, 2026-04-30 = 0.90773, 2026-05-31 = 0.895, 2026-06-30 = 0.69078, 2026-07-31 = 0.68156, 2026-08-31 = 0.72697, 2026-09-30 = 1.17, 2026-10-31 = 0.89897

ultimos_10_cierres_anuales: 2023-12-31 = 0.77657, 2024-12-31 = 4.12, 2025-12-31 = 1.4

### SUI ciclo

| Dato | Valor |
|---|---|
| maximo_cierre_semanal_usd | 5.25 |
| fecha_maximo | 2025-01-05 |
| semanas_desde_maximo | 96 |
| minimo_tras_maximo_usd | 0.67086 |
| fecha_minimo | 2026-08-16 |
| caida_desde_maximo_pct | -84.37 |
| rebote_desde_minimo_pct | 22.29 |

### SUI ratio_btc

| Dato | Valor |
|---|---|
| ratio_btc | 1.168477367897e-05 |
| percentil_52s | 29.9 |
| percentil_desde_listado | 9.7 |
| minimo_52s | 9.07291618781e-06 |
| maximo_52s | 2.034640133263e-05 |

### SUI fundamentales

| Dato | Valor |
|---|---|
| tvl_usd | 404810913.0 |
| tvl_fecha | 2026-11-13 |
| tvl_usd_var_90d_pct | -0.13 |
| tvl_nativo_var_90d_pct | -14.99 |
| tvl_fuente | DefiLlama Sui |
| fees_media_7d_usd | 2786.0 |
| fees_var_vs_30d_previos_pct | -30.96 |
| fees_fuente | DefiLlama red sui |
| ingresos_media_7d_usd | 31.0 |
| ingresos_var_vs_30d_previos_pct | -86.25 |
| ingresos_fuente | DefiLlama red sui |
| fees_apps_ecosistema_media_7d_usd | 109828.0 |
| fees_apps_ecosistema_var_vs_30d_previos_pct | -0.38 |
| mcap_usd | 3190984678.0 |
| fdv_usd | 7709473562.0 |
| oferta_circulante | 4139043544.0 |
| fdv_sobre_mcap | 2.42 |
| mcap_var_30d_pct | SIN DATO |
| valoracion_base | comisiones de red |
| mcap_sobre_base_anualizada | 3138.1 |
| mcap_sobre_base_percentil_365d | 80.7 |
| mcap_sobre_base_min_365d | 412.6 |
| mcap_sobre_base_max_365d | 5006.1 |
| mercado_fuente | CoinGecko |

### SUI derivados

| Dato | Valor |
|---|---|
| funding_medio_7d_pct_hora | 0.000551 |
| funding_medio_7d_anualizado_pct | 4.8 |
| funding_medio_14d_pct_hora | 0.000734 |
| horas_funding_negativo_7d | 37 |
| open_interest_usd | 20546019.0 |
| volumen_24h_usd | 9961686.0 |
| oi_var_7d_pct | -29.22 |
| oi_var_30d_pct | SIN DATO |
| fuente | Hyperliquid (un solo mercado, no agregado) |

### SUI familia valoracion_relativa: ACTIVA · 2 cumplidas, 4 con fuente (4 en total)

- ratio frente a BTC en el 20 % inferior de 52 semanas: no cumple
- precio bajo la media de 200 días: cumple
- caída desde su máximo de al menos 70 %: cumple
- capitalización / comisiones de red en el 20 % más bajo de 12 meses: no cumple

### SUI familia actividad: no activa · 0 cumplidas, 2 con fuente (2 en total)

- comisiones de red de 7 días no caen más del 20 % frente a los 30 anteriores: no cumple
- TVL en unidades nativas estable a 90 días: no cumple

### SUI familia riesgo_oferta: ACTIVA (BASE DÉBIL) · 1 cumplidas, 1 con fuente (1 en total)

- FDV / capitalización por encima de 2 (presión de desbloqueos): cumple

## HYPE

Fuente de precio: Hyperliquid, perpetuo (no es precio spot). Datos desde 2024-12-05.

### HYPE resumen

| Dato | Valor |
|---|---|
| precio_referencia_usd | 71.64 |
| precio_referencia_fecha | 2026-11-13 |
| dato_diario_al_dia | True |
| cierre_semanal_usd | 74.44 |
| cierre_semanal_fecha | 2026-11-08 |
| semanas_desde_maximo | 7 |
| caida_desde_maximo_pct | -20.59 |
| rebote_desde_minimo_pct | 0.0 |

Techo ratio/BTC: percentil 84.3 (umbral 80) → SUPERA

### HYPE tendencia

| Dato | Valor |
|---|---|
| fecha_ultimo_dato | 2026-11-13 |
| fecha_ultimo_cierre_semanal | 2026-11-08 |
| precio_referencia_usd | 71.64 |
| cierre_semanal_usd | 74.44 |
| var_semanal_pct | -15.25 |
| var_7d_pct | -8.72 |
| var_30d_pct | -11.32 |
| sma50d | 82.8 |
| sma200d | 68.92 |
| sma50d_sobre_sma200d | True |
| sma20w | 74.59 |
| ema21w | 74.05 |
| sma200w | SIN DATO |
| cierre_sobre_sma20w | False |
| rsi14_diario | 34.95 |
| rsi14_semanal | 52.25 |
| macd_semanal | 8.29 |
| macd_semanal_senal | 9.47 |
| ultimo_cierre_mensual_fecha | 2026-10-31 |
| ultimo_cierre_mensual_usd | 87.93 |
| var_mensual_pct | -3.31 |
| ultimo_cierre_anual_fecha | 2025-12-31 |
| ultimo_cierre_anual_usd | 25.45 |
| var_anual_pct | 5.77 |
| precio_spot_contraste_usd | 68.22 |
| precio_spot_contraste_fuente | Hyperliquid spot |

ultimos_30_cierres_semanales: 2026-04-19 = 40.69, 2026-04-26 = 42.46, 2026-05-03 = 41.55, 2026-05-10 = 43.01, 2026-05-17 = 45.69, 2026-05-24 = 62.74, 2026-05-31 = 72.05, 2026-06-07 = 59.75, 2026-06-14 = 63.92, 2026-06-21 = 66.9, 2026-06-28 = 61.4, 2026-07-05 = 71.33, 2026-07-12 = 67.29, 2026-07-19 = 61.11, 2026-07-26 = 59.59, 2026-08-02 = 52.53, 2026-08-09 = 53.83, 2026-08-16 = 57.1, 2026-08-23 = 82.37, 2026-08-30 = 79.99, 2026-09-06 = 87.94, 2026-09-13 = 77.26, 2026-09-20 = 93.75, 2026-09-27 = 91.72, 2026-10-04 = 90.57, 2026-10-11 = 86.65, 2026-10-18 = 78.81, 2026-10-25 = 76.22, 2026-11-01 = 87.84, 2026-11-08 = 74.44

ultimos_24_cierres_mensuales: 2024-12-31 = 24.06, 2025-01-31 = 26.92, 2025-02-28 = 19.94, 2025-03-31 = 13.01, 2025-04-30 = 20.03, 2025-05-31 = 32.7, 2025-06-30 = 39.57, 2025-07-31 = 40.83, 2025-08-31 = 44.28, 2025-09-30 = 45.25, 2025-10-31 = 43.7, 2025-11-30 = 31.95, 2025-12-31 = 25.45, 2026-01-31 = 30.98, 2026-02-28 = 31.2, 2026-03-31 = 36.59, 2026-04-30 = 39.69, 2026-05-31 = 72.05, 2026-06-30 = 65.01, 2026-07-31 = 52.5, 2026-08-31 = 84.17, 2026-09-30 = 90.94, 2026-10-31 = 87.93

ultimos_10_cierres_anuales: 2024-12-31 = 24.06, 2025-12-31 = 25.45

### HYPE ciclo

| Dato | Valor |
|---|---|
| maximo_cierre_semanal_usd | 93.75 |
| fecha_maximo | 2026-09-20 |
| semanas_desde_maximo | 7 |
| minimo_tras_maximo_usd | 74.44 |
| fecha_minimo | 2026-11-08 |
| caida_desde_maximo_pct | -20.59 |
| rebote_desde_minimo_pct | 0.0 |

### HYPE ratio_btc

| Dato | Valor |
|---|---|
| ratio_btc | 0.001052068715088 |
| percentil_52s | 84.3 |
| percentil_desde_listado | 92.0 |
| minimo_52s | 0.0002377472471846 |
| maximo_52s | 0.001166703118615 |

### HYPE fundamentales

| Dato | Valor |
|---|---|
| tvl_usd | 2358202440.0 |
| tvl_fecha | 2026-11-13 |
| tvl_usd_var_90d_pct | 96.03 |
| tvl_nativo_var_90d_pct | 55.62 |
| tvl_fuente | DefiLlama Hyperliquid L1 |
| fees_media_7d_usd | 2580736.0 |
| fees_var_vs_30d_previos_pct | -9.56 |
| fees_fuente | DefiLlama protocolo hyperliquid-perps |
| ingresos_media_7d_usd | 1976833.0 |
| ingresos_var_vs_30d_previos_pct | -11.27 |
| ingresos_fuente | DefiLlama protocolo hyperliquid-perps |
| mcap_usd | 16267714406.0 |
| fdv_usd | 64998227674.0 |
| oferta_circulante | 237730949.0 |
| fdv_sobre_mcap | 4.0 |
| mcap_var_30d_pct | SIN DATO |
| valoracion_base | ingresos del protocolo |
| mcap_sobre_base_anualizada | 22.5 |
| mcap_sobre_base_percentil_365d | 65.0 |
| mcap_sobre_base_min_365d | 6.0 |
| mcap_sobre_base_max_365d | 42.4 |
| mercado_fuente | CoinGecko |

### HYPE derivados

| Dato | Valor |
|---|---|
| funding_medio_7d_pct_hora | 0.000875 |
| funding_medio_7d_anualizado_pct | 7.7 |
| funding_medio_14d_pct_hora | 0.001321 |
| horas_funding_negativo_7d | 21 |
| open_interest_usd | 1457364527.0 |
| volumen_24h_usd | 699312805.0 |
| oi_var_7d_pct | -16.05 |
| oi_var_30d_pct | SIN DATO |
| fuente | Hyperliquid (un solo mercado, no agregado) |

### HYPE familia valoracion_relativa: no activa · 0 cumplidas, 4 con fuente (4 en total)

- ratio frente a BTC en el 20 % inferior de 52 semanas: no cumple
- precio bajo la media de 200 días: no cumple
- caída desde su máximo de al menos 70 %: no cumple
- capitalización / ingresos del protocolo anualizados por debajo de 20: no cumple

### HYPE familia actividad: ACTIVA · 2 cumplidas, 2 con fuente (2 en total)

- ingresos de 7 días no caen más del 20 % frente a los 30 anteriores: cumple
- TVL en unidades nativas estable a 90 días: cumple

### HYPE familia riesgo_oferta: ACTIVA (BASE DÉBIL) · 1 cumplidas, 1 con fuente (1 en total)

- FDV / capitalización por encima de 2 (presión de desbloqueos): cumple

## PUMP

Fuente de precio: Hyperliquid, perpetuo (no es precio spot). Datos desde 2025-07-10.

### PUMP resumen

| Dato | Valor |
|---|---|
| precio_referencia_usd | 0.003443 |
| precio_referencia_fecha | 2026-11-13 |
| dato_diario_al_dia | True |
| cierre_semanal_usd | 0.003526 |
| cierre_semanal_fecha | 2026-11-08 |
| semanas_desde_maximo | 60 |
| caida_desde_maximo_pct | -56.06 |
| rebote_desde_minimo_pct | 145.2 |

Techo ratio/BTC: percentil 81.9 (umbral 80) → SUPERA

### PUMP tendencia

| Dato | Valor |
|---|---|
| fecha_ultimo_dato | 2026-11-13 |
| fecha_ultimo_cierre_semanal | 2026-11-08 |
| precio_referencia_usd | 0.003443 |
| cierre_semanal_usd | 0.003526 |
| var_semanal_pct | -15.91 |
| var_7d_pct | -12.08 |
| var_30d_pct | -27.9 |
| sma50d | 0.0046923 |
| sma200d | 0.002983 |
| sma50d_sobre_sma200d | True |
| sma20w | 0.0035425 |
| ema21w | 0.0037249 |
| sma200w | SIN DATO |
| cierre_sobre_sma20w | False |
| rsi14_diario | 35.77 |
| rsi14_semanal | 48.85 |
| macd_semanal | 0.00056087 |
| macd_semanal_senal | 0.00058306 |
| ultimo_cierre_mensual_fecha | 2026-10-31 |
| ultimo_cierre_mensual_usd | 0.004205 |
| var_mensual_pct | -29.14 |
| ultimo_cierre_anual_fecha | 2025-12-31 |
| ultimo_cierre_anual_usd | 0.001914 |
| var_anual_pct | SIN DATO |
| precio_spot_contraste_usd | 0.003257 |
| precio_spot_contraste_fuente | Kraken |

ultimos_30_cierres_semanales: 2026-04-19 = 0.001772, 2026-04-26 = 0.001761, 2026-05-03 = 0.001799, 2026-05-10 = 0.002192, 2026-05-17 = 0.001709, 2026-05-24 = 0.001737, 2026-05-31 = 0.0018, 2026-06-07 = 0.001527, 2026-06-14 = 0.001575, 2026-06-21 = 0.001465, 2026-06-28 = 0.001438, 2026-07-05 = 0.001631, 2026-07-12 = 0.001462, 2026-07-19 = 0.002001, 2026-07-26 = 0.002018, 2026-08-02 = 0.002086, 2026-08-09 = 0.002675, 2026-08-16 = 0.00267, 2026-08-23 = 0.005231, 2026-08-30 = 0.004474, 2026-09-06 = 0.004025, 2026-09-13 = 0.00347, 2026-09-20 = 0.004232, 2026-09-27 = 0.005164, 2026-10-04 = 0.006526, 2026-10-11 = 0.005634, 2026-10-18 = 0.004164, 2026-10-25 = 0.004231, 2026-11-01 = 0.004193, 2026-11-08 = 0.003526

ultimos_24_cierres_mensuales: 2025-07-31 = 0.002507, 2025-08-31 = 0.003366, 2025-09-30 = 0.005952, 2025-10-31 = 0.004613, 2025-11-30 = 0.002944, 2025-12-31 = 0.001914, 2026-01-31 = 0.002694, 2026-02-28 = 0.001923, 2026-03-31 = 0.001676, 2026-04-30 = 0.001776, 2026-05-31 = 0.0018, 2026-06-30 = 0.001416, 2026-07-31 = 0.002071, 2026-08-31 = 0.004457, 2026-09-30 = 0.005934, 2026-10-31 = 0.004205

ultimos_10_cierres_anuales: 2025-12-31 = 0.001914

### PUMP ciclo

| Dato | Valor |
|---|---|
| maximo_cierre_semanal_usd | 0.008024 |
| fecha_maximo | 2025-09-14 |
| semanas_desde_maximo | 60 |
| minimo_tras_maximo_usd | 0.001438 |
| fecha_minimo | 2026-06-28 |
| caida_desde_maximo_pct | -56.06 |
| rebote_desde_minimo_pct | 145.2 |

### PUMP ratio_btc

| Dato | Valor |
|---|---|
| ratio_btc | 5.056074071143e-08 |
| percentil_52s | 81.9 |
| percentil_desde_listado | 81.7 |
| minimo_52s | 1.981320105183e-08 |
| maximo_52s | 7.542694925441e-08 |

### PUMP fundamentales

| Dato | Valor |
|---|---|
| fees_media_7d_usd | 1228475.0 |
| fees_var_vs_30d_previos_pct | -33.04 |
| fees_fuente | DefiLlama protocolo pump.fun |
| ingresos_media_7d_usd | 855463.0 |
| ingresos_var_vs_30d_previos_pct | -34.58 |
| ingresos_fuente | DefiLlama protocolo pump.fun |
| mcap_usd | 1501053293.0 |
| fdv_usd | 2693381236.0 |
| oferta_circulante | 458578876050.0 |
| fdv_sobre_mcap | 1.79 |
| mcap_var_30d_pct | SIN DATO |
| valoracion_base | ingresos del protocolo |
| mcap_sobre_base_anualizada | 4.8 |
| mcap_sobre_base_percentil_365d | 79.9 |
| mcap_sobre_base_min_365d | 2.0 |
| mcap_sobre_base_max_365d | 6.9 |
| mercado_fuente | CoinGecko |

### PUMP derivados

| Dato | Valor |
|---|---|
| funding_medio_7d_pct_hora | 0.000539 |
| funding_medio_7d_anualizado_pct | 4.7 |
| funding_medio_14d_pct_hora | 0.000854 |
| horas_funding_negativo_7d | 35 |
| open_interest_usd | 47146173.0 |
| volumen_24h_usd | 39681789.0 |
| oi_var_7d_pct | -41.11 |
| oi_var_30d_pct | SIN DATO |
| fuente | Hyperliquid (un solo mercado, no agregado) |

### PUMP familia valoracion_relativa: no activa · 1 cumplidas, 4 con fuente (4 en total)

- ratio frente a BTC en el 20 % inferior de 52 semanas: no cumple
- precio bajo la media de 200 días: no cumple
- caída desde su máximo de al menos 70 %: no cumple
- capitalización / ingresos del protocolo anualizados por debajo de 20: cumple

### PUMP familia actividad: no activa · 0 cumplidas, 2 con fuente (2 en total)

- ingresos de 7 días no caen más del 20 % frente a los 30 anteriores: no cumple
- TVL en unidades nativas estable a 90 días: FUENTE CAÍDA (cuenta como no cumple)

### PUMP familia riesgo_oferta: no activa · 0 cumplidas, 1 con fuente (1 en total)

- FDV / capitalización por encima de 2 (presión de desbloqueos): no cumple

## Macro

| Dato | Valor | Fecha | Var. 30 d % | Fuente |
|---|---|---|---|---|
| tipo_real_10a_pct | 2.86 | 2026-11-12 | -0.69 | FRED DFII10 |
| bono_10a_pct | 5.1 | 2026-11-12 | -2.11 | FRED DGS10 |
| dolar_amplio_fed_no_es_dxy | 121.88 | 2026-11-06 | 0.52 | FRED DTWEXBGS |
| m2_eeuu_no_es_global_mm_usd | 23508.0 | 2026-10-05 | 1.06 | FRED WM2NS |
| stablecoins_total_usd | 286982255561.0 | 2026-11-14 | -5.41 | DefiLlama |

### Sentimiento

| Dato | Valor |
|---|---|
| valor | 13.0 |
| fecha | 2026-11-14 |
| dias_seguidos_miedo_extremo | 2 |
| fuente | alternative.me |

## Eventos de calibración

- **evento_4s**: En las próximas 4 semanas no habrá un cierre semanal más de un 10 % por debajo del cierre semanal de referencia. Se resuelve a las 4 semanas, o antes si ocurre ese cierre.
- **evento_8s**: El cierre semanal más bajo de las próximas 26 semanas ocurre dentro de las próximas 8. Se resuelve a las 26 semanas, o antes si un cierre posterior a la semana 8 ya es más bajo.
- **evento_ciclo**: Tres escenarios excluyentes que suman 100 %. Referencia: el mínimo del ciclo (suelo.minimo_usd) en la semana de la predicción. A = ningún cierre semanal por debajo de esa referencia hasta el horizonte (el suelo ya está hecho). B = el cierre semanal más bajo hasta el horizonte queda por debajo de la referencia y ocurre en la fecha de corte o antes (suelo nuevo pronto). C = queda por debajo y ocurre después de la fecha de corte (ciclo largo). Fechas en umbrales.ciclo_fecha_*. Se puntúa con el Brier de tres categorías: suma de (probabilidad − resultado)² en A, B y C.
- **como_puntuar**: Una predicción hecha en la semana del cierre D se puntúa con la fila D de resolucion_eventos. true = ocurrió, false = no ocurrió, pendiente = aún sin resolver. El Brier score es la media de (probabilidad − resultado)².

## Sin dato

- liquidaciones agregadas: sin fuente gratuita fiable
- skew de opciones y mapas de liquidaciones: no incluidos
- reservas y netflows de exchanges: métrica de pago
- flujos de ETF: sin fuente gratuita estable
- M2 global: solo se publica M2 de EE. UU.
- DXY: se publica el índice amplio del dólar de la Fed, no el DXY
- unlocks y staking neto de SOL: sin fuente gratuita estable
- direcciones activas y volumen DEX de SUI, HYPE y PUMP: no incluidos; la actividad se mide por ingresos y TVL
- sentimiento en X: lo aporta Grok, no este archivo

Datos de red y precio: Coin Metrics Community (CC BY-NC 4.0). También DefiLlama, FRED, alternative.me, Hyperliquid, Kraken y BGeometrics.
