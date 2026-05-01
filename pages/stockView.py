import streamlit as st
from pandas import DataFrame
import database as db
from database.utils import to_monetary_decimal
import yfinance as yf
import datetime as dt
from datetime import datetime
from decimal import Decimal
import textwrap

# ── Métodos
@st.cache_data(ttl=300)  # cache de 5 minutos
def buscar_dados_acao(ticker: str, bolsa_sulfixo: str, datahora: datetime) -> dict:
    ticker = f"{ticker}{bolsa_sulfixo}"
    ticker_dict = {"preco": Decimal('0'), "variacao": Decimal('0'), "pl": None, "dy": None, "pvp": None, "roe": None, "historico": DataFrame()}
    if not ticker:
        return ticker_dict
    try:
        ticker_obj = yf.Ticker(ticker)
        ticker_info = ticker_obj.info #Para os indicadores

        #Cálculo de preço
        data_ini = datahora - dt.timedelta(days=10) #Busca até 10 dias anteriores ao dia passado
        hist_10d_df = ticker_obj.history(start=data_ini, end=datahora + dt.timedelta(days=1))
        if hist_10d_df.empty:
            print(f"Ticker {ticker} inexistente")
            return ticker_dict
        closes = hist_10d_df["Close"].dropna() #Últimos 10 fechamentos
        datahora_str = datahora.strftime("%d/%m/%Y %H:%M")
        preco_ticker_dec = Decimal(str(closes.iloc[-1])) #Pega o preço mais recente disponível
        print(f"Preço da ação {ticker}: {to_monetary_decimal(preco_ticker_dec) if preco_ticker_dec else '0.00'} em {datahora_str}")
        ticker_dict["preco"] = preco_ticker_dec

        # Variação (compara o último fechamento com o penúltimo disponível)
        if len(closes) >= 2:
            preco_anterior = Decimal(str(closes.iloc[-2]))
            ticker_dict["variacao"] = ((preco_ticker_dec - preco_anterior) / preco_anterior) * 100

        # Histórico de 60 dias para o gráfico
        hist_60d_df = ticker_obj.history(period="60d")
        if not hist_60d_df.empty:
            ticker_dict["historico"] = hist_60d_df["Close"].dropna().reset_index().rename(
                columns={"Date": "data", "Close": "preco"})

        # P/L (Price-to-Earnings)
        pl = ticker_info.get("trailingPE") or ticker_info.get("forwardPE")
        ticker_dict["pl"] = round(pl, 2) if pl else None

        # Dividend Yield (valor de dividendos nos últimos 12 meses comparado ao preço atual)
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

def fmt_ind(valor, sufixo=""):
    if valor is None:
        return "—"
    return f"{valor:.2f}{sufixo}"

def enviar():
    st.session_state.tickers_selecionados = [
        {
            "ti_ticker": ticker_obj["ti_ticker"],
            "ti_empresa": ticker_obj["ti_empresa"],
            "valor": buscar_dados_acao(ticker_obj["ti_ticker"], bolsa["bo_sufixo"], datahora_datetime)["preco"],
        }
        for ticker in buscas_list
        for ticker_obj in tickers_list
        if ticker.split(" - ")[0] == ticker_obj["ti_ticker"]
    ]
    st.switch_page("form.py")

# ── Configuração da página
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

# ── Configuração inicial
if "init_stockView" not in st.session_state:
    st.session_state.init_stockView = True
    # ── Configuração de dados
    bolsa_str = st.session_state.bolsa_selecionada
    st.session_state.tickers_list = db.selecionar_tickers(bolsa_str)
    st.session_state.tickers_list_str = [ticker["ti_ticker"] for ticker in st.session_state.tickers_list]
    st.session_state.bolsa = db.selecionar_bolsa(bolsa_str)
    st.session_state.ticker_selecionado = None
    st.session_state.tickers_selecionados = []
    if not st.session_state.bolsa:
        st.error("Erro em selecionar_bolsa")
# Atribuição a variáveis para facilitar a leitura
tickers_list = st.session_state.tickers_list
tickers_list_str = st.session_state.tickers_list_str
bolsa = st.session_state.bolsa
datahora_datetime = st.session_state.datahora_selecionada

# ── Layout principal
col_lista, col_detalhe = st.columns([1, 2], gap="large")

# ── Coluna esquerda: lista de ações
with col_lista:
    st.markdown(f"#### Ações da {bolsa["bo_bolsa"]}")
    buscas_list = st.multiselect("", placeholder="Buscar ticker ou empresa...",
                                 label_visibility="collapsed",
                                 options=(textwrap.shorten(f"{ticker['ti_ticker']} - {ticker['ti_empresa']}", width=25, placeholder="...")
                                          for ticker in tickers_list),)

    if not buscas_list:
        st.info("Selecione um ou mais tickers...")
        st.stop()
    st.caption("Tickers selecionados:")
    for busca in buscas_list:
        ticker_nome, ticker_empresa = busca.split(" - ", maxsplit=1)
        ticker_empresa_srt = textwrap.shorten(ticker_empresa, width=20, placeholder="...")
        ticker = next(( t for t in tickers_list if t["ti_ticker"] == ticker_nome), None)
        if ticker is None:
            continue
        selecionado = st.session_state.get("ticker_selecionado") == ticker
        if st.button(
                f"**{ticker_nome}** — {ticker_empresa_srt}",
                key=f"btn_{ticker_nome}",
                use_container_width=True,
                type="primary" if selecionado else "secondary"
        ):
            st.session_state.ticker_selecionado = ticker
            st.rerun()

# ── Coluna direita: detalhes da ação
if st.session_state.ticker_selecionado:
    with col_detalhe:
        if st.button("Confirmar Tickers", type="primary"):
            enviar()
        ticker = st.session_state.ticker_selecionado
        # detalhes da ação
        dados = buscar_dados_acao(ticker["ti_ticker"], bolsa["bo_sufixo"], datahora_datetime)

        preco = dados.get("preco", 0)
        variacao = dados.get("variacao", 0)
        pl = dados.get("pl")
        dy = dados.get("dy")
        pvp = dados.get("pvp")
        roe = dados.get("roe")

        # Cabeçalho
        col_h1, col_h2 = st.columns([2, 1])
        with col_h1:
            st.markdown(f"### {ticker["ti_empresa"]}")
            sinal = "+" if variacao >= 0 else ""
            cor = "chg-pos" if variacao >= 0 else "chg-neg"
            st.markdown(
                f"<span style='font-size:26px; font-weight:700;'>{bolsa["bo_moeda"]} {preco:.2f}</span> &nbsp;"
                f"<span class='{cor}' style='font-size:15px;'>{sinal}{variacao:.2f}% hoje</span>",
                unsafe_allow_html=True
            )

        with col_h2:
            st.markdown(f"<div style='padding-top:8px; color:#888; font-size:13px;'>Ticker</div>"
                        f"<div style='font-size:20px; font-weight:700;'>{ticker["ti_ticker"]}</div>",
                        unsafe_allow_html=True)

        st.divider()

        # Gráfico histórico (usando st.line_chart — substitua por Plotly se quiser mais controle)
        st.markdown("**Histórico de preços dos últimos 60 dias**")

        st.line_chart(dados["historico"], x="data", x_label="Data", y="preco", y_label=f"Preço ({bolsa['bo_moeda']})", height=220, use_container_width=True)

        # Indicadores fundamentalistas
        st.markdown("**Indicadores fundamentalistas**")

        i1, i2, i3, i4 = st.columns(4)

        with i1:
            st.metric("P/L", fmt_ind(pl, "x"))
        with i2:
            st.metric("Div. Yield", fmt_ind(dy, "%"))
        with i3:
            st.metric("P/VP", fmt_ind(pvp, "x"))
        with i4:
            st.metric("ROE", fmt_ind(roe, "%"))