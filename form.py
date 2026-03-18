import streamlit as st
import database as db
import yfinance as yf
import datetime as dt
from datetime import datetime

if "mostrar_form" not in st.session_state:
    st.session_state["mostrar_form"] = False

@st.cache_data()
def inicializacao():
    lista_bolsa = db.selecionar_bolsas()
    print(lista_bolsa)
    return lista_bolsa

contratos_id = db.selecionar_contrato_id()
bolsas_str = db.selecionar_bolsas()
lista_bolsa = inicializacao()

@st.cache_data(show_spinner=False, ttl="6h")
def preco_acao_data(ticker: str, data: str):
    if ticker is not None or "":
        ticker_obj = yf.Ticker(ticker)
        data = datetime.strptime(data, "%Y-%m-%d")
        dado = ticker_obj.history(start=data, end=data+dt.timedelta(days=1))
        return float(dado["Close"].iloc[0]) if not dado.empty else 0.00
    else:
        return None

def st_trocar_form():
    st.session_state["mostrar_form"] = not st.session_state["mostrar_form"]

def st_enviar_form():
    if not st.session_state["ticker_ms"]:
        st.error("Não foi registrado nenhum ticker!")
    else:
        montante_total = 0.00

        for montante in st.session_state["ticker_ms"]:
            montante_total += st.session_state[f"montante_{montante}"]
        contrato_id = db.inserir_contrato(montante_total, str(st.session_state["data_di"]), st.session_state["duracao_ni"])
        db.inserir_taxa(contrato_id, st.session_state["indexador_sb"], st.session_state["spread_ni"])

        for t in st.session_state["ticker_ms"]:
            db.inserir_acao(contrato_id, t, st.session_state["bolsa_sb"], st.session_state[f"qtd_compra_{t}"], st.session_state[f"montante_{t}"])
        st.success("Contrato adicionado com sucesso!")

#Começo
st.title("Contratos")
""
st.write("Adicionar contrato")

st.button("Adicionar contrato", on_click=st_trocar_form)

enviado = False
if st.session_state.mostrar_form:
    st.date_input("Coloque a data de início", key="data_di", format="DD/MM/YYYY")
    bolsa = st.selectbox("Selecione a Bolsa", lista_bolsa, key="bolsa_sb", index=None, placeholder="")

    lista_ticker = db.selecionar_tickers(bolsa)

    st.multiselect("Selecione o Ticker", lista_ticker, placeholder="", accept_new_options=True, key="ticker_ms", disabled=(lista_ticker is None))
    for ticker in st.session_state["ticker_ms"]:
        valor_acao = preco_acao_data(ticker, st.session_state["data_di"])
        qtd = st.number_input(f"Quantidade de ações de {ticker}", min_value=0, key=f"qtd_compra_{ticker}")
        montante = valor_acao * qtd
        st.number_input(f"Valor do montante de {ticker}", min_value=0.00, key=f"montante_{ticker}", value=montante)
    st.number_input("Duração do contrato em meses", min_value=0, key="duracao_ni")
    st.write("Taxas")
    st.selectbox("Selecione o indexador", ["CDI", "SELIC"], index=None, placeholder="", key="indexador_sb")
    st.number_input("Spread em (%)", min_value=0.0, key="spread_ni")
    if st.button("Adicionar", disabled=(st.session_state["spread_ni"] == 0)):
        st_enviar_form()
        st_trocar_form()

with st.expander("Adicionar Movimentação"):
    tipo = st.radio("Selecione o tipo de movimentação", options=["Compra", "Venda"], horizontal=True)
    contrato_id = st.selectbox("Selecione o contrato", options=contratos_id, key="contrato_id")
    if not contratos_id:
        st.error("Não tem contratos cadastrados")
    bolsa_str = st.selectbox("Selecione a bolsa", options=bolsas_str)
    ticker_str = st.text_input("Selecione o ticker")
    data = st.date_input("Coloque a data desejada", format="DD/MM/YYYY", key="data_di_2")
    ticker_qtd = st.number_input("Selecione a quantidade", min_value=0)
    ticker_valor = st.number_input("Selecione o valor de cada ação", min_value=0.00, placeholder="", value=float(f"{preco_acao_data(ticker_str, str(data)):.2f}"))
    taxa_unica = st.number_input("Selecione o valor da taxa de transação (se houver)", min_value=0.00, placeholder="")
    st.caption(f"Valor final: {(ticker_valor*ticker_qtd)+taxa_unica:.2f}")
    if st.button("Registrar movimentação"):
        if tipo == "Compra":
            tipo = 0
        else:
            tipo = 1
        if db.inserir_movimentacao(contrato_id, bolsa_str, ticker_str, ticker_qtd, ticker_valor*ticker_qtd, data.strftime("%Y-%m-%d"), tipo):
            st.success("Movimentação registrada com sucesso")
        else:
            st.error("Não foi possível fazer a movimentação")