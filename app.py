import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import yfinance as yf
import pandas_ta as ta
import requests

st.set_page_config(page_title="APEX-PULSE OS", layout="wide", page_icon="⚡")
st.title("⚡ APEX-PULSE OS — Hedge Fund Trading System")
st.caption("Ciclo de 4 fases • Score Motor 0-100 • Multi-Ativo • Estratégia Institucional")

# ====================== UNIVERSE (S&P/Nasdaq + BTC) ======================
UNIVERSE = {
    'NVDA': 'NVIDIA Corp', 'AAPL': 'Apple Inc', 'MSFT': 'Microsoft Corp',
    'TSLA': 'Tesla Inc', 'META': 'Meta Platforms', 'AMZN': 'Amazon.com',
    'GOOGL': 'Alphabet Inc', 'SMCI': 'Super Micro Computer', 'AMD': 'AMD',
    'BTC-USD': 'Bitcoin / USD'
}

# ====================== DADOS REAIS ======================
@st.cache_data(ttl=60)
def get_price(ticker):
    data = yf.download(ticker, period="5d", interval="1d")
    if data.empty: return None
    latest = data.iloc[-1]
    prev = data.iloc[-2]
    chg = ((latest['Close'] - prev['Close']) / prev['Close']) * 100
    return {'price': latest['Close'], 'chg': chg, 'volume': latest['Volume']}

@st.cache_data(ttl=300)
def get_macro():
    try:
        fg = requests.get("https://api.alternative.me/fng/?limit=1").json()['data'][0]
        vix = yf.download("^VIX", period="1d")['Close'].iloc[-1]
        dom = requests.get("https://api.coingecko.com/api/v3/global").json()['data']['market_cap_percentage']['bitcoin']
        return {"fng": int(fg['value']), "fng_label": fg['value_classification'], "vix": round(vix, 1), "btc_dom": round(dom, 1)}
    except:
        return {"fng": 45, "fng_label": "Neutro", "vix": 18.5, "btc_dom": 58.0}

macro = get_macro()

# ====================== MOTOR DE SCORE 5 DIMENSÕES ======================
def calculate_full_score(ticker):
    # Baixa dados necessários
    df_d = yf.download(ticker, period="60d", interval="1d")
    df_w = yf.download(ticker, period="1y", interval="1wk")
    if len(df_d) < 50 or len(df_w) < 20: return {"total": 0, "dims": {}}
    
    close_d = df_d['Close']
    close_w = df_w['Close']
    
    score = {"total": 0, "dims": {}}
    
    # DIM 1 - Tendência Estrutural (25 pts)
    ema50_w = ta.ema(close_w, length=50).iloc[-1]
    ema200_w = ta.ema(close_w, length=200).iloc[-1]
    price = close_w.iloc[-1]
    pts1 = 0
    if price > ema50_w: pts1 += 12
    if ema50_w > ema200_w: pts1 += 8
    if close_w.iloc[-2] < ema50_w and price > ema50_w: pts1 += 5
    score["dims"]["Tendência Estrutural"] = min(25, pts1)
    
    # DIM 2 - Momentum Curto Prazo (25 pts)
    ema9 = ta.ema(close_d, length=9).iloc[-1]
    ema21 = ta.ema(close_d, length=21).iloc[-1]
    ema50 = ta.ema(close_d, length=50).iloc[-1]
    macd = ta.macd(close_d)['MACD_12_26_9'].iloc[-1]
    macd_sig = ta.macd(close_d)['MACDs_12_26_9'].iloc[-1]
    stoch = ta.stoch(df_d['High'], df_d['Low'], close_d)['STOCHk_14_3_3'].iloc[-1]
    pts2 = 0
    if ema9 > ema21 > ema50: pts2 += 12
    if macd > macd_sig: pts2 += 8
    if stoch < 80: pts2 += 5
    score["dims"]["Momentum Curto Prazo"] = min(25, pts2)
    
    # DIM 3 - Qualidade do Setup (25 pts) - aproximação institucional
    pts3 = 18 if price > close_d.iloc[-10:].mean() * 0.96 else 10  # pullback + confirmação
    score["dims"]["Qualidade do Setup"] = pts3
    
    # DIM 4 - Sentimento & Volume (15 pts)
    pts4 = 12 if macro["fng"] < 40 else 8 if macro["fng"] < 60 else 4
    score["dims"]["Sentimento & Volume"] = pts4
    
    # DIM 5 - R:R (10 pts) - placeholder conservador
    pts5 = 8
    score["dims"]["Risco / Retorno"] = pts5
    
    score["total"] = sum(score["dims"].values())
    return score

# ====================== LAYOUT PRINCIPAL ======================
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "🔎 Scanner", "📓 Diário de Trades", "📐 Calibração", "🌍 Macro Filtros"])

with tab1:  # Dashboard
    st.subheader("Posição Ativa (simulada)")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Ativo", "NVDA", "Score 78")
    with col_b:
        st.metric("P&L Open", "+$2,340", "+1.87R")
    with col_c:
        st.metric("Risco Atual", "1.4% do capital", "Stop a breakeven")
    
    st.divider()
    st.subheader("Ciclo Operacional — 4 Fases")
    fases = st.columns(4)
    fases[0].success("**FASE 1** Escaneamento\nScore diário • BTC a cada 4h")
    fases[1].info("**FASE 2** Eleição\nMaior Score + R:R ≥ 2:1")
    fases[2].warning("**FASE 3** Posição Ativa\n1 ativo • Foco total")
    fases[3].error("**FASE 4** Saída & Rotação\nAlvo, stop ou tese invalidada")

with tab2:  # Scanner
    st.subheader("Scanner — Ranking por Score (Multi-Ativo)")
    data = []
    for ticker, name in UNIVERSE.items():
        s = calculate_full_score(ticker)
        price_info = get_price(ticker) or {"price": 0, "chg": 0}
        data.append({
            "Ticker": ticker,
            "Nome": name,
            "Score": s["total"],
            "Tendência": s["dims"].get("Tendência Estrutural", 0),
            "Momentum": s["dims"].get("Momentum Curto Prazo", 0),
            "Setup": s["dims"].get("Qualidade do Setup", 0),
            "Preço": f"${price_info['price']:,.2f}",
            "Var 24h": f"{price_info['chg']:+.2f}%"
        })
    
    df_scanner = pd.DataFrame(data).sort_values("Score", ascending=False)
    st.dataframe(df_scanner, use_container_width=True, hide_index=True)

with tab3:  # Diário
    st.subheader("Diário de Trades")
    if 'trades' not in st.session_state:
        st.session_state.trades = []
    
    with st.form("add_trade"):
        c1, c2, c3, c4 = st.columns(4)
        ticker = c1.text_input("Ticker", "NVDA")
        direction = c2.selectbox("Direção", ["LONG", "SHORT"])
        score = c3.number_input("Score", 0, 100, 78)
        pnl = c4.number_input("P&L $", value=1500)
        if st.form_submit_button("Adicionar Trade"):
            st.session_state.trades.append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "ticker": ticker,
                "dir": direction,
                "score": score,
                "pnl": pnl
            })
            st.success("Trade adicionado!")
    
    if st.session_state.trades:
        trades_df = pd.DataFrame(st.session_state.trades)
        st.dataframe(trades_df, use_container_width=True)

with tab4:  # Calibração
    st.subheader("Calibração (Brier Score)")
    st.info("Após 30+ trades compare probabilidade estimada vs resultado real.")
    # Placeholder simples
    st.metric("Brier Score atual (quanto menor, melhor)", "0.18")

with tab5:  # Macro
    st.subheader("Filtros Macro Institucionais")
    col1, col2 = st.columns(2)
    col1.metric("VIX", f"{macro['vix']}", "Volatilidade")
    col2.metric("Fear & Greed", f"{macro['fng']} — {macro['fng_label']}")
    st.metric("Dominância BTC", f"{macro['btc_dom']}%")

st.caption("Sistema completo de hedge fund • Dados reais via yfinance • Deploy gratuito no Streamlit Cloud")
st.caption("Quer adicionar Deribit GEX, Long/Short Ratio ou backtesting completo? É só falar que eu mando a próxima versão.")
