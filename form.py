import streamlit as st
import database as db
import yfinance as yf
import datetime as dt

if "mostrar_form" not in st.session_state:
    st.session_state["mostrar_form"] = False
elif "lista_bolsa" not in st.session_state:
    lista_bolsa = db.selecionar_bolsas()
    st.session_state["lista_bolsa"] = lista_bolsa

def preco_acao_data(ticker, data):
    dados = yf.download(ticker, start=data, end=data + dt.timedelta(days=1))
    return dados["Open"].iloc[0]

def st_trocar_form():
    st.session_state["mostrar_form"] = not st.session_state["mostrar_form"]

def st_enviar_form():
    if not st.session_state["ticker_ms"]:
        st.error("Não foi registrado nenhum ticker!")
    else:
        montante_total = 0
        for montante in st.session_state["ticker_ms"]:
            montante_total += st.session_state[f"montante_{montante}"]

        contrato_id = db.inserir_contrato(
            montante_total, st.session_state["data_di"], st.session_state["duracao_ni"])
        #Inserir também a taxa
        for t in st.session_state["ticker_ms"]:
            db.inserir_acao(contrato_id, t, st.session_state["bolsa_sb"], st.session_state[f"qtd_compra_{t}"], st.session_state[f"montante_{t}"])
        st.success("Contrato adicionado com sucesso!")

st.title("Contratos")
""
st.write("Adicionar contrato")

st.button("Adicionar contrato", on_click=st_trocar_form)

enviado = False
if st.session_state.mostrar_form:
    st.date_input("Coloque a data de início", key="data_di", format="DD/MM/YYYY")
    st.selectbox("Selecione a Bolsa", lista_bolsa, key="bolsa_sb", index=None, placeholder="")

    if st.session_state["bolsa_sb"] == "B3":
         lista_ticker = lista_ticker_b3
    elif st.session_state["bolsa_sb"] == "NASDAQ":
         lista_ticker = lista_ticker_nasdaq
    else:
        lista_ticker = None

    st.multiselect("Selecione o Ticker", lista_ticker, placeholder="", accept_new_options=True, key="ticker_ms", disabled=(lista_ticker is None))
    for ticker in st.session_state["ticker_ms"]:
        st.number_input(f"Quantidade de ações de {ticker}", min_value=0, key=f"qtd_compra_{ticker}")
        st.number_input(f"Valor do montante de {ticker}", min_value=0.00, key=f"montante_{ticker}", value=(preco_acao_data(ticker, st.session_state["data_di"])*st.session_state[f"qtd_compra_{ticker}"]))
    st.number_input("Duração do contrato em meses", min_value=0, key="duracao_ni")
    st.write("Taxas")
    st.selectbox("Selecione o indexador", ["CDI", "SELIC"], index=None, placeholder="", key="indexador_sb")
    st.number_input("Spread em (%)", min_value=0.0, key="spread_ni")
    if st.button("Adicionar", disabled=(st.session_state["spread_ni"] == 0)):
        st_enviar_form()
        st_trocar_form()