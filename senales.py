#!/usr/bin/env python3
"""Archivo diario de señales para Bull, Bear y Estrategia.

BTC y SOL alimentan los tramos de recompra. SUI, HYPE y PUMP van aparte.

Descarga datos brutos, calcula los indicadores y escribe:
  salida/senales_latest.json   lo que leen los agentes
  salida/senales_latest.md     la misma información, legible
  salida/historico/            una copia por día, para auditar

Este script no opina ni decide tramos: solo publica hechos. Lo que no se
puede obtener gratis sale como "SIN DATO", nunca estimado.
Uso: python senales.py [--salida DIRECTORIO]
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import requests

VERSION = "1.9.2"
CM = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
HYPERLIQUID = "https://api.hyperliquid.xyz/info"
SIN_DATO = "SIN DATO"

# Umbrales de las condiciones. Salen de la tabla de familias de señales.
# Los marcados "provisional" concretan algo que la tabla dejaba abierto.
# La regla de cuándo una familia cuenta como "activa" es de la POLÍTICA.
UMBRALES = {
    "mvrv_z_max": 0,
    "nupl_max": 0,
    "puell_max": 0.5,
    "cerca_sma200w_factor": 1.10,       # provisional: hasta un 10 % por encima
    "funding_7d_max": 0,
    "oi_caida_30d_pct": -30,            # provisional
    "fng_miedo_extremo_max": 24,
    "fng_dias_minimos": 14,
    "rsi_sobreventa": 30,
    "rsi_ventana_semanas": 4,           # provisional
    "ratio_percentil_52s_max": 10,      # provisional
    "tvl_usd_caida_90d_pct": -30,       # provisional
    "tvl_sol_estable_90d_pct": 10,      # provisional
    "pausa_caida_semanal_pct": -15,
    # Activos cesta (SUI, HYPE, PUMP): valoración relativa y techo. Todos provisionales.
    "cesta_ratio_percentil_bajo": 20,       # ratio vs BTC en el 20 % inferior de 52 s = castigado
    "cesta_ratio_percentil_techo": 80,      # por encima: sobrecompra relativa (techo de la política)
    "cesta_caida_maximo_pct": -70,          # caída desde su máximo que cuenta como castigo
    "cesta_mcap_ingresos_max": 20,          # capitalización / ingresos anualizados por debajo de esto
    "cesta_ingresos_caida_max_pct": -20,    # ingresos 7 d frente a 30 d previos: más caída = actividad hundida
    "cesta_tvl_nativo_estable_pct": -10,    # TVL en unidades nativas a 90 d
    "cesta_fdv_mcap_aviso": 2,              # FDV / capitalización: presión de oferta por desbloquear
    # Cadenas (BTC, SOL, SUI): capitalización / comisiones de red frente a su propio último año.
    # Una cadena casi no tiene "ingresos" (lo que quema), así que no se compara con un umbral fijo.
    "cadena_valoracion_percentil_max": 20,  # en el 20 % más bajo de 12 meses = barata frente a sí misma
    # Eventos de calibración de Bull y Bear (definición común a los agentes)
    "evento_4s_caida_pct": 10,
    "evento_8s_ventana": 8,
    "evento_8s_horizonte": 26,
}
EVENTOS = {
    "evento_4s": "En las próximas 4 semanas no habrá un cierre semanal más de un 10 % por "
                 "debajo del cierre semanal de referencia. Se resuelve a las 4 semanas, o antes "
                 "si ocurre ese cierre.",
    "evento_8s": "El cierre semanal más bajo de las próximas 26 semanas ocurre dentro de las "
                 "próximas 8. Se resuelve a las 26 semanas, o antes si un cierre posterior a la "
                 "semana 8 ya es más bajo.",
    "como_puntuar": "Una predicción hecha en la semana del cierre D se puntúa con la fila D de "
                    "resolucion_eventos. true = ocurrió, false = no ocurrió, pendiente = aún "
                    "sin resolver. El Brier score es la media de (probabilidad − resultado)².",
}
# Seguimiento aparte: informativas, fuera de los tramos RT1-RT4.
# Para cada activo cesta: id de CoinGecko y candidatos de DefiLlama (se prueban en orden; el
# primero que responda queda registrado como fuente). Vacío = esa métrica no aplica.
CESTA = {
    "SUI":  {"tipo": "cadena", "apps": "sui",
             "coingecko": "sui", "tvl_chain": ["Sui"], "fees_chain": ["sui"], "fees_protocolo": [],
             "spot": ("kraken", "SUIUSD")},
    "HYPE": {"tipo": "protocolo", "coingecko": "hyperliquid", "tvl_chain": ["Hyperliquid L1", "Hyperliquid"],
             "fees_chain": ["hyperliquid-l1", "hyperliquid"], "fees_protocolo": ["hyperliquid-perps", "hyperliquid"],
             "spot": ("hyperliquid_spot", "HYPE")},
    "PUMP": {"tipo": "protocolo", "coingecko": "pump-fun", "tvl_chain": [], "fees_chain": [], "fees_protocolo": ["pump.fun", "pumpfun"],
             "spot": ("kraken", "PUMPUSD")},
}
OTRAS_MONEDAS = list(CESTA)
PAUSA_COINGECKO = 2.5   # segundos entre llamadas de historial (API gratuita sin clave)
# Solo los precios son críticos. Si falta el precio realizado (o la oferta, que solo sirve
# para calcularlo), el archivo sale PARCIAL y la pausa en SIN DATO.
CRITICOS = ["btc_precio", "sol_precio"]


def limpiar(texto) -> str:
    """Borra claves de API de los mensajes: el archivo se publica en un repositorio público."""
    return re.sub(r"(api_key=)[^&\s'\"]+", r"\1***", str(texto))


class Fallos:
    """Registro de fuentes que no respondieron o no pasaron validación."""

    def __init__(self):
        self.items: list[dict] = []

    def add(self, clave: str, motivo: object):
        self.items.append({"clave": clave, "motivo": limpiar(motivo)[:400]})

    def contiene(self, clave: str) -> bool:
        return any(i["clave"] == clave for i in self.items)


def get_json(url, params=None, reintentos=3):
    for intento in range(reintentos):
        r = None
        try:
            r = requests.get(url, params=params, timeout=45,
                             headers={"User-Agent": "senales-recompra/1.0"})
            if r.status_code == 429 or r.status_code >= 500:
                raise requests.HTTPError(f"HTTP {r.status_code}", response=r)
            r.raise_for_status()
            return r.json()
        except requests.RequestException:
            if intento == reintentos - 1 or (r is not None and 400 <= r.status_code < 429):
                raise
            time.sleep(4 * (intento + 1))


def post_json(url, cuerpo):
    r = requests.post(url, json=cuerpo, timeout=45)
    r.raise_for_status()
    return r.json()


def get_texto(url, timeout=20):
    r = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    return r.text


# ---------------------------------------------------------------- descargas
def coinmetrics(activo: str, metrica: str) -> pd.Series:
    """Una métrica cada vez: si una deja de ser gratuita, las demás siguen."""
    url, params, filas = CM, {
        "assets": activo, "metrics": metrica, "frequency": "1d",
        "page_size": 10000, "paging_from": "start",
        "start_time": "2010-01-01",
    }, []
    while url:
        d = get_json(url, params)
        filas += d.get("data", [])
        url, params = d.get("next_page_url"), None
        time.sleep(0.7)  # límite gratuito: 10 peticiones cada 6 segundos
    if not filas:
        raise ValueError("respuesta sin datos")
    s = pd.Series(
        {pd.Timestamp(f["time"]).tz_localize(None).normalize(): float(f[metrica])
         for f in filas if f.get(metrica) not in (None, "")}, dtype=float)
    return s.sort_index()


def serie_ts(pares, escala=1) -> pd.Series:
    """Convierte [[segundos_unix, valor], ...] en serie diaria."""
    s = pd.Series({pd.Timestamp(int(t), unit="s").normalize(): float(v) for t, v in pares})
    return s.sort_index() * escala


def defillama_tvl_solana():
    d = get_json("https://api.llama.fi/v2/historicalChainTvl/Solana")
    return serie_ts([(x["date"], x["tvl"]) for x in d])


def defillama_fees_apps(cadena: str, tipo: str):
    """Suma de las aplicaciones que corren SOBRE la cadena (DEX, préstamos...). No es la red."""
    d = get_json(f"https://api.llama.fi/overview/fees/{cadena}", {
        "excludeTotalDataChart": "false",
        "excludeTotalDataChartBreakdown": "true", "dataType": tipo})
    return serie_ts(d["totalDataChart"])


def defillama_stablecoins(red="all"):
    d = get_json(f"https://stablecoins.llama.fi/stablecoincharts/{red}")
    return serie_ts([(x["date"], x["totalCirculatingUSD"]["peggedUSD"]) for x in d])


def fear_greed() -> pd.Series:
    d = get_json("https://api.alternative.me/fng/", {"limit": 120, "format": "json"})
    return serie_ts([(x["timestamp"], x["value"]) for x in d["data"]])


def fred(serie: str) -> pd.Series:
    """Con FRED_API_KEY usa la API oficial (más fiable); sin ella, el CSV público."""
    clave = os.environ.get("FRED_API_KEY", "").strip()
    if clave:
        d = get_json("https://api.stlouisfed.org/fred/series/observations", {
            "series_id": serie, "api_key": clave, "file_type": "json",
            "observation_start": "2024-01-01"}, reintentos=1)
        s = pd.Series({pd.Timestamp(o["date"]): float(o["value"])
                       for o in d["observations"] if o["value"] not in (".", "")}, dtype=float)
        if s.empty:
            raise ValueError("sin observaciones")
        return s.sort_index()
    for intento in range(2):
        try:
            texto = get_texto(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={serie}")
            break
        except requests.RequestException:
            if intento == 1:
                raise
            time.sleep(3)
    df = pd.read_csv(io.StringIO(texto))
    df.columns = ["fecha", "valor"]
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df.dropna().set_index("fecha")["valor"].sort_index()


_FECHAS_BG = {"d", "date", "day", "theday", "unixts", "t", "time", "timestamp"}


def _bg_filas(d):
    if isinstance(d, dict):
        for k in ("data", "result", "values"):
            if isinstance(d.get(k), list):
                return d[k]
        return [d]
    return d if isinstance(d, list) else []


def _bg_fecha(fila: dict) -> pd.Timestamp:
    for k, v in fila.items():
        if str(k).lower() in ("d", "date", "day", "theday"):
            return pd.Timestamp(v).tz_localize(None).normalize()
    for k, v in fila.items():
        if str(k).lower() in ("unixts", "t", "time", "timestamp"):
            try:
                x = float(v)
                return pd.Timestamp(int(x / 1000 if x > 1e11 else x), unit="s").normalize()
            except (TypeError, ValueError):
                return pd.Timestamp(v).tz_localize(None).normalize()
    raise ValueError("sin fecha")


def _bg_valor(fila: dict, endpoint: str) -> float:
    clave = endpoint.replace("-", "").lower()
    cand = {k: v for k, v in fila.items() if str(k).lower() not in _FECHAS_BG}
    for k, v in cand.items():
        if str(k).lower().replace("_", "") == clave:
            return float(v)
    if len(cand) == 1:
        return float(next(iter(cand.values())))
    raise ValueError(f"valor no identificado entre {list(fila)[:6]}")


def bgeometrics(endpoint: str, ultimo: bool = False) -> pd.Series:
    """Plan gratuito: 10 peticiones/hora y 15/día, sin reintentos para no gastarlas."""
    d = get_json(f"https://bitcoin-data.com/v1/{endpoint}" + ("/last" if ultimo else ""), reintentos=1)
    try:
        s = pd.Series({_bg_fecha(f): _bg_valor(f, endpoint) for f in _bg_filas(d)}, dtype=float).sort_index()
        if s.empty:
            raise ValueError("vacía")
    except Exception as e:
        raise ValueError(f"respuesta no reconocida ({e}): {json.dumps(d)[:150]}") from None
    return s


def hyperliquid(moneda: str, ahora: datetime) -> dict:
    meta, ctxs = post_json(HYPERLIQUID, {"type": "metaAndAssetCtxs"})
    nombres = [u["name"] for u in meta["universe"]]
    ctx = ctxs[nombres.index(moneda)]
    desde = int((ahora - timedelta(days=14)).timestamp() * 1000)
    hist = post_json(HYPERLIQUID, {"type": "fundingHistory", "coin": moneda, "startTime": desde})
    s = pd.Series({pd.Timestamp(h["time"], unit="ms"): float(h["fundingRate"]) for h in hist}).sort_index()
    corte = s.index.max() - pd.Timedelta(days=7)
    f7 = s[s.index > corte].mean()
    return {
        "funding_medio_7d_pct_hora": pct(f7 * 100, 6),
        "funding_medio_7d_anualizado_pct": pct(f7 * 24 * 365 * 100, 1),
        "funding_medio_14d_pct_hora": pct(s.mean() * 100, 6),
        "horas_funding_negativo_7d": int((s[s.index > corte] < 0).sum()),
        "open_interest_usd": n(float(ctx["openInterest"]) * float(ctx["markPx"]), 0),
        "volumen_24h_usd": n(float(ctx["dayNtlVlm"]), 0) if ctx.get("dayNtlVlm") is not None else None,
    }


def hyperliquid_velas(moneda: str, ahora: datetime) -> pd.Series:
    """Cierres diarios completos del perpetuo; la historia empieza en su listado."""
    fin = int(ahora.timestamp() * 1000)
    velas = post_json(HYPERLIQUID, {"type": "candleSnapshot", "req": {
        "coin": moneda, "interval": "1d", "startTime": fin - 5000 * 86_400_000, "endTime": fin}})
    s = pd.Series({pd.Timestamp(v["t"], unit="ms").normalize(): float(v["c"])
                   for v in velas if v["T"] < fin}, dtype=float).sort_index()
    if s.empty:
        raise ValueError(f"sin velas para {moneda}")
    return s


def hyperliquid_spot(token: str, referencia: float | None = None) -> float:
    """Precio spot en Hyperliquid del par token/stable.

    Puede haber varios tokens con el mismo nombre (réplicas que cotizan a céntimos). Se reúnen todos
    los pares con USDC/USDH/USDT0. Con `referencia` (el precio del perpetuo) gana el par cuyo precio
    más se acerca; si ninguno está a menos de un 50 %, no se inventa nada: se lanza un error que
    lista los candidatos para poder diagnosticarlo. Sin referencia, canónicos primero y mayor volumen.
    """
    meta, ctxs = post_json(HYPERLIQUID, {"type": "spotMetaAndAssetCtxs"})
    candidatos = [t for t in meta["tokens"] if t["name"] == token]
    quotes = {t["index"] for t in meta["tokens"] if t["name"] in ("USDC", "USDH", "USDT0")}
    if not candidatos or not quotes:
        raise ValueError(f"sin par spot para {token}")
    canonicos = {t["index"] for t in candidatos if t.get("isCanonical")}
    todos = {t["index"] for t in candidatos}
    try:  # precio por nombre de par: no depende de cómo se alinean las listas de la respuesta
        mids = post_json(HYPERLIQUID, {"type": "allMids"})
        mids = mids if isinstance(mids, dict) else {}
    except Exception:
        mids = {}
    pares = []  # (volumen, precio, nombre_par, canonico)
    for i, u in enumerate(meta["universe"]):
        a, b = u["tokens"]
        if (a in todos and b in quotes) or (b in todos and a in quotes):
            nombre = u.get("name", str(i))
            try:
                ctx = ctxs[u["index"]] if isinstance(u.get("index"), int) and u["index"] < len(ctxs) else ctxs[i]
                px = float(mids[nombre]) if nombre in mids else float(ctx["markPx"])
                pares.append((float(ctx.get("dayNtlVlm") or 0), px, nombre, bool({a, b} & canonicos)))
            except (KeyError, ValueError, TypeError, IndexError):
                continue
    if not pares:
        raise ValueError(f"sin par spot para {token}")
    if referencia:
        mejor = min(pares, key=lambda x: abs(x[1] / referencia - 1))
        if abs(mejor[1] / referencia - 1) > 0.5:
            lista = ", ".join(f"{x[2]}={x[1]:g} (vol {x[0]:.0f}, canónico={x[3]})" for x in pares[:6])
            raise ValueError(f"ningún par {token} cercano al perpetuo ({referencia:g}); candidatos: {lista}")
        return mejor[1]
    return max(pares, key=lambda x: (x[3], x[0]))[1]


def defillama_chain_tvl(cadena: str) -> pd.Series:
    d = get_json(f"https://api.llama.fi/v2/historicalChainTvl/{cadena}")
    return serie_ts([(x["date"], x["tvl"]) for x in d])


def defillama_fees_cadena(slug: str, tipo: str) -> pd.Series:
    """Comisiones o ingresos de la PROPIA red (gas que pagan los usuarios a validadores/mineros).

    Ojo: overview/fees/{cadena} sería la suma de las apps sobre la cadena, otra cosa (ver
    defillama_fees_apps). Hasta v1.9 se usaba esa por error.
    """
    d = get_json(f"https://api.llama.fi/summary/fees/{slug}", {"dataType": tipo})
    return serie_ts(d["totalDataChart"])


def defillama_fees_protocolo(slug: str, tipo: str) -> pd.Series:
    d = get_json(f"https://api.llama.fi/summary/fees/{slug}", {"dataType": tipo})
    return serie_ts(d["totalDataChart"])


def coingecko_mercado(ids: list[str]) -> dict:
    """Capitalización, FDV y oferta circulante en una sola llamada. Sin clave; puede fallar."""
    d = get_json("https://api.coingecko.com/api/v3/coins/markets",
                 {"vs_currency": "usd", "ids": ",".join(ids), "per_page": 50}, reintentos=2)
    out = {}
    for x in d:
        out[x["id"]] = {"mcap_usd": x.get("market_cap"), "fdv_usd": x.get("fully_diluted_valuation"),
                        "oferta_circulante": x.get("circulating_supply"), "oferta_total": x.get("total_supply"),
                        "precio_spot_usd": x.get("current_price")}
    if not out:
        raise ValueError("respuesta vacía")
    return out


def coingecko_historial_mcap(id_cg: str) -> pd.Series:
    """Capitalización diaria del último año (máximo gratuito sin clave)."""
    d = get_json(f"https://api.coingecko.com/api/v3/coins/{id_cg}/market_chart",
                 {"vs_currency": "usd", "days": 365, "interval": "daily"}, reintentos=2)
    s = pd.Series({pd.Timestamp(int(t), unit="ms").normalize(): float(v) for t, v in d["market_caps"] if v})
    if s.empty:
        raise ValueError("sin capitalizaciones")
    return s[~s.index.duplicated(keep="last")].sort_index()


def anadir_historiales(mercado: dict | None, ids: list[str], fallos: Fallos) -> None:
    """Mete en mercado[id]['historial_mcap'] el último año de capitalización. Un fallo por bloque."""
    if not mercado:
        return
    malos = []
    for i, id_cg in enumerate(ids):
        if id_cg not in mercado:
            continue
        if i and PAUSA_COINGECKO:
            time.sleep(PAUSA_COINGECKO)
        try:
            mercado[id_cg]["historial_mcap"] = coingecko_historial_mcap(id_cg)
        except Exception as e:
            malos.append(f"{id_cg}: {type(e).__name__}")
    if malos:
        fallos.add("coingecko_historial", limpiar("; ".join(malos)))


def primera_que_funcione(candidatos, f, *args):
    """Prueba cada candidato en orden. Devuelve (serie, candidato, motivos_de_los_fallidos)."""
    motivos = []
    for c in candidatos:
        try:
            r = f(c, *args)
            if r is not None and len(r):
                return r, c, motivos
            motivos.append(f"{c}: vacío")
        except Exception as e:
            motivos.append(f"{c}: {type(e).__name__}: {str(e)[:60]}")
    return None, None, motivos


def kraken_precio(par: str) -> float:
    d = get_json("https://api.kraken.com/0/public/Ticker", {"pair": par})
    return float(next(iter(d["result"].values()))["c"][0])


# ------------------------------------------------------------- indicadores
def semanal(s: pd.Series) -> pd.Series:
    """Cierres de semana completos (domingo, UTC). Quita la semana en curso."""
    w = s.resample("W-SUN").last().dropna()
    if len(w) and w.index[-1] > s.index[-1]:
        w = w.iloc[:-1]
    return w


def cierres_periodo(s: pd.Series, regla: str) -> pd.Series:
    """Cierres de mes ("ME") o año ("YE") completos. Quita el periodo en curso."""
    c = s.resample(regla).last().dropna()
    return c[c.index <= s.index[-1]]


def resumen_cierres(c: pd.Series, nombre: str, cuantos: int) -> dict:
    return {
        f"ultimo_cierre_{nombre}_fecha": c.index[-1].strftime("%Y-%m-%d") if len(c) else None,
        f"ultimo_cierre_{nombre}_usd": n(c.iloc[-1]) if len(c) else None,
        f"var_{nombre}_pct": pct((c.iloc[-1] / c.iloc[-2] - 1) * 100) if len(c) > 1 else None,
        f"ultimos_{cuantos}_cierres_{nombre}es": {d.strftime("%Y-%m-%d"): n(v) for d, v in c.tail(cuantos).items()},
    }


def rsi(s: pd.Series, n: int = 14) -> pd.Series:
    delta = s.diff()
    subida = delta.clip(lower=0).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    bajada = (-delta.clip(upper=0)).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    return 100 - 100 / (1 + subida / bajada)


def macd(s: pd.Series):
    linea = s.ewm(span=12, adjust=False).mean() - s.ewm(span=26, adjust=False).mean()
    return linea, linea.ewm(span=9, adjust=False).mean()


def n(x, dec=2):
    """Redondea y convierte NaN en None. Los valores menores de 1 conservan cifras significativas."""
    if x is None or pd.isna(x):
        return None
    x = float(x)
    if not math.isfinite(x):
        return None
    if x != 0 and abs(x) < 1:
        dec += math.ceil(-math.log10(abs(x))) + 2
    return round(x, dec)


def pct(x, dec=2):
    """Porcentajes y ratios: decimales fijos, sin la expansión que usan los precios."""
    if x is None or pd.isna(x) or not math.isfinite(float(x)):
        return None
    return round(float(x), dec)


def ultimo(s, i=-1):
    return s.iloc[i] if len(s) >= abs(i) else None


def var_pct(s: pd.Series, dias: int):
    """Variación frente al valor de hace `dias` días naturales."""
    if s is None or s.empty:
        return None
    previo = s[s.index <= s.index[-1] - pd.Timedelta(days=dias)]
    if previo.empty or previo.iloc[-1] == 0:
        return None
    return pct((s.iloc[-1] / previo.iloc[-1] - 1) * 100)


def tendencia_precio(p: pd.Series) -> dict:
    w = semanal(p)
    sma200d, sma50d = p.rolling(200).mean(), p.rolling(50).mean()
    sma200w, sma20w = w.rolling(200).mean(), w.rolling(20).mean()
    ema21w = w.ewm(span=21, adjust=False).mean()
    rsi_d, rsi_w = rsi(p), rsi(w)
    macd_l, macd_s = macd(w)
    return {
        "fecha_ultimo_dato": p.index[-1].strftime("%Y-%m-%d"),
        "fecha_ultimo_cierre_semanal": w.index[-1].strftime("%Y-%m-%d"),
        "precio_referencia_usd": n(p.iloc[-1]),
        "cierre_semanal_usd": n(w.iloc[-1]),
        "var_semanal_pct": pct((w.iloc[-1] / w.iloc[-2] - 1) * 100) if len(w) > 1 else None,
        "var_7d_pct": var_pct(p, 7),
        "var_30d_pct": var_pct(p, 30),
        "sma50d": n(sma50d.iloc[-1]),
        "sma200d": n(sma200d.iloc[-1]),
        "sma50d_sobre_sma200d": bool(sma50d.iloc[-1] > sma200d.iloc[-1]) if pd.notna(sma200d.iloc[-1]) else None,
        "sma20w": n(sma20w.iloc[-1]),
        "ema21w": n(ema21w.iloc[-1]),
        "sma200w": n(sma200w.iloc[-1]),
        "cierre_sobre_sma20w": bool(w.iloc[-1] > sma20w.iloc[-1]) if pd.notna(sma20w.iloc[-1]) else None,
        "rsi14_diario": n(rsi_d.iloc[-1]),
        "rsi14_semanal": n(rsi_w.iloc[-1]),
        "macd_semanal": n(macd_l.iloc[-1]),
        "macd_semanal_senal": n(macd_s.iloc[-1]),
        "ultimos_30_cierres_semanales": {d.strftime("%Y-%m-%d"): n(v) for d, v in w.tail(30).items()},
        **resumen_cierres(cierres_periodo(p, "ME"), "mensual", 24),
        **resumen_cierres(cierres_periodo(p, "YE"), "anual", 10),
    }


def ciclo(p: pd.Series) -> dict:
    """Máximo histórico y mínimo posterior, en cierres semanales."""
    w = semanal(p)
    fecha_max = w.idxmax()
    tras = w[w.index >= fecha_max]
    fecha_min = tras.idxmin()
    return {
        "maximo_cierre_semanal_usd": n(w.max()),
        "fecha_maximo": fecha_max.strftime("%Y-%m-%d"),
        "semanas_desde_maximo": int((w.index[-1] - fecha_max).days / 7),
        "minimo_tras_maximo_usd": n(tras.min()),
        "fecha_minimo": fecha_min.strftime("%Y-%m-%d"),
        "caida_desde_maximo_pct": pct((w.iloc[-1] / w.max() - 1) * 100),
        "rebote_desde_minimo_pct": pct((w.iloc[-1] / tras.min() - 1) * 100),
    }


def pausa(p: pd.Series, precio_realizado: pd.Series) -> dict:
    """Aplica la condición de pausa de Estrategia semana a semana."""
    w, rp = semanal(p), semanal(precio_realizado).reindex(semanal(p).index).ffill()
    cambio, activa, encima, desde = w.pct_change() * 100, False, 0, None
    for fecha in w.index:
        bajo = w[fecha] < rp[fecha]
        if not activa and bajo and cambio[fecha] < UMBRALES["pausa_caida_semanal_pct"]:
            activa, encima, desde = True, 0, fecha
        elif activa:
            encima = 0 if bajo else encima + 1
            if encima >= 2:
                activa, desde = False, None
    return {
        "activa": activa,
        "desde": desde.strftime("%Y-%m-%d") if desde is not None else None,
        "cierres_seguidos_sobre_realized": encima if activa else None,
        "ultimo_cierre_bajo_realized": bool(w.iloc[-1] < rp.iloc[-1]),
    }


def resolucion_eventos(w: pd.Series, semanas: int = 60) -> dict:
    """Tabla de verdad de los eventos de calibración, por fecha de cierre semanal."""
    u, vals, out = UMBRALES, w.values, {}
    for i in range(max(0, len(w) - semanas), len(w)):
        c, sig = vals[i], vals[i + 1:]
        e4: object = "pendiente"
        prox4 = sig[:4]
        if len(prox4) and (prox4 < c * (1 - u["evento_4s_caida_pct"] / 100)).any():
            e4 = False
        elif len(prox4) == 4:
            e4 = True
        e8: object = "pendiente"
        if len(sig) >= u["evento_8s_ventana"]:
            min_ventana = sig[:u["evento_8s_ventana"]].min()
            resto = sig[u["evento_8s_ventana"]:u["evento_8s_horizonte"]]
            if len(resto) and (resto < min_ventana).any():
                e8 = False
            elif len(sig) >= u["evento_8s_horizonte"]:
                e8 = True
        out[w.index[i].strftime("%Y-%m-%d")] = {"cierre": n(c), "evento_4s": e4, "evento_8s": e8}
    return out


def resumen_activo(t: dict, c: dict, fam: dict, pausa_sis: dict | None, al_dia: bool,
                   diario_al_dia: bool | None = None) -> dict:
    """Lo que las reglas de Estrategia nombran, en un solo bloque corto."""
    return {
        "precio_referencia_usd": t["precio_referencia_usd"],
        "precio_referencia_fecha": t["fecha_ultimo_dato"],
        "dato_diario_al_dia": diario_al_dia,
        "cierre_semanal_usd": t["cierre_semanal_usd"],
        "cierre_semanal_fecha": t["fecha_ultimo_cierre_semanal"],
        "cierre_semanal_al_dia": al_dia,
        "evento_4s_umbral_usd": n(t["cierre_semanal_usd"] * (1 - UMBRALES["evento_4s_caida_pct"] / 100)),
        "familias_cumplidas_de_medibles": {k: f"{v['cumplidas']}/{v['medibles']}" for k, v in fam.items()},
        # Condición única del sistema, calculada sobre BTC: congela T3 y T4 en AMBOS activos.
        "pausa_sistema_activa": None if pausa_sis is None else pausa_sis["activa"],
        "semanas_desde_maximo": c["semanas_desde_maximo"],
        "caida_desde_maximo_pct": c["caida_desde_maximo_pct"],
        "rebote_desde_minimo_pct": c["rebote_desde_minimo_pct"],
    }


def ultimo_domingo_cerrado(ahora: datetime) -> pd.Timestamp:
    hoy = pd.Timestamp(ahora).tz_localize(None).normalize()
    atras = (hoy.weekday() + 1) % 7 or 7   # lunes → 1 día; domingo → 7
    return hoy - pd.Timedelta(days=atras)


def condiciones_planas(doc: dict) -> dict:
    out = {}
    for activo in ("btc", "sol"):
        a = doc.get(activo) or {}
        for fam, f in (a.get("familias") or {}).items():
            for c in f["condiciones"]:
                out[f"{activo}.{fam}.{c['condicion']}"] = c["cumple"]
    if (doc.get("pausa_sistema") or {}).get("activa") is not None:
        out["pausa_sistema_activa"] = doc["pausa_sistema"]["activa"]
    return out


def cambios(doc: dict, anterior: dict | None) -> dict:
    if not anterior:
        return {"archivo_anterior_snapshot": None, "condiciones_cambiadas": []}
    antes, ahora = condiciones_planas(anterior), condiciones_planas(doc)
    return {
        "archivo_anterior_snapshot": anterior.get("snapshot_id"),
        "archivo_anterior_generado": anterior.get("generado_utc"),
        "condiciones_cambiadas": [{"clave": k, "antes": antes.get(k), "ahora": v}
                                  for k, v in ahora.items() if antes.get(k) != v],
    }


def archivo_hace_7_dias(dir_salida: Path, ahora: datetime, fallos: Fallos) -> dict | None:
    """El archivo histórico más reciente con al menos 7 días de antigüedad."""
    limite = (pd.Timestamp(ahora).tz_localize(None).normalize() - pd.Timedelta(days=7)).strftime("%Y-%m-%d")
    candidatos = sorted(f for f in (dir_salida / "historico").glob("senales_*.json")
                        if f.stem.removeprefix("senales_") <= limite)
    if not candidatos:
        return None
    try:
        return json.loads(candidatos[-1].read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        fallos.add("archivo_7_dias", f"no se pudo leer {candidatos[-1].name}: {e}")
        return None


def onchain_btc(p, mcap, rcap, rp, hash_rate, emision, lth_sopr=None) -> dict:
    """Cada bloque es independiente: si falta el precio realizado, Puell y hash ribbons siguen."""
    out: dict = {}
    if mcap is not None and rcap is not None and rp is not None:
        rp_al = rp[rp.index <= p.index[-1]].dropna()
        mvrv = (mcap / rcap).dropna()
        z = ((mcap - rcap) / mcap.expanding(365).std()).dropna()
        out["realized_price_usd"] = n(rp_al.iloc[-1])
        out["realized_price_fecha"] = rp_al.index[-1].strftime("%Y-%m-%d")
        out["precio_bajo_realized"] = bool(p.iloc[-1] < rp_al.iloc[-1])
        out["mvrv"] = n(mvrv.iloc[-1], 3)
        out["mvrv_z"] = n(z.iloc[-1], 3)
        out["nupl"] = n((1 - rcap / mcap).dropna().iloc[-1], 3)
    if emision is not None:
        out["puell"] = n((emision / emision.rolling(365).mean()).dropna().iloc[-1], 3)
    if hash_rate is not None:
        r30, r60 = hash_rate.rolling(30).mean(), hash_rate.rolling(60).mean()
        bajo = (r30 < r60).dropna()
        cruces = bajo[bajo != bajo.shift()].index
        out["hash_ribbons_30_bajo_60"] = bool(bajo.iloc[-1])
        out["hash_ribbons_dias_en_estado"] = int((bajo.index[-1] - cruces[-1]).days)
    if lth_sopr is not None and len(lth_sopr):
        out["lth_sopr"] = n(lth_sopr.iloc[-1], 3)
        out["lth_sopr_fecha"] = lth_sopr.index[-1].strftime("%Y-%m-%d")
    return out


def _rc_cm(mcap, oferta):
    c = coinmetrics("btc", "CapRealUSD")
    return c, c / oferta


def _rc_mvrv(mcap, oferta):
    c = mcap / coinmetrics("btc", "CapMVRVCur")
    return c, c / oferta


def _rc_bg(mcap, oferta):
    rp = bgeometrics("realized-price")
    return rp * oferta, rp


FUENTES_REALIZADO = [("Coin Metrics CapRealUSD", _rc_cm), ("Coin Metrics CapMVRVCur", _rc_mvrv),
                     ("BGeometrics realized-price", _rc_bg)]


def realizado_btc(p, mcap, oferta, fallos: Fallos, avisos: list):
    """Capitalización y precio realizados, con tres fuentes por orden. Devuelve (rcap, rp, fuente)."""
    if mcap is None or oferta is None:
        fallos.add("btc_realized", "faltan la capitalización o la oferta de Coin Metrics")
        return None, None, None
    motivos = []
    for nombre, f in FUENTES_REALIZADO:
        try:
            rcap, rp = f(mcap, oferta)
            ultimo = rp.dropna().iloc[-1]
            # Rango histórico de BTC: MVRV entre ~0,6 y ~7, es decir, realizado/precio entre 0,14 y 1,7.
            if not 0.1 < ultimo / p.iloc[-1] < 3:
                raise ValueError(f"valor implausible: {ultimo:.4g} frente a precio {p.iloc[-1]:.4g}")
            if motivos:
                avisos.append(limpiar(f"Precio realizado tomado de {nombre}. Antes fallaron: " + " | ".join(motivos)))
            return rcap, rp, nombre
        except Exception as e:
            motivos.append(f"{nombre}: {type(e).__name__}: {str(e)[:90]}")
    fallos.add("btc_realized", " | ".join(motivos))
    return None, None, None


def cond(nombre: str, resultado) -> dict:
    return {"condicion": nombre, "cumple": None if resultado is None else bool(resultado)}


def familia(condiciones: list[dict]) -> dict:
    medibles = [c for c in condiciones if c["cumple"] is not None]
    return {"cumplidas": sum(c["cumple"] for c in medibles), "medibles": len(medibles),
            "total": len(condiciones), "condiciones": condiciones}


def si(valor, f):
    return None if valor is None else f(valor)


def rsi_sale_sobreventa(p: pd.Series):
    r = rsi(semanal(p)).dropna().tail(UMBRALES["rsi_ventana_semanas"] + 1)
    if len(r) < 2:
        return None
    return bool((r.iloc[:-1] < UMBRALES["rsi_sobreventa"]).any() and r.iloc[-1] >= UMBRALES["rsi_sobreventa"])


def familias_btc(t, oc, der, sent, hash_rate, p) -> dict:
    u = UMBRALES
    recuperacion = None
    if "hash_ribbons_30_bajo_60" in oc:
        recuperacion = (not oc["hash_ribbons_30_bajo_60"]) and oc["hash_ribbons_dias_en_estado"] <= 30
    return {
        "valoracion": familia([
            cond("MVRV Z < 0", si(oc.get("mvrv_z"), lambda v: v < u["mvrv_z_max"])),
            cond("precio bajo realized price", oc.get("precio_bajo_realized")),
            cond("precio cerca o bajo la media de 200 semanas",
                 None if t["sma200w"] is None else t["precio_referencia_usd"] <= t["sma200w"] * u["cerca_sma200w_factor"]),
        ]),
        "capitulacion": familia([
            cond("NUPL < 0", si(oc.get("nupl"), lambda v: v < u["nupl_max"])),
            cond("LTH-SOPR < 1", si(oc.get("lth_sopr"), lambda v: v < 1)),
            cond("Puell < 0,5", si(oc.get("puell"), lambda v: v < u["puell_max"])),
            cond("hash ribbons en capitulación", oc.get("hash_ribbons_30_bajo_60")),
        ]),
        "derivados": familia(condiciones_derivados(der)),
        "sentimiento": familia(condiciones_sentimiento(sent)),
        "confirmacion": familia([
            cond("cierre semanal sobre la media de 20 semanas", t["cierre_sobre_sma20w"]),
            cond("RSI semanal saliendo de sobreventa", rsi_sale_sobreventa(p)),
            cond("hash ribbons recuperadas en los últimos 30 días", recuperacion),
        ]),
    }


def condiciones_derivados(der: dict) -> list[dict]:
    return [
        cond("funding medio de 7 días negativo",
             si(der.get("funding_medio_7d_pct_hora"), lambda v: v < UMBRALES["funding_7d_max"])),
        cond("open interest desplomado en 30 días",
             si(der.get("oi_var_30d_pct"), lambda v: v <= UMBRALES["oi_caida_30d_pct"])),
        cond("grandes liquidaciones de largos", None),
    ]


def condiciones_sentimiento(sent: dict) -> list[dict]:
    return [cond("Fear & Greed en miedo extremo 14 días o más",
                 si(sent.get("dias_seguidos_miedo_extremo"), lambda v: v >= UMBRALES["fng_dias_minimos"]))]


def familias_sol(t, ratio_pct, sol_datos, der, sent, confirmacion_btc) -> dict:
    u = UMBRALES
    tvl_usd, tvl_sol = sol_datos.get("tvl_usd_var_90d_pct"), sol_datos.get("tvl_en_sol_var_90d_pct")
    tvl = None
    if tvl_usd is not None and tvl_sol is not None:
        tvl = tvl_usd <= u["tvl_usd_caida_90d_pct"] and abs(tvl_sol) <= u["tvl_sol_estable_90d_pct"]
    return {
        "valoracion": familia([
            cond("precio bajo la media de 200 semanas",
                 None if t["sma200w"] is None else t["precio_referencia_usd"] < t["sma200w"]),
            cond("ratio SOL/BTC en mínimos del rango de 52 semanas",
                 si(ratio_pct, lambda v: v <= u["ratio_percentil_52s_max"])),
            cond("capitalización / comisiones de red en el 20 % más bajo de 12 meses",
                 si(sol_datos.get("mcap_sobre_base_percentil_365d"), lambda v: v <= u["cadena_valoracion_percentil_max"])),
        ]),
        "capitulacion": familia([
            cond("TVL en USD cae y TVL en SOL estable", tvl),
            cond("pico de unstaking", None),
        ]),
        "derivados": familia(condiciones_derivados(der)),
        "sentimiento": familia(condiciones_sentimiento(sent)),
        "confirmacion": familia([
            cond("cierre semanal sobre la media de 20 semanas", t["cierre_sobre_sma20w"]),
            cond("BTC ya en confirmación", confirmacion_btc),
        ]),
    }


def dias_miedo(fg: pd.Series) -> int:
    dias = 0
    for v in fg.sort_index(ascending=False):
        if v > UMBRALES["fng_miedo_extremo_max"]:
            break
        dias += 1
    return dias


# --------------------------------------------------------------- utilidades
def intenta(fallos: Fallos, clave: str, f, *args):
    try:
        return f(*args)
    except Exception as e:  # una fuente caída no debe tumbar el archivo
        fallos.add(clave, f"{type(e).__name__}: {e}")
        return None


def actualizar_historial(ruta: Path, fecha: str, moneda: str, valor: float, columna: str) -> pd.Series:
    """Series sin histórico gratuito (open interest, capitalización): las acumulamos nosotros."""
    columnas = ["fecha", "moneda", columna]
    df = pd.read_csv(ruta) if ruta.exists() else pd.DataFrame(columns=columnas)
    df = df[~((df["fecha"] == fecha) & (df["moneda"] == moneda))]
    df = pd.concat([df, pd.DataFrame([[fecha, moneda, valor]], columns=columnas)], ignore_index=True)
    df = df.sort_values(["fecha", "moneda"])
    df.to_csv(ruta, index=False)
    h = df[df["moneda"] == moneda]
    return pd.Series(h[columna].astype(float).values, index=pd.to_datetime(h["fecha"]))


def actualizar_oi(ruta: Path, fecha: str, moneda: str, oi: float) -> pd.Series:
    return actualizar_historial(ruta, fecha, moneda, oi, "oi_usd")


def validar_precio(p, nombre, ahora, fallos, spot=None):
    edad = (pd.Timestamp(ahora).tz_localize(None).normalize() - p.index[-1]).days
    if edad > 3:
        fallos.add(f"{nombre}_precio", f"dato con {edad} días de antigüedad")
    salto = p.tail(30).pct_change().abs().max()
    if pd.notna(salto) and salto > 0.4:
        fallos.add(f"{nombre}_salto", f"variación diaria de {salto:.0%} en 30 días; revisar")
    if spot:
        brecha = abs(spot / p.iloc[-1] - 1)
        # La comparación es orientativa: Kraken es precio actual y CM cierre diario.
        if brecha > 0.15:
            fallos.add(f"{nombre}_contraste", f"el precio spot de contraste difiere {brecha:.0%} del último cierre")
        return n(spot)
    return None


def macro_datos(fallos) -> dict:
    out: dict = {}
    series = {"tipo_real_10a_pct": "DFII10", "bono_10a_pct": "DGS10",
              "dolar_amplio_fed_no_es_dxy": "DTWEXBGS", "m2_eeuu_no_es_global_mm_usd": "WM2NS"}
    fred_caido = False
    for nombre, codigo in series.items():
        if fred_caido:  # no esperar el tiempo límite cuatro veces seguidas
            fallos.add(f"fred_{codigo}", "omitido: FRED no respondió en la serie anterior")
            continue
        s = intenta(fallos, f"fred_{codigo}", fred, codigo)
        fred_caido = s is None
        if s is not None and len(s):
            out[nombre] = {"valor": n(s.iloc[-1]), "fecha": s.index[-1].strftime("%Y-%m-%d"),
                           "var_30d_pct": var_pct(s, 30), "fuente": f"FRED {codigo}"}
    s = intenta(fallos, "stablecoins", defillama_stablecoins)
    if s is not None and len(s):
        out["stablecoins_total_usd"] = {"valor": n(s.iloc[-1], 0), "fecha": s.index[-1].strftime("%Y-%m-%d"),
                                        "var_30d_pct": var_pct(s, 30), "var_90d_pct": var_pct(s, 90),
                                        "fuente": "DefiLlama"}
    return out


def derivados(moneda, ahora, ruta_oi, fecha, fallos) -> dict:
    d = intenta(fallos, f"hyperliquid_{moneda}", hyperliquid, moneda, ahora)
    if d is None:
        return {}
    h = actualizar_oi(ruta_oi, fecha, moneda, d["open_interest_usd"])
    d["oi_var_7d_pct"], d["oi_var_30d_pct"] = var_pct(h, 7), var_pct(h, 30)
    d["fuente"] = "Hyperliquid (un solo mercado, no agregado)"
    return d


def solana_datos(sol_precio, fallos) -> dict:
    out: dict = {}
    tvl = intenta(fallos, "tvl_solana", defillama_tvl_solana)
    if tvl is not None:
        tvl = tvl[tvl.index <= sol_precio.index[-1]]  # misma fecha que el precio de SOL
    if tvl is not None and len(tvl):
        out["tvl_usd"], out["tvl_fecha"] = n(tvl.iloc[-1], 0), tvl.index[-1].strftime("%Y-%m-%d")
        out["tvl_usd_var_90d_pct"] = var_pct(tvl, 90)
        out["tvl_en_sol_var_90d_pct"] = var_pct((tvl / sol_precio).dropna(), 90)
    for clave, tipo in (("fees", "dailyFees"), ("ingresos_red", "dailyRevenue")):
        s = intenta(fallos, f"{clave}_solana", defillama_fees_cadena, "solana", tipo)
        if s is not None and len(s) > 7:
            s = s.iloc[:-1]  # el último día suele ir incompleto
            if clave == "fees":
                out["_serie_comisiones"] = s
            out[f"{clave}_media_7d_usd"] = n(s.tail(7).mean(), 0)
            out[f"{clave}_var_vs_30d_previos_pct"] = pct((s.tail(7).mean() / s.iloc[-37:-7].mean() - 1) * 100)
            out[f"{clave}_fuente"] = "DefiLlama red solana"
    s = intenta(fallos, "fees_apps_solana", defillama_fees_apps, "solana", "dailyFees")
    if s is not None and len(s) > 7:  # informativo: actividad del ecosistema, no de la red
        s = s.iloc[:-1]
        out["fees_apps_ecosistema_media_7d_usd"] = n(s.tail(7).mean(), 0)
        out["fees_apps_ecosistema_var_vs_30d_previos_pct"] = pct((s.tail(7).mean() / s.iloc[-37:-7].mean() - 1) * 100)
    s = intenta(fallos, "stablecoins_solana", defillama_stablecoins, "Solana")
    if s is not None and len(s):
        out["stablecoins_solana_usd"] = n(s.iloc[-1], 0)
        out["stablecoins_solana_var_30d_pct"] = var_pct(s, 30)
    return out


def valoracion_mercado(moneda: str, m: dict | None, base: pd.Series | None, base_nombre: str,
                       dir_salida: Path, fecha: str) -> dict:
    """Bloque común a las cinco monedas.

    `base` es la serie diaria con la que se divide la capitalización: comisiones de red en las
    cadenas (BTC, SOL, SUI) e ingresos del protocolo en HYPE y PUMP. Además del cociente actual,
    se da su percentil frente a los últimos 12 meses de la misma moneda: así cada una se compara
    consigo misma, que es lo único que tiene sentido entre activos tan distintos.
    """
    out: dict = {}
    if not (m and m.get("mcap_usd")):
        return out
    out["mcap_usd"], out["fdv_usd"] = n(m["mcap_usd"], 0), n(m.get("fdv_usd"), 0)
    out["oferta_circulante"] = n(m.get("oferta_circulante"), 0)
    if m.get("fdv_usd"):
        out["fdv_sobre_mcap"] = pct(m["fdv_usd"] / m["mcap_usd"], 2)
    h = actualizar_historial(dir_salida / "historial_mcap.csv", fecha, moneda, float(m["mcap_usd"]), "mcap_usd")
    out["mcap_var_30d_pct"] = var_pct(h, 30)
    out["valoracion_base"] = base_nombre
    if base is not None and len(base) >= 7 and base.tail(7).mean() > 0:
        actual = m["mcap_usd"] / (base.tail(7).mean() * 365)
        out["mcap_sobre_base_anualizada"] = pct(actual, 1)
        hist = m.get("historial_mcap")
        if hist is not None and len(hist):
            anual = base.rolling(7).mean() * 365
            ratio = (hist / anual.reindex(hist.index)).replace([float("inf")], float("nan")).dropna()
            ratio = ratio[ratio.index > ratio.index.max() - pd.Timedelta(days=365)]
            if len(ratio) >= 180:
                out["mcap_sobre_base_percentil_365d"] = pct((ratio <= actual).mean() * 100, 1)
                out["mcap_sobre_base_min_365d"] = pct(ratio.min(), 1)
                out["mcap_sobre_base_max_365d"] = pct(ratio.max(), 1)
    out["mercado_fuente"] = "CoinGecko"
    return out


def fundamentales_btc(mercado: dict | None, dir_salida: Path, fecha: str, fallos: Fallos) -> dict:
    """Comisiones de BTC (DefiLlama) y valoración común. Informativo: para BTC manda el MVRV."""
    out: dict = {}
    s = intenta(fallos, "btc_comisiones", defillama_fees_cadena, "bitcoin", "dailyFees")
    if s is not None and len(s) <= 7:
        s = None
    if s is not None:
        s = s.iloc[:-1]  # el último día suele ir incompleto
        out["comisiones_media_7d_usd"] = n(s.tail(7).mean(), 0)
        if len(s) >= 37:
            out["comisiones_var_vs_30d_previos_pct"] = pct((s.tail(7).mean() / s.iloc[-37:-7].mean() - 1) * 100)
        out["comisiones_fuente"] = "DefiLlama red bitcoin"
    out.update(valoracion_mercado("BTC", (mercado or {}).get("bitcoin"), s, "comisiones de red (sin emisión)",
                                  dir_salida, fecha))
    out["nota"] = ("Informativo, no entra en ninguna familia: a los mineros les paga sobre todo la "
                   "emisión. La métrica de valoración de BTC es el MVRV (sección onchain).")
    return out


def fundamentales_cesta(moneda: str, p: pd.Series, mercado: dict | None, dir_salida: Path,
                        fecha: str, fallos: Fallos) -> dict:
    """TVL, comisiones, ingresos y capitalización de un activo cesta, con sus fuentes."""
    cfg, k, out = CESTA[moneda], moneda.lower(), {}
    tvl, usado, motivos = primera_que_funcione(cfg["tvl_chain"], defillama_chain_tvl)
    if cfg["tvl_chain"]:
        if tvl is None:
            fallos.add(f"{k}_tvl", " | ".join(motivos))
        else:
            tvl = tvl[tvl.index <= p.index[-1]]
            if len(tvl):
                out.update({"tvl_usd": n(tvl.iloc[-1], 0), "tvl_fecha": tvl.index[-1].strftime("%Y-%m-%d"),
                            "tvl_usd_var_90d_pct": var_pct(tvl, 90),
                            "tvl_nativo_var_90d_pct": var_pct((tvl / p).dropna(), 90), "tvl_fuente": f"DefiLlama {usado}"})
    series: dict = {}
    for clave, tipo in (("fees", "dailyFees"), ("ingresos", "dailyRevenue")):
        serie, usado, motivos = None, None, []
        if cfg["fees_protocolo"]:
            serie, usado, motivos = primera_que_funcione(cfg["fees_protocolo"], defillama_fees_protocolo, tipo)
            usado = usado and f"DefiLlama protocolo {usado}"
        if serie is None and cfg["fees_chain"]:
            serie, u2, m2 = primera_que_funcione(cfg["fees_chain"], defillama_fees_cadena, tipo)
            usado, motivos = (u2 and f"DefiLlama red {u2}"), motivos + m2
        if serie is None:
            if cfg["fees_protocolo"] or cfg["fees_chain"]:
                fallos.add(f"{k}_{clave}", " | ".join(motivos))
            continue
        serie = serie.iloc[:-1] if len(serie) > 7 else serie  # el último día suele ir incompleto
        series[clave] = serie
        if len(serie) >= 37:
            out[f"{clave}_media_7d_usd"] = n(serie.tail(7).mean(), 0)
            out[f"{clave}_var_vs_30d_previos_pct"] = pct((serie.tail(7).mean() / serie.iloc[-37:-7].mean() - 1) * 100)
        elif len(serie) >= 7:
            out[f"{clave}_media_7d_usd"] = n(serie.tail(7).mean(), 0)
        out[f"{clave}_fuente"] = usado
    if cfg.get("apps"):  # informativo: suma de las apps sobre la cadena (no es la red)
        a = intenta(fallos, f"{k}_fees_apps", defillama_fees_apps, cfg["apps"], "dailyFees")
        if a is not None and len(a) > 37:
            a = a.iloc[:-1]
            out["fees_apps_ecosistema_media_7d_usd"] = n(a.tail(7).mean(), 0)
            out["fees_apps_ecosistema_var_vs_30d_previos_pct"] = pct((a.tail(7).mean() / a.iloc[-37:-7].mean() - 1) * 100)
    cadena = cfg.get("tipo") == "cadena"
    out.update(valoracion_mercado(moneda, (mercado or {}).get(cfg["coingecko"]),
                                  series.get("fees" if cadena else "ingresos"),
                                  "comisiones de red" if cadena else "ingresos del protocolo", dir_salida, fecha))
    return out


def familias_cesta(t: dict, c: dict, rel: dict, f: dict, tipo: str = "protocolo") -> dict:
    u, pr = UMBRALES, rel.get("percentil_52s")
    if tipo == "cadena":
        c_val = cond("capitalización / comisiones de red en el 20 % más bajo de 12 meses",
                     si(f.get("mcap_sobre_base_percentil_365d"), lambda v: v <= u["cadena_valoracion_percentil_max"]))
        c_act = cond("comisiones de red de 7 días no caen más del 20 % frente a los 30 anteriores",
                     si(f.get("fees_var_vs_30d_previos_pct"), lambda v: v >= u["cesta_ingresos_caida_max_pct"]))
    else:
        c_val = cond("capitalización / ingresos del protocolo anualizados por debajo de 20",
                     si(f.get("mcap_sobre_base_anualizada"), lambda v: v < u["cesta_mcap_ingresos_max"]))
        c_act = cond("ingresos de 7 días no caen más del 20 % frente a los 30 anteriores",
                     si(f.get("ingresos_var_vs_30d_previos_pct"), lambda v: v >= u["cesta_ingresos_caida_max_pct"]))
    return {
        "valoracion_relativa": familia([
            cond("ratio frente a BTC en el 20 % inferior de 52 semanas", si(pr, lambda v: v <= u["cesta_ratio_percentil_bajo"])),
            cond("precio bajo la media de 200 días",
                 None if t["sma200d"] is None else t["precio_referencia_usd"] < t["sma200d"]),
            cond("caída desde su máximo de al menos 70 %", c["caida_desde_maximo_pct"] <= u["cesta_caida_maximo_pct"]),
            c_val,
        ]),
        "actividad": familia([
            c_act,
            cond("TVL en unidades nativas estable a 90 días",
                 si(f.get("tvl_nativo_var_90d_pct"), lambda v: v >= u["cesta_tvl_nativo_estable_pct"])),
        ]),
        "riesgo_oferta": familia([
            cond("FDV / capitalización por encima de 2 (presión de desbloqueos)",
                 si(f.get("fdv_sobre_mcap"), lambda v: v > u["cesta_fdv_mcap_aviso"])),
        ]),
    }


def otra_moneda(moneda, p_btc, ahora, ruta_oi, fecha, fallos, mercado=None, dir_salida=None,
                ayer=None) -> dict | None:
    p = intenta(fallos, f"{moneda.lower()}_precio", hyperliquid_velas, moneda, ahora)
    if p is None:
        return None
    k, cfg = moneda.lower(), CESTA[moneda]
    tipo_spot, par = cfg["spot"]
    try:  # contraste orientativo: que no exista par spot no es un fallo del archivo
        if tipo_spot == "hyperliquid_spot":
            spot = hyperliquid_spot(par, float(p.iloc[-1]))
        else:
            spot = kraken_precio(par)
        fuente_spot = "Hyperliquid spot" if tipo_spot == "hyperliquid_spot" else "Kraken"
    except Exception as e:
        spot, fuente_spot = None, None
        cg = ((mercado or {}).get(cfg["coingecko"]) or {}).get("precio_spot_usd")
        if cg:  # respaldo: precio spot agregado de CoinGecko
            spot, fuente_spot = float(cg), "CoinGecko (respaldo)"
        elif str(e).startswith("ningún par"):  # hay pares pero ninguno encaja: se anota para diagnosticar
            fallos.add(f"{k}_contraste_par", limpiar(str(e))[:400])
    spot = validar_precio(p, k, ahora, fallos, spot)
    rel: dict = {}
    if p_btc is not None:
        ratio = (p / p_btc).dropna()
        if len(ratio):
            r52 = ratio.tail(364)
            rel = {"ratio_btc": n(ratio.iloc[-1], 10), "percentil_52s": pct((r52 <= ratio.iloc[-1]).mean() * 100, 1),
                   "percentil_desde_listado": pct((ratio <= ratio.iloc[-1]).mean() * 100, 1),
                   "minimo_52s": n(r52.min(), 10), "maximo_52s": n(r52.max(), 10)}
    t, c = tendencia_precio(p), ciclo(p)
    t["precio_spot_contraste_usd"] = spot
    t["precio_spot_contraste_fuente"] = fuente_spot
    f = fundamentales_cesta(moneda, p, mercado, dir_salida or Path("."), fecha, fallos)
    fam = familias_cesta(t, c, rel, f, cfg.get("tipo", "protocolo"))
    pr = rel.get("percentil_52s")
    techo = {"percentil_52s": pr, "umbral": UMBRALES["cesta_ratio_percentil_techo"],
             "supera": None if pr is None else bool(pr > UMBRALES["cesta_ratio_percentil_techo"])}
    diario = None if ayer is None else t["fecha_ultimo_dato"] == ayer
    if diario is False:
        fallos.add(f"{k}_dato_diario_retrasado", f"último dato diario {t['fecha_ultimo_dato']}, se esperaba {ayer}")
    return {"fuente_precio": "Hyperliquid, perpetuo (no es precio spot)",
            "primer_dato": p.index[0].strftime("%Y-%m-%d"),
            "resumen": {
                "precio_referencia_usd": t["precio_referencia_usd"], "precio_referencia_fecha": t["fecha_ultimo_dato"],
                "dato_diario_al_dia": diario, "cierre_semanal_usd": t["cierre_semanal_usd"],
                "cierre_semanal_fecha": t["fecha_ultimo_cierre_semanal"],
                "familias_cumplidas_de_medibles": {kk: f"{v['cumplidas']}/{v['medibles']}" for kk, v in fam.items()},
                "techo_ratio_btc": techo,
                "semanas_desde_maximo": c["semanas_desde_maximo"], "caida_desde_maximo_pct": c["caida_desde_maximo_pct"],
                "rebote_desde_minimo_pct": c["rebote_desde_minimo_pct"]},
            "tendencia": t, "ciclo": c, "ratio_btc": rel, "fundamentales": f, "familias": fam,
            "derivados": derivados(moneda, ahora, ruta_oi, fecha, fallos)}


NO_DISPONIBLES = {
    "LTH-SOPR": "BGeometrics no respondió en esta ejecución",
    "liquidaciones agregadas": "sin fuente gratuita fiable",
    "skew de opciones y mapas de liquidaciones": "no incluidos",
    "reservas y netflows de exchanges": "métrica de pago",
    "flujos de ETF": "sin fuente gratuita estable",
    "M2 global": "solo se publica M2 de EE. UU.",
    "DXY": "se publica el índice amplio del dólar de la Fed, no el DXY",
    "unlocks y staking neto de SOL": "sin fuente gratuita estable",
    "direcciones activas y volumen DEX de SUI, HYPE y PUMP": "no incluidos; la actividad se mide por ingresos y TVL",
    "sentimiento en X": "lo aporta Grok, no este archivo",
}


def construir(ahora: datetime, dir_salida: Path) -> dict:
    fallos = Fallos()
    avisos: list[str] = []
    fecha = ahora.strftime("%Y-%m-%d")
    ruta_oi = dir_salida / "historial_oi.csv"
    domingo = ultimo_domingo_cerrado(ahora)
    anterior = None
    ruta_anterior = dir_salida / "senales_latest.json"
    if ruta_anterior.exists():
        try:
            anterior = json.loads(ruta_anterior.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            fallos.add("archivo_anterior", f"no se pudo leer: {e}")
    semana = archivo_hace_7_dias(dir_salida, ahora, fallos)

    def al_dia(t: dict, nombre: str) -> bool:
        ok = t["fecha_ultimo_cierre_semanal"] == domingo.strftime("%Y-%m-%d")
        if not ok:
            fallos.add(f"{nombre}_cierre_semanal_retrasado",
                       f"último cierre semanal {t['fecha_ultimo_cierre_semanal']}, se esperaba {domingo:%Y-%m-%d}")
        return ok

    ayer = (pd.Timestamp(ahora).tz_localize(None).normalize() - pd.Timedelta(days=1)).strftime("%Y-%m-%d")

    def diario_al_dia(t: dict, nombre: str) -> bool:
        """El cierre diario de ayer (UTC) ya está en el archivo."""
        ok = t["fecha_ultimo_dato"] == ayer
        if not ok:
            fallos.add(f"{nombre}_dato_diario_retrasado",
                       f"último dato diario {t['fecha_ultimo_dato']}, se esperaba {ayer}")
        return ok

    def cm(clave, activo, metrica):
        return intenta(fallos, clave, coinmetrics, activo, metrica)

    p_btc = cm("btc_precio", "btc", "PriceUSD")
    mcap = cm("btc_capmercado", "btc", "CapMrktCurUSD")
    oferta = cm("btc_oferta", "btc", "SplyCur")
    hash_rate = cm("btc_hashrate", "btc", "HashRate")
    emision = cm("btc_emision", "btc", "IssTotUSD")
    p_sol = cm("sol_precio", "sol", "PriceUSD")

    resultado: dict = {"btc": {}, "sol": {}, "macro": macro_datos(fallos)}
    fg = intenta(fallos, "fear_greed", fear_greed)
    sent: dict = {}
    if fg is not None and len(fg):
        sent = {"valor": n(fg.iloc[-1], 0), "fecha": fg.index[-1].strftime("%Y-%m-%d"),
                "dias_seguidos_miedo_extremo": dias_miedo(fg), "fuente": "alternative.me"}
    resultado["sentimiento"] = sent

    ids_cg = ["bitcoin", "solana"] + [CESTA[m]["coingecko"] for m in OTRAS_MONEDAS]
    mercado = intenta(fallos, "coingecko", coingecko_mercado, ids_cg)
    anadir_historiales(mercado, ids_cg, fallos)

    confirmacion_btc = None
    if p_btc is not None:
        spot = intenta(fallos, "kraken_btc", kraken_precio, "XBTUSD")
        spot = validar_precio(p_btc, "btc", ahora, fallos, spot)
        t = tendencia_precio(p_btc)
        t["precio_kraken_contraste_usd"] = spot
        der = derivados("BTC", ahora, ruta_oi, fecha, fallos)
        rcap, rp, fuente_rp = realizado_btc(p_btc, mcap, oferta, fallos, avisos)
        lth = intenta(fallos, "btc_lth_sopr", bgeometrics, "lth-sopr", True)
        oc = intenta(fallos, "btc_onchain", onchain_btc, p_btc, mcap, rcap, rp, hash_rate, emision, lth) or {}
        if fuente_rp:
            oc["realized_fuente"] = fuente_rp
        if rp is not None:
            resultado["pausa_sistema"] = intenta(fallos, "btc_pausa", pausa, p_btc, rp)
        fam = familias_btc(t, oc, der, sent, hash_rate, p_btc)
        confirmacion_btc = fam["confirmacion"]["cumplidas"] > 0 if fam["confirmacion"]["medibles"] else None
        c = ciclo(p_btc)
        resultado["btc"].update({
            "resumen": resumen_activo(t, c, fam, resultado.get("pausa_sistema"), al_dia(t, "btc"),
                                      diario_al_dia(t, "btc")),
            "tendencia": t, "ciclo": c, "onchain": oc, "derivados": der,
            "fundamentales": fundamentales_btc(mercado, dir_salida, fecha, fallos), "familias": fam,
            "resolucion_eventos": resolucion_eventos(semanal(p_btc))})
    if p_sol is not None:
        spot = intenta(fallos, "kraken_sol", kraken_precio, "SOLUSD")
        spot = validar_precio(p_sol, "sol", ahora, fallos, spot)
        t = tendencia_precio(p_sol)
        t["precio_kraken_contraste_usd"] = spot
        der = derivados("SOL", ahora, ruta_oi, fecha, fallos)
        sd = solana_datos(p_sol, fallos)
        sd.update(valoracion_mercado("SOL", (mercado or {}).get("solana"), sd.pop("_serie_comisiones", None),
                                     "comisiones de red", dir_salida, fecha))
        ratio_pct = None
        rel: dict = {}
        if p_btc is not None:
            ratio = (p_sol / p_btc).dropna()
            r52 = ratio.tail(364)
            ratio_pct = pct((r52 <= ratio.iloc[-1]).mean() * 100, 1)
            rel = {"ratio_sol_btc": n(ratio.iloc[-1], 6), "percentil_52s": ratio_pct,
                   "minimo_52s": n(r52.min(), 6), "maximo_52s": n(r52.max(), 6)}
        fam = familias_sol(t, ratio_pct, sd, der, sent, confirmacion_btc)
        c = ciclo(p_sol)
        resultado["sol"] = {"resumen": resumen_activo(t, c, fam, resultado.get("pausa_sistema"), al_dia(t, "sol"),
                                                      diario_al_dia(t, "sol")),
                            "tendencia": t, "ciclo": c, "ratio_sol_btc": rel,
                            "derivados": der, "fundamentales": sd, "familias": fam,
                            "resolucion_eventos": resolucion_eventos(semanal(p_sol))}

    resultado["otras_monedas"] = {
        "nota": "Activos cesta: sus tramos siguen a los de SOL según la política; aquí van sus hechos propios.",
        **{m.lower(): otra_moneda(m, p_btc, ahora, ruta_oi, fecha, fallos, mercado, dir_salida, ayer)
           for m in OTRAS_MONEDAS}}

    sin_dato = dict(NO_DISPONIBLES)
    if (resultado["btc"].get("onchain") or {}).get("lth_sopr") is not None:
        sin_dato.pop("LTH-SOPR", None)

    criticos = [c for c in CRITICOS if fallos.contiene(c)]
    estado = "FALLO" if criticos else ("PARCIAL" if fallos.items else "OK")
    doc = {
        "version_script": VERSION,
        "generado_utc": ahora.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "valido_hasta_utc": (ahora + timedelta(hours=36)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "estado": estado,
        "fallos_criticos": criticos,
        "fallos": fallos.items,
        "avisos": avisos,
        "aviso": "Solo datos y condiciones objetivas. Lo que no aparece es SIN DATO.",
        "ultimo_domingo_cerrado": domingo.strftime("%Y-%m-%d"),
        "cambios_desde_archivo_anterior": cambios(resultado, anterior),
        "cambios_desde_hace_7_dias": cambios(resultado, semana),
        "eventos_calibracion": EVENTOS,
        "sin_dato": sin_dato,
        "umbrales": UMBRALES,
        "atribucion": "Datos de red y precio: Coin Metrics Community (CC BY-NC 4.0). "
                      "También DefiLlama, FRED, alternative.me, Hyperliquid, Kraken y BGeometrics.",
        **resultado,
    }
    doc = {"snapshot_id": hashlib.sha256(
        json.dumps(doc, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:12], **doc}
    return doc


def tabla(titulo: str, d: dict) -> list[str]:
    filas = [f"\n### {titulo}\n", "| Dato | Valor |", "|---|---|"]
    for k, v in d.items():
        if not isinstance(v, (dict, list)):
            filas.append(f"| {k} | {SIN_DATO if v is None else v} |")
    for k, v in d.items():
        if k.startswith("ultimos_") and v:
            filas.append(f"\n{k}: " + ", ".join(f"{f} = {x}" for f, x in v.items()))
    return filas


def a_markdown(doc: dict) -> str:
    o = [f"# Señales {doc['generado_utc'][:10]}", "",
         f"- Snapshot: `{doc['snapshot_id']}`", f"- Estado: **{doc['estado']}**",
         f"- Generado: {doc['generado_utc']}", f"- Válido hasta: {doc['valido_hasta_utc']}"]
    for f in doc["fallos"]:
        o.append(f"- Fallo `{f['clave']}`: {f['motivo']}")
    for a in doc.get("avisos", []):
        o.append(f"- Aviso: {a}")
    for titulo, clave_doc in (("Cambios desde el archivo anterior", "cambios_desde_archivo_anterior"),
                              ("Cambios en los últimos 7 días", "cambios_desde_hace_7_dias")):
        cb = doc.get(clave_doc) or {}
        o.append(f"\n## {titulo}\n")
        if not cb.get("archivo_anterior_snapshot"):
            o.append("Sin archivo de referencia.")
        elif not cb["condiciones_cambiadas"]:
            o.append(f"Ninguna condición ha cambiado desde el snapshot `{cb['archivo_anterior_snapshot']}` "
                     f"({cb.get('archivo_anterior_generado')}).")
        for c in cb.get("condiciones_cambiadas", []):
            f = lambda v: SIN_DATO if v is None else v
            o.append(f"- {c['clave']}: {f(c['antes'])} → {f(c['ahora'])}")
    for activo in ("btc", "sol"):
        a = doc.get(activo) or {}
        o.append(f"\n## {activo.upper()}")
        if a.get("resumen"):
            o += tabla("Resumen para Estrategia", a["resumen"])
        for clave in ("tendencia", "ciclo", "onchain", "derivados", "ratio_sol_btc", "fundamentales"):
            if a.get(clave):
                o += tabla(clave.capitalize(), a[clave])
        for nombre, f in (a.get("familias") or {}).items():
            o.append(f"\n### Familia {nombre}: {f['cumplidas']} de {f['medibles']} medibles ({f['total']} en total)\n")
            for c in f["condiciones"]:
                marca = {True: "cumple", False: "no cumple", None: SIN_DATO}[c["cumple"]]
                o.append(f"- {c['condicion']}: {marca}")
        res = a.get("resolucion_eventos") or {}
        if res:
            o.append("\n### Resolución de eventos (últimas 30 semanas)\n\n| Cierre | USD | Evento 4 s | Evento 8 s |\n|---|---|---|---|")
            for fecha, r in list(res.items())[-30:]:
                o.append(f"| {fecha} | {r['cierre']} | {r['evento_4s']} | {r['evento_8s']} |")
    if doc.get("pausa_sistema"):
        o += tabla("Pausa del sistema (calculada sobre BTC, aplica a BTC y SOL)", doc["pausa_sistema"])
    otras = doc.get("otras_monedas") or {}
    o.append(f"\n## Otras monedas\n\n{otras.get('nota', '')}")
    for m in OTRAS_MONEDAS:
        a = otras.get(m.lower())
        o.append(f"\n## {m}")
        if not a:
            o.append(f"\n{SIN_DATO}")
            continue
        o.append(f"\nFuente de precio: {a['fuente_precio']}. Datos desde {a['primer_dato']}.")
        if a.get("resumen"):
            r = dict(a["resumen"]); techo = r.pop("techo_ratio_btc", None)
            o += tabla(f"{m} resumen", r)
            if techo:
                o.append(f"\nTecho ratio/BTC: percentil {techo['percentil_52s']} (umbral {techo['umbral']}) → "
                         f"{'SUPERA' if techo['supera'] else 'no supera' if techo['supera'] is not None else SIN_DATO}")
        for clave in ("tendencia", "ciclo", "ratio_btc", "fundamentales", "derivados"):
            if a.get(clave):
                o += tabla(f"{m} {clave}", a[clave])
        for nombre, fm in (a.get("familias") or {}).items():
            o.append(f"\n### {m} familia {nombre}: {fm['cumplidas']} de {fm['medibles']} medibles ({fm['total']} en total)\n")
            for cnd in fm["condiciones"]:
                marca = {True: "cumple", False: "no cumple", None: SIN_DATO}[cnd["cumple"]]
                o.append(f"- {cnd['condicion']}: {marca}")
    o.append("\n## Macro\n\n| Dato | Valor | Fecha | Var. 30 d % | Fuente |\n|---|---|---|---|---|")
    for k, v in doc["macro"].items():
        o.append(f"| {k} | {v['valor']} | {v['fecha']} | {v.get('var_30d_pct')} | {v['fuente']} |")
    if doc["sentimiento"]:
        o += tabla("Sentimiento", doc["sentimiento"])
    o.append("\n## Eventos de calibración\n")
    o += [f"- **{k}**: {v}" for k, v in doc["eventos_calibracion"].items()]
    o.append("\n## Sin dato\n")
    o += [f"- {k}: {v}" for k, v in doc["sin_dato"].items()]
    o.append(f"\n{doc['atribucion']}\n")
    return "\n".join(o)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", default="salida")
    args = ap.parse_args()
    dir_salida = Path(args.salida)
    (dir_salida / "historico").mkdir(parents=True, exist_ok=True)
    ahora = datetime.now(timezone.utc).replace(microsecond=0)
    doc = construir(ahora, dir_salida)
    texto = json.dumps(doc, ensure_ascii=False, indent=2)
    (dir_salida / "senales_latest.json").write_text(texto, encoding="utf-8")
    (dir_salida / "senales_latest.md").write_text(a_markdown(doc), encoding="utf-8")
    (dir_salida / "historico" / f"senales_{ahora:%Y-%m-%d}.json").write_text(texto, encoding="utf-8")
    print(f"{doc['estado']} · snapshot {doc['snapshot_id']} · fallos: {len(doc['fallos'])}")
    for f in doc["fallos"]:
        print(f"  - {f['clave']}: {f['motivo']}")
    return 1 if doc["estado"] == "FALLO" else 0


if __name__ == "__main__":
    sys.exit(main())
