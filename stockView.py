import streamlit as st

import database as db
import yfinance as yf
import datetime as dt
from datetime import datetime

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(layout="wide", page_title="Seleção de Ações")

st.markdown("""
<style>
    /* Remove padding padrão do Streamlit */
    .block-container { padding: 2rem 2rem 1.5rem 2rem; }

    /* Painel esquerdo — lista de ações */
    .stock-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 12px;
        border-radius: 8px;
        margin-bottom: 4px;
        cursor: pointer;
        font-size: 14px;
        transition: background 0.15s;
    }
    .stock-item:hover { background: #f0f4ff; }
    .stock-item.selected { background: #e8f0fe; font-weight: 600; color: #1a56db; }
    .stock-ticker { font-weight: 600; }
    .stock-price { color: #555; font-size: 13px; }

    /* Cartões de indicadores */
    .ind-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        margin-top: 1rem;
    }
    .ind-card {
        background: #f8f9fb;
        border-radius: 10px;
        padding: 14px 16px;
    }
    .ind-label { font-size: 12px; color: #888; margin-bottom: 4px; }
    .ind-value { font-size: 20px; font-weight: 600; color: #111; }

    /* Variação do preço */
    .chg-pos { color: #0f9d58; font-size: 13px; font-weight: 500; }
    .chg-neg { color: #d93025; font-size: 13px; font-weight: 500; }

    /* Divider entre colunas */
    .col-divider {
        border-left: 1px solid #e8eaed;
        padding-left: 2rem;
    }
</style>
""", unsafe_allow_html=True)


# ── Funções de dados ────────────────────────────────────────────────────────

@st.cache_data(ttl=300)  # cache de 5 minutos
def buscar_acoes_disponiveis(bolsa) -> list[str]:
    return db.selecionar_tickers(bolsa) # Retorna apenas o nome dos tickers

@st.cache_data(ttl=60)  # cache de 1 minuto
def buscar_dados_acao(ticker: str, data: str = '2026-04-29') -> dict:
    ticker = f"{ticker}.SA"
    ticker_dict = {"preco": 0.0, "variacao": 0.0, "pl": None, "dy": None, "pvp": None, "roe": None, "historico": []}
    if ticker is None or "":
        return ticker_dict
    try:
        ticker_obj = yf.Ticker(ticker)
        ticker_info = ticker_obj.info #Para os indicadores

        #Cálculo de preço
        data_ref = datetime.strptime(data, "%Y-%m-%d")
        data_ini = data_ref - dt.timedelta(days=10) #Busca até 10 dias anteriores ao dia passado
        hist_10d_df = ticker_obj.history(start=data_ini, end=data_ref + dt.timedelta(days=1))
        if hist_10d_df.empty:
            print(f"Ticker {ticker} inexistente")
            return ticker_dict
        closes = hist_10d_df["Close"].dropna() #Últimos 10 fechamentos
        preco_acao_float = float(closes.iloc[-1]) #Pega o preço mais recente disponível
        print(f"Preço da ação {ticker}: {preco_acao_float if preco_acao_float != 0.00 else '0.00'} no dia {data}")
        ticker_dict["preco"] = preco_acao_float

        # Variação (compara o último fechamento com o penúltimo disponível)
        if len(closes) >= 2:
            preco_anterior = float(closes.iloc[-2])
            ticker_dict["variacao"] = ((preco_acao_float - preco_anterior) / preco_anterior) * 100

        # Histórico de 60 dias para o gráfico
        hist_60d_df = ticker_obj.history(period="60d")
        if not hist_60d_df.empty:
            ticker_dict["historico"] = hist_60d_df["Close"].dropna().reset_index().rename(
                columns={"Date": "data", "Close": "preco"}
            ).to_dict(orient="records")

        # P/L (Price-to-Earnings)
        pl = ticker_info.get("trailingPE") or ticker_info.get("forwardPE")
        ticker_dict["pl"] = round(pl, 2) if pl else None

        # Dividend Yield (valor de dividendos nos últimos 12 meses)
        dy = ticker_info.get("trailingAnnualDividendYield")
        ticker_dict["dy"] = round(dy * 100, 2) if dy else None

        # P/VP (Price-to-Book)
        pvp = ticker_info.get("priceToBook")
        ticker_dict["pvp"] = round(pvp, 2) if pvp else None

        # ROE (Return on Equity — também em decimal)
        roe = ticker_info.get("returnOnEquity")
        ticker_dict["roe"] = round(roe * 100, 2) if roe else None

    except ValueError as ve:
        print(ve)
        return ticker_dict
    return ticker_dict

# ── Estado da sessão ────────────────────────────────────────────────────────
if "acao_selecionada" not in st.session_state:
    st.session_state.acao_selecionada = None

# ── Layout principal ────────────────────────────────────────────────────────
acoes = buscar_acoes_disponiveis("B3")

col_lista, col_detalhe = st.columns([1, 2], gap="large")

# ── Coluna esquerda: lista de ações ────────────────────────────────────────
with col_lista:
    st.markdown("#### Ações disponíveis")

    busca = st.selectbox("", placeholder="Buscar ticker ou empresa...", label_visibility="collapsed", options=buscar_acoes_disponiveis('B3'))

    acoes_filtradas = [
        a for a in acoes
        if busca.upper() in a #or busca.lower() in a["nome"].lower()
    ] if busca else acoes

    for acao in acoes_filtradas:
        dados = buscar_dados_acao(acao)
        preco = dados.get("preco", 0)
        variacao = dados.get("variacao", 0)
        selecionada = st.session_state.acao_selecionada == acao
        cor_var = "#0f9d58" if variacao >= 0 else "#d93025"
        sinal = "+" if variacao >= 0 else ""

        # Cada item é um botão estilizado
        label = f"""
        <div style="display:flex; justify-content:space-between; align-items:center; width:100%;">
            <div>
                <span style="font-weight:600; font-size:14px;">{acao}</span><br>
                <!-- <span style="font-size:12px; color:#888;">{acao}</span> -->
            </div>
            <div style="text-align:right;">
                <span style="font-size:14px; font-weight:500;">R$ {preco:.2f}</span><br>
                <span style="font-size:12px; color:{cor_var};">{sinal}{variacao:.2f}%</span>
            </div>
        </div>
        """

        # Botão com borda destacada se selecionado
        border = "2px solid #1a56db" if selecionada else "1px solid #e8eaed"
        bg = "#eef2ff" if selecionada else "transparent"

        st.markdown(
            f'<div style="background:{bg}; border:{border}; border-radius:10px; '
            f'padding:10px 14px; margin-bottom:6px;">{label}</div>',
            unsafe_allow_html=True
        )

        # Botão invisível por cima para capturar o clique
        if st.button(f"Selecionar {acao}", key=f"btn_{acao}", use_container_width=True):
            st.session_state.acao_selecionada = acao
            st.rerun()

        # Esconde o botão visualmente (ele fica por cima do card)
        st.markdown(f"""
        <style>
            div[data-testid="stButton"] button[kind="secondary"]:has(+ *) {{}}
            [data-testid="stBaseButton-secondary"][aria-label="Selecionar {acao}"] {{
                position: relative;
                margin-top: -58px;
                opacity: 0;
                height: 54px;
                cursor: pointer;
            }}
        </style>
        """, unsafe_allow_html=True)


# ── Coluna direita: detalhes da ação ───────────────────────────────────────
with col_detalhe:

    if st.session_state.acao_selecionada is None:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.info("Selecione uma ação na lista para ver os detalhes.")

    else:
        ticker = st.session_state.acao_selecionada
        acao_info = next((a for a in acoes if a == ticker), {})
        dados = buscar_dados_acao(ticker)

        preco = dados.get("preco", 0)
        variacao = dados.get("variacao", 0)
        pl = dados.get("pl")
        dy = dados.get("dy")
        pvp = dados.get("pvp")
        roe = dados.get("roe")

        # Cabeçalho
        col_h1, col_h2 = st.columns([2, 1])
        with col_h1:
            st.markdown(f"### {ticker}")
            sinal = "+" if variacao >= 0 else ""
            cor = "chg-pos" if variacao >= 0 else "chg-neg"
            st.markdown(
                f"<span style='font-size:26px; font-weight:700;'>R$ {preco:.2f}</span> &nbsp;"
                f"<span class='{cor}' style='font-size:15px;'>{sinal}{variacao:.2f}% hoje</span>",
                unsafe_allow_html=True
            )

        with col_h2:
            st.markdown(f"<div style='padding-top:8px; color:#888; font-size:13px;'>Ticker</div>"
                        f"<div style='font-size:20px; font-weight:700;'>{ticker}</div>",
                        unsafe_allow_html=True)

        st.divider()

        # Gráfico histórico (usando st.line_chart — substitua por Plotly se quiser mais controle)
        st.markdown("**Histórico de preços (simulado)**")

        import pandas as pd
        import numpy as np

        np.random.seed(hash(ticker) % 2**32)
        historico = pd.DataFrame({
            "Preço (R$)": (preco * (1 + np.cumsum(np.random.randn(60) * 0.01)))[::-1]
        }, index=pd.date_range(end=pd.Timestamp.today(), periods=60, freq="D"))

        st.line_chart(historico, height=220, use_container_width=True)

        # Indicadores fundamentalistas
        st.markdown("**Indicadores fundamentalistas**")

        i1, i2, i3, i4 = st.columns(4)

        def fmt_ind(valor, sufixo=""):
            if valor is None:
                return "—"
            return f"{valor:.2f}{sufixo}"

        with i1:
            st.metric("P/L", fmt_ind(pl, "x"))
        with i2:
            st.metric("Div. Yield", fmt_ind(dy, "%"))
        with i3:
            st.metric("P/VP", fmt_ind(pvp, "x"))
        with i4:
            st.metric("ROE", fmt_ind(roe, "%"))

        st.divider()

        # Botão de confirmação
        col_b1, col_b2 = st.columns([2, 1])
        with col_b1:
            if st.button(f"Confirmar seleção de {ticker}", type="primary", use_container_width=True):
                st.success(f"Ação {ticker} selecionada com sucesso!")
                # Aqui você continua o fluxo da sua aplicação
                # Ex: salvar no session_state, ir para próxima etapa, etc.
        with col_b2:
            if st.button("Limpar seleção", use_container_width=True):
                st.session_state.acao_selecionada = None
                st.rerun()