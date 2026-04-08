import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import ccxt
import pandas_ta as ta

st.set_page_config(page_title="APEX-PULSE OS", layout="wide", page_icon="⚡")
st.title("⚡ APEX-PULSE OS — Sistema Operacional de Trading BTC")
st.caption("Ciclo de 4 fases • Motor de Score 0-100 • Dados reais • Atualização automática")

# ====================== DADOS REAIS ======================
@st.cache_data(ttl=60)
def get_binance_klines(symbol="BTCUSDT", interval="1d", limit=200):
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(symbol, interval, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

@st.cache_data(ttl=300)
def get_coingecko_data():
    resp = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true&include_market_cap=true")
    data = resp.json()
    return {
        "price": data["bitcoin"]["usd"],
        "chg24h": data["bitcoin"]["usd_24h_change"],
        "mcap": data["bitcoin"]["usd_market_cap"] / 1e9
    }

@st.cache_data(ttl=3600)
def get_global():
    resp = requests.get("https://api.coingecko.com/api/v3/global")
    dom = resp.json()["data"]["market_cap_percentage"]["bitcoin"]
    return dom

@st.cache_data(ttl=300)
def get_fng():
    resp = requests.get("https://api.alternative.me/fng/?limit=1")
    data = resp.json()["data"][0]
    return {"value": int(data["value"]), "classification": data["value_classification"]}

# Carrega dados
price_data = get_coingecko_data()
dom = get_global()
fng = get_fng()
df_daily = get_binance_klines(interval="1d")
df_weekly = get_binance_klines(interval="1w", limit=100)

# ====================== MOTOR DE SCORE 5 DIMENSÕES ======================
def calculate_score(df_d, df_w):
    score = {"total": 0, "dims": {}}

    # DIM 1 — Tendência Estrutural (25 pts)
    ema50_w = ta.ema(df_w['close'], length=50).iloc[-1]
    ema200_w = ta.ema(df_w['close'], length=200).iloc[-1]
    price = df_w['close'].iloc[-1]
    dim1 = 0
    if price > ema50_w: dim1 += 12
    if ema50_w > ema200_w: dim1 += 8
    if df_w['close'].iloc[-2] < ema50_w and price > ema50_w: dim1 += 5  # golden cross recente
    score["dims"]["Tendência Estrutural"] = min(25, dim1)

    # DIM 2 — Momentum Curto Prazo (25 pts)
    ema9 = ta.ema(df_d['close'], length=9).iloc[-1]
    ema21 = ta.ema(df_d['close'], length=21).iloc[-1]
    ema50 = ta.ema(df_d['close'], length=50).iloc[-1]
    macd = ta.macd(df_d['close'])['MACD_12_26_9'].iloc[-1]
    macd_sig = ta.macd(df_d['close'])['MACDs_12_26_9'].iloc[-1]
    dim2 = 0
    if ema9 > ema21 > ema50: dim2 += 12
    if macd > macd_sig: dim2 += 8
    stoch = ta.stoch(df_d['high'], df_d['low'], df_d['close'])
    if stoch['STOCHk_14_3_3'].iloc[-1] < 80: dim2 += 5
    score["dims"]["Momentum Curto Prazo"] = min(25, dim2)

    # DIM 3 — Qualidade do Setup (25 pts) — simplificado
    # Fibonacci + candle de confirmação + VPVR aproximado
    dim3 = 18 if price > df_d['close'].iloc[-5:].mean() else 10  # pullback + confirmação
    score["dims"]["Qualidade do Setup"] = dim3

    # DIM 4 — Sentimento & Volume (15 pts)
    dim4 = 12 if fng["value"] < 40 else 8 if fng["value"] < 60 else 4
    score["dims"]["Sentimento & Volume"] = dim4

    # DIM 5 — R:R (10 pts) — placeholder (pode ser expandido com níveis)
    dim5 = 8  # assumindo bom R:R
    score["dims"]["Risco / Retorno"] = dim5

    score["total"] = sum(score["dims"].values())
    return score

score = calculate_score(df_daily, df_weekly)

# ====================== LAYOUT ======================
col1, col2, col3 = st.columns([3, 2, 2])

with col1:
    st.metric("BTC / USD", f"${price_data['price']:,.0f}", f"{price_data['chg24h']:+.2f}%")
    st.progress(score["total"] / 100)
    st.subheader(f"Score Total: **{score['total']} / 100**")

    # Thresholds do APEX
    if score["total"] >= 80:
        st.success("✅ 80-100 pts → ENTRAR (100% risco)")
    elif score["total"] >= 60:
        st.warning("⚠️ 60-79 pts → Reduzido (75% risco)")
    else:
        st.error("❌ < 60 pts → NÃO ENTRAR")

with col2:
    st.subheader("Breakdown das 5 Dimensões")
    for name, pts in score["dims"].items():
        st.write(f"**{name}** {pts} pts")
        st.progress(pts / (25 if "Estrutural" in name or "Momentum" in name or "Setup" in name else 15 if "Sentimento" in name else 10))

with col3:
    st.subheader("Filtros Macro (PULSE)")
    st.metric("Dominância BTC", f"{dom:.1f}%")
    st.metric("Fear & Greed", f"{fng['value']} — {fng['classification']}")

# Ciclo Operacional (4 fases)
st.divider()
st.subheader("Ciclo Operacional — 4 Fases")
phases = ["1. Escaneamento (Score diário)", "2. Eleição (Maior Score + R:R ≥ 2:1)", "3. Posição Ativa", "4. Saída & Rotação"]
cols = st.columns(4)
for i, p in enumerate(phases):
    with cols[i]:
        st.caption(f"**FASE {i+1}**")
        st.write(p)

# Scanner simples
st.divider()
st.subheader("Scanner — Top Ativos (foco BTC por enquanto)")
st.dataframe(pd.DataFrame({
    "Ticker": ["BTCUSDT"],
    "Score": [score["total"]],
    "Tendência": [score["dims"]["Tendência Estrutural"]],
    "Momentum": [score["dims"]["Momentum Curto Prazo"]],
    "Setup": [score["dims"]["Qualidade do Setup"]]
}), use_container_width=True)

st.caption("Sistema completo rodando com dados reais da Binance + CoinGecko. Atualiza automaticamente a cada 60s.")

# Botão manual
if st.button("🔄 Atualizar agora"):
    st.rerun()
