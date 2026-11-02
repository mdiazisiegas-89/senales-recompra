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

VERSION = "1.5"
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
OTRAS_MONEDAS = ["SUI", "HYPE", "PUMP"]
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


def defillama_fees_solana(tipo: str):
    d = get_json("https://api.llama.fi/overview/fees/solana", {
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
        "funding_medio_7d_pct_hora": n(f7 * 100, 6),
        "funding_medio_7d_anualizado_pct": n(f7 * 24 * 365 * 100, 1),
        "funding_medio_14d_pct_hora": n(s.mean() * 100, 6),
        "horas_funding_negativo_7d": int((s[s.index > corte] < 0).sum()),
        "open_interest_usd": n(float(ctx["openInterest"]) * float(ctx["markPx"]), 0),
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
        f"var_{nombre}_pct": n((c.iloc[-1] / c.iloc[-2] - 1) * 100) if len(c) > 1 else None,
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


def ultimo(s, i=-1):
    return s.iloc[i] if len(s) >= abs(i) else None


def var_pct(s: pd.Series, dias: int):
    """Variación frente al valor de hace `dias` días naturales."""
    if s is None or s.empty:
        return None
    previo = s[s.index <= s.index[-1] - pd.Timedelta(days=dias)]
    if previo.empty or previo.iloc[-1] == 0:
        return None
    return n((s.iloc[-1] / previo.iloc[-1] - 1) * 100)


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
        "var_semanal_pct": n((w.iloc[-1] / w.iloc[-2] - 1) * 100) if len(w) > 1 else None,
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
        "caida_desde_maximo_pct": n((w.iloc[-1] / w.max() - 1) * 100),
        "rebote_desde_minimo_pct": n((w.iloc[-1] / tras.min() - 1) * 100),
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


def resumen_activo(t: dict, c: dict, fam: dict, pausa_d: dict | None, al_dia: bool) -> dict:
    """Lo que las reglas de Estrategia nombran, en un solo bloque corto."""
    return {
        "precio_referencia_usd": t["precio_referencia_usd"],
        "precio_referencia_fecha": t["fecha_ultimo_dato"],
        "cierre_semanal_usd": t["cierre_semanal_usd"],
        "cierre_semanal_fecha": t["fecha_ultimo_cierre_semanal"],
        "cierre_semanal_al_dia": al_dia,
        "evento_4s_umbral_usd": n(t["cierre_semanal_usd"] * (1 - UMBRALES["evento_4s_caida_pct"] / 100)),
        "familias_cumplidas_de_medibles": {k: f"{v['cumplidas']}/{v['medibles']}" for k, v in fam.items()},
        "pausa_activa": None if pausa_d is None else pausa_d["activa"],
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
        if a.get("pausa"):
            out[f"{activo}.pausa_activa"] = a["pausa"]["activa"]
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
            cond("market cap / fees en mínimos", None),
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


def actualizar_oi(ruta: Path, fecha: str, moneda: str, oi: float) -> pd.Series:
    """El open interest no tiene histórico gratuito: lo guardamos nosotros."""
    columnas = ["fecha", "moneda", "oi_usd"]
    df = pd.read_csv(ruta) if ruta.exists() else pd.DataFrame(columns=columnas)
    df = df[~((df["fecha"] == fecha) & (df["moneda"] == moneda))]
    df = pd.concat([df, pd.DataFrame([[fecha, moneda, oi]], columns=columnas)], ignore_index=True)
    df = df.sort_values(["fecha", "moneda"])
    df.to_csv(ruta, index=False)
    h = df[df["moneda"] == moneda]
    return pd.Series(h["oi_usd"].astype(float).values, index=pd.to_datetime(h["fecha"]))


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
            fallos.add(f"{nombre}_contraste", f"Kraken difiere {brecha:.0%} del último cierre")
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
        s = intenta(fallos, f"{clave}_solana", defillama_fees_solana, tipo)
        if s is not None and len(s) > 7:
            s = s.iloc[:-1]  # el último día suele ir incompleto
            out[f"{clave}_media_7d_usd"] = n(s.tail(7).mean(), 0)
            out[f"{clave}_var_vs_30d_previos_pct"] = n((s.tail(7).mean() / s.iloc[-37:-7].mean() - 1) * 100)
    s = intenta(fallos, "stablecoins_solana", defillama_stablecoins, "Solana")
    if s is not None and len(s):
        out["stablecoins_solana_usd"] = n(s.iloc[-1], 0)
        out["stablecoins_solana_var_30d_pct"] = var_pct(s, 30)
    return out


def otra_moneda(moneda, p_btc, ahora, ruta_oi, fecha, fallos) -> dict | None:
    p = intenta(fallos, f"{moneda.lower()}_precio", hyperliquid_velas, moneda, ahora)
    if p is None:
        return None
    validar_precio(p, moneda.lower(), ahora, fallos)
    rel: dict = {}
    if p_btc is not None:
        ratio = (p / p_btc).dropna()
        if len(ratio):
            r52 = ratio.tail(364)
            rel = {"ratio_btc": n(ratio.iloc[-1], 10), "percentil_52s": n((r52 <= ratio.iloc[-1]).mean() * 100, 1)}
    return {"fuente_precio": "Hyperliquid, perpetuo (no es precio spot)",
            "primer_dato": p.index[0].strftime("%Y-%m-%d"),
            "tendencia": tendencia_precio(p), "ciclo": ciclo(p), "ratio_btc": rel,
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
            resultado["btc"]["pausa"] = intenta(fallos, "btc_pausa", pausa, p_btc, rp)
        fam = familias_btc(t, oc, der, sent, hash_rate, p_btc)
        confirmacion_btc = fam["confirmacion"]["cumplidas"] > 0 if fam["confirmacion"]["medibles"] else None
        c = ciclo(p_btc)
        resultado["btc"].update({
            "resumen": resumen_activo(t, c, fam, resultado["btc"].get("pausa"), al_dia(t, "btc")),
            "tendencia": t, "ciclo": c, "onchain": oc, "derivados": der, "familias": fam,
            "resolucion_eventos": resolucion_eventos(semanal(p_btc))})
    if p_sol is not None:
        spot = intenta(fallos, "kraken_sol", kraken_precio, "SOLUSD")
        spot = validar_precio(p_sol, "sol", ahora, fallos, spot)
        t = tendencia_precio(p_sol)
        t["precio_kraken_contraste_usd"] = spot
        der = derivados("SOL", ahora, ruta_oi, fecha, fallos)
        sd = solana_datos(p_sol, fallos)
        ratio_pct = None
        rel: dict = {}
        if p_btc is not None:
            ratio = (p_sol / p_btc).dropna()
            r52 = ratio.tail(364)
            ratio_pct = n((r52 <= ratio.iloc[-1]).mean() * 100, 1)
            rel = {"ratio_sol_btc": n(ratio.iloc[-1], 6), "percentil_52s": ratio_pct,
                   "minimo_52s": n(r52.min(), 6), "maximo_52s": n(r52.max(), 6)}
        fam = familias_sol(t, ratio_pct, sd, der, sent, confirmacion_btc)
        c = ciclo(p_sol)
        resultado["sol"] = {"resumen": resumen_activo(t, c, fam, None, al_dia(t, "sol")),
                            "tendencia": t, "ciclo": c, "ratio_sol_btc": rel,
                            "derivados": der, "fundamentales": sd, "familias": fam,
                            "resolucion_eventos": resolucion_eventos(semanal(p_sol))}

    resultado["otras_monedas"] = {
        "nota": "Solo informativas: no forman parte de los tramos RT1-RT4.",
        **{m.lower(): otra_moneda(m, p_btc, ahora, ruta_oi, fecha, fallos) for m in OTRAS_MONEDAS}}

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
        for clave in ("tendencia", "ciclo", "onchain", "derivados", "pausa", "ratio_sol_btc", "fundamentales"):
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
    otras = doc.get("otras_monedas") or {}
    o.append(f"\n## Otras monedas\n\n{otras.get('nota', '')}")
    for m in OTRAS_MONEDAS:
        a = otras.get(m.lower())
        o.append(f"\n## {m}")
        if not a:
            o.append(f"\n{SIN_DATO}")
            continue
        o.append(f"\nFuente de precio: {a['fuente_precio']}. Datos desde {a['primer_dato']}.")
        for clave in ("tendencia", "ciclo", "ratio_btc", "derivados"):
            if a.get(clave):
                o += tabla(f"{m} {clave}", a[clave])
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
